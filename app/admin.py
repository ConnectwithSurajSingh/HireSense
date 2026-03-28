"""
app/admin.py

Admin Blueprint - User management, approvals, and audit features.

NLP integration points
──────────────────────
• nlp_stats()          – new route: aggregated NLP parse statistics across
  all resumes (total parsed, success/failure breakdown, skill extraction
  coverage).  Gives admins visibility into NLP health.

• re_parse_all_resumes() – new route: bulk re-triggers the NLP pipeline
  on every resume in the system (e.g. after a model upgrade).

All other admin routes are preserved exactly as before.
"""

import csv
import json
import logging
from datetime import datetime
from functools import wraps
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.models import Notification, Resume, User
from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------


def admin_required(f):
    """Restrict route to authenticated users with the 'admin' role."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------


def notify_admin(message: str, type: str = "info") -> None:
    """Persist an in-app notification for the current admin user."""
    try:
        db.session.add(
            Notification(user_id=current_user.id, message=message, type=type)
        )
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()


@admin_bp.context_processor
def inject_notifications():
    """Inject unread notifications into every admin template context."""
    if current_user.is_authenticated and current_user.role == "admin":
        notifs = (
            Notification.query.filter_by(user_id=current_user.id)
            .order_by(Notification.created_at.desc())
            .limit(15)
            .all()
        )
        unread_count = sum(1 for n in notifs if not n.is_read)

        if unread_count > 0:
            for n in notifs:
                n.is_read = True
            db.session.commit()

        return {"admin_notifications": notifs, "admin_unread_count": unread_count}
    return {}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin dashboard: pending approvals and headline user stats."""
    search_query = request.args.get("q", "").strip()

    query = User.query.filter_by(is_approved=False, is_blacklisted=False)
    if search_query:
        query = query.filter(
            (User.username.ilike(f"%{search_query}%"))
            | (User.email.ilike(f"%{search_query}%"))
        )

    pending_users = query.all()
    total_users   = User.query.filter_by(is_approved=True, is_blacklisted=False).count()

    return render_template(
        "admin/dashboard.html",
        pending_users=pending_users,
        total_users=total_users,
        active_page="Dashboard",
        search_query=search_query,
    )


# ---------------------------------------------------------------------------
# NLP Statistics  (new – admin visibility into NLP pipeline health)
# ---------------------------------------------------------------------------


@admin_bp.route("/nlp-stats")
@admin_required
def nlp_stats():
    """
    Aggregated NLP parsing statistics across all employee resumes.

    Metrics surfaced:
      • Total resumes on file.
      • Resumes with a successful NLP parse.
      • Resumes with a failed / degraded parse.
      • Resumes not yet parsed.
      • Average number of skills extracted per successful parse.
      • Per-status breakdown list for the table view.
    """
    all_resumes = Resume.query.all()

    total        = len(all_resumes)
    success      = 0
    degraded     = 0
    failed       = 0
    not_parsed   = 0
    total_skills = 0
    detail_rows  = []

    for resume in all_resumes:
        row = {
            "user_id":           resume.user_id,
            "username":          resume.user.username if resume.user else "—",
            "original_filename": resume.original_filename,
            "last_updated":      resume.last_updated,
            "nlp_status":        "not_parsed",
            "skill_count":       0,
            "parsed_at":         None,
        }

        if resume.parsed_content:
            try:
                parsed            = json.loads(resume.parsed_content)
                status            = parsed.get("status", "unknown")
                skills_found      = len(parsed.get("extracted_skills", []))
                row["nlp_status"] = status
                row["skill_count"] = skills_found
                row["parsed_at"]  = parsed.get("parsed_at")

                if status == "success":
                    success      += 1
                    total_skills += skills_found
                elif "degraded" in status:
                    degraded += 1
                else:
                    failed += 1
            except (json.JSONDecodeError, TypeError):
                row["nlp_status"] = "parse_error"
                failed += 1
        else:
            not_parsed += 1

        detail_rows.append(row)

    avg_skills = round(total_skills / success, 1) if success else 0

    stats = {
        "total":      total,
        "success":    success,
        "degraded":   degraded,
        "failed":     failed,
        "not_parsed": not_parsed,
        "avg_skills": avg_skills,
    }

    return render_template(
        "admin/nlp_stats.html",
        stats=stats,
        detail_rows=detail_rows,
        active_page="NLP Stats",
    )


@admin_bp.route("/nlp-stats/reparse-all", methods=["POST"])
@admin_required
def reparse_all_resumes():
    """
    Bulk re-trigger the NLP pipeline on every resume in the system.

    Runs synchronously – for large datasets consider moving this to a
    Celery task.  Progress is tracked and summarised in a flash message.
    """
    all_resumes = Resume.query.all()

    success_count = 0
    fail_count    = 0

    for resume in all_resumes:
        if not resume.file_path:
            continue
        try:
            parsed    = ResumeService.parse_resume_skills(resume.id)
            extracted = parsed.get("extracted_skills", [])
            ResumeService.sync_parsed_skills_to_profile(
                resume.user_id, extracted, default_proficiency=2
            )
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Bulk reparse failed for resume id=%d: %s", resume.id, exc
            )
            fail_count += 1

    notify_admin(
        f"Bulk NLP re-parse complete: {success_count} succeeded, {fail_count} failed.",
        "success" if fail_count == 0 else "warning",
    )
    return redirect(url_for("admin.nlp_stats"))


@admin_bp.route("/nlp-stats/reparse/<int:resume_id>", methods=["POST"])
@admin_required
def reparse_single_resume(resume_id):
    """Re-trigger NLP parsing for a single resume by its ID."""
    resume = db.session.get(Resume, resume_id)
    if not resume:
        abort(404)

    try:
        parsed    = ResumeService.parse_resume_skills(resume.id)
        extracted = parsed.get("extracted_skills", [])
        added     = ResumeService.sync_parsed_skills_to_profile(
            resume.user_id, extracted, default_proficiency=2
        )
        notify_admin(
            f"Re-parsed resume for '{resume.user.username}': "
            f"{len(extracted)} skill(s) found, {added} new skill(s) added.",
            "success",
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Single reparse failed for resume id=%d: %s", resume_id, exc)
        notify_admin("NLP re-parse failed. Check server logs.", "danger")

    return redirect(url_for("admin.nlp_stats"))


# ---------------------------------------------------------------------------
# User export
# ---------------------------------------------------------------------------


@admin_bp.route("/users/export")
@admin_required
def export_users():
    """Stream a CSV export of users with optional role/status filters."""
    role_filter   = request.args.get("role_filter", "")
    status_filter = request.args.get("status_filter", "")

    query = User.query

    if role_filter:
        query = query.filter(User.role == role_filter)

    if status_filter == "approved":
        query = query.filter(User.is_approved.is_(True), User.is_blacklisted.is_(False))
    elif status_filter == "pending":
        query = query.filter(User.is_approved.is_(False), User.is_blacklisted.is_(False))
    elif status_filter == "blacklisted":
        query = query.filter(User.is_blacklisted.is_(True))

    def generate():
        data   = StringIO()
        writer = csv.writer(data)
        writer.writerow(["ID", "USERNAME", "EMAIL", "ROLE", "STATUS"])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for user in query:
            status = (
                "Blacklisted"
                if user.is_blacklisted
                else ("Approved" if user.is_approved else "Pending")
            )
            writer.writerow([user.id, user.username, user.email, user.role, status])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    return Response(
        stream_with_context(generate()),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=users_export.csv"},
    )


# ---------------------------------------------------------------------------
# User approval / rejection
# ---------------------------------------------------------------------------


@admin_bp.route("/approve/<int:user_id>", methods=["POST"])
@admin_required
def approve_user(user_id):
    """Approve a pending user registration."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    user.is_approved = True
    db.session.commit()
    notify_admin(f"User '{user.username}' has been approved.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/reject/<int:user_id>", methods=["POST"])
@admin_required
def reject_user(user_id):
    """Reject and delete a pending user registration."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    notify_admin(f"User '{user.username}' registration rejected.", "success")
    return redirect(url_for("admin.manage_users"))


# ---------------------------------------------------------------------------
# User management (list, edit, delete, blacklist)
# ---------------------------------------------------------------------------


@admin_bp.route("/users")
@admin_required
def manage_users():
    """Paginated user management table with role/status filters."""
    total_users       = User.query.filter_by(is_approved=True).count()
    pending_count     = User.query.filter_by(is_approved=False).count()
    blacklisted_count = User.query.filter_by(is_blacklisted=True).count()

    first_of_month = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    new_users_count = User.query.filter(User.created_at >= first_of_month).count()

    role_filter   = request.args.get("role_filter", "", type=str)
    status_filter = request.args.get("status_filter", "", type=str)
    per_page      = request.args.get("per_page", 10, type=int)
    page          = request.args.get("page", 1, type=int)

    query = User.query.filter(User.id != current_user.id)

    if role_filter:
        query = query.filter(User.role == role_filter)

    if status_filter == "approved":
        query = query.filter(User.is_approved.is_(True), User.is_blacklisted.is_(False))
    elif status_filter == "pending":
        query = query.filter(User.is_approved.is_(False), User.is_blacklisted.is_(False))
    elif status_filter == "blacklisted":
        query = query.filter(User.is_blacklisted.is_(True))

    pagination = query.order_by(User.created_at.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "admin/manage_users.html",
        users=pagination.items,
        user_pagination=pagination,
        total_users=total_users,
        pending_count=pending_count,
        blacklisted_count=blacklisted_count,
        new_users_count=new_users_count,
        active_page="Manage Users",
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    """Edit a user's username, email, role, and status flags."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot edit your own account from here.", "danger")
        return redirect(url_for("admin.manage_users"))

    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        new_email    = request.form.get("email", "").strip()
        new_role     = request.form.get("role", "employee")

        if new_role not in ("employee", "manager", "admin"):
            notify_admin("Invalid role.", "danger")
            return render_template("admin/edit_user.html", user=user)

        existing = User.query.filter(
            User.email == new_email, User.id != user.id
        ).first()
        if existing:
            notify_admin("Email already in use.", "danger")
            return render_template("admin/edit_user.html", user=user)

        user.username    = new_username
        user.email       = new_email
        user.role        = new_role
        user.is_active   = "is_active" in request.form
        user.is_approved = "is_approved" in request.form
        db.session.commit()
        notify_admin(f"User '{user.username}' updated.", "success")
        return redirect(url_for("admin.manage_users"))

    return render_template("admin/edit_user.html", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    """Permanently delete a user account."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.manage_users"))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    notify_admin(f"User '{username}' deleted.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@admin_required
def blacklist_user(user_id):
    """Blacklist a user (deactivates account)."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot blacklist yourself.", "danger")
        return redirect(url_for("admin.manage_users"))

    user.is_blacklisted = True
    user.is_active      = False
    db.session.commit()
    notify_admin(f"User '{user.username}' blacklisted.", "success")
    return redirect(url_for("admin.manage_users"))


# ---------------------------------------------------------------------------
# Credential reset
# ---------------------------------------------------------------------------


@admin_bp.route("/reset-credentials")
@admin_required
def reset_credentials():
    """Search for a user to reset credentials."""
    query = request.args.get("q", "").strip()
    users = None
    if query:
        users = User.query.filter(
            (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
        ).all()
    return render_template(
        "admin/reset_credentials.html", users=users, query=query
    )


@admin_bp.route("/reset-password/<int:user_id>", methods=["POST"])
@admin_required
def do_reset_password(user_id):
    """Reset a user's password (admin action)."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    new_password = request.form.get("new_password", "")
    if len(new_password) < 6:
        notify_admin("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.reset_credentials", q=user.username))

    user.set_password(new_password)
    db.session.commit()
    notify_admin(f"Password for '{user.username}' reset.", "success")
    return redirect(url_for("admin.reset_credentials", q=user.username))


@admin_bp.route("/force-logout/<int:user_id>", methods=["POST"])
@admin_required
def force_logout(user_id):
    """Force-logout a user by deactivating their account."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    user.is_active = False
    db.session.commit()
    notify_admin(
        f"User '{user.username}' force-logged out (account deactivated). "
        "Re-activate via Manage Users.",
        "success",
    )
    return redirect(url_for("admin.reset_credentials", q=user.username))


# ---------------------------------------------------------------------------
# Blacklist management
# ---------------------------------------------------------------------------


@admin_bp.route("/blacklisted")
@admin_required
def blacklisted_users():
    """List all blacklisted users."""
    users = (
        User.query.filter_by(is_blacklisted=True)
        .order_by(User.updated_at.desc())
        .all()
    )
    return render_template(
        "admin/blacklisted_users.html",
        users=users,
        active_page="Blacklisted Users",
    )


@admin_bp.route("/whitelist/<int:user_id>", methods=["POST"])
@admin_required
def whitelist_user(user_id):
    """Remove a user from the blacklist and reactivate their account."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    user.is_blacklisted = False
    user.is_active      = True
    db.session.commit()
    notify_admin(f"User '{user.username}' whitelisted.", "success")
    return redirect(url_for("admin.manage_users"))