import asyncio
import argparse
import os
import time

from pikvm import PiKVM
import json
import cv2

async def setup():
    pikvm = PiKVM()
    img = await pikvm.get_screenshot()
    cv2.imwrite("./pikvm_actions_data/full_screenshot.jpg", img)
    
    with open('pikvm_actions_data/config.json', 'r') as f:
        config = json.load(f)
    
    x, y = config['taskbar']['x'], config['taskbar']['y']
    width, height = config['taskbar']['width'], config['taskbar']['height']

    img = cv2.imread('pikvm_actions_data/full_screenshot.jpg')
    cropped_img = img[y:y+height, x:x+width]
    cv2.imwrite('pikvm_actions_data/taskbar.jpg', cropped_img)

    # Ensure all items are unselected in the taskbar
    for icon in config['taskbar_icons']:
        icon_name = icon['icon']
        x, y = icon['x'], icon['y']
        width, height = icon['width'], icon['height']
        cropped_icon = cropped_img[y:y+height, x:x+width]
        cv2.imwrite(f'./pikvm_actions_data/{icon_name}.jpg', cropped_icon)

    await pikvm.close()

async def browser_actions():
    pass

async def editor_actions():
    pass

async def notepad_actions():
    pass

async def main():
    pikvm = PiKVM()
    image = await pikvm.get_screenshot()
    with open('screenshot.jpg', 'wb') as f:
        f.write(image)

    await pikvm.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate human typing through PiKVM HID.")
    parser.add_argument("-f", "--file", help="Path to the file containing text to type.")
    parser.add_argument("-s", "--setup", action='store_true', help="Setup the system.")
    args = parser.parse_args()

    if args.setup:
        asyncio.run(setup())
    else:
        print(f"Do actions on the laptop")
        time.sleep(2)
        asyncio.run(main())