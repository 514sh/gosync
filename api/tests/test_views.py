import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory

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
