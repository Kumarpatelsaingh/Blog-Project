from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from authentication.renderers import UserRenderer
from authentication.serializers import (
    UserLoginSerializer,
    UserSignupSerializer,
)


# Generating Token
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserSignup(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {"msg": "User Signed Up Successfully!", "token": token},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response(
                    {"msg": "User Logged In Successfully!", "token": token},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "errors": {
                            "non_field_errors": [
                                "Email or Password is not Valid!"
                            ]
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if "refresh" in request.data:
            token = request.data["refresh"]
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
            return Response(
                {"msg": "User Logged Out Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"msg": "Something went wrong!"},
            status=status.HTTP_400_BAD_REQUEST,
        )
