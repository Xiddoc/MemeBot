# MemeBot
 
A simple Telegram bot to download memes from your favorite
Reddit subs and send them over to you on Telegram.

## Installation & Setup

To install the packages necessary, run:
```cmd
pip install -r requirements.txt
```

Now you need to get an API key for your bot. You can do this by 
[messaging the BotFather](https://t.me/BotFather), a Telegram bot 
which lets you create your own bots (for free).

Once you get your API key, make a new file called `.env` and in it, 
write the following:
```.env
BOT_KEY=123457890:AAAAABBBBBCCCCCDDDDD
```
Obviously, switch out `123457890:AAAAABBBBBCCCCCDDDDD` with your API key.

## Usage

Before running, you might want to check out the `config.py` file to change
the settings to your liking. 

Once you're all set, run the following command to start the bot:
```cmd
python memebot.py
```