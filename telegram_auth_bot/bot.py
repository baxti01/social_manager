import logging
import os
from pathlib import Path

import environ
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid
from pyromod import listen  # type: ignore

WORK_DIR = Path(__file__).resolve().parent
BASE_DIR = WORK_DIR.parent

env = environ.Env()
env.read_env(env_file=os.path.join(BASE_DIR, ".env"))
os.chdir(WORK_DIR)

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = Client(
    "bot",
    api_id=env("API_ID"),
    api_hash=env('API_HASH'),
    bot_token=env('BOT_TOKEN'),
    in_memory=True,
    plugins=dict(root="StringSessionBot"),
)

if __name__ == "__main__":
    print("Starting the bot")
    try:
        app.start()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        raise Exception("Your API_ID/API_HASH is not valid.")
    except AccessTokenInvalid:
        raise Exception("Your BOT_TOKEN is not valid.")
    uname = app.get_me().username
    print(f"@{uname} is now running!")
    idle()
    app.stop()
    print("Bot stopped. Alvida!")
