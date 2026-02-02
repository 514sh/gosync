import pytest
from mixer.backend.django import mixer


@pytest.fixture
def super_user():
    return mixer.blend(
        "api.User",
        username="super_user",
        email="super_user@email.com",
        is_staff=True,
        is_superuser=True,
        role="admin",
    )


@pytest.fixture
def default_user():
    return mixer.blend("api.User", email="default@email.com")


@pytest.fixture
def default_task(default_user):
    return mixer.blend("api.Task", title="Default Task", created_by=default_user)
