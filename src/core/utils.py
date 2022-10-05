from typing import List
from core.exceptions import GenericErrorException
from core.models import Site


class GetSitesMixin:
    def get_sites(self, request) -> List[Site]:
        sites = request.query_params.get('sites', '')

        if not sites:
            return Site.objects.all()

        site_ids = sites.split(',')
        return self.search_sites(site_ids)

    def search_sites(self, site_ids: List[str]) -> List[Site]:
        sites = []

        for site_id in site_ids:
            try:
                sites.append(Site.objects.get(id=int(site_id)))
            except Site.DoesNotExist:
                raise GenericErrorException(f'Site: {site_id} does not exist')

        return sites
