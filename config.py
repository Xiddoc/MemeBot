"""
Configuration of the bot.
"""

# Which subs to scrape
SUBS = [
    'shitposting',
    '196',
    '197',
    'discordVideos',
    'okbuddyretard',
    'gayspiderbrothel',
    'greentext',
    'dankvideos'
]

# How many posts to download at a time (max 100)
MAX_POSTS_PER_QUERY = 100

# How long to wait between queries
QUERY_DELAY = 3600

# NSFW Posts
ENABLE_NSFW = False

# Log to console as well as to a debug file
LOG_TO_CONSOLE = False
