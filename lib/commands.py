import json
import os
from random import randint
import time
import uuid

import discord
import requests

from lib.api import API, APIError
from lib.giphy import Giphy
from lib.poll import POLL_DIR
from lib.version import VERSION
from lib.youtube import Youtube

MSG_DICT = {
    "!help (!h)": "Shows this help message.",
    "!jeopardy (!j)": (
        "Receive a category with 5 questions and answers. The "
        "answers are marked as spoilers and are not revealed "
        "until you click them XD"
    ),
    "!whisper (!pm)": (
        "Get a salty DM from SaltBot. This can be used as a "
        "playground for experiencing all of the salty features"
    ),
    "!gif (!g)": (
        "Type !gif followed by keywords to get a cool gif. For example: !gif dog"
    ),
    "!waifu (!w)": "Get a picture of a personal waifu that's different each time",
    "!anime (!a)": "Get an anime recommendation just for you UwU",
    "!nut (!n)": "Receive a funny nut 'n go line",
    "!poll (!p)": 'Type "!poll help" for detailed information',
    "!vote (!v)": 'Vote in a poll. Type "!vote <poll id> <poll choice>" to cast your vote',
    "!youtube (!y)": "Get a youtube search result. Use the '-i' parameter to specify an index",
}

POLL_HELP_MSG = (
    "```How to set a poll:\nType the !poll command followed by the question, the "
    "answers, and the time all separated by semicolons. For Example:\n\n "
    "!poll How many times do you poop daily? ; Less than once ; Once ; Twice ; "
    "More than twice ; ends in 4 hours\n\nThe final poll expiry has to be in "
    'the format "ends in X Y" where "X" is any positive integer and "Y" '
    "is one of (hours, hour, minutes, minute, seconds, second)```"
)

UNIT_DICT = {
    "hours": 3600,
    "hour": 3600,
    "minutes": 60,
    "minute": 60,
    "seconds": 1,
    "second": 1,
}


def parse_expiry(expiry_str):
    """
        Take "ends in X Y" and turn it into a integer time in seconds
        For example:
            ends in 62 minutes -> time.time() + 3720
    """
    words = expiry_str.split(" ")
    unit = words.pop(-1).lower()
    amount = words.pop(-1).lower()
    return int(time.time()) + int(amount) * UNIT_DICT[unit]


def write_poll(prompt, choices, expiry, poll_id, channel_id, votes):
    """ Write the poll to disk as a json file """
    data = {
        "prompt": prompt,
        "choices": choices,
        "expiry": expiry,
        "poll_id": poll_id,
        "channel_id": channel_id,
        "votes": votes,
    }
    with open(f"{POLL_DIR}/{poll_id}.json", "w") as stream:
        stream.write(json.dumps(data))


def _get_idx_from_args(args):
    """ Parse the index from an API response and pick a random number if idx not present """
    if "-i" in args:
        if args[len(args) - 1] == "-i":
            raise ValueError('```Sorry, the last keyword cannot be "-i"```')

        for i in range(len(args)):
            if args[i] == "-i":
                idx = args[i + 1]
                args.remove("-i")
                args.remove(idx)
                try:
                    return int(idx)
                except ValueError:
                    raise ValueError(
                        f"```The argument after '-i' must be an integer```"
                    )

        return None


class Command(object):
    def __init__(self, user_msg):
        self._full_user = str(user_msg.author)
        self._user = self._full_user.split("#")[0]
        self._user_msg = user_msg
        self._channel = user_msg.channel
        self.commands = {
            "!whisper": self._whisper,
            "!pm": self._whisper,
            "!gif": self._gif,
            "!g": self._gif,
            "!nut": self._nut,
            "!u": self._nut,
            "!jeopardy": self._jeopardy,
            "!j": self._jeopardy,
            "!help": self._help,
            "!h": self._help,
            "!waifu": self._waifu,
            "!w": self._waifu,
            "!anime": self._anime,
            "!a": self._anime,
            "!vote": self._vote,
            "!v": self._vote,
            "!poll": self._poll,
            "!p": self._poll,
            "!youtube": self._youtube,
            "!y": self._youtube,
        }

    def _help(self, *args):
        """
            Return a help message that gives a list of commands
        """
        ret_msg = (
            f"```Good salty day to you {self._user}! Here's a list of commands "
            "commands that I understand:\n\n"
        )

        for msg in MSG_DICT:
            ret_msg += f"{msg} -> {MSG_DICT[msg]}\n\n"

        ret_msg += (
            "If you have any further questions/concerns or if SaltBot "
            "goes down, please hesitate to contact my developer: "
            "HighSaltLevels. He's salty enough without your help and "
            f"doesn't write buggy code. Current Version: {VERSION}```"
        )

        return "text", ret_msg

    def _vote(self, *args):
        """
            Cast a vote on an existing poll
        """
        cmd_args = list(args)
        try:
            poll_id = cmd_args.pop(0)
            choice = int(cmd_args.pop(0))
        except (IndexError, ValueError):
            return (
                "text",
                '```Please format your vote as "!vote <poll id> <choice number>"```',
            )

        try:
            with open(f"{POLL_DIR}/{poll_id}.json", "r") as stream:
                poll_data = json.loads(stream.read())
        except FileNotFoundError:
            return "text", f"```Poll {poll_id} does not exist or has expired```"

        choice_len = len(poll_data["choices"])

        if choice not in range(1, choice_len + 1):
            response = f"```{choice} is not an available selection from:\n\n"
            for choice_num in range(choice_len):
                response += f"{choice_num+1}.\t{poll_data['choices'][choice_num]}\n"
            return "text", f"{response}```"

        for option, takers in poll_data["votes"].items():
            if self._full_user in takers:
                poll_data["votes"][option].remove(self._full_user)

        poll_data["votes"][str(choice - 1)].append(self._full_user)
        write_poll(**poll_data)
        return "text", f"```You have selected {poll_data['choices'][choice-1]}```"

    def _poll(self, *args):
        """
            Start a poll
        """
        if "help" in self._user_msg.content.lower():
            return "text", POLL_HELP_MSG

        if isinstance(self._channel, discord.channel.DMChannel):
            return "text", "```Polls don't work in DMs :(```"

        full_phrase = " ".join(args)
        choices = [phrase.strip() for phrase in self._user_msg.content.split(";")]
        prompt = choices.pop(0)

        try:
            expiry_str = (
                choices.pop(-1)
                if "ends in" in choices[-1].lower()
                else "ends in 1 hour"
            )
            expiry = parse_expiry(expiry_str)
        except (KeyError, IndexError, ValueError) as error:
            return "text", POLL_HELP_MSG

        poll_id = str(uuid.uuid4()).split("-")[0]

        votes = {}
        for choice in range(len(choices)):
            votes[choice] = []

        write_poll(
            prompt, choices, expiry, poll_id, channel_id=self._channel.id, votes=votes
        )

        return_str = f"```{prompt} ({expiry_str})\n\n"
        for choice_num in range(len(choices)):
            return_str += f"{choice_num+1}.\t{choices[choice_num]}\n"
        return_str += f'\n\nType or DM me "!vote {poll_id} <choice number>" to vote```'

        return "text", return_str

    def _jeopardy(self, *args):
        """
            Return a 5 jeopardy questions and answers
        """
        # Get a random set of questions
        rand = randint(0, 18417)
        resp = requests.get(f"http://jservice.io/api/category?id={rand}")

        # Verify status code
        if resp.status_code != 200:
            return "```I'm Sorry. Something went wrong getting the questions```"

        # Convert to a json
        q_and_a = json.loads(resp.text)

        # Build and return the questions and answers
        msg = f'The Category is: "{q_and_a["title"]}"\n\n'

        for i in range(5):
            question = self._remove_html_crap(q_and_a["clues"][i]["question"])
            answer = self._remove_html_crap(q_and_a["clues"][i]["answer"])
            msg += f"Question {i+1}: {question}\nAnswer: ||{answer}||\n\n"

        return "text", msg

    def _whisper(self, *args):
        """
            Return a hello message as a DM to the person who requested
        """
        return (
            "user",
            (
                f"```Hello {self._user}! You can talk to me here (Where no one can hear our "
                "mutual salt).```"
            ),
        )

    def _gif(self, *args):
        """
            Use the giphy api to query and return one or all gif
        """
        # Convert from tuple to list so we can modify
        args = list(args)
        if "-a" in args:
            if not isinstance(self._user_msg.channel, discord.abc.PrivateChannel):
                return "text", "```You can only use -a in a DM!```"

            args.remove("-a")
            giphy = Giphy(*args)
            return "list", giphy.all_gifs

        try:
            idx = _get_idx_from_args(args)
        except ValueError as error:
            return "text", str(error)

        try:
            giphy = Giphy(args)
            if idx is None:
                idx = randint(0, giphy.num_gifs - 1)
            return "text", giphy.get_gif(idx)

        except APIError as error:
            return "text", str(error)

    def _youtube(self, *args):
        """
            Use the Youtube API to return a youtube video
        """
        # Convert from tuple to list so we can modify
        args = list(args)
        try:
            idx = _get_idx_from_args(args)
        except ValueError as error:
            return "text", str(error)

        try:
            youtube = Youtube(*args)
            if not idx:
                idx = randint(0, youtube.num_videos - 1)
            return "text", youtube.get_video(idx)

        except APIError as error:
            return "text", str(error)

    def _waifu(self, *args):
        for _ in range(5):
            rand = randint(0, 99999)
            url = f"https://www.thiswaifudoesnotexist.net/example-{rand}.jpg"

            resp = requests.get(url, stream=True)
            if resp.status_code == 200:
                with open("temp.jpg", "wb") as fw:
                    fw.write(resp.content)
                return "file", "temp.jpg"

        log("admin", f"Got HTTP Status {resp.status_code} with content -> {resp.text}")
        return "text", "```Sorry, I coudn't get that waifu :(```"

    def _anime(self, *args):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0."
        }
        resp = requests.get("https://anidb.net/anime/random", headers=headers)
        if resp.status_code != 200:
            return "```Sowwy. Couldn't connect to the internet to get an anime recommendation :(```"
        data = resp.text
        title_idx = data.find("<title>")
        title_idx += 1
        title = ""
        for char in data[title_idx:]:
            if char == "<":
                break
            else:
                title += char
        title = title[6:-15]

        description_idx = data.find("content=")
        description_idx += 8
        description = ""
        for char in data[description_idx:]:
            if char == "/":
                break
            else:
                description += char
        return (
            "text",
            "```Here's an anime for you:\n\nTitle:\n{}\n\nDescription:\n{}```".format(
                title, description
            ),
        )

    def _nut(self, *args):
        with open("nut.txt") as fread:
            lines = [line for line in fread.readlines()]

        rand = randint(0, len(lines) - 1)
        return "text", f"```Remember {self._user}, don't {lines[rand]}```"

    def _remove_html_crap(self, text):
        return (
            text.replace("<i>", "")
            .replace("</i>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("\\", " ")
        )
