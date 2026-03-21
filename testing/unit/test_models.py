"""
Unit tests for database models (User, Notification).

This module tests the User and Notification model functionality including
password hashing, user creation, relationships, and model methods.
"""

import pytest
from datetime import datetime
from app.models import User, Notification
from app import db


class TestUserModel:
    """Test suite for User model."""

    def test_user_creation(self, db_session):
        """Test basic user creation with required fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            role="employee",
        )
        user.set_password("SecurePass123")
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "employee"
        assert user.is_active is True
        assert user.is_approved is False
        assert user.is_blacklisted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_set_password(self, db_session):
        """Test password hashing functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            role="employee",
        )
        user.set_password("MyPassword123")
        db_session.add(user)
        db_session.commit()

        assert user.password_hash is not None
        assert user.password_hash != "MyPassword123"
        assert len(user.password_hash) > 20

    def test_check_password_correct(self, db_session):
        """Test password verification with correct password."""
        user = User(
            username="testuser",
            email="test@example.com",
            role="employee",
        )
        user.set_password("CorrectPassword123")
        db_session.add(user)
        db_session.commit()

        assert user.check_password("CorrectPassword123") is True

    def test_check_password_incorrect(self, db_session):
        """Test password verification with incorrect password."""
        user = User(
            username="testuser",
            email="test@example.com",
            role="employee",
        )
        user.set_password("CorrectPassword123")
        db_session.add(user)
        db_session.commit()

        assert user.check_password("WrongPassword") is False

    def test_user_email_uniqueness(self, db_session):
        """Test that email field enforces uniqueness constraint."""
        user1 = User(
            username="user1",
            email="duplicate@example.com",
            role="employee",
        )
        user1.set_password("Pass123")
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            username="user2",
            email="duplicate@example.com",
            role="manager",
        )
        user2.set_password("Pass456")
        db_session.add(user2)

        with pytest.raises(Exception):
            db_session.commit()

    def test_user_default_values(self, db_session):
        """Test default values for user fields."""
        user = User(
            username="defaultuser",
            email="default@example.com",
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        assert user.role == "employee"
        assert user.is_active is True
        assert user.is_approved is False
        assert user.is_blacklisted is False

    def test_user_role_assignment(self, db_session):
        """Test different role assignments (admin, manager, employee)."""
        roles = ["admin", "manager", "employee"]
        for idx, role in enumerate(roles):
            user = User(
                username=f"{role}_user",
                email=f"{role}@example.com",
                role=role,
            )
            user.set_password("Pass123")
            db_session.add(user)

        db_session.commit()

        admin = User.query.filter_by(role="admin").first()
        manager = User.query.filter_by(role="manager").first()
        employee = User.query.filter_by(role="employee").first()

        assert admin.role == "admin"
        assert manager.role == "manager"
        assert employee.role == "employee"

    def test_user_is_active_flag(self, db_session):
        """Test is_active flag modification."""
        user = User(
            username="activeuser",
            email="active@example.com",
            role="employee",
            is_active=True,
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        assert user.is_active is True

        user.is_active = False
        db_session.commit()

        assert user.is_active is False

    def test_user_is_approved_flag(self, db_session):
        """Test is_approved flag modification."""
        user = User(
            username="approveduser",
            email="approved@example.com",
            role="employee",
            is_approved=False,
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        assert user.is_approved is False

        user.is_approved = True
        db_session.commit()

        assert user.is_approved is True

    def test_user_is_blacklisted_flag(self, db_session):
        """Test is_blacklisted flag modification."""
        user = User(
            username="blacklistuser",
            email="blacklist@example.com",
            role="employee",
            is_blacklisted=False,
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        assert user.is_blacklisted is False

        user.is_blacklisted = True
        db_session.commit()

        assert user.is_blacklisted is True

    def test_user_updated_at_modification(self, db_session):
        """Test that updated_at timestamp changes on modification."""
        user = User(
            username="updateuser",
            email="update@example.com",
            role="employee",
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        original_updated_at = user.updated_at
        user.username = "modified_username"
        db_session.commit()

        assert user.updated_at >= original_updated_at

    def test_user_mixin_methods(self, admin_user):
        """Test Flask-Login UserMixin methods."""
        assert admin_user.is_authenticated is True
        assert admin_user.is_anonymous is False
        assert admin_user.get_id() == str(admin_user.id)

    def test_user_query_by_email(self, db_session, admin_user):
        """Test querying users by email."""
        fetched_user = User.query.filter_by(email="admin@hiresense.test").first()
        assert fetched_user is not None
        assert fetched_user.id == admin_user.id
        assert fetched_user.email == admin_user.email

    def test_user_query_by_role(self, db_session, admin_user, manager_user, employee_user):
        """Test querying users by role."""
        admins = User.query.filter_by(role="admin").all()
        managers = User.query.filter_by(role="manager").all()
        employees = User.query.filter_by(role="employee").all()

        assert len(admins) >= 1
        assert len(managers) >= 1
        assert len(employees) >= 1

    def test_user_deletion(self, db_session):
        """Test user deletion from database."""
        user = User(
            username="deleteuser",
            email="delete@example.com",
            role="employee",
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        user_id = user.id
        db_session.delete(user)
        db_session.commit()

        deleted_user = db_session.get(User, user_id)
        assert deleted_user is None


class TestNotificationModel:
    """Test suite for Notification model."""

    def test_notification_creation(self, db_session, admin_user):
        """Test basic notification creation."""
        notification = Notification(
            user_id=admin_user.id,
            message="Test notification",
            type="info",
        )
        db_session.add(notification)
        db_session.commit()

        assert notification.id is not None
        assert notification.user_id == admin_user.id
        assert notification.message == "Test notification"
        assert notification.type == "info"
        assert notification.is_read is False
        assert isinstance(notification.created_at, datetime)

    def test_notification_default_values(self, db_session, admin_user):
        """Test notification default values."""
        notification = Notification(
            user_id=admin_user.id,
            message="Default notification",
        )
        db_session.add(notification)
        db_session.commit()

        assert notification.type == "info"
        assert notification.is_read is False

    def test_notification_types(self, db_session, admin_user):
        """Test different notification types (success, error, info)."""
        types = ["success", "error", "info"]
        for notif_type in types:
            notification = Notification(
                user_id=admin_user.id,
                message=f"{notif_type} notification",
                type=notif_type,
            )
            db_session.add(notification)

        db_session.commit()

        success_notif = Notification.query.filter_by(type="success").first()
        error_notif = Notification.query.filter_by(type="error").first()
        info_notif = Notification.query.filter_by(type="info").first()

        assert success_notif.type == "success"
        assert error_notif.type == "error"
        assert info_notif.type == "info"

    def test_notification_is_read_flag(self, db_session, admin_user):
        """Test marking notifications as read."""
        notification = Notification(
            user_id=admin_user.id,
            message="Unread notification",
            type="info",
            is_read=False,
        )
        db_session.add(notification)
        db_session.commit()

        assert notification.is_read is False

        notification.is_read = True
        db_session.commit()

        assert notification.is_read is True

    def test_notification_cascade_delete(self, db_session):
        """Test cascade deletion when user is deleted."""
        user = User(
            username="cascadeuser",
            email="cascade@example.com",
            role="employee",
        )
        user.set_password("Pass123")
        db_session.add(user)
        db_session.commit()

        notification = Notification(
            user_id=user.id,
            message="Will be deleted",
            type="info",
        )
        db_session.add(notification)
        db_session.commit()

        notification_id = notification.id

        db_session.delete(user)
        db_session.commit()

        deleted_notification = db_session.get(Notification, notification_id)
        assert deleted_notification is None

    def test_notification_query_by_user(self, db_session, admin_user, manager_user):
        """Test querying notifications by user_id."""
        notification1 = Notification(
            user_id=admin_user.id,
            message="Admin notification",
            type="info",
        )
        notification2 = Notification(
            user_id=manager_user.id,
            message="Manager notification",
            type="info",
        )
        db_session.add_all([notification1, notification2])
        db_session.commit()

        admin_notifs = Notification.query.filter_by(user_id=admin_user.id).all()
        manager_notifs = Notification.query.filter_by(user_id=manager_user.id).all()

        assert len(admin_notifs) >= 1
        assert len(manager_notifs) >= 1
        assert any(n.message == "Admin notification" for n in admin_notifs)
        assert any(n.message == "Manager notification" for n in manager_notifs)

    def test_notification_query_unread(self, db_session, admin_user):
        """Test querying unread notifications."""
        notification1 = Notification(
            user_id=admin_user.id,
            message="Unread notification 1",
            type="info",
            is_read=False,
        )
        notification2 = Notification(
            user_id=admin_user.id,
            message="Read notification",
            type="info",
            is_read=True,
        )
        db_session.add_all([notification1, notification2])
        db_session.commit()

        unread_notifs = Notification.query.filter_by(
            user_id=admin_user.id,
            is_read=False
        ).all()

        assert len(unread_notifs) >= 1
        assert all(not n.is_read for n in unread_notifs)

    def test_notification_ordering(self, db_session, admin_user):
        """Test notification ordering by created_at."""
        for i in range(3):
            notification = Notification(
                user_id=admin_user.id,
                message=f"Notification {i}",
                type="info",
            )
            db_session.add(notification)

        db_session.commit()

        notifications = Notification.query.filter_by(
            user_id=admin_user.id
        ).order_by(Notification.created_at.desc()).all()

        assert len(notifications) >= 3
        for i in range(len(notifications) - 1):
            assert notifications[i].created_at >= notifications[i + 1].created_at
