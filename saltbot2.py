import os
import discord
from random import randint

GIPHY_AUTH = os.getenv('GIPHY_AUTH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = discord.Client()

def help_fun():
    return '```Sorry this feature is not implemented yet```'

def jeopardy():
    return '```Sorry this feature is not implemented yet```'

def whisper():
    return '```Sorry this feature is not implemented yet```'

def hi(user=''):
    '''
        This function reads greetings.txt and returns a random hello message
    '''

    # Read all of the greetings into memory
    with open('greetings.txt','r') as greets:
        hellos = [line for line in greets.readlines()]

        # Get a random number to index with and return the message
        msg = hellos[randint(0, len(hellos)-1)]
        return '```Hi {}! {}```'.format(user, msg)

def goodnight(user=''):
    '''
        This function reads goodnights.txt and returns a random goodnight message
    '''

    # Read all of the goodnights into memory
    with open('goodnights.txt','r') as nights:
        goodnights = [line for line in nights.readlines()]

        # Get a random number to index with and return the message
        msg = goodnights[randint(0, len(goodnights)-1)]
        return '```Goodnight {}! {}```'.format(user, msg)

def gif():
    return '```Sorry this feature is not implemented yet```'

cmd_dict = {'!help':      help_fun,
            '!jeopardy':  jeopardy,
            '!whisper':   whisper,
            '!hi':        hi,
            '!goodnight': goodnight,
            '!gif':       gif}

@client.event
async def on_message(msg):
    # Only do something if command starts with ! or bot is not sending message
    if msg.author != client.user and msg.content.startswith('!'):
        # Get the command
        cmd = msg.content.split(' ')[0]

        # Notify user/channel if that command does not exist
        if cmd not in cmd_dict.keys():
            ret_msg = ("```Hello. I'm sorry I don't understand " + cmd + ". " 
                  " Please type \"!help\" to see a list of available commands"
                  "\n```")
            await client.send_message(message.channel, ret_msg)
        
        # Otherwise, call its assiciated function to get the string to send
        else:
            # Parse the author's username
            author = str(msg.author).split('#')[0]
            await client.send_message(msg.channel, cmd_dict[cmd](author))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)
