import os, requests

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User


@api_view(["GET"])
@permission_classes([AllowAny])
def kakaoLogin(request):
    REST_API = os.environ.get("KAKAO_REST_API")
    REDIRECT_URL = os.environ.get("KAKAO_REDIRECT_URL")
    url = (f'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={REST_API}'
           f'&redirect_uri={REDIRECT_URL}')
    return redirect(url)


@api_view(["GET"])
@permission_classes([AllowAny])
def kakaoCallback(request):
    code = request.GET.get("code")
    if code is None:
        raise Exception("code is None")

    url = "https://kauth.kakao.com/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.environ.get("KAKAO_REST_API"),
        'redirect_uri': os.environ.get("KAKAO_REDIRECT_URL"),
        'code': code,
        'client_secret': os.environ.get("KAKAO_SECRET"),
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    try:
        token_request = requests.post(url, data, headers)
        token_json = token_request.json()
    except requests.RequestException:
        return Response({"message": "카카오 토큰 요청에 실패했습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if 'access_token' not in token_json:
        return Response({"message": "kakao에서 정보를 불러오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)

    access_token = token_json["access_token"]
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    try:
        profile_request = requests.get(url, headers=headers)
        profile_json = profile_request.json()
    except requests.RequestException:
        return Response({"message": "카카오 프로필 요청에 실패했습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    kakaoId = profile_json.get("id")
    username = profile_json.get("properties", {}).get('nickname')

    if kakaoId is None:
        return Response({"message": "kakao에서 정보를 불러오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(kakaoId=kakaoId, defaults={'username': username})
    refresh = RefreshToken.for_user(user)
    data = {
        "user": {
            "id": user.id,
            "kakaoId": user.kakaoId,
            "username": user.username,
        },
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
    return Response(data, status=status.HTTP_200_OK)