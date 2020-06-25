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
            await CLIENT.send_message(
                msg.channel,
                (
                    f"```Hello. I'm sorry I don't understand {cmd}. Please type "
                    '"!help" to see a list of available commands\n```'
                ),
            )

        else:
            type_, resp = bot_cmd.commands[cmd](*args)
            LOGGER.log_sent(msg.author, msg.channel, resp)

            if type_ == "text":
                await CLIENT.send_message(msg.channel, resp)
            elif type_ == "file":
                await CLIENT.send_file(msg.channel, resp)
            elif type_ == "list":
                for item in resp:
                    await CLIENT.send_message(msg.channel, item)
            else:
                err_msg = "```Unexpected error :(```"
                await CLIENT.send_message(msg.channel, err_msg)


@CLIENT.event
async def on_ready():
    print("Logged in as")
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print("------")
    await CLIENT.change_presence(game=discord.Game(name="The Salt Shaker"))
