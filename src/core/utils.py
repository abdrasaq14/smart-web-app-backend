from typing import List
from core.exceptions import GenericErrorException
from core.models import Site


class GetSitesMixin:
    def get_sites(self, request) -> List[Site]:
        sites = request.query_params.get('sites', '')

        if not sites:
            sites = Site.objects.all()
            if len(sites) < 1:
                raise GenericErrorException('No devices linked!')

            return sites

        site_ids = sites.split(',')
        return self._search_sites(site_ids)

    def _search_sites(self, site_ids: List[str]) -> List[Site]:
        sites = []

        for site_id in site_ids:
            try:
                sites.append(Site.objects.get(id=int(site_id)))
            except Site.DoesNotExist:
                raise GenericErrorException(f'Site: {site_id} does not exist')

        return sites
