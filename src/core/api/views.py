from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, filters
from django.db.models import Q

from core.models import Alert, TransactionHistory
from core.api.serializers import AlertSerializer, SiteSerializer, TransactionHistorySerializer
from core.pagination import TablePagination
from core.utils import GetSitesMixin


class HealthCheckView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response(status=status.HTTP_200_OK)


class AlertApiView(ListAPIView, GetSitesMixin):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by('time')
    pagination_class = TablePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['alert_id', 'zone', 'district', 'activity', 'status', 'time']

    def get_queryset(self):
        q = Q()
        queryset = super().get_queryset()
        sites = self.get_sites(self.request)

        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date and end_date:
            q = Q(time__range=[start_date, end_date])
        elif start_date and end_date is None:
            q = Q(time__gte=start_date)
        elif end_date and start_date is None:
            q = Q(time__lte=end_date)

        if sites:
            q = q & Q(site__in=sites)

        return queryset.filter(q)


class TransactionHistoryApiView(ListAPIView):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by('time')
    pagination_class = TablePagination


class SiteApiView(ListAPIView, GetSitesMixin):
    serializer_class = SiteSerializer
    pagination_class = TablePagination

    def get_queryset(self):
        sites = self.get_sites(self.request)
        return sites.order_by('time')
