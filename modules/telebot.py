from json import loads, dumps
from os.path import exists
from time import sleep
from typing import Dict

from requests import Session

from utils.constants import *
from utils.logger import log


class TeleBot:

    def __init__(self) -> None:
        # Initialize the session for later
        self.s = Session()
        self.post_queue = {}
        self.offset = 0
        self.users = set()

        # Login to the bot
        bot_data = self.__api("getMe")
        log.info(f"Logged into {bot_data['first_name']} (@{bot_data['username']})...")

        # If we have updated previously
        self.load_users()
        log.info(f"Loaded {len(self.users)} users...")

        # Get IDs of people who want memes
        self.update_users()

    def send_photo(self, photo: bytes) -> None:
        # Send to all users
        for user in self.users:
            self.__api(
                "sendPhoto",
                data={"chat_id": user},
                files={"photo": photo}
            )

            # Don't hit rate limit
            sleep(1.5)

    def send_video(self, video: bytes) -> None:
        # Send to all users
        for user in self.users:
            self.__api(
                "sendVideo",
                data={"chat_id": user},
                files={"video": video}
            )

            # Don't hit rate limit
            sleep(1.5)

    def update_users(self) -> None:
        # Get updates
        updates = self.__api("getUpdates", data={"offset": self.offset})
        # Get count for logging
        start_count = len(self.users)
        for msg in updates:
            # Add the user ID to the set
            self.users.add(str(msg['message']['from']['id']))
            # Update the last update
            self.offset = msg['update_id'] + 1

        # Save to cache
        self.save_users()

        # Get the difference = users added
        dif_count = len(self.users) - start_count
        if dif_count > 0:
            log.info(f"Found {dif_count} new users...")

    def load_users(self) -> None:
        # Load from cache if it exists
        self.offset = 0
        self.users = set()
        if exists(f"{CACHE_PATH}/users.json"):
            with open(f"{CACHE_PATH}/users.json") as f:
                user_data = loads(f.read())
                self.users = set(user_data['users'])
                self.offset = user_data['offset']

    def save_users(self) -> None:
        # Load from cache if it exists
        with open(f"{CACHE_PATH}/users.json", 'w') as f:
            # Dump dict to a string
            f.write(
                dumps({
                    "users": list(self.users),
                    "offset": self.offset
                })
            )

    def __api(self, method: str, *args, **kwargs) -> Dict:
        # Format the API call and send it
        resp = self.s.post(
            TELE_API.format(method),
            *args,
            **kwargs
        )
        # Return the result
        if resp.status_code == 200:
            return resp.json()['result']
        else:
            # Log HTTP errors
            log.error(f"HTTP Error at Path={method}: {resp.text}")
