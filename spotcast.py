#!/usr/bin/env python3

import os
from urllib.parse import urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

SHOW_URL = "https://open.spotify.com/show/2G3qmhWe8reqyCc7SRqI8F"
DOWNLOAD_PATH = "./downloads"

def get_episodes(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")

    meta = soup.findAll("meta", {"property": "music:song"})
    url_list = [tag["content"] for tag in meta]
    return [urlparse(url).path.split("/")[-1] for url in url_list]


def sanitize_filename(name):
    return "".join(x for x in name if (x.isalnum() or x in "._- "))


def fetch_episode(episode_id):

    url = "https://api.spotify.com/v1/episodes/" + episode_id
    headers = {
        "Authorization": "Bearer {}".format(os.getenv("SPOTIFY_TOKEN")),
        "Origin": "https://open.spotify.com",
        "Referer": "https://open.spotify.com/show/2G3qmhWe8reqyCc7SRqI8F",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    parsed = response.json()

    print(f"Fetching episode {episode_id} - {parsed['name']}")
    download_url = parsed["external_playback_url"]
    filename = "{}.mp3".format(sanitize_filename(parsed["name"]))

    print(" --> " + download_url)
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
        "Referer": "https://open.spotify.com/show/2G3qmhWe8reqyCc7SRqI8F",
        "Accept-Encoding": "identity",
        "Connection": "Keep-Alive",
    }

    episode = requests.get(download_url, headers=headers)
    file_dir = Path(DOWNLOAD_PATH)
    file_dir.mkdir(parents=True, exist_ok=True)
    with open(file_dir / filename, "wb") as f:
        f.write(episode.content)


episodes = get_episodes(SHOW_URL)
print(f"Found {len(episodes)} episodes")
print(episodes)

for ep in episodes:
    fetch_episode(ep)
