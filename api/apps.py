from django.apps import AppConfig
from django.db import connection
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        post_migrate.connect(setup_rls_policies, sender=self)


def setup_rls_policies(sender, **kwargs):
    """Automatically create RLS policies for all TenantModel tables"""
    from django.apps import apps

    from .models import TenantPolicyDependent

    # Skip during test migrations
    if kwargs.get("verbosity", 1) >= 2:
        print("Setting up RLS policies...")

    with connection.cursor() as cursor:
        # Get all models that inherit from TenantModel
        for model in apps.get_models():
            if (
                issubclass(model, TenantPolicyDependent)
                and model != TenantPolicyDependent
            ):
                table_name = model._meta.db_table
                print(f"Processing table: {table_name}")  # Debug

                try:
                    # Enable RLS
                    cursor.execute(
                        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"
                    )

                    # Force RLS
                    cursor.execute(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY")

                    # Drop existing policy if it exists
                    cursor.execute(
                        f"DROP POLICY IF EXISTS tenant_isolation_select ON {table_name}"
                    )
                    cursor.execute(
                        f"DROP POLICY IF EXISTS tenant_isolation_insert ON {table_name}"
                    )
                    cursor.execute(
                        f"DROP POLICY IF EXISTS tenant_isolation_update ON {table_name}"
                    )
                    cursor.execute(
                        f"DROP POLICY IF EXISTS tenant_isolation_delete ON {table_name}"
                    )

                    # Create separate policies for each operation

                    # SELECT: Must match current tenant context
                    cursor.execute(f"""
                        CREATE POLICY tenant_isolation_select ON {table_name}
                            FOR SELECT
                            TO PUBLIC
                            USING (tenant_id::text = NULLIF(current_setting('app.current_tenant_id', TRUE), ''))
                    """)

                    # INSERT: Allow if tenant_id matches context OR if no context set (for tests)
                    cursor.execute(f"""
                        CREATE POLICY tenant_isolation_insert ON {table_name}
                            FOR INSERT
                            TO PUBLIC
                            WITH CHECK (
                                tenant_id::text = NULLIF(current_setting('app.current_tenant_id', TRUE), '')
                                OR current_setting('app.current_tenant_id', TRUE) = ''
                            )
                    """)

                    # UPDATE: Can only update rows in your tenant
                    cursor.execute(f"""
                        CREATE POLICY tenant_isolation_update ON {table_name}
                            FOR UPDATE
                            TO PUBLIC
                            USING (tenant_id::text = NULLIF(current_setting('app.current_tenant_id', TRUE), ''))
                            WITH CHECK (tenant_id::text = NULLIF(current_setting('app.current_tenant_id', TRUE), ''))
                    """)

                    # DELETE: Can only delete rows in your tenant
                    cursor.execute(f"""
                        CREATE POLICY tenant_isolation_delete ON {table_name}
                            FOR DELETE
                            TO PUBLIC
                            USING (tenant_id::text = NULLIF(current_setting('app.current_tenant_id', TRUE), ''))
                    """)

                    print(f"✓ RLS policies created for {table_name}")
                except Exception as e:
                    print(f"✗ Error setting up RLS for {table_name}: {e}")
