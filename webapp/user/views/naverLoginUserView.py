import os, requests

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User


@api_view(["GET"])
@permission_classes([AllowAny])
def naverLogin(request):
    CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
    REDIRECT_URL = os.environ.get("NAVER_REDIRECT_URL")
    STATE = "RANDOM_STATE"
    url = (f"https://nid.naver.com/oauth2.0/authorize"
           f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}&state={STATE}")
    return redirect(url)


@api_view(["GET"])
@permission_classes([AllowAny])
def naverCallback(request):
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_SECRET")
    state = request.GET.get("state")
    code = request.GET.get("code")

    if code is None:
        raise Exception("code is None")

    redirect_uri = os.environ.get("NAVER_REDIRECT_URL")
    url = "https://nid.naver.com/oauth2.0/token"

    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code,
        'state': state,
    }

    token_request = requests.post(url, data=data)
    token_json = token_request.json()

    if 'access_token' in token_json:
        access_token = token_json["access_token"]
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        profile_request = requests.get(url, headers=headers)
        profile_json = profile_request.json()

        if 'response' in profile_json:
            naverId = profile_json["response"].get("id")
            username = profile_json["response"].get("email")
            email = profile_json["response"].get("email")

            if naverId is not None:
                if User.objects.filter(naverId=naverId).exists():
                    if User.objects.filter(email=email).exists():
                        return Response({"message": "이미 가입된 이메일 주소입니다."}, status=status.HTTP_400_BAD_REQUEST)

                    User(naverId=naverId, username=username, email=email).save()

                    user = User.objects.get(naverId=naverId)
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "user": {
                            "id": user.id,
                            "naverId": user.naverId,
                            "username": user.username,
                            'email': user.email,
                        },
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    User(naverId=naverId, username=username, email=email).save()
                    user = User.objects.get(naverId=naverId)
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "user": {
                            "id": user.id,
                            "naverId": user.naverId,
                            "username": user.username,
                        },
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                    return Response(data, status=status.HTTP_200_OK)
    return Response({"message": "naver에서 정보를 불러오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)
