from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import BuyerProfile

User = get_user_model()


# ---------------- Buyer Register Serializer ----------------
class BuyerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')

        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone')

        # Force role to 'buyer'
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'].split('@')[0],
            password=password,
            role='buyer'
        )

        # Create buyer profile
        BuyerProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone
        )

        return user


# ---------------- Login Serializer ----------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# ---------------- Buyer Profile Serializer ----------------
class BuyerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = BuyerProfile
        fields = [
            'full_name',
            'email',
            'phone',
            'address',
            'city',
            'postal_code',
            'role',
        ]


# ---------------- Reset Password Serializer ----------------
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
