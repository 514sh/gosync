from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response({"detail": serializer.errors}, status=400)


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
