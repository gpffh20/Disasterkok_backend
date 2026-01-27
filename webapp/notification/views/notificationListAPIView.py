from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from notification.models import NotificationMessage
from notification.serializers import NotificationMessageSerializer


class NotificationListAPIView(ListAPIView):
    """List all notifications for the authenticated user."""
    serializer_class = NotificationMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationMessage.objects.filter(
            user=self.request.user
        ).select_related('related_post').order_by('-created_at')
