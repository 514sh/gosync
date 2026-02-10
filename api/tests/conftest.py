import pytest
from mixer.backend.django import mixer

from api.models import Tenant, User


@pytest.fixture
def default_user():
    user = User.objects.create_user(
        username="testuser",
        email="default@email.com",
        password="testpass123",
    )
    return user


@pytest.fixture
def another_user():
    user = User.objects.create_user(
        username="anotheruser", email="anotheruser@email.com", password="testpass123"
    )
    return user


@pytest.fixture
def admin_user(tenant_and_owner):
    tenant, owner_user = tenant_and_owner
    user = User.objects.create_user(
        username="adminuser",
        password="adminpass123",
        role="admin",
        created_by=owner_user,
    )
    return user


@pytest.fixture
def regular_user(admin_user):
    user = User.objects.create_user(
        username="regularuser", password="testpass123", created_by=admin_user
    )
    return user


@pytest.fixture
def default_to_owner_user():
    user = User.objects.create_user(
        username="owneruser",
        password="ownerpass123",
    )
    return user


@pytest.fixture
def tenant_and_owner(default_to_owner_user):
    tenant = Tenant(name="Test Tenant")
    tenant.save(owner=default_to_owner_user)

    return tenant, default_to_owner_user


@pytest.fixture()
def owner_user(tenant_and_owner):
    tenant, owner = tenant_and_owner
    return owner


@pytest.fixture()
def default_tenant(tenant_and_owner):
    tenant, owner = tenant_and_owner
    return tenant


@pytest.fixture
def default_task(default_user):
    return mixer.blend("api.Task", title="Default Task", created_by=default_user)
