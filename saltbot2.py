"""
    SALTBOT 2
"""
import os

from lib.controller import CLIENT

BOT_TOKEN = os.environ["BOT_TOKEN"]

if __name__ == "__main__":
    CLIENT.run(BOT_TOKEN)
