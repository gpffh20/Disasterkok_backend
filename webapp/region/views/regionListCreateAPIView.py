from django.db.models import QuerySet
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from notification.models import NotificationSetting
from region.models import Region
from region.serializers import RegionSerializer


class RegionListCreateAPIView(ListCreateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            notification_setting, created = NotificationSetting.objects.get_or_create(user=self.request.user)
            queryset = queryset.filter(notification_setting=notification_setting)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if not queryset:
            exist = False
        else:
            exist = True

        data = {
            "exist": exist,
            "results": serializer.data,
        }

        return Response(data)

    def perform_create(self, serializer):
        user = self.request.user
        notification_setting, created = NotificationSetting.objects.get_or_create(user=user)
        serializer.save(notification_setting=notification_setting)
