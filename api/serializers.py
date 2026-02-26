from rest_framework import serializers

from api.models import Project, Task, TaskComment, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = ["id", "content", "author_id", "task_id", "created_at"]

    def create(self, validated_data):
        comment = TaskComment.objects.create(**validated_data)
        return comment


class TaskSerializer(serializers.ModelSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ["id", "name", "project_id", "comments"]

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        return task


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "tenant_id", "tasks"]

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)
        return project
