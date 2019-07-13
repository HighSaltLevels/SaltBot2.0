import os
import requests
import discord
import json
from random import randint

GIPHY_AUTH = os.getenv('GIPHY_AUTH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

msg_list = ['!help:      Shows this help message.\n',
            '!jeopardy:  Receive a category with 5 questions and answers. The ' +
                        'answers are marked as\n            spoilers and are not ' +
                        'revealed until you click them XD\n',
            '!whisper:   Get a salty DM from SaltBot. This can be used as a ' +
                        'playground for\n            experiencing all of the '
                        'salty features.\n',
            '!hi:        Be greeted by SaltBot with a little added salt\n',
            '!goodnight: Hear a salty goodnight from SaltBot\n',
            '!gif:       Type "!gif" followed by keywords to get a cool gif ' +
                        'For example: !gif dog\n']

client = discord.Client()

def help_fun(author=''):
    ret_msg = '```Good salty day to you ' + author + '! Here\'s a list of ' + \
          'commands that I understand:\n\n'
    for msg in msg_list:
        ret_msg+=msg

    ret_msg+='\n\nIf you have any further questions/concerns or if SaltBot ' + \
             'goes down, please hesitate to\ncontact my developer: ' + \
             'HighSaltLevels. He\'s salty enough without your help and ' + \
             'doesn\'t\nwrite buggy code.```'

    return ret_msg

def jeopardy():
    return '```Sorry this feature is not implemented yet```'

def whisper(author=''):
    '''
        This function returns a hello message as a DM to the person who requested
    '''
    return '```Hello ' + author + '! You can talk to me here (Where no one ' + \
           'hear our mutual salt).```' 

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

def gif(keywords='whoops', index=None):
    '''
        This function uses the giphy api to query and return a gif
    '''

    # Validate the index
    try:
        index = int(index) if index else randint(0, 24)
        if index < 0 or index > 24:
            return '```The index must be between 0 and 24```'

    except ValueError:
        return '```You have to specify a number between 0 and 24 if you want ' + \
               'query by index!```'

    # Build the keywords for the url
    search_kw = ''
    for kw in keywords:
        search_kw+=(kw + '+')

    # Remove the training '+'
    search_kw = search_kw[:-1]

    # Request the gif from giphy
    resp = requests.get('http://api.giphy.com/v1/gifs/search?q=' + search_kw +
                        '&api_key=' + GIPHY_AUTH)

    # Verify status code and send an error message if not good
    if resp.status_code != 200:
        return '```Sorry, I had trouble getting that gif :(```'
    else:
        txt_json = json.loads(resp.text)
        return txt_json['data'][index]['bitly_gif_url']

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

            # If it is a whisper request...
            if cmd == '!whisper':
                await client.send_message(msg.author, cmd_dict[cmd](author))

            # Or if it is a gif request...
            elif cmd == '!gif':

                # Get the keywords and grab the index if specified
                keywords = str(msg.content).split(' ')
                keywords.remove(cmd)
                idx = None
                if '-i' in keywords:
                    i = 0
                    for i in range(len(keywords)):
                        if keywords[i] == '-i':
                            idx = keywords[i+1]
                            keywords.remove('-i')
                            keywords.remove(idx)
                            break
                        
                await client.send_message(msg.channel, cmd_dict[cmd](keywords, idx))

            # Otherwise, it is a regular command
            else:
                await client.send_message(msg.channel, cmd_dict[cmd](author))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)