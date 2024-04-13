import os
from json import JSONDecodeError

import requests
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import *

# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")
BASE_URL = 'http://localhost:8888/'
GOOGLE_CALLBACK_URI = BASE_URL + 'users/google/callback/'


# 구글 로그인
@permission_classes([AllowAny])
class googleLogin(APIView):
    def get(self, request, *args, **kwargs):
        scope = "https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email"
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        return redirect(
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


# 구글 callback
@permission_classes([AllowAny])
class googleCallback(APIView):
    def get(self, request, *args, **kwargs):
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_SECRET")
        code = request.GET.get('code')
        token_req = requests.post(
            f"https://oauth2.googleapis.com/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_CALLBACK_URI,
                "state": state
            }
        )
        access_token = token_req.json().get('access_token')
        error = token_req.json().get("error")
        if error is not None:
            raise JSONDecodeError(error)
        user_req = requests.get(f"https://www.googleapis.com/oauth2/v2/tokeninfo?access_token={access_token}")
        if not user_req.ok:
            raise ValidationError('Failed to obtain user info from Google.')

        user_req_json = user_req.json()
        email = user_req_json.get('email')
        user_id = user_req_json.get('user_id')
        try:
            user = User.objects.get(googleID=email)
            refresh = RefreshToken.for_user(user)
            data = {
                "user": {
                    "id": user.id,
                    "googleID": user.googleID,
                    "username": user.username,
                },
                "token": {
                    "access": f"{str(refresh.access_token)}",
                    "refresh": f"{str(refresh)}"
                }
            }
            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            User(googleID=email, username=user_id).save()
            user = User.objects.get(googleID=email)
            refresh = RefreshToken.for_user(user)
            data = {
                "user": {
                    "id": user.id,
                    "googleId": user.googleID,
                    "username": user.username,
                },
                "token": {
                    "access": f"{str(refresh.access_token)}",
                    "refresh": f"{str(refresh)}"
                }
            }
            return Response(data, status=status.HTTP_200_OK)
