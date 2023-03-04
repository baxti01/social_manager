from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import Message

from telegram_auth_bot.data import Data
from social_manager.settings import env


async def generate_session(bot: Client, msg: Message):
    await msg.reply("Starting Pyrogram Session Generation...")

    user_id = msg.chat.id
    api_id = env("API_ID")
    api_hash = env('API_HASH')

    t = "Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`'"

    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return

    phone_number = phone_number_msg.text
    await msg.reply("Sending OTP...")

    client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()

    try:
        code = await client.send_code(phone_number)
    except ApiIdInvalid:
        await msg.reply('`API_ID` and `API_HASH` combination is invalid.'
                        ' Please start generating session again.',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except PhoneNumberInvalid:
        await msg.reply('`PHONE_NUMBER` is invalid. Please start generating session again.',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return

    try:
        phone_code_msg = await bot.ask(user_id,
                                       "Please check for an OTP in official telegram account."
                                       " If you got it, send OTP here after reading the below format."
                                       " \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.",
                                       filters=filters.text, timeout=600)
        if await cancelled(phone_code_msg):
            return
    except TimeoutError:
        await msg.reply('Time limit reached of 10 minutes. Please start generating session again.',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return

    phone_code = phone_code_msg.text.replace(" ", "")

    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await msg.reply('OTP is invalid. Please start generating session again.',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except PhoneCodeExpired:
        await msg.reply('OTP is expired. Please start generating session again.',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(user_id,
                                         'Your account has enabled two-step verification.'
                                         ' Please provide the password.',
                                         filters=filters.text, timeout=300)
        except TimeoutError:
            await msg.reply('Time limit reached of 5 minutes. Please start generating session again.',
                            reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return

        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('Invalid Password Provided. Please start generating session again.',
                                     quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return

    string_session = await client.export_session_string()
    text = f"**PYRORGAM STRING SESSION** \n\n`{string_session}` \n\n"

    try:
        await bot.send_message(user_id, text)
    except KeyError:
        pass

    await client.disconnect()


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("Cancelled the Process!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("Restarted the Bot!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False
