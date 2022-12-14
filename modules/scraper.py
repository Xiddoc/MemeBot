from hashlib import sha1
from json import loads, dumps
from os import mkdir, remove
from os.path import exists
from subprocess import PIPE, run
from time import sleep

# noinspection PyPackageRequirements
from ffmpeg import input as ffmpeg_input, Error
from requests import Session, RequestException

from utils.constants import *
from utils.logger import log


class Scraper:

    def __init__(self):
        # Create new session
        self.s = Session()
        self.s.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/99.106.0.0 Safari/537.36 "
        })

        # Get IDs
        self.read_ids = []
        self.load_ids()

    def download_posts(self, subreddit: str, img_cb=None, vid_cb=None) -> None:
        # Download the JSON data
        resp = self.s.get(JSON_API.format(subreddit))

        # For each post, download the media
        new_count = 0
        for post in resp.json()['data']['children']:
            # Check if processed already
            if not post['data']['name'] in self.read_ids:
                # Add to the list
                self.read_ids.append(post['data']['name'])
                new_count += 1

                # Save IDs again in case of quit
                self.save_ids()

                # Check NSFW status
                if 'thumbnail' in post['data'] \
                        and post['data']['thumbnail'] == 'nsfw' \
                        and not ENABLE_NSFW:
                    # Ignore this post
                    # If this post is NSFW and NSFW isn't on
                    continue

                try:
                    # Check media type
                    if 'post_hint' in post['data']:
                        # If video
                        if post['data']['post_hint'] == 'hosted:video' and img_cb is not None:
                            # Download the video,
                            # Then run the callback with that data
                            vid_cb(self.download_mpd(post['data']['secure_media']['reddit_video']['dash_url']))

                        # If image
                        elif post['data']['post_hint'] == 'image' and img_cb is not None:
                            # Download the image data for now
                            img_data = self.download_image(post['data']['url'])
                            # There is still a chance that this is a GIF and not a 'normal picture'
                            if img_data[:3] == b"GIF":
                                vid_cb(img_data)
                            else:
                                img_cb(img_data)
                except RequestException:
                    log.error("HTTP request exception while scraping...")
                    sleep(15)
                except Error:
                    log.error("FFMPEG error...")

        # Helpful log info
        log.info(f"Processed {new_count} new posts...")

    def download_image(self, image_url: str) -> bytes:
        return self.s.get(image_url).content

    @staticmethod
    def download_mpd(mpd_url: str) -> bytes:
        # Create filename
        file_path = f"{CACHE_PATH}/{sha1(mpd_url.encode()).hexdigest()}.mp4"
        out_path = file_path + '_.mp4'
        # Download and write to stream
        ffmpeg_input(mpd_url).output(file_path).run(quiet=True)
        # Compress the video
        run(f'ffmpeg -i "{file_path}" -vcodec libx265 -crf 25 "{out_path}"',
            shell=True, stdout=PIPE, stderr=PIPE)
        # Read the data back from the file
        with open(out_path, 'rb') as f:
            buf = f.read()
        # Delete the files after finished
        remove(out_path)
        remove(file_path)
        # Return the buffer
        return buf

    def load_ids(self):
        # Get cached IDs
        if not exists(CACHE_PATH):
            mkdir(CACHE_PATH)
        # Create default dict, then read for cached dict
        if exists(f"{CACHE_PATH}/read_ids.json"):
            with open(f"{CACHE_PATH}/read_ids.json") as f:
                self.read_ids = loads(f.read())

    def save_ids(self):
        # Dump to file
        with open(f"{CACHE_PATH}/read_ids.json", "w") as f:
            f.write(dumps(self.read_ids))
