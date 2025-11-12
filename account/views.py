from utils.helpers import Response
from rest_framework import status 
from rest_framework.views import APIView
from .serilizers import UserLoginSerializer,UserRegistrationSerializer,UserProfileSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer,LogoutSerializer
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

# generate jwt token manually 
def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: UserRegistrationSerializer,  # Successful registration response
            400: UserRegistrationSerializer   # Validation errors
        },
        description="Register a new user with email, first_name, last_name, password, and role"
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                tokens = get_tokens_for_user(user)
            except AuthenticationFailed as e:
                return Response(
                success=False,
                status=status.HTTP_401_UNAUTHORIZED,
                message="Authentication Failed",
                errors={"detail": str(e)}
                )
            return Response(success=True, status=status.HTTP_201_CREATED, message="Registration Successful", data={
                "user": serializer.data,
                "tokens": tokens
            })
        return Response(success=False, status=status.HTTP_400_BAD_REQUEST, message="Registration failed", errors=serializer.errors)
    
class UserLoginView(APIView):
    @extend_schema(
        request=UserLoginSerializer,
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(email=email,password=password)
            if user is not None:
                try:
                    tokens = get_tokens_for_user(user)
                except AuthenticationFailed as e:
                    return Response(
                    success=False,
                    status=status.HTTP_401_UNAUTHORIZED,
                    message="Authentication Failed",
                    errors={"detail": str(e)}
                    )
                return Response(message="Login Successful", data={
                "user": serializer.data,
                "tokens": tokens
                })
            else:
                return Response(success=False, message="Login Failed", status=status.HTTP_404_NOT_FOUND, errors="Email or Password is not valid")
        return Response(success=False, message="Login Failed", status=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=UserProfileSerializer,
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(message="User info retrieved successfully", data=serializer.data)
    
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserChangePasswordSerializer,
    )
    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid():
            return Response(
                success=True,
                status=status.HTTP_200_OK,
                message="Password changed successfully"
            )  
        return Response(
            success=False,
            status=status.HTTP_400_BAD_REQUEST,
            message="Password change failed",
            errors=serializer.errors
        )
    
class SendPasswordResetEmailView(APIView):
    @extend_schema(
        request=SendPasswordResetEmailSerializer,
    )
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            return Response(message="Password Resent Link Send. Please Check Your Email")
        return Response(
            success=False,
            message="Password reset link sending failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
    
class UserPasswordResetView(APIView):
    @extend_schema(
        request=UserPasswordResetSerializer,
    )
    def post(self,request,uid,token ):
        serializer = UserPasswordResetSerializer(data=request.data, context= {'uid':uid, 'token':token})
        if serializer.is_valid():
            return Response(message="Password reset successful.")
        return Response(
            success=False,
            message="Password reset failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response(
                    message='Logout successsful',
                    status=status.HTTP_205_RESET_CONTENT
                )
            except Exception as e:
                return Response(
                    success=False,
                    message="Invalid or expired token",
                    status=status.HTTP_400_BAD_REQUEST,
                    errors=str(e)
                )
        return Response(
            success=False,
            message="Logout failed",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )