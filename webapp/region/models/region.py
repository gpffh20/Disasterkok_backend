from django.db import models

from notification.models import NotificationSetting


ALIASTYPE_CATEGORY_CHOICES = (
    ('home', 'home'),
    ('school', 'school'),
    ('work', 'work'),
    ('etc', 'etc'),
)


class Region(models.Model):
    class Meta:
        db_table = 'region'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

    notification_setting = models.ForeignKey(
        NotificationSetting,
        on_delete=models.CASCADE,
        related_name='regions'
    )

    default = models.BooleanField(
        default=False,
    )

    onOff = models.BooleanField(
        default=True,
        null=False,
    )

    name = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    address = models.TextField(
        null=True,
    )

    roadAddress = models.CharField(
        max_length=255,
        null=True,
    )

    zoneCode = models.CharField(
        max_length=10,
        null=True,
    )

    xCoordinate = models.CharField(
        max_length=50,
        null=True,
    )

    yCoordinate = models.CharField(
        max_length=50,
        null=True,
    )

    aliasType = models.CharField(
        max_length=10,
        choices=ALIASTYPE_CATEGORY_CHOICES,
        null=True,
    )

