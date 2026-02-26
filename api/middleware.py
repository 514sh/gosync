from django.db import connection, transaction
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


def set_tenant_context_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        tenant_id = None
        user_id = None

        # 1. Get user_id via JWT Token
        if "Authorization" in request.headers:
            user_auth_tuple = JWTAuthentication().authenticate(Request(request))
            if user_auth_tuple is not None:
                request.user, request.auth = user_auth_tuple
                user_id = request.auth.payload.get("user_id") if request.auth else None

        # 2. If user_id is not found in JWT, check if user is authenticated via session
        if not user_id and request.user.is_authenticated:
            user_id = request.user.id

        # 3. If user_id is found, set tenant context
        if user_id:
            from api.models import User

            try:
                user = User.objects.get(id=user_id)
                request.user = user
                tenant_id = request.user.tenant.id
            except User.DoesNotExist:
                request.user = None
        else:
            request.user = None

        # 4. Set tenant context for the request
        if tenant_id:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET LOCAL app.current_tenant_id = %s",
                        [str(tenant_id)],
                    )
                    print("before")
                    response = get_response(request)
                return response
        else:
            print("No tenant context set")
            return get_response(request)

    return middleware
