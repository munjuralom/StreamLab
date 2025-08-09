
from rest_framework.views import APIView
from rest_framework.response import Response
from .accounts.models import User
from .accounts.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .accounts.send_otp import send_otp
import random
import string
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from .accounts.models import User, UserRole
import uuid


class SigninView(APIView):
    """
    Handle user login.
    """
    def post(self, request):
        email = request.data.get('email_address')
        password = request.data.get('password')
        role = request.data.get('role')

        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"message": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not role or role not in [UserRole.FILMMAKER, UserRole.VIEWER]:
            return Response({"message": "Invalid role. Must be login as 'filmmaker' or 'viewer'."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user:
            if user.role != role:
                return Response({"message": 'Role mismatch'}, status=status.HTTP_400_BAD_REQUEST)
        
        # return Response(user.role)
        if user is None:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "user_id": user.id,
            "role": user.role,
            "refer_code": user.referral_code
        }, status=status.HTTP_200_OK)


class AdminLoginView(APIView):
    """
    Handle user login.
    """
    def post(self, request):
        email = request.data.get('email_address')
        password = request.data.get('password')

        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"message": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)

        if user.is_superuser is False:
            return Response({"message": "You are not authorized to access this resource."}, status=status.HTTP_403_FORBIDDEN)

        if user is None:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"message": "Your account is inactive."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "access_token": str(access_token),
            "refresh_token": str(refresh),
            "user_id": user.id,
            "role": user.role
        }, status=status.HTTP_200_OK)
    


class SignupView(APIView):
    """
    Handle user signup.
    """
    def post(self, request):
        data = request.data.copy()
        # Accept referral code param 'refer_by_code' in POST data (optional)
        refer_by_code = data.get('refer_by_code')
        if refer_by_code:
            try:
                refer_by_user = User.objects.get(referral_code=refer_by_code)
                data['refer_by_code'] = refer_by_code  # keep for serializer
            except User.DoesNotExist:
                return Response({"message": "Invalid referral code."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['refer_by_code'] = None

        # Use serializer to validate and create user
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            full_name = data.get('full_name')
            email = data.get('email_address') or data.get('email')

            # Custom checks outside serializer for confirm_password & terms
            if not full_name:
                return Response({"message": "Full name is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({"message": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not confirm_password:
                return Response({"message": "Confirm password is required."}, status=status.HTTP_400_BAD_REQUEST)
            if password != confirm_password:
                return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get("terms_agreed"):
                return Response({"message": "You must agree to the Terms of Service."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                validate_password(password)
            except Exception as e:
                return Response({"message": list(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Check email uniqueness
            if User.objects.filter(email=email).exists():
                return Response({"message": "The email is already taken."}, status=status.HTTP_400_BAD_REQUEST)

            # Create user with serializer create() (which handles password & refer_by)
            user = serializer.save()
            user.set_password(password)
            user.terms_agreed = data.get('terms_agreed', False)
            user.full_name = full_name
            user.email = email
            user.role = data.get('role', UserRole.VIEWER)
            user.save()

            return Response({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "referral_code": user.referral_code,
                "referral_link": user.referral_link,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email_address')
        
        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        otp = ''.join(random.choices(string.digits, k=6))
        try:
            user.otp = otp
            user.otp_expired = timezone.now() + timedelta(minutes=5)
            user.save()
            send_email = send_otp(email, otp)
        except Exception as e:
            return Response({"message": f"Failed to process OTP. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if send_email:
            return Response({'user_id': user.id}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Failed to send OTP email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('verification_code')

        if not user_id or not otp:
            return Response({"message": "Both User ID and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if timezone.now() > user.otp_expired:
            return Response({"message": "verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if str(user.otp) == otp:
            secret_key = uuid.uuid4()
            user.reset_secret_key = secret_key
            user.save()
            return Response(
                {
                    "secret_key": str(secret_key)
                },
                status=status.HTTP_200_OK
            )

        return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        secret_key = request.data.get('secret_key')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Validate fields
        if not user_id or not secret_key or not new_password or not confirm_password:
            return Response(
                {"message": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"message": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id, reset_secret_key=secret_key)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid secret key or user ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Set new password
        user.set_password(new_password)
        # user.reset_secret_key = None  # Invalidate the secret key
        # user.otp = None
        # user.otp_expired = None
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response(
                {"message": "Please provide all required password fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"message": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=old_password)
        print(email)
        if user is None:
            return Response(
                {"message": "Invalid old password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)