import os, requests
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User

import logging

@api_view(["GET"])
@permission_classes([AllowAny])
def googleLogin(request):
    CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL")
    STATE = "RANDOM_STATE"
    SCOPE = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    url = (f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code"
           f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}&scope={SCOPE}&state={STATE}")
    return redirect(url)

@api_view(["GET"])
@permission_classes([AllowAny])
def googleCallback(request):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_SECRET")
    code = request.GET.get("code")
    state = request.GET.get("state")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URL")

    if code is None:
        raise Exception("Authorization code is missing.")

    url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    try:
        token_response = requests.post(url, data=data)
        token_json = token_response.json()
    except requests.RequestException:
        return Response({"message": "구글 토큰 요청에 실패했습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    access_token = token_json.get("access_token")

    if 'error' in token_json:
        error_description = token_json.get('error_description', 'No description provided.')
        logging.error(f"Failed to retrieve access token: {error_description}")
        return Response({"message": f"Failed to retrieve access token: {error_description}"},
                        status=status.HTTP_400_BAD_REQUEST)

    if access_token:
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            profile_response = requests.get(userinfo_url, headers=headers)
            profile_json = profile_response.json()
        except requests.RequestException:
            return Response({"message": "구글 프로필 요청에 실패했습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        googleId = profile_json.get("id")
        username = profile_json.get("email")
        email = profile_json.get("email")

        if googleId:
            user, created = User.objects.get_or_create(googleId=googleId, defaults={'username': username, 'email': email})
            refresh = RefreshToken.for_user(user)
            data = {
                "user": {
                    "id": user.id,
                    "googleId": user.googleId,
                    "username": user.username,
                    "email": user.email,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)

    return Response({"message": "Failed to retrieve information from Google."}, status=status.HTTP_400_BAD_REQUEST)