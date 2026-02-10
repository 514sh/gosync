# tests.py
import pytest
from django.db import connection, transaction, utils

from api.models import Project, Tenant

pytestmark = pytest.mark.django_db


@pytestmark
class TestTenantIsolation:
    def test_rls_is_enabled(self):
        """First, verify RLS is actually enabled"""
        with connection.cursor() as cursor:
            # Check if RLS is enabled on projects table
            cursor.execute("""
                SELECT relrowsecurity 
                FROM pg_class 
                WHERE relname = 'api_project'
            """)
            result = cursor.fetchone()
            assert result is not None
            assert result[0] is True
            # Check if policy exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_policies 
                WHERE tablename = 'api_project' 
                AND policyname  in('tenant_isolation_select', 'tenant_isolation_insert', 'tenant_isolation_update', 'tenant_isolation_delete')
            """)
            count = cursor.fetchone()[0]
            assert count == 4

    def test_rls_prevents_cross_tenant_access(self, default_user, another_user):
        tenant1 = Tenant(name="Tenant 1")
        tenant1.save(owner=default_user)
        tenant2 = Tenant(name="Tenant 2")
        tenant2.save(owner=another_user)

        # Verify without context returns nothing
        projects_no_ctx = Project.objects.all()
        assert projects_no_ctx.count() == 0, (
            "RLS not working - projects visible without context before transaction!"
        )
        # Set context to tenant1
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET LOCAL app.current_tenant_id = %s", [str(tenant1.id)]
                )
            project1 = Project.objects.create(name="Project 1", tenant=tenant1)

            projects = Project.objects.all()
            assert projects.count() == 1
            assert projects.first().id == project1.id
            with pytest.raises(utils.ProgrammingError):
                Project.objects.create(name="Invalid Project", tenant=tenant2)

        projects_no_ctx = Project.objects.all()
        assert projects_no_ctx.count() == 0, (
            "RLS not working - projects are visible without context after transaction!"
        )
