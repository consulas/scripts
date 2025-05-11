import asyncio
import argparse
import os
import time

from pikvm import PiKVM

async def main(text: str, wpm: int, error_rate: float, error_upper_limit: int):
    """
    Main function to simulate human typing using the PiKVM class.
    """
    pikvm = PiKVM()
    await pikvm.human_typing(text, wpm, error_rate, error_upper_limit)
    await pikvm.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate human typing through PiKVM HID.")
    parser.add_argument("-f", "--file", help="Path to the file containing text to type.")
    parser.add_argument("-t", "--text", default="Hello World. Chicken Jockey. Flint and Steel.\n", help="Text string to type.")
    parser.add_argument("--wpm", type=int, default=120, help="Words per minute.")
    parser.add_argument("--error_rate", type=float, default=0.05, help="Error rate (probability of a typo).")
    parser.add_argument("--error_upper_limit", type=int, default=3, help="Maximum number of characters in a typo.")
    args = parser.parse_args()

    if args.file and os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text

    print(f"Typing with {args.wpm} wpm")
    time.sleep(2)
    asyncio.run(main(text, args.wpm, args.error_rate, args.error_upper_limit))