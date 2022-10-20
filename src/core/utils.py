from typing import List
from rest_framework.generics import GenericAPIView
from django.db.models import Q

from core.exceptions import GenericErrorException
from core.models import Company, Site


class GetSitesMixin:
    ...


class CompanySiteFiltersMixin:
    def get_sites(self, request) -> List[Site]:
        sites = request.query_params.get("sites", "")

        if not sites:
            sites = Site.objects.all()
            if len(sites) < 1:
                raise GenericErrorException("No devices linked!")

            return sites

        site_ids = sites.split(",")
        return self._search_sites(site_ids)

    def get_companies(self, request) -> List[Company]:
        companies = request.query_params.get("companies", "")

        if not companies:
            companies = Company.objects.all()
            if len(companies) < 1:
                raise GenericErrorException("No devices linked!")

            return companies

        company_id = companies.split(",")
        return self._search_companies(company_id)

    def _search_sites(self, site_ids: List[str]) -> List[Site]:
        sites = []

        for site_id in site_ids:
            try:
                sites.append(Site.objects.get(id=int(site_id)))
            except Site.DoesNotExist:
                raise GenericErrorException(f"Site: {site_id} does not exist")

        return sites

    def _search_companies(self, company_ids: List[str]) -> List[Company]:
        companies = []

        for company_id in company_ids:
            try:
                companies.append(Company.objects.get(id=int(company_id)))
            except Company.DoesNotExist:
                raise GenericErrorException(f"Company: {company_id} does not exist")

        return companies


class CompanySiteDateQuerysetMixin(GenericAPIView, CompanySiteFiltersMixin):
    """"""
    time_related_field = 'time'
    site_related_field = 'site'
    company_related_field = 'site__company'

    def get_queryset(self):
        q = Q()
        queryset = super().get_queryset()

        sites = self.get_sites(self.request)
        companies = self.get_companies(self.request)

        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)

        if start_date and end_date:
            q = Q(**{f'{self.time_related_field}': [start_date, end_date]})
        elif start_date and end_date is None:
            q = Q(**{f'{self.time_related_field}__gte': start_date})
        elif end_date and start_date is None:
            q = Q(**{f'{self.time_related_field}__lte': end_date})

        if companies:
            q = q & Q(**{f'{self.company_related_field}__in': companies})

        if sites:
            q = q & Q(site__in=sites)
            q = q & Q(**{f'{self.site_related_field}__in': sites})

        return queryset.filter(q)
