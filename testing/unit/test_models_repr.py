"""
Unit tests for model repr methods and string representations.

Tests __repr__ methods for all database models.
"""

import pytest
from app import db
from app.models import (
    User, Department, Skill, Notification, Resume, LearningPath,
    Project, ProjectSkill, ProjectAssignment, UserSkill
)


class TestModelReprMethods:
    """Tests for model __repr__ methods."""

    def test_department_repr(self, db_session):
        """Test Department __repr__ method."""
        dept = Department(name="Engineering")
        db_session.add(dept)
        db_session.commit()
        
        repr_str = repr(dept)
        assert "Department" in repr_str
        assert "Engineering" in repr_str

    def test_skill_repr(self, db_session):
        """Test Skill __repr__ method."""
        skill = Skill(name="Python", category="technical")
        db_session.add(skill)
        db_session.commit()
        
        repr_str = repr(skill)
        assert "Skill" in repr_str
        assert "Python" in repr_str

    def test_user_repr(self, db_session):
        """Test User __repr__ method."""
        user = User(username="testuser", email="test@test.com", role="employee")
        user.set_password("Test@123")
        db_session.add(user)
        db_session.commit()
        
        repr_str = repr(user)
        assert isinstance(repr_str, str)

    def test_notification_repr(self, db_session):
        """Test Notification __repr__ method."""
        user = User(username="testuser", email="test@test.com", role="employee")
        user.set_password("Test@123")
        db_session.add(user)
        db_session.commit()
        
        notif = Notification(user_id=user.id, message="Test", type="info")
        db_session.add(notif)
        db_session.commit()
        
        repr_str = repr(notif)
        assert isinstance(repr_str, str)

    def test_resume_repr(self, db_session):
        """Test Resume __repr__ method."""
        user = User(username="testuser", email="test@test.com", role="employee")
        user.set_password("Test@123")
        db_session.add(user)
        db_session.commit()
        
        resume = Resume(user_id=user.id, file_path="/path/to/resume.pdf")
        db_session.add(resume)
        db_session.commit()
        
        repr_str = repr(resume)
        assert "Resume" in repr_str
        assert str(user.id) in repr_str

    def test_learning_path_repr(self, db_session):
        """Test LearningPath __repr__ method."""
        user = User(username="testuser", email="test@test.com", role="employee")
        user.set_password("Test@123")
        db_session.add(user)
        db_session.commit()
        
        path = LearningPath(user_id=user.id, target_role="Senior Engineer")
        db_session.add(path)
        db_session.commit()
        
        repr_str = repr(path)
        assert "LearningPath" in repr_str
        assert "Senior Engineer" in repr_str

    def test_project_repr(self, db_session):
        """Test Project __repr__ method."""
        user = User(username="manager", email="manager@test.com", role="manager")
        user.set_password("Test@123")
        db_session.add(user)
        db_session.commit()
        
        project = Project(title="Website Redesign", description="Redesign site", manager_id=user.id)
        db_session.add(project)
        db_session.commit()
        
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "Website Redesign" in repr_str

    def test_project_skill_repr(self, db_session):
        """Test ProjectSkill __repr__ method."""
        user = User(username="manager", email="manager@test.com", role="manager")
        user.set_password("Test@123")
        db_session.add(user)
        
        skill = Skill(name="React", category="technical")
        db_session.add(skill)
        db_session.commit()
        
        project = Project(title="App Dev", description="Dev", manager_id=user.id)
        db_session.add(project)
        db_session.commit()
        
        ps = ProjectSkill(project_id=project.id, skill_id=skill.id)
        db_session.add(ps)
        db_session.commit()
        
        repr_str = repr(ps)
        assert "ProjectSkill" in repr_str

    def test_project_assignment_repr(self, db_session):
        """Test ProjectAssignment __repr__ method."""
        manager = User(username="manager", email="manager@test.com", role="manager")
        manager.set_password("Test@123")
        db_session.add(manager)
        
        employee = User(username="employee", email="emp@test.com", role="employee")
        employee.set_password("Test@123")
        db_session.add(employee)
        db_session.commit()
        
        project = Project(title="Project X", description="Desc", manager_id=manager.id)
        db_session.add(project)
        db_session.commit()
        
        pa = ProjectAssignment(project_id=project.id, user_id=employee.id)
        db_session.add(pa)
        db_session.commit()
        
        repr_str = repr(pa)
        assert "ProjectAssignment" in repr_str

    def test_user_skill_repr(self, db_session):
        """Test UserSkill __repr__ method."""
        user = User(username="testuser", email="test@test.com", role="employee")
        user.set_password("Test@123")
        db_session.add(user)
        
        skill = Skill(name="Python", category="technical")
        db_session.add(skill)
        db_session.commit()
        
        us = UserSkill(user_id=user.id, skill_id=skill.id, proficiency_level=4)
        db_session.add(us)
        db_session.commit()
        
        repr_str = repr(us)
        assert "UserSkill" in repr_str
        assert "level=" in repr_str


class TestModelCreation:
    """Tests for model creation and initialization."""

    def test_user_password_hashing(self, db_session):
        """Test that user passwords are properly hashed."""
        user = User(username="test", email="test@test.com", role="employee")
        user.set_password("MyPassword@123")
        
        assert user.password_hash != "MyPassword@123"
        assert user.check_password("MyPassword@123") is True
        assert user.check_password("WrongPassword") is False

    def test_user_password_verification(self, db_session):
        """Test incorrect password verification."""
        user = User(username="test", email="test@test.com")
        user.set_password("SecurePass@456")
        db_session.add(user)
        db_session.commit()
        
        assert user.check_password("SecurePass@456") is True
        assert user.check_password("WrongPassword") is False
        assert user.check_password("") is False
