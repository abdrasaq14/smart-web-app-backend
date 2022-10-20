from rest_framework import filters, status
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response

from core.api.serializers import (
    AlertSerializer,
    CompanySerializer,
    DeviceSerializer,
    EventLogSerializer,
    ListDeviceSerializer,
    SiteSerializer,
    TransactionHistorySerializer,
    UserLogSerializer,
    DeviceTariffSerializer
)
from core.models import Alert, Company, Device, EventLog, Site, TransactionHistory, UserLog, DeviceTariff
from core.pagination import TablePagination
from core.utils import CompanySiteDateQuerysetMixin


class HealthCheckView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response(status=status.HTTP_200_OK)


class BaseActivityLogView(ListAPIView, CompanySiteDateQuerysetMixin):
    pagination_class = TablePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["alert_id", "zone", "district", "activity", "status"]


class AlertApiView(BaseActivityLogView):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by("time")


class EventLogApiView(BaseActivityLogView):
    serializer_class = EventLogSerializer
    queryset = EventLog.objects.all().order_by("time")


class UserLogApiView(BaseActivityLogView):
    serializer_class = UserLogSerializer
    queryset = UserLog.objects.all().order_by("time")


class TransactionHistoryApiView(ListAPIView, CompanySiteDateQuerysetMixin):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by("time")
    pagination_class = TablePagination


class SiteApiView(ListAPIView, CompanySiteDateQuerysetMixin):
    queryset = Site.objects.all().order_by("time")
    serializer_class = SiteSerializer
    pagination_class = TablePagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "asset_name",
        "asset_type",
        "asset_co_ordinate",
        "asset_capacity",
    ]
    site_related_field = ''
    company_related_field = 'company'


class CompanyApiView(ListAPIView, CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class DeviceApiView(ListAPIView, CreateAPIView, CompanySiteDateQuerysetMixin):
    queryset = Device.objects.all()
    serializer_class = ListDeviceSerializer
    action_serializer_class = DeviceSerializer

    site_related_field = 'site'
    company_related_field = 'company'
    time_related_field = 'linked_at'

    def post(self, request, *args, **kwargs):
        serializer = self.action_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DeviceTariffApiView(ListAPIView):
    queryset = DeviceTariff.objects.all()
    serializer_class = DeviceTariffSerializer
