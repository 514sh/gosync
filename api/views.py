from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.models import Project, Task, Tenant, User

from .serializers import (
    ProjectSerializer,
    TaskCommentSerializer,
    TaskSerializer,
    UserSerializer,
)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response({"detail": serializer.errors}, status=400)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id=None, *args, **kwargs):
        if task_id is not None:
            task = get_object_or_404(Task, id=task_id)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            new_task = serializer.save(
                tenant=request.user.tenant,
                project=Project.objects.get(id=request.data.get("project_id")),
            )
            return Response(
                {
                    "message": f"Task created in project {new_task.project.name}",
                    "id": new_task.id,
                },
                status=201,
            )
        return Response({"detail": serializer.errors}, status=400)


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id, *args, **kwargs):
        # Placeholder for comment creation logic
        task = get_object_or_404(Task, id=task_id)
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid():
            new_comment = serializer.save(
                tenant=request.user.tenant,
                author=request.user,
                task=task,
            )
            return Response(
                {
                    "message": "Comment created successfully",
                    "id": new_comment.id,
                    "comment": new_comment.content,
                    "author": new_comment.author.username,
                    "created_at": new_comment.created_at,
                },
                status=201,
            )
        return Response({"detail": serializer.errors}, status=400)

    def get(self, request, *args, **kwargs):
        # Placeholder for comment retrieval logic
        return Response({"comments": []}, status=200)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id=None, *args, **kwargs):
        if project_id is not None:
            project = get_object_or_404(Project, id=project_id)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            new_project = serializer.save(tenant=request.user.tenant)
            return Response(
                {"message": "Project created successfully", "id": new_project.id},
                status=201,
            )
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
