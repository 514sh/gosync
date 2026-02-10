from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.models import Project, Tenant, User

from .serializers import ProjectSerializer, UserSerializer


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response({"detail": serializer.errors}, status=400)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            print(f"my tenant: {request.user.tenant}")
            serializer.save(tenant=request.user.tenant)
            return Response({"message": "Project created successfully"}, status=201)
        return Response({"detail": serializer.errors}, status=400)


class TenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = request.user.tenant
        if tenant:
            return Response({"tenant": tenant.name})
        return Response({"detail": "You are not part of any tenant."}, status=404)

    def post(self, request, *args, **kwargs):
        tenant_name = request.data.get("tenant_name")

        new_tenant = Tenant(name=tenant_name)
        payload = request.auth.payload
        user_id = payload.get("user_id")
        owner = User.objects.get(id=user_id)
        new_tenant.save(owner=owner)
        return Response(
            {"message": f"Tenant '{tenant_name}' created successfully"}, status=201
        )


class ObtainTokenPairView(TokenObtainPairView):
    """
    Custom view to obtain JWT token pair.
    """

    pass


class ObtainRefreshTokenView(TokenRefreshView):
    """
    Custom view to obtain JWT refresh token.
    """

    pass
