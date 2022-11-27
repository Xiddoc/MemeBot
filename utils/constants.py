from os import environ

from dotenv import load_dotenv
from config import *

load_dotenv()

# The URL to access posts
JSON_API = "https://www.reddit.com/r/{}/hot/.json?limit=" + str(MAX_POSTS_PER_QUERY)

# Cache folder
CACHE_PATH = "../cache"

# Telegram API URL
if 'BOT_KEY' in environ:
    TELE_API = "https://api.telegram.org/bot" + environ['BOT_KEY'] + "/{}"
else:
    raise ValueError("No telegram bot API key found in .env file.")
