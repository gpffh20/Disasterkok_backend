from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from post.models import PostLike
from notification.models import NotificationMessage


def send_notification_to_websocket(notification):
    """Send notification to user's WebSocket channel."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f'notifications_{notification.user.id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'notification_type': notification.notification_type,
                    'is_read': notification.is_read,
                    'related_post_id': notification.related_post_id,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )
    except Exception:
        # WebSocket/Redis connection failed - notification is still saved to DB
        pass


@receiver(post_save, sender=PostLike)
def create_like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes a post."""
    if not created:
        return

    post = instance.post
    post_author = post.user
    liker = instance.user

    # Don't notify if user likes their own post
    if post_author == liker or post_author is None:
        return

    liker_name = liker.username if not post.is_anonymous else '익명'

    notification = NotificationMessage.objects.create(
        user=post_author,
        title='게시글 좋아요',
        content=f'{liker_name}님이 회원님의 게시글 "{post.title}"을 좋아합니다.',
        notification_type='POST_LIKE',
        related_post=post,
    )

    # Send real-time notification via WebSocket
    send_notification_to_websocket(notification)
