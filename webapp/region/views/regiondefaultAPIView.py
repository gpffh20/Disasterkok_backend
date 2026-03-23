from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from notification.models import NotificationSetting
from region.models import Region


class RegionDefaultAPIView(APIView):
    lookup_url_kwarg = 'region_id'

    def post(self, request, *args, **kwargs):
        region_id = self.kwargs.get(self.lookup_url_kwarg)
        user = request.user
        notification_setting = get_object_or_404(NotificationSetting, user=user)
        regions = Region.objects.filter(notification_setting=notification_setting)
        for region in regions:
            region.default = False
            region.save()

        default_region = get_object_or_404(Region, id=region_id)
        default_region.default = True
        default_region.save()

        return Response({'message': '변경되었습니다.'}, status=status.HTTP_200_OK)