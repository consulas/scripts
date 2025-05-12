import asyncio
import aiohttp
import random
import time
import urllib3

import cv2
import numpy as np

# Suppress SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PiKVM:
    def __init__(self, base_url="192.168.0.112", username="admin", password="admin"):
        self.BASE_URL = base_url
        self.USERNAME = username
        self.PASSWORD = password
        self.auth = aiohttp.BasicAuth(self.USERNAME, self.PASSWORD)
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    async def get_screenshot(self):
        """Get screenshot from PiKVM using the streamer/snapshot endpoint"""
        url = f"https://{self.BASE_URL}/streamer/snapshot"
        params = {
            "save": "false",
            "load": "false",
            "allow_offline": "false",
            "ocr": "false",
            "preview": "false",
        }
        async with self.session.get(url, params=params, auth=self.auth) as response:
            if response.status == 200:
                image_data = await response.read()
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                print("Got Screenshot")
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            else:
                print(f"Failed to get image. Status code: {response.status}")
                return None

    async def send_text(self, text: str):
        """Sends text to the pikvm hid print endpoint asynchronously.
        
        Args:
            text: Text to send to the HID print endpoint
        """
        params = {
            "keymap": "en-us",
            "slow": "false"
        }
        url = f"https://{self.BASE_URL}/api/hid/print"
        async with self.session.post(url, params=params, data=text, auth=self.auth) as r:
            r.raise_for_status()

    async def send_key(self, key: str, state: bool = None, finish: bool = False):
        """Sends key events to PiKVM.
        
        Args:
            key: Key name (see key mappings)
            state: True for press, False for release. If None, sends press+release
            finish: Whether to finish the key sequence (default: False)
        """
        params = {"key": key}
        if state is not None:
            params["state"] = str(state).lower()
            params["finish"] = str(finish).lower()
            
        url = f"https://{self.BASE_URL}/api/hid/events/send_key"
        async with self.session.post(url, params=params, auth=self.auth) as r:
            r.raise_for_status()

    async def human_typing(self, text: str, wpm=120, error_rate=0.05, error_upper_limit=3):
        """Sends text one character at a time with human-like delay and typos.
        
        Args:
            text: Text to type
            wpm: Words per minute (default: 120)
            error_rate: Probability of making a typo (default: 0.05)
            error_upper_limit: Maximum number of characters in a typo (default: 3)
        """
        char_delay = 60 / (wpm * 5)
        typo_string = "abcdefghijklmnopqrstuvwxyz"
        
        async def delay():
            delay = max(.01, min(random.gauss(char_delay, char_delay * 0.2), 1))
            await asyncio.sleep(delay)

        for char in text:
            if random.random() < error_rate:
                typo_length = random.randint(1, error_upper_limit)
                typo_chars = ''.join(random.choice(typo_string) for _ in range(typo_length))
                for typo_char in typo_chars:
                    await self.send_text(typo_char)
                    await delay()
                for _ in range(typo_length):
                    await self.send_key("Backspace")
                    await delay()

            await self.send_text(char)
            await delay()

            if char == " ":
                await delay()

    async def send_mouse_move(self, to_x: int, to_y: int):
        """Sends relative mouse movement to PiKVM.
        
        Args:
            to_x: Relative X movement (pixels)
            to_y: Relative Y movement (pixels)
        """
        params = {
            "to_x": str(to_x),
            "to_y": str(to_y)
        }
        url = f"https://{self.BASE_URL}/api/hid/events/send_mouse_move"
        async with self.session.post(url, params=params, auth=self.auth) as r:
            r.raise_for_status()

    async def send_mouse_button(self, button: str, state: bool = None):
        """Sends mouse button events to PiKVM.
        
        Args:
            button: Mouse button name (left, right, middle)
            state: True for press, False for release. If None, sends press+release
        """
        params = {"button": button}
        if state is not None:
            params["state"] = str(state).lower()
            
        url = f"https://{self.BASE_URL}/api/hid/events/send_mouse_button"
        async with self.session.post(url, params=params, auth=self.auth) as r:
            r.raise_for_status()

    async def send_mouse_wheel(self, delta_x: int, delta_y: int):
        """Sends mouse wheel events to PiKVM.
        
        Args:
            delta_x: Horizontal scroll amount
            delta_y: Vertical scroll amount
        """
        params = {
            "delta_x": str(delta_x),
            "delta_y": str(delta_y)
        }
        url = f"https://{self.BASE_URL}/api/hid/events/send_mouse_wheel"
        async with self.session.post(url, params=params, auth=self.auth) as r:
            r.raise_for_status()
    
    async def send_websocket_events(self, events):
        """Sends a list of events to the PiKVM websocket.

        Args:
            events: List of events to send
        """
        headers = {"X-KVMD-User": self.USERNAME, "X-KVMD-Passwd": self.PASSWORD}
        async with self.session.ws_connect(f"wss://{self.BASE_URL}/api/ws", headers=headers, ssl=False) as ws:
            for event in events:
                if event["event_type"] == "delay":
                    await asyncio.sleep(event["event"]["millis"] / 1000)
                else:
                    await ws.send_json(event)

    async def close(self):
        await self.session.close()

async def main():
    pikvm = PiKVM()
    text = "Hello World, Chicken Jockey Bacon and Eggs\n"

    await asyncio.gather( # Do all actions in parallel
        pikvm.human_typing(text),
        pikvm.send_mouse_move(0, 0),
        pikvm.send_mouse_button("left")
    )

    await pikvm.send_mouse_move(1000, 0),
    await pikvm.send_mouse_button("left")
    await pikvm.human_typing(text), # Do actions sequentially

    await pikvm.close()

if __name__ == "__main__":
    time.sleep(2)
    asyncio.run(main())
