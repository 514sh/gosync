from django.urls import path

from .views import ObtainRefreshTokenView, ObtainTokenPairView, RegisterUserView

app_name = "api"  # Optional: for namespacing

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", ObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", ObtainRefreshTokenView.as_view(), name="token_refresh"),
]
