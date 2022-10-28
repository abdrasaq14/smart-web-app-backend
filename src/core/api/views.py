from rest_framework import filters, status
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from core.api.serializers import (
    AlertSerializer,
    CompanySerializer,
    DeviceSerializer,
    EventLogSerializer,
    ListDeviceSerializer,
    ListTransactionHistorySerializer,
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


class BaseActivityLogView(ListAPIView, UpdateAPIView, CompanySiteDateQuerysetMixin):
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


class TransactionHistoryApiView(ListAPIView, CreateAPIView, CompanySiteDateQuerysetMixin):
    queryset = TransactionHistory.objects.all().order_by("time")
    pagination_class = TablePagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TransactionHistorySerializer
        return ListTransactionHistorySerializer


class TransactionHistoryDetailsApiView(RetrieveUpdateDestroyAPIView, CompanySiteDateQuerysetMixin):
    serializer_class = ListTransactionHistorySerializer
    action_serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by("time")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TransactionHistorySerializer
        return ListTransactionHistorySerializer


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
    pagination_class = TablePagination


class CompanyDetailsApiView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class DeviceApiView(ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, CompanySiteDateQuerysetMixin):
    queryset = Device.objects.all()
    serializer_class = ListDeviceSerializer
    action_serializer_class = DeviceSerializer
    pagination_class = TablePagination

    site_related_field = 'site'
    company_related_field = 'company'
    time_related_field = 'linked_at'

    def post(self, request, *args, **kwargs):
        serializer = self.action_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.action_serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class DeviceTariffApiView(ListAPIView):
    queryset = DeviceTariff.objects.all()
    serializer_class = DeviceTariffSerializer
