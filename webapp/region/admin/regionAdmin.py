from django.contrib import admin

from region.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'notification_setting',
        'default',
        'onOff',
        'name',
        'address',
        'roadAddress',
        'zoneCode',
        'xCoordinate',
        'yCoordinate',
        'aliasType',
    )