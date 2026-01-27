from django.db import models

from user.models import User


class NotificationSetting(models.Model):
    """User's notification settings container - holds regional notification preferences."""

    class Meta:
        db_table = 'notification_setting'
        verbose_name = 'NotificationSetting'
        verbose_name_plural = 'NotificationSettings'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_setting'
    )

    def __str__(self):
        return f"NotificationSetting for {self.user}"


# Alias for backward compatibility during migration
Notification = NotificationSetting
