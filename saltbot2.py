import os
import discord

GIPHY_AUTH = os.getenv('GIPHY_AUTH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = discord.Client()

def help_fun():
    return '```Sorry this feature is not implemented yet```'

def jeopardy():
    return '```Sorry this feature is not implemented yet```'

def whisper():
    return '```Sorry this feature is not implemented yet```'

def hi():
    return '```Sorry this feature is not implemented yet```'

def goodnight():
    return '```Sorry this feature is not implemented yet```'

def gif():
    return '```Sorry this feature is not implemented yet```'

cmd_dict = {'!help':      help_fun,
            '!jeopardy':  jeopardy,
            '!whisper':   whisper,
            '!hi':        hi,
            '!goodnight': goodnight,
            '!gif':       gif}

@client.event
async def on_message(message):
    # Only do something if command starts with ! or bot is not sending message
    if message.author != client.user and message.content.startswith('!'):
        # Get the command
        cmd = message.content.split(' ')[0]

        # Notify user/channel if that command does not exist
        if cmd not in cmd_dict.keys():
            msg = ("```Hello. I'm sorry I don't understand " + cmd + ". " 
                  " Please type \"!help\" to see a list of available commands"
                  "\n```")
            await client.send_message(message.channel, msg)
        
        # Otherwise, call its assiciated function to get the string to send
        else:
            await client.send_message(message.channel, cmd_dict[cmd]())

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)
