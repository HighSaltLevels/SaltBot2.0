import asyncio
import glob
import json
import time

import discord

from lib.commands import Command
from lib.logger import Logger

LOGGER = Logger()
CLIENT = discord.Client()


@CLIENT.event
async def on_message(msg):
    # Only do something if command starts with ! or bot is not sending message
    if msg.author != CLIENT.user and msg.content.startswith("!"):
        LOGGER.log_received(msg.author, msg.channel, msg.content)

        args = msg.content.split(" ")
        cmd = args.pop(0)
        bot_cmd = Command(msg)

        if cmd not in bot_cmd.commands:
            await msg.channel.send(
                f"```Hello. I'm sorry I don't understand {cmd}. Please type "
                '"!help" to see a list of available commands\n```'
            )

        else:
            type_, resp = bot_cmd.commands[cmd](*args)
            LOGGER.log_sent(msg.author, msg.channel, cmd)

            if type_ == "text":
                await msg.channel.send(resp)
            elif type_ == "file":
                await msg.channel.send(file=discord.File(resp))
            elif type_ == "list":
                for item in resp:
                    await msg.channel.send(item)
            elif type_ == "user":
                await msg.author.send(resp)
            else:
                err_msg = "```Unexpected error :(```"
                await msg.channel.send(err_msg)


@CLIENT.event
async def on_ready():
    LOGGER.log("Logged in as")
    LOGGER.log(CLIENT.user.name)
    LOGGER.log(str(CLIENT.user.id))
    await CLIENT.change_presence(activity=discord.Game(name="The Salt Shaker"))


async def monitor_polls():
    while True:
        polls = glob.glob("./polls/*")
        for poll in polls:
            with open(poll) as stream:
                poll_data = json.loads(stream.read())
            if time.time() > poll_data["expiry"]:
                channel = CLIENT.get_channel(poll_data["channel_id"])
                total_choices = len(poll_data["choices"])
                results = {}
                for choice_num in range(total_choices):
                    results[coice_num] = len(poll_data["choices"][choice_num])

                response = "```Results:\n\n"
                for result in results:
                    choice = poll_data["choices"][str(result)]
                    response += "\t{choice] -> {int(len(choice)/total_choices)}}\n"

                await channel.send(f"{response}```")

        await asyncio.sleep(5)


POLL_THREAD = asyncio.create_task(monitor_polls())
