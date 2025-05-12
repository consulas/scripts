import asyncio
from pikvm import PiKVM
import json

async def browser_actions():
    pikvm = PiKVM()
    # Click on the browser
    await pikvm.send_mouse_move(-19500, 31200)
    await pikvm.send_mouse_button("left")
    await asyncio.sleep(5)

    # Search bar
    await pikvm.send_mouse_move(-27000, -29000)
    await pikvm.send_mouse_button("left")
    await asyncio.sleep(2)
    await pikvm.human_typing("python fastapi docs")
    await pikvm.send_key("Enter")
    await asyncio.sleep(2)

    # Scroll up & down
    await pikvm.send_mouse_move(-16000, -16000)
    for _ in range(3):
        await pikvm.send_mouse_wheel(0, -5)
        await asyncio.sleep(.5)
    for _ in range(3):
        await pikvm.send_mouse_wheel(0, 5)
        await asyncio.sleep(.5)
    await asyncio.sleep(2)

    # Click away from the browser
    await pikvm.send_mouse_move(-19500, 31200)
    await pikvm.send_mouse_button("left")
    await asyncio.sleep(2)

    await pikvm.close()

async def ws_actions():
    with open("pikvm_events.json", "r") as f:
        action_script = json.load(f)
    pikvm = PiKVM()
    await pikvm.send_websocket_events(action_script)
    await pikvm.close()

if __name__ == "__main__":
    print(f"Performing actions")
    # asyncio.run(browser_actions())
    asyncio.run(ws_actions())