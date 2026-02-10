from django.urls import path

from .views import (
    ObtainRefreshTokenView,
    ObtainTokenPairView,
    ProjectView,
    RegisterUserView,
    TenantView,
)

app_name = "api"  # Optional: for namespacing

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", ObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", ObtainRefreshTokenView.as_view(), name="token_refresh"),
    path("tenant/", TenantView.as_view(), name="tenant_info_create"),
    path("projects/", ProjectView.as_view(), name="project_list_create"),
]
