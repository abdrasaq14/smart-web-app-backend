from typing import List

from core.exceptions import GenericErrorException
from core.models import Company, Site


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
                companies.append(Site.objects.get(id=int(company_id)))
            except Company.DoesNotExist:
                raise GenericErrorException(f"Company: {company_id} does not exist")

        return companies
