from http import HTTPStatus
import os

import requests

GIPHY_AUTH = os.environ["GIPHY_AUTH"]


class GiphyError(Exception):
    """ Raised if there is an issue getting the gif """


class Giphy(object):
    def __init__(self, giphy_kw=[]):
        self._giphy_kw = giphy_kw
        self._url = self._create_url(self._giphy_kw)
        self._response = self._request()
        self._num_gifs = len(self.response["data"]) if self._response else 0

    @property
    def num_gifs(self):
        return self._num_gifs

    @property
    def response(self):
        return self._response.json()

    @response.setter
    def response(self, resp):
        self._response = resp

    @property
    def all_gifs(self):
        return [
            self.response["data"][index]["bitly_gif_url"]
            for index in range(self.num_gifs)
        ]

    def _request(self):
        resp = requests.get(self._url)
        if resp.status_code != HTTPStatus.OK:
            return None

        return resp

    def validate_status(self):
        try:
            self._response.raise_for_status()
        except requests.HTTPError as error:
            raise GiphyError(f"```Sorry, giphy responded with '{error}'```")

        # Non-200 status code
        if not self.response:
            raise GiphyError("```Sorry, I had trouble getting that gif :(```")

        # No gifs returned from query
        if self.num_gifs == 0:
            raise GiphyError("```Sorry, there were no gifs of that query :(```")

    def validate_idx(self, idx):
        # Specified index wasn't an integer
        try:
            idx = int(idx)
        except ValueError:
            raise GiphyError(
                "```You have to specify a number between 0 and 24 if you want "
                "query by index!```"
            )

        if idx < 0 or idx > self.num_gifs:
            raise GiphyError(
                f"```The index must be between 0 and {self.num_gifs-1} for this query```"
            )

    def get_gif(self, idx):
        return self.response["data"][int(idx)]["bitly_gif_url"]

    def _create_url(self, keywords):
        uri = ""
        for kw in keywords:
            uri += f"{kw}+"

        # Remove the last '+'
        uri = uri[:-1]

        return f"http://api.giphy.com/v1/gifs/search?q={uri}&api_key={GIPHY_AUTH}"
