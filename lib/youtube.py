""" Module for youtube related operations """
import os
from lib.api import API

YOUTUBE_AUTH = os.environ["YOUTUBE_AUTH"]
YOUTUBE_MAX_IDX = 49
BASE_URL = "https://www.youtube.com/watch?v="


class Youtube(API):
    """ Represents a Youtube Object """

    def get_video(self, idx):
        self.validate_num_vids()
        max_idx = len(self.data["items"])
        self.validate_idx(idx, max_idx)

        return BASE_URL + self.data["items"][idx]["id"]["videoId"]

    def validate_num_vids(self):
        if self.num_videos == 0:
            raise APIError("```Sorry, there were no videos for that query :(```")

    @property
    def url(self):
        query = self._parse_keywords(self._query_args, separator=",")
        return f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_AUTH}&q={query}&maxResults=50&type=video"

    @property
    def num_videos(self):
        return len(self.data["items"]) if self.response else 0
