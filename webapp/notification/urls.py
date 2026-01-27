from django.urls import path

from notification.views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
    NotificationReadAPIView,
    NotificationReadAllAPIView,
    NotificationUnreadCountAPIView,
)

urlpatterns = [
    path('', NotificationListAPIView.as_view(), name='notification-list'),
    path('<int:notification_id>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('<int:notification_id>/read/', NotificationReadAPIView.as_view(), name='notification-read'),
    path('read-all/', NotificationReadAllAPIView.as_view(), name='notification-read-all'),
    path('unread-count/', NotificationUnreadCountAPIView.as_view(), name='notification-unread-count'),
]
