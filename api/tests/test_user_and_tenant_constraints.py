import pytest

from api.exceptions import AuthorizationError, ValidationError
from api.models import Tenant

pytestmark = pytest.mark.django_db


@pytestmark
class TestUserAndTenantConstraints:
    def test_user_cannot_have_two_tenants(self, regular_user, default_user):
        another_tenant = Tenant(name="another tenant")
        another_tenant.save(owner=default_user)
        assert regular_user.tenant is not None
        with pytest.raises(ValidationError):
            regular_user.tenant = another_tenant
            regular_user.save()

    def test_owner_of_other_tenant_cannot_update_users_from_another_tenant(
        self, owner_user, default_user, another_user
    ):
        another_tenant = Tenant(name="another tenant")
        another_tenant.save(owner=another_user)
        default_user.tenant = another_tenant
        default_user.created_by = another_user
        default_user.save()

        assert default_user.tenant == another_tenant
        assert default_user.role == "user"
        assert owner_user.role == "owner"

        with pytest.raises(AuthorizationError):
            default_user.change_role(new_role="admin", changed_by=owner_user)
