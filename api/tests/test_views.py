import pytest
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from api.views import ObtainRefreshTokenView, ObtainTokenPairView, RegisterUserView

pytestmark = pytest.mark.django_db


@pytestmark
class TestRegisterUserView(TestCase):
    def test_register_new_user(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/register/",
            data={"username": "mark", "password": "6222"},
            content_type="application/json",
        )
        view = RegisterUserView.as_view()

        response = view(request)
        assert response.status_code == 201
        assert "message" in response.data
        assert "detail" not in response.data

    def test_register_new_user_invalid_request(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/register/",
            data={"invalid": "mark", "password": "6222"},
            content_type="application/json",
        )
        view = RegisterUserView.as_view()

        response = view(request)
        assert response.status_code == 400
        assert "detail" in response.data


@pytestmark
class TestTokenView:
    def test_token_obtain_pair_view(
        self,
        default_user,
    ):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            data={"username": default_user.username, "password": "testpass123"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()

        response = view(request)
        assert response.status_code == 200
        assert "access" in response.data, "Expected 'access' key in response"
        assert "refresh" in response.data, "Expected 'refresh' key in response"

    def test_token_obtain_pair_view_invalid_credentials(self, default_user):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            data={"username": default_user.username, "password": "wrongpassword"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()

        response = view(request)
        assert response.status_code == 401
        assert "detail" in response.data, (
            "Expected 'detail' key in response for invalid credentials"
        )


@pytestmark
class TestRefreshTokenView:
    def test_token_refresh_view(self, default_user):
        # First, get tokens
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            {"username": default_user.username, "password": "testpass123"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()
        response = view(request)
        refresh_token = response.data["refresh"]

        # Then, refresh the access token
        refresh_token_request = factory.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            content_type="application/json",
        )
        refresh_token_view = ObtainRefreshTokenView.as_view()
        refresh_token_response = refresh_token_view(refresh_token_request)

        assert refresh_token_response.status_code == 200
        assert "access" in refresh_token_response.data

    def test_token_refresh_view_invalid_refresh_token(self, default_user):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/refresh/",
            data={"refresh": "invalidtoken"},
            content_type="application/json",
        )
        view = ObtainRefreshTokenView.as_view()

        response = view(request)
        assert response.status_code == 401
        assert "detail" in response.data, (
            "Expected 'detail' key in response for invalid credentials"
        )


@pytestmark
class TestProjectView:
    def test_project_list_and_post_view(self, owner_user):
        # Authenticate the client
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            {"username": owner_user.username, "password": "ownerpass123"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()
        response = view(request)
        access_token = response.data["access"]
        client = APIClient()
        response = client.post(
            "/api/projects/",
            data={"name": "Test Project"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201
        assert isinstance(response.data, dict), "Expected response data to be a dict"
        assert "message" in response.data, "Expected 'message' key in response"
        assert response.data["id"] is not None, "Expected project ID to be present"

        response = client.get(
            "/api/projects/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert isinstance(response.data, list), "Expected response data to be a list"
        assert len(response.data) == 1, "Expected one project in response"
        assert response.data[0]["id"] is not None, "Expected project ID to be present"
        assert response.data[0]["name"] == "Test Project", (
            "Expected project name to match"
        )


@pytestmark
class TestTaskView:
    def test_task_list_and_post_view(
        self,
        owner_user,
    ):
        # Authenticate the client
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            {"username": owner_user.username, "password": "ownerpass123"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()
        response = view(request)
        access_token = response.data["access"]
        client = APIClient()
        project_response = client.post(
            "/api/projects/",
            data={"name": "Test Project"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = client.post(
            "/api/tasks/",
            data={"name": "Test Task", "project_id": project_response.data["id"]},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert isinstance(response.data, dict), "Expected response data to be a dict"
        assert "message" in response.data, "Expected 'message' key in response"
        assert response.data["message"] == "Task created in project Test Project", (
            "Expected task creation message to match"
        )
        assert response.data["id"] is not None, "Expected task ID to be present"


@pytestmark
class TestTaskCommentView:
    def test_task_comment_list_and_post_view(self, owner_user):
        # This is a placeholder for future tests related to task comments
        factory = APIRequestFactory()
        request = factory.post(
            "/api/token/",
            {"username": owner_user.username, "password": "ownerpass123"},
            content_type="application/json",
        )
        view = ObtainTokenPairView.as_view()
        response = view(request)
        access_token = response.data["access"]
        client = APIClient()
        project_response = client.post(
            "/api/projects/",
            data={"name": "Test Project"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        task_response = client.post(
            "/api/tasks/",
            data={"name": "Test Task", "project_id": project_response.data["id"]},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response = client.post(
            f"/api/tasks/{task_response.data['id']}/comments/",
            data={"content": "This is a test comment."},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201
        assert isinstance(response.data, dict), "Expected response data to be a dict"
        assert "author" in response.data, "Expected 'author' key in response"
        assert response.data["comment"] == "This is a test comment.", (
            "Expected comment content to match"
        )
        assert response.data["id"] is not None, "Expected comment ID to be present"
        assert response.data["author"] == owner_user.username, (
            "Expected comment author to match"
        )
        # Future implementation will go here
