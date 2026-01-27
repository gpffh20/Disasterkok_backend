from rest_framework import serializers

from notification.models import NotificationMessage


class NotificationMessageSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    related_post_id = serializers.IntegerField(
        source='related_post.id',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = NotificationMessage
        fields = [
            'id',
            'title',
            'content',
            'notification_type',
            'notification_type_display',
            'is_read',
            'related_post_id',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'title',
            'content',
            'notification_type',
            'notification_type_display',
            'related_post_id',
            'created_at',
        ]
