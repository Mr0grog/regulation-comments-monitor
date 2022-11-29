from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
import httpx


class ApiError(Exception):
    pass


class RegulationsGovApi:
    """
    A minimal API client for working with Regulations.gov data. This includes
    a few light-weight wrappers for getting or listing objects.

    Full API documentation is at: https://open.gsa.gov/api/regulationsgov/.

    Parameters
    ----------
    api_key : str
        Your regulations.gov API key. See
        https://open.gsa.gov/api/regulationsgov/#getting-started for
        instructions on getting an API key.
    base_url : str, optional
        The base URL to the regulations.gov API.
    """

    def __init__(self, api_key, base_url='https://api.regulations.gov/'):
        self.base_url = base_url
        self.api_key = api_key

    def get_json(self, path, headers=None, **kwargs):
        url = urljoin(self.base_url, path)

        if not headers:
            headers = {}
        headers['X-Api-Key'] = self.api_key

        response = httpx.get(url, headers=headers, **kwargs)
        data = response.json()
        if 'errors' in data:
            raise ApiError(', '.join(f'(Status {e["status"]}) {e["title"]}'
                                        for e in data['errors']))

        return data

    def get_docket(self, docket_id):
        data = self.get_json(f'/v4/dockets/{docket_id}')
        return data['data']


    def list_docket_comments(self, docket_id, after=None):
        if not after:
            after = datetime.now(tz=timezone.utc) - timedelta(weeks=25)

        after_string = after.astimezone(timezone.utc).strftime('%Y-%m-%d')

        page = 1
        while page > 0:
            # Filtering on dates is tricky; they expect very specific formats:
            # - postedDate: "%Y-%m-%d"
            # - lastModifiedDate: "%Y-%m-%d %H:%M:%S" (note no time zone, and uses
            #   space instead of "T" separator)
            # - receiveDate: can't filter (it's in the docs, but doesn't work)
            data = self.get_json('/v4/comments', params={
                'filter[docketId]': docket_id,
                'filter[postedDate][ge]': after_string,
                'sort': '-postedDate',
                'page[size]': 250,
                'page[number]': page
            })
            yield from data['data']

            page = (page + 1) if data['meta']['hasNextPage'] else -1
