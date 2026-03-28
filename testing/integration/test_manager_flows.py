"""
Integration tests for Manager workflows.
"""
import pytest


class TestManagerDashboard:
    """Tests for manager dashboard."""

    def test_manager_dashboard_access(self, authenticated_manager_client):
        """Test manager can access dashboard."""
        response = authenticated_manager_client.get("/manager/")
        assert response.status_code == 200
        assert b"Manager Dashboard" in response.data

    def test_employee_cannot_access_manager_dashboard(self, authenticated_employee_client):
        """Test employee cannot access manager routes."""
        response = authenticated_employee_client.get("/manager/")
        assert response.status_code == 403

    def test_admin_cannot_access_manager_dashboard(self, authenticated_admin_client):
        """Test admin cannot access manager routes."""
        response = authenticated_admin_client.get("/manager/")
        assert response.status_code == 403


class TestManagerProjects:
    """Tests for manager project management."""

    def test_list_projects(self, authenticated_manager_client, project):
        """Test listing projects."""
        response = authenticated_manager_client.get("/manager/projects")
        assert response.status_code == 200
        assert b"Test Project" in response.data

    def test_create_project_page(self, authenticated_manager_client):
        """Test create project page loads."""
        response = authenticated_manager_client.get("/manager/projects/create")
        assert response.status_code == 200
        assert b"Create New Project" in response.data

    def test_create_project_success(self, authenticated_manager_client):
        """Test creating a project."""
        response = authenticated_manager_client.post(
            "/manager/projects/create",
            data={
                "title": "New Test Project",
                "description": "Test description",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"New Test Project" in response.data

    def test_create_project_empty_title(self, authenticated_manager_client):
        """Test creating project with empty title."""
        response = authenticated_manager_client.post(
            "/manager/projects/create",
            data={
                "title": "",
                "description": "Test",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_view_project(self, authenticated_manager_client, project):
        """Test viewing a project."""
        response = authenticated_manager_client.get(f"/manager/projects/{project.id}")
        assert response.status_code == 200
        assert b"Test Project" in response.data

    def test_view_nonexistent_project(self, authenticated_manager_client):
        """Test viewing non-existent project."""
        response = authenticated_manager_client.get("/manager/projects/99999")
        assert response.status_code == 404


class TestManagerProjectSkills:
    """Tests for managing project skill requirements."""

    def test_view_project_skills(self, authenticated_manager_client, project):
        """Test viewing project skill requirements."""
        response = authenticated_manager_client.get(f"/manager/projects/{project.id}/skills")
        assert response.status_code == 200
        assert b"Skill Requirements" in response.data

    def test_add_project_skill(self, authenticated_manager_client, project, skills):
        """Test adding skill to project."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{project.id}/skills/add",
            data={
                "skill_id": skills[0].id,
                "is_mandatory": "on",
                "minimum_proficiency": 3,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Skill requirement added" in response.data


class TestManagerEmployeeMatching:
    """Tests for employee matching functionality."""

    def test_match_employees(self, authenticated_manager_client, project_with_skills, employee_with_skills):
        """Test matching employees to project."""
        response = authenticated_manager_client.get(
            f"/manager/projects/{project_with_skills.id}/match"
        )
        assert response.status_code == 200
        assert b"Find Matches" in response.data

    def test_assign_employee(self, authenticated_manager_client, project, employee_user):
        """Test assigning employee to project."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{project.id}/assign",
            data={
                "user_id": employee_user.id,
                "role_in_project": "Developer",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Check employee was assigned
        assert b"employee" in response.data.lower()


class TestManagerUpdates:
    """Tests for viewing employee updates."""

    def test_view_updates(self, authenticated_manager_client):
        """Test viewing updates page."""
        response = authenticated_manager_client.get("/manager/updates")
        assert response.status_code == 200
        assert b"Recent Updates" in response.data

    def test_view_employee_skills(self, authenticated_manager_client, employee_with_skills):
        """Test viewing an employee's skills."""
        response = authenticated_manager_client.get(
            f"/manager/employees/{employee_with_skills.id}/skills"
        )
        assert response.status_code == 200
        assert b"Python" in response.data


class TestManagerSelfService:
    """Tests for manager self-service features."""

    def test_view_profile(self, authenticated_manager_client):
        """Test viewing own profile."""
        response = authenticated_manager_client.get("/manager/profile")
        assert response.status_code == 200
        assert b"My Profile" in response.data

    def test_view_my_skills(self, authenticated_manager_client):
        """Test viewing own skills."""
        response = authenticated_manager_client.get("/manager/skills")
        assert response.status_code == 200
        assert b"My Skills" in response.data

    def test_add_skill(self, authenticated_manager_client, skills):
        """Test adding a skill to own profile."""
        response = authenticated_manager_client.post(
            "/manager/skills/add",
            data={
                "skill_id": skills[0].id,
                "proficiency_level": 3,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Skill added" in response.data

    def test_view_learning_paths(self, authenticated_manager_client):
        """Test viewing learning paths."""
        response = authenticated_manager_client.get("/manager/learning-paths")
        assert response.status_code == 200
        assert b"Learning Paths" in response.data

    def test_generate_learning_path(self, authenticated_manager_client):
        """Test generating a learning path."""
        response = authenticated_manager_client.post(
            "/manager/learning-paths/generate",
            data={"target_role": "senior_developer"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Learning path generated" in response.data or b"Senior Developer" in response.data

    def test_compare_roles(self, authenticated_manager_client):
        """Test comparing with target role."""
        response = authenticated_manager_client.get(
            "/manager/compare?target_role=senior_developer"
        )
        assert response.status_code == 200
        assert b"Role Comparison" in response.data


class TestManagerProjectEditing:
    """Tests for manager project editing capabilities."""

    def test_edit_project_page(self, authenticated_manager_client, project):
        """Test accessing edit project page."""
        response = authenticated_manager_client.get(f"/manager/projects/{project.id}/edit")
        assert response.status_code == 200
        assert project.title.encode() in response.data

    def test_edit_project_submit(self, authenticated_manager_client, project):
        """Test submitting project edit."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{project.id}/edit",
            data={
                "title": "Updated Project Title",
                "description": "Updated description",
                "status": "active",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Project updated" in response.data

    def test_delete_project(self, authenticated_manager_client, project):
        """Test deleting a project."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{project.id}/delete",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"deleted successfully" in response.data

    def test_remove_skill_from_project(self, authenticated_manager_client, project_with_skills, skills):
        """Test removing skill requirement from project."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{project_with_skills.id}/skills/remove",
            data={"skill_id": skills[0].id},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_unassign_employee_from_project(self, authenticated_manager_client, assignment):
        """Test removing employee from project team."""
        response = authenticated_manager_client.post(
            f"/manager/projects/{assignment.project_id}/unassign/{assignment.user_id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"from the project" in response.data


class TestManagerSkillManagement:
    """Tests for manager managing own skills."""

    def test_update_own_skill(self, authenticated_manager_client, manager_user, skills):
        """Test updating manager's own skill proficiency."""
        # First add a skill
        authenticated_manager_client.post(
            "/manager/skills/add",
            data={"skill_id": skills[0].id, "proficiency_level": 2},
        )

        # Then update it
        response = authenticated_manager_client.post(
            "/manager/skills/update",
            data={"skill_id": skills[0].id, "proficiency_level": 4},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Skill updated" in response.data or b"updated" in response.data.lower()

    def test_remove_own_skill(self, authenticated_manager_client, manager_user, skills):
        """Test removing manager's own skill."""
        # First add a skill
        authenticated_manager_client.post(
            "/manager/skills/add",
            data={"skill_id": skills[0].id, "proficiency_level": 3},
        )

        # Then remove it
        response = authenticated_manager_client.post(
            "/manager/skills/remove",
            data={"skill_id": skills[0].id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Skill removed" in response.data or b"removed" in response.data.lower()


class TestManagerLearningPaths:
    """Tests for manager learning path features."""

    def test_view_learning_path_detail(self, db_session, authenticated_manager_client, manager_user, learning_path):
        """Test viewing learning path details."""
        learning_path.user_id = manager_user.id
        db_session.commit()
        response = authenticated_manager_client.get(f"/manager/learning-paths/{learning_path.id}")
        assert response.status_code == 200
        assert learning_path.target_role.replace("_", " ").title().encode() in response.data

    # Removed invalid test `test_complete_learning_path` for manager, as the complete endpoint only exists for employees.


class TestManagerEmployeeSkillVerification:
    """Tests for manager verifying employee skills."""

    def test_verify_employee_skill(self, authenticated_manager_client, employee_with_skills, skills):
        """Test manager verifying an employee's skill."""
        response = authenticated_manager_client.post(
            f"/manager/employees/{employee_with_skills.id}/skills/verify",
            data={"skill_id": skills[0].id},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"verified" in response.data.lower() or b"Skill" in response.data

