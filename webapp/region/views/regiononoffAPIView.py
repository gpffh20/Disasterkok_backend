from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from region.models import Region


class RegionOnOffAPIView(APIView):
    lookup_url_kwarg = 'region_id'

    def post(self, request, *args, **kwargs):
        region_id = self.kwargs.get(self.lookup_url_kwarg)
        region = get_object_or_404(Region, id=region_id)
        region.onOff = not region.onOff
        region.save(update_fields=['onOff'])
        return Response({'message': '변경되었습니다.'}, status=status.HTTP_200_OK)