from django.db import connection, transaction
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


def set_tenant_context_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not request.path.startswith("/api/projects/"):
            return get_response(request)
        user_auth_tuple = JWTAuthentication().authenticate(Request(request))

        if user_auth_tuple is not None:
            # If authentication is successful, set request.user and request.auth
            request.user, request.auth = user_auth_tuple
        print(request.user)
        user_id = request.auth.payload.get("user_id") if request.auth else None
        if user_id:
            from api.models import User

            try:
                user = User.objects.get(id=user_id)
                request.user = user
            except User.DoesNotExist:
                request.user = None
        else:
            request.user = None
        if request.user and request.user.tenant:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET LOCAL app.current_tenant_id = %s",
                        [str(request.user.tenant.id)],
                    )
                    print("before")
                    response = get_response(request)
                return response
        else:
            print("No tenant context set")
            return get_response(request)

    return middleware
