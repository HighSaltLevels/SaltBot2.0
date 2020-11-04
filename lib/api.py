from http import HTTPStatus
import requests


class APIError(Exception):
    """ Raised if there is an issue getting the API query """


class API:
    def __init__(self, *query_args):
        self._query_args = query_args
        self.response = self._request()
        self.data = self.response.json()
        self.validate_status()

    def _request(self):
        resp = requests.get(self.url)
        if resp.status_code != HTTPStatus.OK:
            return None

        return resp

    def validate_status(self):
        try:
            self.response.raise_for_status()
        except requests.HTTPError as error:
            raise APIError(f"```Sorry, the server responded with '{error}'```")

        # Non-200 status code
        if not self.response:
            raise APIError("```Sorry, I had trouble getting that query :(```")

    def validate_idx(self, idx, max_idx):
        # Specified index wasn't an integer
        try:
            idx = int(idx)
        except ValueError:
            raise APIError(
                "```You have to specify an integer if you want query by index!```"
            )

        if idx < 0 or idx > max_idx:
            raise APIError(
                f"```The index must be between 0 and {max_idx} for this query```"
            )

    def _parse_keywords(self, keywords, separator):
        query = ""
        for kw in keywords:
            query += f"{kw}{separator}"

        # Remove the last '+'
        query = query[:-1]
        return query
