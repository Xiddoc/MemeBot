from json import loads, dumps
from os.path import exists
from time import sleep
from typing import Dict, Set

from requests import Session

from utils.constants import *
from utils.logger import log


class TeleBot:

    def __init__(self) -> None:
        # Initialize the session for later
        self.s = Session()
        self.post_queue = {}
        self.offset = 0
        self.users: Set[str] = set()

        # Login to the bot
        bot_data = self.__api("getMe")
        log.info(f"Logged into {bot_data['first_name']} (@{bot_data['username']})...")

        # If we have updated previously
        self.load_users()
        log.info(f"Loaded {len(self.users)} users...")

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
            # First check if we got blocked
            # https://core.telegram.org/bots/api#update
            # > For private chats, this update is received only when the bot is blocked or unblocked by the user.
            if 'my_chat_member' in msg and msg['my_chat_member']['chat']['type'] == 'private':
                # Figure out if the user unblocked us ...
                if msg['my_chat_member']['new_chat_member']['status'] == 'member':
                    # Add the user ID to the set
                    new_user = str(msg['my_chat_member']['new_chat_member']['from']['id'])
                    log.info(f"Re-added user #{new_user}...")
                    self.users.add(new_user)

                # ... or blocked us
                elif msg['my_chat_member']['new_chat_member']['status'] == 'kicked':
                    # The user blocked us, and we have them registered, then remove them
                    try:
                        old_user = str(msg['my_chat_member']['from']['id'])
                        log.info(f"Removed user #{old_user}...")
                        self.users.remove(old_user)
                    except KeyError:
                        pass
            else:
                # Add the user ID to the set
                new_user = str(msg['message']['from']['id'])
                log.info(f"Added new user #{new_user}...")
                self.users.add(new_user)

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
            # Log HTTP fails
            log.error(f"HTTP {resp.status_code}: {method} {resp.text}")
