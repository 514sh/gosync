# tests.py
import pytest
from django.db import connection, transaction, utils
from django.test import TransactionTestCase

from api.models import Project, Tenant

pytestmark = pytest.mark.django_db


@pytestmark
class TenantIsolationTest(TransactionTestCase):
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
            self.assertIsNotNone(result, "api_project table not found")
            self.assertTrue(result[0], "RLS is NOT enabled on api_project table!")
            # Check if policy exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_policies 
                WHERE tablename = 'api_project' 
                AND policyname  in('tenant_isolation_select', 'tenant_isolation_insert', 'tenant_isolation_update', 'tenant_isolation_delete')
            """)
            count = cursor.fetchone()[0]
            self.assertEqual(count, 4, "tenant_isolation policies not found!")

    def test_rls_prevents_cross_tenant_access(self):
        tenant1 = Tenant.objects.create(name="Tenant 1")
        tenant2 = Tenant.objects.create(name="Tenant 2")

        # Verify without context returns nothing
        projects_no_ctx = Project.objects.all()
        print(f"Without context: {projects_no_ctx.count()} projects")
        self.assertEqual(
            projects_no_ctx.count(),
            0,
            "RLS not working - projects visible without context before transaction!",
        )
        # Set context to tenant1
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET LOCAL app.current_tenant_id = %s", [str(tenant1.id)]
                )
            project1 = Project.objects.create(name="Project 1", tenant=tenant1)
            # Should only see tenant1's projects
            projects = Project.objects.all()
            self.assertEqual(projects.count(), 1)
            self.assertEqual(projects.first().id, project1.id)
            with self.assertRaises(utils.ProgrammingError):
                Project.objects.create(name="Invalid Project", tenant=tenant2)

        projects_no_ctx = Project.objects.all()
        print(f"Without context: {projects_no_ctx.count()} projects")
        self.assertEqual(
            projects_no_ctx.count(),
            0,
            "RLS not working - projects are visible without context after transaction!",
        )
