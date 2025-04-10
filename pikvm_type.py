import asyncio
import aiohttp
import random
import time
import urllib3
import argparse
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "192.168.0.112"  # Adjust as needed
USERNAME = "admin"
PASSWORD = "admin"
WPM = 120
CHAR_DELAY = 60 / (WPM * 5)  # Convert WPM to average delay per character in seconds
ERROR_RATE = 0.05
ERROR_UPPER_LIMIT = 3
TYPO_STRING = "abcdefghijklmnopqrstuvwxyz"

async def send_text(text: str):
    """
    Sends text to the pikvm hid print endpoint asynchronously.
    """
    params = {
        "keymap": "en-us",
        "slow": "false"
    }

    auth = aiohttp.BasicAuth(USERNAME, PASSWORD)

    url = f"https://{BASE_URL}/api/hid/print"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, params=params, data=text, auth=auth) as r:
            r.raise_for_status()

async def send_backspace():
    params = {
        "key": "Backspace"
    }

    auth = aiohttp.BasicAuth(USERNAME, PASSWORD)

    url = f"https://{BASE_URL}/api/hid/events/send_key"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, params=params, auth=auth) as r:
            r.raise_for_status()

async def human_typing(text: str):
    """
    Sends text one character at a time asynchronously.
    Adds random typos and random gaussian delays.
    """
    async def delay() -> float:
        delay = max(.01, min(random.gauss(CHAR_DELAY, CHAR_DELAY * 0.2), 1))
        await asyncio.sleep(delay)

    for char in text:
        # Add 1-3 typos randomly
        if random.random() < ERROR_RATE:
            typo_length = random.randint(1, ERROR_UPPER_LIMIT)
            typo_chars = ''.join(random.choice(TYPO_STRING) for _ in range(typo_length))
            for typo_char in typo_chars:
                await send_text(typo_char)
                await delay()
            for _ in range(typo_length):
                await send_backspace()
                await delay() # Backspace delay is faster than typing

        # Send character with delay
        await send_text(char)
        await delay()

        # Slight pause after spaces
        if char == " ":
            await delay()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate human typing through PiKVM HID.")
    parser.add_argument("-f", "--file", help="Path to the file containing text to type.")
    parser.add_argument("-t", "--text", default="Hello World. Chicken Jockey. Flint and Steel.\n", help="Text string to type.")
    args = parser.parse_args()

    if args.file and os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text
    print(f"Words per minute: {WPM}, Average character delay: {CHAR_DELAY} seconds")

    time.sleep(2)
    asyncio.run(human_typing(text))
