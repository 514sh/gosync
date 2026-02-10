# tests.py
import random

import pytest

from api.exceptions import AuthorizationError, ValidationError
from api.models import Tenant, User

pytestmark = pytest.mark.django_db


@pytestmark
class TestTenantModel:
    def test_tenant_creation(self, default_tenant):
        assert default_tenant.name == "Test Tenant"
        assert default_tenant.id is not None

        with pytest.raises(ValidationError):
            tenant = (
                Tenant.objects.create(name="Test Tenant"),
                "All tenant should have an owner",
            )

    def test_tenant_owner_assignment(self):
        user = User.objects.create_user(username="owneruser", password="testpass")

        assert user.role == "user"
        tenant = Tenant(name="Test Tenant")
        tenant.save(owner=user)
        assert user.role == "owner"


@pytestmark
class TestUserModel:
    def test_user_creation(self, default_user):
        assert default_user.username == "testuser"
        assert default_user.role == "user"

    def test_user_without_created_by_and_organization_cannot_update_its_role(
        self, default_user
    ):
        default_user.role = "admin"
        default_user.save()
        assert default_user.role == "user"

    def test_owner_can_create_admin(self, tenant_and_owner):
        """Owner can create users with admin role"""
        tenant, owner_user = tenant_and_owner
        admin = User.objects.create_user(
            username="newadmin",
            password="pass123",
            role="admin",
            created_by=owner_user,
        )

        assert admin.role == "admin"
        assert admin.tenant == tenant

    def test_owner_can_create_regular_user(self, tenant_and_owner):
        """Owner can create users with user role"""
        tenant, owner_user = tenant_and_owner
        user = User.objects.create_user(
            username="newuser",
            password="pass123",
            role="user",
            created_by=owner_user,
        )

        assert user.role == "user"
        assert user.tenant == tenant

    def test_owner_can_create_another_owner(self, tenant_and_owner):
        """Owner can create users with owner role"""
        tenant, owner_user = tenant_and_owner
        new_owner = User.objects.create_user(
            username="newowner",
            password="pass123",
            role="owner",
            created_by=owner_user,
        )

        assert new_owner.role == "owner"
        assert new_owner.tenant == tenant

    # Admin permissions tests
    def test_admin_can_create_regular_user(self, admin_user):
        """Admin can create users with user role"""
        user = User.objects.create_user(
            username="regularuser",
            password="pass123",
            role="user",
            created_by=admin_user,
        )

        assert user.role == "user"
        assert admin_user.tenant == user.tenant

    def test_admin_cannot_create_admin(self, admin_user):
        """Admin cannot create users with admin role"""
        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newadmin",
                password="pass123",
                role="admin",
                created_by=admin_user,
            )

    def test_admin_cannot_create_owner(self, admin_user):
        """Admin cannot create users with owner role"""
        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newowner",
                password="pass123",
                role="owner",
                created_by=admin_user,
            )

    # Regular user restrictions tests
    def test_regular_user_cannot_create_admin(self, regular_user):
        """Regular user cannot create users with admin role"""
        # Assign default_user to tenant first

        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newadmin",
                password="pass123",
                role="admin",
                created_by=regular_user,
            )

    def test_regular_user_cannot_create_owner(self, regular_user):
        """Regular user cannot create users with owner role"""

        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newowner",
                password="pass123",
                role="owner",
                created_by=regular_user,
            )

    def test_regular_user_cannot_create_user(self, regular_user):
        """Regular user cannot create any users"""
        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newuser",
                password="pass123",
                role="user",
                created_by=regular_user,
            )

    # Regular user restrictions tests
    def test_default_user_cannot_create_admin(self, default_user):
        """Regular user cannot create users with admin role"""
        # Assign default_user to tenant first

        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newadmin",
                password="pass123",
                role="admin",
                created_by=default_user,
            )

    def test_default_user_cannot_create_owner(self, default_user):
        """Regular user cannot create users with owner role"""

        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newowner",
                password="pass123",
                role="owner",
                created_by=default_user,
            )

    def test_default_user_cannot_create_user(self, default_user):
        """Regular user cannot create any users"""
        with pytest.raises(AuthorizationError):
            User.objects.create_user(
                username="newuser",
                password="pass123",
                role="user",
                created_by=default_user,
            )

    def test_any_user_cannot_change_its_own_role(
        self, default_user, regular_user, admin_user, owner_user
    ):
        for user in [default_user, regular_user, admin_user, owner_user]:
            roles = ["user", "admin", "owner"]
            new_role = random.choice([role for role in roles if role != user.role])
            with pytest.raises(ValidationError):
                user.change_role(new_role)

    def test_owner_can_update_roles_to_admin(self, tenant_and_owner, regular_user):
        """Owner can update users to admin role"""
        tenant, owner_user = tenant_and_owner
        regular_user.change_role(new_role="admin", changed_by=owner_user)
        assert regular_user.role == "admin"
        assert regular_user.tenant == tenant

    def test_owner_can_update_roles_to_regular_user(self, tenant_and_owner, admin_user):
        """Owner can update users to user role"""
        tenant, owner_user = tenant_and_owner
        admin_user.change_role(new_role="user", changed_by=owner_user)
        assert admin_user.role == "user"
        assert admin_user.tenant == tenant

    def test_owner_can_update_roles_to_another_owner(
        self, tenant_and_owner, regular_user
    ):
        """Owner can update users to owner role"""
        tenant, owner_user = tenant_and_owner
        regular_user.change_role(new_role="owner", changed_by=owner_user)
        assert regular_user.role == "owner"
        assert regular_user.tenant == tenant

    # Admin permissions tests
    def test_admin_cannot_update_roles_to_regular_user(self, admin_user, regular_user):
        """Admin cannot update users to user role"""
        with pytest.raises(AuthorizationError):
            regular_user.change_role(new_role="user", changed_by=admin_user)

    def test_admin_cannot_update_roles_to_admin(self, admin_user, regular_user):
        """Admin cannot update users to admin role"""
        with pytest.raises(AuthorizationError):
            regular_user.change_role(new_role="admin", changed_by=admin_user)

    def test_admin_cannot_update_roles_to_owner(self, admin_user, regular_user):
        """Admin cannot create users to owner role"""
        with pytest.raises(AuthorizationError):
            regular_user.change_role(new_role="owner", changed_by=admin_user)

    # Regular user restrictions tests
    def test_regular_user_cannot_update_roles_to_admin(self, regular_user, admin_user):
        """Regular user cannot create users to admin role"""
        # Assign default_user to tenant first

        with pytest.raises(AuthorizationError):
            admin_user.change_role(new_role="admin", changed_by=regular_user)

    def test_regular_user_cannot_update_roles_to_owner(self, regular_user, admin_user):
        """Regular user cannot create users to owner role"""
        with pytest.raises(AuthorizationError):
            admin_user.change_role(new_role="owner", changed_by=regular_user)

    def test_regular_user_cannot_update_roles_to_user(self, regular_user, admin_user):
        """Regular user cannot create any users"""
        with pytest.raises(AuthorizationError):
            admin_user.change_role(new_role="user", changed_by=regular_user)

    # Regular user restrictions tests
    def test_default_user_cannot_use_the_change_role_method(
        self, default_user, another_user
    ):
        """Default user cannot use changed_role() method"""
        with pytest.raises(ValidationError):
            another_user.change_role(new_role="user", changed_by=default_user)
