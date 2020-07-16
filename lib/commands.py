import json
from random import randint

import discord
import requests

from lib.constants import VERSION
from lib.giphy import Giphy, GiphyError

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
        "Type !gif followed by keywords to get a cool gif. For " "example: !gif dog"
    ),
    "!waifu (!w)": ("Get a picture of a personal waifu that's different each" "time"),
    "!anime (!a)": "Get an anime recommendation just for you UwU",
    "!nut (!n)": "Receive a funny nut 'n go line",
}


class Command(object):
    def __init__(self, user_msg):
        self._user = str(user_msg.author).split("#")[0]
        self._user_msg = user_msg
        self._commands = {
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
        }

    @property
    def commands(self):
        return self._commands

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

    def _jeopardy(self, *args):
        """
            Return a 5 jeopardy questions and answers
        """
        # Get a random set of questions
        rand = randint(0, 18417)
        resp = requests.get("http://jservice.io/api/category?id={}".format(rand))

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
            "text",
            (
                f"```Hello {self._user}! You can talk to me here (Where no one can hear our "
                "mutual salt).```"
            ),
        )

    def _gif(self, *args):
        """
            Use the giphy api to query and return one or all gif
        """
        args = list(args)
        if "-a" in args:
            if not isinstance(self._user_msg.channel, discord.channel.PrivateChannel):
                return "text", "```You can only use -a in a DM!```"

            args.remove("-a")
            giphy = Giphy(args)
            return "list", giphy.all_gifs

        idx = None
        if "-i" in args:
            for i in range(len(args)):
                if args[len(args) - 1] == "-i":
                    return "text", '```Sorry, the last keyword cannot be "-i"```'

                if args[i] == "-i":
                    idx = args[i + 1]
                    args.remove("-i")
                    args.remove(idx)
                    break

        giphy = Giphy(args)

        try:
            giphy.validate_status()
        except GiphyError as error:
            return "text", str(error)

        if not idx:
            idx = randint(0, giphy.num_gifs - 1)

        try:
            giphy.validate_idx(idx)
        except GiphyError as error:
            return "text", str(error)

        return "text", giphy.get_gif(idx)

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
