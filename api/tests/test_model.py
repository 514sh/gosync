import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db

@pytestmark
class TestOrganizationModel:
    def test_organization_creation(self):
        org = mixer.blend('api.Organization', name="Test Org")
        assert org.name == "Test Org", "Should create organization instance "

@pytestmark
class TestDepartmentModel:
    def test_department_creation(self):
        dept = mixer.blend('api.Department', name="Test Dept")
        assert dept.name == "Test Dept", "Should create department instance"

@pytestmark
class TestProjectModel:
    def test_project_creation(self):
        proj = mixer.blend('api.Project', name="Test Project")
        assert proj.name == "Test Project", "Should create project instance"

@pytestmark
class TestUserModel:
    def test_user_creation(self, default_user):
        assert default_user.first_name == "Default", "Should create user instance"

@pytestmark
class TestTaskModel:
  def test_task_creation_requires_a_user(self, default_user ):
      task = mixer.blend('api.Task', title="Test Task", created_by=default_user)
      assert task.title == "Test Task", "Should create task instance"
      
      with pytest.raises(Exception):
        task_no_user = mixer.blend('api.Task', title="Task without user"), "Should not create task without user"

@pytestmark
class TestTaskCommentModel:
    def test_task_comment_creation(self, default_task, default_user):
        comment = mixer.blend('api.TaskComment', content="This is a comment", user=default_user, task=default_task)
        assert comment.content == "This is a comment", "Should create task comment instance"

@pytestmark
class TestTaskAttachmentModel:
    def test_task_attachment_creation(self, default_task, default_user):
        attachment = mixer.blend('api.TaskAttachment', filename="file.txt", task=default_task, uploaded_by=default_user)
        assert attachment.filename == "file.txt", "Should create task attachment instance"