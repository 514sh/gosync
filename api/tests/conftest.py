import pytest

from mixer.backend.django import mixer

@pytest.fixture
def default_user():
    return mixer.blend('api.User', first_name="Default", last_name="User", email="default@email.com")

@pytest.fixture
def default_task(default_user):
    return mixer.blend('api.Task', title="Default Task", created_by=default_user)