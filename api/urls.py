from django.urls import path

from .views import (
    ObtainRefreshTokenView,
    ObtainTokenPairView,
    ProjectView,
    RegisterUserView,
    TaskCommentView,
    TaskView,
    TenantView,
)

app_name = "api"  # Optional: for namespacing

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", ObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", ObtainRefreshTokenView.as_view(), name="token_refresh"),
    path("tenant/", TenantView.as_view(), name="tenant_info_create"),
    path("projects/<int:project_id>/", ProjectView.as_view(), name="project_detail"),
    path("projects/", ProjectView.as_view(), name="project_list_create"),
    path(
        "tasks/<int:task_id>/comments/", TaskCommentView.as_view(), name="task_comments"
    ),
    path("tasks/<int:task_id>/", TaskView.as_view(), name="task_detail"),
    path("tasks/", TaskView.as_view(), name="task_list_create"),
]
