import pytest
from mixer.backend.django import mixer

from api.models import User


@pytest.fixture
def super_user():
    return mixer.blend(
        "api.User",
        username="super_user",
        password="superpassword",
        email="super_user@email.com",
        is_staff=True,
        is_superuser=True,
        role="admin",
    )


@pytest.fixture
def default_user():
    user = User.objects.create_user(
        username="testuser",
        email="default@email.com",
        password="testpass123",  # Properly hashed
    )
    return user


@pytest.fixture
def default_task(default_user):
    return mixer.blend("api.Task", title="Default Task", created_by=default_user)
