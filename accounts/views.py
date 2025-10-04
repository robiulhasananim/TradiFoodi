from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    BuyerRegisterSerializer,
    LoginSerializer,
    BuyerProfileSerializer,
    ResetPasswordSerializer
)
from .models import BuyerProfile
from utils.helpers import Response

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class BuyerRegisterView(generics.CreateAPIView):
    serializer_class = BuyerRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            success=True,
            status_code=status.HTTP_201_CREATED,
            message="Buyer registered successfully",
            data=serializer.data
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if not user or user.role != 'buyer':
            return Response(
                success=False,
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid credentials",
                data=[]
            )

        token = get_tokens_for_user(user)
        resp_data = {
            'token': token,
            'user': {
                'email': user.email,
                'username': user.username,
                'role': user.role,
            }
        }
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Login successful",
            data=resp_data
        )


class BuyerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.buyer_profile

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Profile fetched",
            data=serializer.data
        )

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Profile updated",
            data=serializer.data
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Profile partially updated",
            data=serializer.data
        )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=email, role='buyer')
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                success=True,
                status_code=status.HTTP_200_OK,
                message="Password reset successful",
                data=[]
            )
        except User.DoesNotExist:
            return Response(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Buyer not found",
                data=[]
            )
