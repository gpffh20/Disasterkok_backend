from rest_framework import status
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from notification.models import NotificationMessage
from notification.serializers import NotificationMessageSerializer


class NotificationDetailAPIView(RetrieveDestroyAPIView):
    """Retrieve or delete a specific notification."""
    serializer_class = NotificationMessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'notification_id'

    def get_queryset(self):
        return NotificationMessage.objects.filter(
            user=self.request.user
        ).select_related('related_post')
