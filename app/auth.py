from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from .models import User
from . import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _role_dashboard_url(user):
    if user.role == "admin":
        return url_for("admin.dashboard")
    elif user.role == "manager":
        return url_for("manager.dashboard")
    return url_for("employee.dashboard")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_role_dashboard_url(current_user))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html")

        if user.is_blacklisted:
            flash("Your account has been blacklisted. Contact an administrator.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Your account is deactivated. Contact an administrator.", "danger")
            return render_template("auth/login.html")

        if not user.is_approved:
            flash("Your account is pending admin approval.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=bool(request.form.get("remember")))
        next_page = request.args.get("next")
        return redirect(next_page or _role_dashboard_url(user))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(_role_dashboard_url(current_user))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "employee")

        if role not in ("manager", "employee"):
            flash("Invalid role.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register.html")

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
