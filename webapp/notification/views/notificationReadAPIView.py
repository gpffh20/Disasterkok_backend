from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import NotificationMessage
from notification.serializers import NotificationMessageSerializer


class NotificationReadAPIView(APIView):
    """Mark a single notification as read."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        try:
            notification = NotificationMessage.objects.get(
                id=notification_id,
                user=request.user
            )
        except NotificationMessage.DoesNotExist:
            return Response(
                {'error': '알림을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=['is_read'])

        serializer = NotificationMessageSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationReadAllAPIView(APIView):
    """Mark all notifications as read."""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        count = NotificationMessage.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {'message': f'{count}개의 알림을 읽음 처리했습니다.'},
            status=status.HTTP_200_OK
        )
