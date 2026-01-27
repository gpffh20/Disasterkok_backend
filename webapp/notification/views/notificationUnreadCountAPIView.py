from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import NotificationMessage


class NotificationUnreadCountAPIView(APIView):
    """Get the count of unread notifications."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = NotificationMessage.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count}, status=status.HTTP_200_OK)
