from django.db import models

from user.models import User


class NotificationMessage(models.Model):
    """Actual notification messages sent to users."""

    NOTIFICATION_TYPE_CHOICES = [
        ('POST_LIKE', '게시글 좋아요'),
        ('DISASTER_ALERT', '재난 알림'),
        ('SYSTEM', '시스템 알림'),
    ]

    class Meta:
        db_table = 'notification_message'
        verbose_name = 'NotificationMessage'
        verbose_name_plural = 'NotificationMessages'
        ordering = ['-created_at']

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=100,
    )

    content = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='SYSTEM',
    )

    is_read = models.BooleanField(
        default=False,
    )

    related_post = models.ForeignKey(
        'post.Post',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"[{self.notification_type}] {self.title} - {self.user}"
