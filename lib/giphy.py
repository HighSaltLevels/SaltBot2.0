import os

from lib.api import API

GIPHY_AUTH = os.environ["GIPHY_AUTH"]


class Giphy(API):
    @property
    def num_gifs(self):
        return len(self.data["data"]) if self.response else 0

    @property
    def all_gifs(self):
        self.validate_num_gifs()
        return [
            self.data["data"][index]["bitly_gif_url"] for index in range(self.num_gifs)
        ]

    def get_gif(self, idx):
        self.validate_num_gifs()
        max_idx = len(self.data["data"])
        self.validate_idx(idx, max_idx)
        return self.data["data"][idx]["bitly_gif_url"]

    @property
    def url(self):
        query = self._parse_keywords(self._query_args, separator="+")
        return f"http://api.giphy.com/v1/gifs/search?q={query}&api_key={GIPHY_AUTH}"

    def validate_num_gifs(self):
        if self.num_gifs == 0:
            raise APIError("```Sorry, there were no gifs for that query :(```")
