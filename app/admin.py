from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import User, Notification

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


def notify_admin(message: str, type: str = "info"):
    try:
        new_notification = Notification(user_id=current_user.id, message=message, type=type)
        db.session.add(new_notification)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


@admin_bp.context_processor
def inject_notifications():
    if current_user.is_authenticated and current_user.role == "admin":
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(15).all()
        unread_count = sum(1 for n in notifs if not n.is_read)
        
        if unread_count > 0:
            for n in notifs:
                n.is_read = True
            db.session.commit()
            
        return {"admin_notifications": notifs, "admin_unread_count": unread_count}
    return {}


@admin_bp.route("/")
@admin_required
def dashboard():
    search_query = request.args.get("q", "").strip()
    
    query = User.query.filter_by(is_approved=False, is_blacklisted=False)
    if search_query:
        query = query.filter((User.username.ilike(f"%{search_query}%")) | (User.email.ilike(f"%{search_query}%")))
        
    pending_users = query.all()
    total_users = User.query.filter_by(is_approved=True, is_blacklisted=False).count()
    return render_template("admin/dashboard.html", pending_users=pending_users, total_users=total_users, active_page="Dashboard", search_query=search_query)


@admin_bp.route("/approve/<int:user_id>", methods=["POST"])
@admin_required
def approve_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    user.is_approved = True
    db.session.commit()
    notify_admin(f"User '{user.username}' has been approved.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/reject/<int:user_id>", methods=["POST"])
@admin_required
def reject_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    notify_admin(f"User '{user.username}' registration has been rejected.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users")
@admin_required
def manage_users():
    users = User.query.filter(User.id != current_user.id).order_by(User.created_at.desc()).all()
    return render_template("admin/manage_users.html", users=users, active_page="Manage Users")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot edit your own account from here.", "danger")
        return redirect(url_for("admin.manage_users"))

    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        new_email = request.form.get("email", "").strip()
        new_role = request.form.get("role", "employee")

        if new_role not in ("employee", "manager", "admin"):
            notify_admin("Invalid role.", "danger")
            return render_template("admin/edit_user.html", user=user)

        existing = User.query.filter(User.email == new_email, User.id != user.id).first()
        if existing:
            notify_admin("Email already in use.", "danger")
            return render_template("admin/edit_user.html", user=user)

        user.username = new_username
        user.email = new_email
        user.role = new_role
        user.is_active = "is_active" in request.form
        user.is_approved = "is_approved" in request.form
        db.session.commit()
        notify_admin(f"User '{user.username}' updated.", "success")
        return redirect(url_for("admin.manage_users"))

    return render_template("admin/edit_user.html", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.manage_users"))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    notify_admin(f"User '{username}' has been deleted.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@admin_required
def blacklist_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        notify_admin("You cannot blacklist yourself.", "danger")
        return redirect(url_for("admin.manage_users"))
    user.is_blacklisted = True
    user.is_active = False
    db.session.commit()
    notify_admin(f"User '{user.username}' has been blacklisted.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/reset-credentials")
@admin_required
def reset_credentials():
    query = request.args.get("q", "").strip()
    users = None
    if query:
        users = User.query.filter(
            (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
        ).all()
    return render_template("admin/reset_credentials.html", users=users, query=query)


@admin_bp.route("/reset-password/<int:user_id>", methods=["POST"])
@admin_required
def do_reset_password(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    new_password = request.form.get("new_password", "")
    if len(new_password) < 6:
        notify_admin("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.reset_credentials", q=user.username))
    user.set_password(new_password)
    db.session.commit()
    notify_admin(f"Password for '{user.username}' has been reset.", "success")
    return redirect(url_for("admin.reset_credentials", q=user.username))


@admin_bp.route("/force-logout/<int:user_id>", methods=["POST"])
@admin_required
def force_logout(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    user.is_active = False
    db.session.commit()
    notify_admin(f"User '{user.username}' has been force-logged out (account deactivated). Re-activate via Manage Users.", "success")
    return redirect(url_for("admin.reset_credentials", q=user.username))


@admin_bp.route("/blacklisted")
@admin_required
def blacklisted_users():
    users = User.query.filter_by(is_blacklisted=True).order_by(User.updated_at.desc()).all()
    return render_template("admin/blacklisted_users.html", users=users, active_page="Blacklisted Users")


@admin_bp.route("/whitelist/<int:user_id>", methods=["POST"])
@admin_required
def whitelist_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    user.is_blacklisted = False
    user.is_active = True
    db.session.commit()
    notify_admin(f"User '{user.username}' has been whitelisted.", "success")
    return redirect(url_for("admin.blacklisted_users"))
