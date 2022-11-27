from os import listdir, remove
from time import sleep

from utils.constants import *
from utils.logger import log
from modules.scraper import Scraper
from modules.telebot import TeleBot

# Spawn fake session
log.info("Loading...")
scr = Scraper()
log.info(f"Loaded {len(scr.read_ids)} IDs...")

# Initialize bot
bot = TeleBot()

# Clean cache
log.info("Removing old cache files...")
# Make sure not to remove ID cache
remove_files = [file for file in listdir(CACHE_PATH) if not file.endswith(".json")]
for file in remove_files:
    remove(f"{CACHE_PATH}/{file}")
log.info(f"Removed {len(remove_files)} cached files...")

log.info("Starting bot...")
while True:
    # Download the new posts from each sub
    for sub in SUBS:
        # Callback to the send function of the bot
        scr.download_posts(
            subreddit=sub,
            img_cb=bot.send_photo,
            vid_cb=bot.send_video,
        )

    # Wait till next iteration
    sleep(QUERY_DELAY)