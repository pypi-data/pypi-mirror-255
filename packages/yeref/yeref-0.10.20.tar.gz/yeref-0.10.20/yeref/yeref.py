#!/usr/bin/python3
# region data
import ast
import asyncio
import binascii
# import whisper
import datetime
import hashlib
import hmac
import io
import json
import logging
import mimetypes
import os
import random
import re
import shutil
import sqlite3
import string
import zipfile

from PIL import ImageOps, ImageDraw
import time
from calendar import monthrange
# from contextlib import closing
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
from pathlib import Path
from random import randrange
from urllib.parse import parse_qsl
from uuid import uuid4

import aiofiles
import aiohttp
import aiosqlite
import cv2
import emoji
import g4f
import httplib2
import moviepy.editor as mp
import numpy as np
import speech_recognition as sr
from PIL import Image
from aiogram import html
from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import KeyboardButtonRequestChat, ChatAdministratorRights
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from exiftool import ExifToolHelper
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from gtts import gTTS
from loguru import logger
from moviepy.editor import AudioFileClip, VideoClip
from moviepy.video.fx.crop import crop
from oauth2client.service_account import ServiceAccountCredentials
from openai import AsyncOpenAI
from pydub import AudioSegment
from pyrogram import enums, Client, utils
from pyrogram.errors import FloodWait, UserAlreadyParticipant, UsernameInvalid, BadRequest, SlowmodeWait, \
    UserDeactivatedBan, SessionRevoked, SessionExpired, AuthKeyUnregistered, AuthKeyInvalid, AuthKeyDuplicated, \
    InviteHashExpired, InviteHashInvalid, ChatAdminRequired, UserDeactivated, UsernameNotOccupied, ChannelBanned
from pyrogram.raw import functions
from pyrogram.raw.functions.account import SetPrivacy, SetAccountTTL, SetAuthorizationTTL
from pyrogram.raw.types import InputPrivacyKeyStatusTimestamp, InputPrivacyValueAllowAll, InputPrivacyKeyChatInvite, \
    InputPrivacyKeyAddedByPhone, InputPrivacyKeyForwards, InputPrivacyKeyPhoneNumber, InputPrivacyValueAllowContacts, \
    AccountDaysTTL, InputPrivacyValueDisallowAll, InputPrivacyKeyPhoneCall, InputPrivacyKeyVoiceMessages, \
    InputPrivacyKeyProfilePhoto
from pyrogram.raw.functions.messages import SendReaction
from pyrogram.raw.types import ReactionEmoji
from rembg import remove
from stegano import lsb, exifHeader
from telegraph.aio import Telegraph

from yeref.l_ import l_inline_demo, l_inline_bot, l_inline_post, l_inline_media, l_inline_channel, l_inline_group, \
    l_inline_find, l_inline_ai, l_inline_target, l_inline_user, l_inline_tools, l_inline_work, l_post_finish, \
    l_post_time_future, l_generate_calendar_time, l_post_button, l_post_media_toobig, l_post_text, l_post_media, \
    l_post_media_wait, l_post_text_limit, l_me, l_all, l_ids, l_spoiler_text, l_preview_text, l_gallery_text, \
    l_buttons_text, l_weekday_1, l_weekday_2, l_weekday_3, l_weekday_4, l_weekday_5, l_weekday_6, l_weekday_7, \
    l_month_1, l_month_2, l_month_3, l_month_4, l_month_5, l_month_6, l_month_7, l_month_8, l_month_9, l_month_10, \
    l_month_11, l_month_12, l_broadcast_finish, l_broadcast_process, l_post_has_restricted, l_gallery, l_btn, \
    l_post_datetime, l_off, l_post_new, l_post_delete, l_post_change, l_silence, l_grp_btn1, l_grp_btn2, \
    l_choose_direction, l_post_buttons, l_pin, l_preview, l_spoiler, l_broadcast_start, l_post_timer, l_post_date, \
    l_enter, l_subscribe_channel_for_post, l_chn_btn1, l_chn_btn2, l_post_publish, l_recipient, l_inline_sticker, \
    l_template_is_ready, l_all_json, l_one_json, l_order_act, l_rand_act, l_msg_photo, l_msg_gif, l_msg_video, \
    l_msg_video_note, l_msg_audio, l_msg_voice, l_msg_document, l_msg_sticker, l_msg_dice, l_msg_web, l_sec, \
    l_act_wait_title, l_msg_quiz, l_msg_text

elly_a = 5900268983
my_tid = 5491025132
BOT_TID_TEST = 6066611486
my_tids = ['5900268983', '6179455648', '6236215930', '5754810063', '5491025132', '5360564451', '6281795468']
tids_not_for_trans = [5134596871, 5152320320, 5200969162, 5240041587, 5277505344, 5298580533, 5300792695, 5304873693,
                      5318482236, 5372068352, 5380838469, 5456863561, 5588781655, 5621199443, 5805890320, 5846446387,
                      5850795580, 5868482417, 5951232918, 5962132892, 5969907012]
GROUP_ANON_TID = 1087968824
CHANNEL_BOT_ = 136817688
ferey_channel_europe = -1001471122743
ferey_channel_en = -1001833151619
ferey_channel_es = -1001988190840
ferey_channel_fr = -1001942773697
ferey_channel_ar = -1001913015662
ferey_channel_zh = -1001904073819
e18b_bot = '@e18be3f08cf66117744a889900dc_bot'
e18b_channel = -1001956430283
kjs = 10000
one_minute = 60
one_hour = 3600
seconds_in_day = 86400
old_tid = 5_000_000_000
old_tid_del = 1_000_000_000
lat_company = 59.395881
long_company = 24.658980
bin_empty = b'\xe2\x81\xa0\xe2\x81\xa0'  # .encode("utf-8")
hex_empty = 'e281a0e281a0'  # .encode("utf-8").hex()  || bytes.fromhex()
str_empty = bin_empty.decode('utf-8')  # ​
log_ = f"\033[{92}m%s\033[0m"
bot_father = "@BotFather"
placeholder = '/content'
SECTION = 'CONFIG'
LINES_ON_PAGE = 5
short_name = 'me'
const_url = 'https://t.me/'
phone_number = '19999999999'
website = 'https://google.com'
facebook = 'https://www.facebook.com'
telegram_account = 'https://t.me'
ferey_telegram_username = 'ferey_support'
ferey_telegram_demo_bot = 'FereyDemoBot'
ferey_address = "Estônia, Tāllin, Mäepealse, 2/1"
ferey_title = "Ferey Inc."

# region group links
payment_link = 'http://bagazhznaniy.ru/wp-content/uploads/2014/03/zhivaya-priroda.jpg'
channel_library_ru_link = 'https://t.me/+f-0AbTALTOg4ODBk'
channel_library_en_link = 'https://t.me/+CHIMCacxEZw4YjA8'
channel_library_ru = -1001484489131
channel_library_en = -1001481302043
donate_deposit_rub = 'https://t.me/ferey_channel_europe/32'
donate_deposit_eur = 'https://t.me/ferey_channel_europe/44'

donate_bot_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4Njc=-0xXD'
donate_bot_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NjY=-0xXD'
donate_user_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NTU=-0xXD'
donate_user_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NzE=-0xXD'
donate_channel_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NTM=-0xXD'
donate_channel_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NzA=-0xXD'
donate_group_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NTE=-0xXD'
donate_group_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4Njk=-0xXD'
donate_post_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NTc=-0xXD'
donate_post_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NzI=-0xXD'
donate_media_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NTk=-0xXD'
donate_media_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NzM=-0xXD'
donate_find_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NjQ=-0xXD'
donate_find_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NzQ=-0xXD'
donate_ai_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NDk=-0xXD'
donate_ai_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4Njg=-0xXD'
donate_codex_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NDk=-0xXD'
donate_codex_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4Njg=-0xXD'
donate_fest_rub = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4NDk=-0xXD'
donate_fest_eur = 'https://t.me/donate?start=Y2hhcml0eV9pbnZvaWNlX3JlcXVlc3QtMzE4Njg=-0xXD'

ferey_thumb = 'https://telegra.ph/file/bf7d8c073cdfa91b6d624.jpg'
ferey_theme = 'https://t.me/addtheme/lzbKZktZjqv5VDdY'
ferey_wp = 'https://t.me/bg/Mr2tXPkzQUoGAgAAv-ssUh01-P4'
ferey_set = 'https://t.me/addstickers/ferey_sticker_by_FereyStickerBot'
ferey_emoji = 'https://t.me/addemoji/ferey_emoji_by_FereyStickerBot'

text_jpeg = 'https://telegra.ph/file/0c675e5a3724deff3b2e1.jpg '
bot_logo_jpeg = 'https://telegra.ph/file/99d4f150a52dcf78b3e8a.jpg'
channel_logo_jpeg = 'https://telegra.ph/file/8418e1cd70484eac89477.jpg'
group_logo_jpeg = 'https://telegra.ph/file/a55c9f4e74b86b0b4f55f.jpg'
user_logo_jpeg = 'https://telegra.ph/file/3c14f9f5ed347e51785c7.jpg'
payment_photo = 'https://telegra.ph/file/75747cf7bc68f45a0e8b8.jpg'
logo_photo = 'https://telegra.ph/file/4882ddb35357f1b079659.jpg'

photo_jpg = 'https://telegra.ph/file/d39e358971fc050e4fc88.jpg'
gif_jpg = 'https://telegra.ph/file/e147d6798a43fb1fc4bea.jpg'
video_jpg = 'https://telegra.ph/file/692d65420f9801d757b0c.jpg'
video_note_jpg = 'https://telegra.ph/file/a0ebd72b7ab97b8d6de24.jpg'
audio_jpg = 'https://telegra.ph/file/15da5534cb4edfbdf7601.jpg'
voice_jpg = 'https://telegra.ph/file/10ada321eaa60d70a125d.jpg'
document_jpg = 'https://telegra.ph/file/28b6c218157833c0f4030.jpg'
sticker_jpg = 'https://telegra.ph/file/986323df1836577cbe55d.jpg'

bot_welcome_instruction = 'https://telegra.ph/FereyBotBot-11-13'
# user_welcome_instruction = 'https://telegra.ph/FereyBotBot-11-13'
# endregion

# region default
BOT_CONFIG_ = '☑☑☐☐☐☐☐☑☑☐☐'
BOT_CBAN_ = '☐☐☑☐☐'
BOT_CNEURO_ = '☐☐☐☐☐☐☐☐'
BOT_CINTEGRATION_ = '☐☐'
BOT_CNOTIFICATION_ = '☑☐☑☐'
BOT_CUSER_ = '☑☐☐'
BOT_VARS_ = '{"BOT_PROMO": "#911", "BOT_CHANNEL": 0, "BOT_CHANNELTID": 0, "BOT_GROUP": 0, "BOT_GROUPTID": 0, "BOT_GEO": 0, "BOT_TZ": "+00:00", "BOT_DT": "", "BOT_LZ": "en", "BOT_LC": "en", "BOT_ISSTARTED": 0}'
BOT_LSTS_ = '{"BOT_ADMINS": [], "BOT_COMMANDS": ["/start"]}'
USER_VARS_ = '{"USER_TEXT": "", "USER_REACTION": "", "USER_PUSH": "", "USER_EMAIL": "", "USER_PROMO": "", "USER_PHONE": "", "USER_GEO": "", "USER_UTM": "", "USER_ID": 0, "USER_DT": "", "USER_TZ": "+00:00", "USER_LC": "en", "USER_ISADMIN": 0, "USER_ISPREMIUM": 0, "USER_BALL": 0, "USER_RAND": 0, "USER_QUIZ": 0, "USER_DICE": 0, "USER_PAY": 0, "DATE_TIME": 0}'
USER_LSTS_ = '{"USER_UTMREF": []}'

UB_CONFIG_ = '☑☑☑☐☐☑☑☐☐☐☐☐☐'
UB_CFORMAT_ = '☑☑☑☑☐'
UB_CBAN_ = '☐☑☐☐☐'
UB_CNEURO_ = '☐☐☐☐☐☐☐☐'
UB_CSERVICE_ = '☑☑☑☑☑'
UB_CREACTION_ = '☑☑☑'
UB_CTRANSCRIBE_ = '☐☐'
UB_CPODCAST_ = '☐☑'
UB_CGEO_ = '☑☑☑☐'
UB_CSENDCNT_ = 1
UB_VARS_ = '{"UB_PROMO": "#911", "UB_CHANNEL": 0, "UB_CHANNELTID": 0, "UB_GROUP": 0, "UB_GROUPTID": 0, "USER_COMMENT": "","UB_TZ": "+00:00", "UB_DT": "", "UB_LZ": "en", "UB_LC": "en"}'
UB_LSTS_ = '{}'
# endregion

bot_emj_react = ["👍", "❤", "🔥", "👏", "🎉", "🙏", "👌", "🕊", "🐳", "❤‍🔥", "🌚", "💯", "⚡", "🏆", "💔", "👻", "👨‍💻", "👀", "🎃", "🤝",
                 "✍", "🎄", "☃", "🗿", "🆒", "💘", "🦄", "👾", "🤷‍♂", "🤷‍♀"]
reactions_2 = ['👍', '❤', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🙏', '👌', '🕊', '🤡', '🥱', '🥴', '😍', '🐳',
               '❤\u200d🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓', '🍾', '💋', '😈', '😴', '😭', '🤓', '👻',
               '👨\u200d💻', '👀', '🎃', '🙈', '😇', '😨', '🤝', '✍', '🤗', '\U0001fae1', '😂', '🎄', '⛄', ' 🆒', '🗿']
reactions_ = ['👍', '👎', '❤', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🤮', '💩', '🙏', '👌', '🕊', '🤡', '🥱',
              '🥴', '😍', '🐳', '❤\u200d🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓', '🍾', '💋', '🖕', '😈', '😴',
              '😭', '🤓', '👻', '👨\u200d💻', '👀', '🎃', '🙈', '😇', '😨', '🤝', '✍', '🤗', '\U0001fae1', '🎅', '🎄', '☃', '💅', '🤪',
              '🗿', '🆒', '💘', '🙉', '🦄', '😘', '💊', '🙊', '😎', '👾', '🤷\u200d♂', '🤷', '🤷\u200d♀', '😡', '😂']
emojis_ = ['🙂', '😶‍🌫️', '🫥', '🎃', '😻', '🫶🏽', '🙌🏽', '👍🏽', '🤌🏾', '🫳🏽', '👉🏼', '☝🏽', '👋🏽', '✍🏽', '🙏🏼', '👣', '🫀', '👤', '👥',
           '👮🏽', '👩🏽‍💻', '🥷🏽', '💁🏽‍♂️', '🤷🏽‍♂️', '👕', '🧢', '🎓', '👓', '🐳', '🐋', '🌱', '🌿', '☘️', '🍀', '🍃', '🍂', '🍁', '🌚',
           '🌗', '🌏', '⭐️', '⚡️', '🔥', '☀️', '🌤️', '❄️', '🫧', '🌬️', '🧊', '🥏', '🎗️', '🧩', '🚀', '🗽', '🗿', '⛰️', '🏔️', '🗻',
           '🏠', '🏙️', '💻', '🎥', '🧭', '⏳', '🔋', '💡', '💵', '💰', '💳', '⚒️', '🛡️', '📍', '🪬', '🛋️', '🎉', '✉️', '📬', '📜', '📄',
           '📅', '🧾', '📇', '📋', '🗄️', '📁', '📰', '📘', '📖', '🖤', '〽️', '🔆', '✅', '🌐', '💠', '🔹', '💭', '🚩']
animated_emoji = ["🇸🇴", "🏁", "🏴", "🚩", "🏳", "🦕", "🐻", "🐻‍❄", "🦊", "🐼", "🐈", "🦋", "🐛", "🦟", "🐜", "🦙", "🦬", "🦌", "🐎", "🐂",
                  "🐆", "🐦", "🕊️", "🦆", "🦢", "🦉", "🦜", "🦔", "🐟", "🐳", "🐾", "🌳", "🌼", "🌲", "🎄", "🏕️", "🌵", "🍀", "🌿", "🌱",
                  "☘️", "☁️", "🌨️", "🌧️", "⛈️", "🌩️", "🌓", "🌛", "🌕", "🌗", "🌜", "❄️", "☃️", "☀️", "⛅", "🌦️", "🎉", "💣",
                  "🧨", "🔥", "💥", "✨", "⚡", "🎆", "🥂", "🍪", "🍳", "🍌", "🍱", "🧃", "🎂", "🍾", "🥫", "🧋", "🍫", "🧁", "🍮", "🍽️",
                  "🥛", "☕", "🧉", "🥞", "🥧", "🍕", "🍗", "🍙", "🥪", "🥙", "👌🏽", "🤙🏽", "👏🏽", "👇🏽", "👉🏽", "🤞🏽", "💪🏽", "🙌🏽",
                  "🙏🏽", "👣", "🫱🏽‍🫲🏼", "🫶🏽", "☝🏽", "😶‍🌫", "👤", "👥", "🫂", "🗣️", "👩🏽‍💻", "👾", "🫥", "👀", "🗯", "🗿", "🎃",
                  "❤️", "💙", "🤍", "💔", "🖤", "💓", "❤️‍🔥", "📉", "📈", "☑️", "✔️", "✅", "🆙", "🆓", "🆕", "🆗", "🆒", "🔝", "💱",
                  "❗", "❓", "❔", "❕", "💯", "🎵", "🎶", "🥇", "🏆", "🎗️", "🪙", "🧭", "🎨", "🔍", "⏳", "🎓", "🎤", "📣", "🎈", "🎬",
                  "🏠", "🏛️", "🚀", "✈️", "🚓", "🚕", "📱", "📲", "📞", "📺", "💻", "🖨️", "⚽", "🏀", "🔬", "🔭", "🗝️", "🎫", "🎟",
                  "🪪", "📝", "📰", "📖", "📨", "📤", "📆", "🗂️", "📂", "📚", "📭", "💼", "👜", "🧳", ]
themes_ = ['🐥', '⛄', '💎', '👨\u200d🏫', '🌷', '💜', '🎄', '🎮']
extra_prompt = 'a candid portrait, hyper-realistic image, iphone photo, ultra-realistic photography, cinematic photo, uhd motion capture, high-contrast image, 8k camera, atmospheric light'
short_description = f"""👩🏽‍💻 New @tg-tech neuro-#marketing apps

Start: t.me/FereyDemoBot
🇬🇧🇨🇳🇦🇪🇪🇸🇷🇺🇫🇷
"""
TGPH_TOKEN_MAIN = 'a9335172886eae62ec0743bf8a4e195286ec30cff067da5fd1db2899d008'
TGPH_TOKENS = {
    "https://telegra.ph/pst-FereyDemoBot-05-08": "f8c69d50846e8d55e08f8e3de514f41266e0150434219059f2c91fb4d75f",
    "https://telegra.ph/pst-FereyBotBot-05-08": "e7f943fcc98bac07ad6aaf6e570d0f51abadf02567938c997dbc1ad1923b",
    "https://telegra.ph/pst-FereyPostBot-05-08": "14085be3058c0a25616d094f4bb65c73dc61f783468f01da41d99fb6ace1",
    "https://telegra.ph/pst-FereyMediaBot-05-08": "cf71a596b7ecdc96d30ddffdbf1e26863dd39755f47b4fc343fc3867f373",
    "https://telegra.ph/pst-FereyChannelBot-05-08": "f43f375b8aec531cee0d5048878943a3ccee97da4143d311d5b2c7ed3237",
    "https://telegra.ph/pst-FereyGroupBot-05-08": "c08f94618b94dd25ef75de70c1ed565853efef5479057c68a5720609bb7f",
    "https://telegra.ph/pst-FereyFindBot-05-08": "2d005bb366dc5bef023d58b93d5f45fb9a02a7d2b0f9063a6fc277b5a62d",
    "https://telegra.ph/pst-FereyTargetBot-05-08": "bda8c0a4b7a35101d34252568acd46df7bd3d8d85f4e13dd35f3bddc2f80",
    "https://telegra.ph/pst-FereyToolsBot-05-08": "ea83403eb6ac7d2ad24d7e7a86163be20cd2d7f4734267808e154a8fd0a6",
    "https://telegra.ph/pst-FereyVPNBot-05-08": "38086caf43905ef827715da999aae0be2427ebd7a05d9ff7420543b50613",
    "https://telegra.ph/pst-FereyAIBot-05-08": "bcda631d991c16b4fdfd15e7af6512bcf8fd679fee6bd4c717f6266671a0",
    "https://telegra.ph/pst-FereyUserBot-05-08": "3698a3432c233bef48c238b35cfe94db844858b2ba98594007c7757dcf03",
    "https://telegra.ph/pst-FereyWorkBot-05-08": "d4930b2a9311ad63f7f0ae3d61ca7224ecf76a2434a50161e239a45199c5",
    "https://telegra.ph/pst-FereyAdsBot-05-08": "c1024508f1a5de4f9544dd10793b1401da95de5719bdcf0b4c9f6c26a672", }
buttons_lang = [types.InlineKeyboardButton(text="🇬🇧 en", callback_data=f"lang_en"),
                types.InlineKeyboardButton(text="🇨🇳 zh", callback_data=f"lang_zh"),
                types.InlineKeyboardButton(text="🇦🇪 ar", callback_data=f"lang_ar"),
                types.InlineKeyboardButton(text="🇪🇸 es", callback_data=f"lang_es"),
                types.InlineKeyboardButton(text="🇷🇺 ru", callback_data=f"lang_ru"),
                types.InlineKeyboardButton(text="🇫🇷 fr", callback_data=f"lang_fr"), ]
markupAdmin = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text='⬅️ Prev'), types.KeyboardButton(text='↩️ Menu'),
     types.KeyboardButton(text='➡️️ Next')]], resize_keyboard=True, selective=True, row_width=3)
trg_utms = ['360', 'ad', 'advert', 'aesthetic', 'ai', 'air', 'alpha', 'beta', 'big', 'blog', 'boost', 'bot', 'box',
            'brainstorm', 'bravo', 'buy', 'calc', 'care', 'cascade', 'change', 'channel', 'charm', 'chat', 'chn',
            'click', 'cloud', 'club', 'codex', 'color', 'command', 'connect', 'copy', 'course', 'day', 'demo', 'dev',
            'discord', 'discount', 'doc', 'docum', 'document', 'download', 'dream', 'dzen', 'echo', 'element', 'event',
            'facebook', 'fast', 'fest', 'festival', 'field', 'file', 'first', 'fit', 'fix', 'flow', 'fly', 'focus',
            'for', 'forest', 'free', 'fresh', 'fun', 'future', 'get', 'gift', 'giga', 'git', 'go', 'grade', 'grape',
            'guide', 'hackathon', 'have', 'here', 'high', 'hill', 'hot', 'hub', 'ig', 'infinite', 'info', 'intensive',
            'landing', 'last', 'lead', 'league', 'learn', 'lesson', 'level', 'life', 'like', 'lime', 'limit', 'link',
            'linkedin', 'load', 'look', 'map', 'marathon', 'master', 'mastermind', 'max', 'medium', 'meet', 'method',
            'mind', 'mix', 'mobile', 'more', 'msg', 'neuro', 'new', 'newsletter', 'night', 'nike', 'node', 'note',
            'nova', 'number', 'ocean', 'omega', 'one', 'orange', 'paint', 'pinterest', 'plane', 'platform', 'play',
            'podcast', 'portal', 'post', 'present', 'press', 'pro', 'promo', 'puzzle', 'quick', 'ran', 'rate', 'read',
            'ready', 'real', 'reality', 'realm', 'red', 'reddit', 'refer', 'referral', 'review', 'round', 'run', 'safe',
            'salute', 'save', 'scale', 'school', 'sea', 'seminar', 'seo', 'service', 'session', 'set', 'share', 'shop',
            'sky', 'smart', 'snow', 'social', 'soundcloud', 'special', 'spotify', 'spring', 'star', 'stat', 'status',
            'stellar', 'stone', 'subscribe', 'summer', 'sun', 'symposium', 'tap', 'taplink', 'target', 'team', 'tech',
            'technology', 'tele', 'telegram', 'telegraph', 'telescope', 'ten', 'testdrive', 'text', 'this', 'tiktok',
            'time', 'top', 'training', 'trend', 'trigger', 'true', 'try', 'turbo', 'unity', 'university', 'unsubscribe',
            'up', 'utm', 'vimeo', 'vip', 'wait', 'wave', 'web', 'webinar', 'webmaster', 'website', 'week', 'win',
            'winter', 'wordpress', 'work', 'workbook', 'workshop', 'wow', 'x', 'yes', 'you', 'you2b', 'youtube', 'yt',
            'zip']
html_404 = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background-image: url('https://telegra.ph/file/4b093c7e2b68f9f2915b0.jpg'); background-size: cover; background-position: center; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .container {{ text-align: center; padding: 30px; background-color: rgba(255, 255, 255, 0.8); border-radius: 10px; }}
        .error-code {{ font-size: 100px; color: #2c3e50; margin: 0; }}
        .go-back {{ margin-top: 20px; text-decoration: none; color: #3498db; }}
    </style>
</head>
<body><div class="container"><h1 class="error-code">404</h1><a href="https://t.me/FereyBotBot?start=error" class="go-back">@FereyBotBot</a></div></body>
</html>
"""
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        html {{ box-sizing: border-box; }}
        *,*::before, *::after {{ box-sizing: inherit; font-family: Arial, sans-serif; color: rgba(40, 40, 40, 0.99);}}
        a {{ text-decoration: none; }}
        span {{ color: #007bff; }}
        body {{ margin: 0; padding: 0; overflow-x: hidden; }}
        
        .text b, .text u, .text i, .text a, .text code, .text span {{ display: inline; }}
        .text code {{ font-family: 'Courier New', monospace; background-color: #f5f5f5; }}
        .text {{ width: 100%; text-align: justify; }}   
        .text span {{ margin: -1px; }}

        .container-wrapper {{ max-width: 1270px; height: 100vh;  padding: 4px; margin: 0 auto; display: flex; flex-direction: column; justify-content: space-between; gap: 4px; }}
        .container {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-start; font-size: 14px; gap: 4px; }}
        
        .media-wrapper {{ -webkit-text-stroke: 0.5px rgba(50, 50, 50, 0.99); position: relative; width: 100%; min-height: 33vh; display: flex; justify-content: center; align-items: flex-start; max-width: 100%; overflow: hidden; }}
        .media {{ width: 100%; max-height: 33vh; object-fit: cover; height: auto; }}
        .media:not(.rounded-media) {{ border-radius: 4px; }}
        .rounded-media {{ border-radius: 50%; }}
        
        .buttons-wrapper {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 4px;
        }}
        .buttons-row {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: row;
            justify-content: center;
            gap: 4px;
        }}
        .button {{
            width: 100%;
            height: 34px;

            display: flex;
            justify-content: center;
            align-items: center;

            background-color: #007bff;
            color: #fff;
            text-align: center;
            line-height: 34px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            margin-bottom: 4px; 
            color: rgba(140, 150, 160, 0.99);
            font-size: 10px; 
        }}
        
        #media-number {{
            position: absolute;
            top: 1%;
            left: 1%;
            padding: 16px;
            padding-top: 19px;
            font-size: 10px;

            cursor: pointer;
            color: rgba(254, 254, 254, 1.0);
        }}
        #media-prev {{
            position: absolute;
            top: 45%;
            left: 1%;
            padding: 16px;
            cursor: pointer;
            color: rgba(254, 254, 254, 1.0);
        }}
        #media-next {{
            position: absolute;
            top: 45%;
            right: 1%;
            padding: 16px;
            cursor: pointer;
            color: rgba(254, 254, 254, 1.0);
        }}
        .dot {{
            cursor: pointer;
            height: 10px;
            width: 10px;
            margin: 0 2px;

            background-color: rgba(254, 254, 254, 1.0);
            border-radius: 50%;
            border: 0.5px solid rgba(50, 50, 50, 0.99);
            display: inline-block;
            transition: background-color 0.6s ease;
            opacity: 0.2;
        }}
        
        #media-dots {{ position: absolute; bottom: 1%;  text-align: center; padding: 16px; }}
        .active, .dot:hover {{ opacity: 1; }}
        #media-prev:hover {{ opacity: 0.6; }}
        #media-next:hover {{ opacity: 0.6; }}
        #footer-view {{ color: rgba(140, 150, 160, 0.99); }}
    </style>
    <link href="https://cdn.jsdelivr.net/gh/Alaev-Co/snowflakes/dist/snow.min.css" rel="stylesheet">
</head>
<body>
    <script src="https://cdn.jsdelivr.net/gh/Alaev-Co/snowflakes/dist/Snow.min.js"></script>
    <script>new Snow ();</script>

    <div class="container-wrapper">
        <div class="container">{0}{1}{2}</div>
        <div class="footer">
            <div id="footer-view">👁 {3}</div> 
            <div><a href="{4}" style="color: rgba(140, 150, 160, 0.99);">{5}</a></div>
        </div>
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", async () => {{
            let mediaElement = document.querySelector('.media')
            const mediaList = {8}
            let currentIndex = 0

            async function updateMedia() {{
                let mediaNumber = document.getElementById('media-number');
                
                if (mediaElement && mediaNumber) {{
                    let currentMedia = mediaList[currentIndex];
                    
                    let newMediaElement;
                    if (currentMedia.endsWith('.mp4')) {{
                        newMediaElement = document.createElement('video');
                        newMediaElement.className = 'media';
                        newMediaElement.src = currentMedia;
                        newMediaElement.controls = true;
                        newMediaElement.autoplay = true;
                        newMediaElement.loop = true;
                        newMediaElement.muted = true;
                    }} 
                    else {{
                        newMediaElement = document.createElement('img');
                        newMediaElement.className = 'media';
                        newMediaElement.src = currentMedia;
                        newMediaElement.alt = 'Media';
                    }}
                    mediaElement.replaceWith(newMediaElement);
                    mediaElement = newMediaElement;
                    
                    mediaNumber.textContent = (currentIndex + 1) + '/' + mediaList.length;
                    const dots = document.getElementsByClassName('dot');
                    for (let i = 0; i < dots.length; i++) dots[i].classList.remove('active');
                    dots[currentIndex].classList.add('active');
                }}
            }}

            let mediaPrev = document.getElementById('media-prev');
            if (mediaPrev) {{
                mediaPrev.addEventListener('click', async () => {{
                    currentIndex = (currentIndex - 1 + mediaList.length) % mediaList.length;
                    await updateMedia();
                }})
            }}
            
            let mediaNext = document.getElementById('media-next');
            if (mediaNext) {{
                mediaNext.addEventListener('click', async () => {{
                    currentIndex = (currentIndex + 1) % mediaList.length;
                    await updateMedia()
                }})
            }}

            await updateMedia();
            const roundedMedia = document.querySelectorAll('.rounded-media');
            for (let i = 0; i < roundedMedia.length; i++) roundedMedia[i].style.width = "auto";
        }})
        async function fetchData(url) {{
            try {{
                const response = await fetch(url);
                console.log('response:', response)
            }} catch (error) {{
                console.log('Error fetching data:', error);
                return null;
            }}
        }}

        async function handleButtonClick(button) {{
            const url = button.dataset.url;
            const idArr = button.id.split("-");

            let getUrl;
            if (idArr[1] === 'payment') {{
                tg.openInvoice(url, async (status) => {{
                    getUrl = `/{6}?msg_id={7}&btn_id=${{idArr[2]}}&cnt_id=${{idArr[3]}}&kind=${{idArr[1]}}&status=${{status}}&${{tg.initData}}`;
                    await fetchData(getUrl);
                    location.reload();
                }});
            }} else if (idArr[1] === 'phone') {{
                tg.requestContact(async (status) => {{
                    getUrl = `/{6}?msg_id={7}&btn_id=${{idArr[2]}}&cnt_id=${{idArr[3]}}&kind=${{idArr[1]}}&status=${{status}}&${{tg.initData}}`;
                    await fetchData(getUrl);
                    location.reload();
                    console.log(getUrl);
                }});
            }} else if (idArr[1] === 'like') {{
                getUrl = `/{6}?msg_id={7}&btn_id=${{idArr[2]}}&cnt_id=${{idArr[3]}}&kind=${{idArr[1]}}&status=click&${{tg.initData}}`;
                await fetchData(getUrl);
                location.reload();
            }} else if (url.startsWith('https://t.me/')) {{
                tg.openTelegramLink(url);
                getUrl = `/{6}?msg_id={7}&btn_id=${{idArr[2]}}&cnt_id=${{idArr[3]}}&kind=${{idArr[1]}}&status=link&${{tg.initData}}`;
                await fetchData(getUrl);
                location.reload();
            }} else {{
                tg.openLink(url, {{try_instant_view: true}});
                getUrl = `/{6}?msg_id={7}&btn_id=${{idArr[2]}}&cnt_id=${{idArr[3]}}&kind=${{idArr[1]}}&status=link&${{tg.initData}}`;
                await fetchData(getUrl);
                location.reload();
            }}
        }}

        let tg = window.Telegram.WebApp;
        tg.ready();
        console.log('script start', tg.initData);
        if (tg.initData === '') throw new Error('404');
        console.log(tg.initDataUnsafe['start_param']);
        let buttonsClass = document.getElementsByClassName('button');

        let startUrl = `/web?tgWebAppStartParam={6}_{7}&${{tg.initData}}`;
        console.log('startUrl = ', startUrl);
        fetchData(startUrl);

        for (let i = 0; i < buttonsClass.length; i++)  buttonsClass[i].addEventListener('click', async () => {{ await handleButtonClick(buttonsClass[i]); }});
    </script>
</body>
</html>
"""
cat2_mp3 = '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QAEBBgBAAQEGAEABAQYAQAEBBgBAAQEGAEABAQYAQAEBBgBAAQEGAEABAQYAQAEBBgBAAQEGAEABAQYAQAEBBgBAwf8CzeceU00bvzsAAAAASUVORK5CYIIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/++DEAAAAAAAAAAAAAAAAAAAAAABJbmZvAAAADwAAACUAAJsZAAYGDQ0NFBQUGxsiIiIpKSkwMDc3Nz4+PkVFRUxMU1NTWVlZYGBnZ2dubm51dXx8fIODg4qKipGRmJiYn5+fpqasrKyzs7O6usHBwcjIyM/Pz9bW3d3d5OTk6+vy8vL5+fn//wAAADlMQU1FMy4xMDABzQAAAAAAAAAAFP8kBQBBAAFAAACbGYreVCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/++DEAAB2hhLJDmdZxyxCHEHc6zgAEIoAMfh8zVAib4nBY+Ao8AhaYTB5hMFs+bo5LFgABkRILLrrGLsKXs3dSFrkYyhu9C9H0iKPaa6qiCjspjwNDzqNLi0pftgDcV7oZrfQEKQR7VjmnASEQ3bsCAFCUA7GlqRiDUUIEfxn7U0vH5ftkakGHtbTHUaQAKCMhQXlNeXJyNQR7Lllp2HGSWLBuAwyBZ5sKsbDHXYGoPDUUm2dtyAgBQGiouQtowloTEIo3NHxsbMl+o/qUMhXuwBAGocDiAaiNLo4A0EqEDShjCEooGXYQlKPBmEQmqj+mWpNgCJiDiEhmqm7pmAIjQjeW/IBAE4CTxCgESnYcYI7YGJgAogLIljIACpoKwBKpsmpjKtTXBBRoGIATUIZC8ST5jgsuAAiCUmCNd0WKREhpFCOGAcAmHZMAwIUBJY8Wg4IRQuMbyCUpkAJog4O2JIRgpgwYoYM8AMQgNAUBgs0ZECGggiGCzApRaMb9qFRAsEWDMKNKwLBEEBiAQwSMQDNGJMMSCqs1oUwh40yADBTPBgKTCAxkhxVFgEQaQgBS4FACy42lI2AM4ssFWzBFgcgS/nqsXpOGIxWGvE1G9QFmCwzGC4QmAYIFURTEsDyECBYMxQAQwA08wEACBjoqZOqiAXwT3UHLtt3blDlPQMQeRVcHAPEnlgNXbAG8YWv5ppd9QJAxcj/rIjEGqCP4sAzRY7cHAR7SLTARTdNk7+oEQEmwhQ1L5FRDRbJdtYhiANdg8UIGiIeVppkMAwB93GSIVoCoJjkhiakJEXLcIdDQPbAYxCq4UADjEJ6BMs4YQSQCBTXQQNOAAJDm84gEDgFSI6moQuECJAwcGhGcgEKBQ41AoMVWSQQdQeT0NqIzhBkUhDTDABycAXHRqUqIkGJtWLmQQYByQLCE0RAEsUxFCZkKHCUhmimCO6ZKcHMmTSNFoIjgQVGGSDIhmJA8QYXNk9D5QAEjgxpAKNDmkoeLYJLDqzIEQoMdMDXg1s3zzsSCwD4uAVCCjA6RzkyHqDAwPIAGFGwo3FKUAgEpKaamqICPoYCEgplR7KQU7BpUzy4zQQIQDxA2KEcAGaGJHmCIGqVEAYmIjAIwAMxoIWEgSYey8e1eZMOZIIasuPLCg8BQZixh0DRjkBpCANOnNoi0c0D4SMmUEGTNmgODIASgmodGgOPCZlqYkoaQQBBifLfqjAHWNQOI5EkjixIMCDEQgcwSgTNYRBQIMPgQeDSG62QKAzA4HL/usSAEiAChCQ5EB1GE4WDPirttloq6Q7uclM2BIlSoRCWIgkRgSDfgLmCImEdG7c9Tq4GSq7GRsvEQFwDgQSiHyy6e6RcKTVfQhApShevBMhMxSQhIhqpEiT/++LEP4J7YhLsDmNVx63CHhnMaXCiMXdVpR2DcNlQWSIZSaSgl7/jUgcJg4VWgwDFBhSLZa5bjKXYjgl8uQaxpLowAkaFpikWgEYVK0WHfCrWPNzNYxkAwMBTMoy66ZgB0IBgAQ0ggWY7gI4cIRIKIEpkmEIzrMsbXpMII07zCQOVOog8FSYyRLvmXGiBAZQuBAgOYGNLjJlCogPESQAFDXKjNjF3EogEDhAqAg9WwEAwU0AAUv+guEFwsQMgKBRgqhVKjDBhI8YsAGCQYAMURMCVNM2MEVDxJi15pjgZdGg4wABItGMEHDQgDMPzTgDeJDTGgErTxMAUMKCNq5EU5B1cQFLAIQbBIYIIZokBYwGJhDgqOx78JAjDlg4aoiYUCYFOZJAS1DlChUACAQQpMCWNsgOAwEcc0cQBTBRAbpMZgCGAjShzjJDYMDVJgCMOO/NMAM4RCpI+o8lcBVWdx0ZYqahwaRQbpEmIzgtA6l4IQGVlKbG4hpKEHrAAYKHS9jCpTMsi0waBy8D+GCRSDQEUS0BowCFDwEeSA5a4mWthExBA6UDKDG4yqsOJTtuVUgq7ipitaWFTwJAoCgNMwlfZ/QiKYUuVlTBBAAFMmMOISM2FYEBAwQDS7KgVItVXBFECiUb0AizUqi+wFEoLJySBSkv0BA40DQTt3Ao1kacYFAExhrJbNiw0OSFhZZMtMOiEdjGB2AFlUZUvEEKN48HCgQrBqVCxsIOCoeNA4UZIOWdNKJf8twiQDmQYDGjYQQFBRKDEAY0AolOCSweKI+CRAx5MQAlQvuMBiK6EGRUSZFMxNwhYWWjJlJjwxKAICBMiBSQKnDHCxKuY8C08yw2KGGTMVAxcIRmUGExEkFgYAKDGoEU00BYHRAYMBRk14EwYcZDEywAq06i1BiqYWPiTRTowBszRM1aE5JMyZ9uAQdMaaAVcxAQw5MVIk0ICDwsuMcmM4YNYLOscC74OqLtNMICpQ0bMCsDvijAsgU0McXEjBph4GEGlbAaalwBxoGXiS5AHJTRuDNSTLhBZgcRMQgBJqUXUqAcrN2WH2Z5SBoGxvkBqXgjqGywmCKlCI5g4xc80rMakmJdmERE7I7YwdDkAQUPmMtHRBm8AmRVvoLCkJhjlICTPJjU2eRTgIuM9JA2ixTEQIEQcMUhISUQIHRjAkGEySniNEdWJLoKgNPVTILAEwAAExhoOID0xEs3VLaKUMwdxEaPrqX0glY005c6m0JRBHjC77WhCAhzXWj6mU2IOAZW3heEwgVVQarHXZbWPl4S8oIET0YglXD8KbuDghUgy4R0RQ1pSbgKGWQMgjxYwIQCAAtDuZCjLwsAHQKjMgQRKO0u8uMAizJWU4esKmvmMlDVYJGFvAQYk2Ihw//vixFwD/WYO9A5nV8/EQh9B/mkYMQCpBwQiAeMRjBwoILMEFA0BAB0QGXKDxZNLU0CSaQ1zQcsayxoOG0yIjTVRoDWMDDxroVLAAJ/jmAQGAF1QoAHkIKAgssmBpzAjATZUIBKZiGnPScQpnFEwwMJMMc44jYiNV0IGMNIDGGmAaDySaYSHgCdGvOmzCGiACwcx7ECLTEiRApLkgU2Zl+Bl4O8GWeOWa4CLGBYubVMW5MwSMnRAQkWUk3EgOBUUYg4KgyUCb9aEIRExMWeNI0JnwFBmMKFzDxIyYgELTShgxyCh5sZZgjJnEJ235iBhhhJpyJrxg06MwUCzowCIBKTFkgz4bViTBDrzgYqMevNitOPTMyQNEyPqyPSPNSWNRMN07N2COSXOLXJIhqVp42oNRA1AFiw8tA5ww6FDU4iw30A0RwBBBpgNYJ+AACcwOkAXMBTA5TAdgLgwD4BiMQOJ+jPgkfwz3QjKMNXCMDkzbMj2A9NUDilGO5S4x8zzirLMnik0UfjMhOMtCYkEoGdGqRGcHKcKohwCVq7U0a41icVaXgbuWXKB0Pq2L7YUnWyYLAC/C1C+AyJiSj7D+l6VjtyVjR2Z+XwUfQXe961pMyUxAwdjjsCAW57QEgwYBaMKhEM5ePB0jRoO0lRNpKtwhCl03kC4QgCIWoIV8wIpokGFhRggyNzMUpXJMKODg4QASJdcwwJD2IS1xTQAlKGitZHgKhMeHRIVFThhRhMVEQJPRAel8YkMngARAIApmJuIULFCowLCUQwKbJkwcXNAXhoWIlQewku4FjBgQ5UAosiSYvCMAkxDCiDHiWmjyM1YQDOGehQ4Z4UXSMUOQmFUWmeHDTIBRJCQFQykYMytYIEBQaYEYlYMCTTFgAESuNyQMQUB2ATDmXMEScyo1hoO5GbFhA5E4wZsywwSMgJIZgaaFmbcmaFSHJUzzBnQE+Kx0ZMCUKgMGBwUha6Z5mnoFihkwZKzC5gRGyYIZlabYmZMYZg2qwRnyBUYQSaQSIz94zywwDwHHy2prTJiAhkyDAUOJjAxnrxgAoAaiE2CXBkAJtU4CxkV4xYRHExEY44AOEppF9WKKgEAAYH0BGGBsgj5gHYDeIAPkwCMC+MBIBtTGNyOM3w9O9OVQxMxEwmzOJFPMWkPkyIAwDB1OHNLs7Uy5iSTC5EuBAZ5g7BqmCEAQCALTARDHML8EJMNWCVM2Zy5BdyB1NWJtCIhSKUenSsW8ny3Z9RAGpNrCui8qa7YHfgxt1erVeV8S55ZMcKVVT2MAEaTMEVcqklMlgUf1cPE14s2qohwTqexlyxiEOKNSb1wBHErUUAoOlAKdUWVEskOQVc10BJMQQYC5BepkBMCtxYUvWghTpIREwVcomoXK//74sRtgvtGEv6v+ydHikJfwf9k4OZs0hCWDgy66xphHt1lhQ4Zjgs+WuQAqLF0lUTLLEQRCGtNnRIcDAzSDQDkoCWgOSGjwECPFhgbmtcAQLBFSOQFAguIlUmyl2QhtfTseYIyR/QHL5InBAchCupDQcBRQAxIwOYZg80MiJ1y4GFmCIoyj0ADiyIKsQJjyZgEAKsyhgcm0lAey1lhkpFCQXWGlRGWWzAoSHInaUCNsUOiMt9w0F3cTfLPjJpgPDXgKMNUEy1SL8AMjKoAMByphimKqyI0XjMXMcE6iwx00wDFHOMUMCTGDyDHpAQpZ83iwLSnACHQYG/7KjtVORAWdFNTpCUGNkUNEMjg4lTFKGkJjpga4DgYCwA3mAFgGhgVYDQYG0AJmDBhwpgTLHmcsCX1GJkMiY5YO5kzHBmBUFmYK555re4Vmw+QYZAYppitAtGCADWYBIDxgYhXmHCGmYIoOhnlgAN7ZSXXRBQlNafkYEAgBKiA1jwtRWcovugHUeMhoQkAYJH8CCIaF7GYq8TAbdKwcYEmy9okGMDxY1njs2EbZP8gyUTqWKMXFqJ4uCq5pCQymaSBfZXjuJtP6W0XmBh1bAwQyiBIwmRT8Bw8QTWeFS0ZDiaKiZwYIpssxxU9wcEpYo8FhmJqVoBp0cEMMRBpTy5G8RHFCQKGgCCwdcZSQ2IA1vqOLBkgqX5fJwQuctdRWMFzAEKyUtgY4bGGBCEVs5koMhEZi4QaIaZIocBkgAKpal6mmFRy2IOUIki6qPY9iOB0QcIgsKCEVJgLInCyoUKUGflyhaIS3AooKDR6EawJMSjQMBj6NawRd4ONBg4E0RLWWDBQSAvMxnB6IhBMAUWcCwgO9BxYQGFUi8QVGGRSrcWBgkUAEmuOQhjsQgwGljKkFETAIR0CGwEAMPhiRlmkJJpslQwyiAWmZjhlJnNSOPmF8ARTBdImQBmGDprAwMwzBAybuwqOLGghwAYnKqBqgSKKnmEEVTSsFlkn7QBAAFg2TBdBtMGIHcwtwtjESBZNX/jk9RaNDWLEQMuAWMwVQITCmH7M6BMw1ZF7TKBL8Mw8JIwjwkDA8BlMSQe4zkyHzFoCeMBMAAHAmGORgUUQOS76PhEBTnUwAp0CmAuFGRaZYWfD3MvCZMjCRETM8HNAGMMCBgNS8MGtCDDa6VqoOvOUFxoA15TNIUzKAwVAwyA3BseMgkyNPhwEpWkojMrhgSaac6jkte1dyYjT09FG0KDITMtECnJiIthxBqnM4IQkUy4RkjuuoXFnuYqDAUUVmPy9TpxiCyQJ/VJIC0OAWASwTESzREBgLxqXqzK5R9Y21xDdSZdACACSCayp0zUghgJQZzGkL+b1uiPaCUODiTAk1gU+3ZFJb6L/++LEjwL6uhMCr2sxR5bCIIH94nCYCJWg3YvMoA+jNjCAERJcNRUADMEITlgqcKjI6JeQ6qwiDFQk13eBhCA5FZVdZrvBCY0HB61DHGRyjK2waMYAY4EgIGp8iYgwBSAZBMtcsygNERifICRBiAVTBwD5kBjepyzg8e9gRWYgxlFiAFCBkpZogBQXSSMAsDEGcOly4A5QASC0oOvAow2cLFl6i+BKkpsDgw4oOHMAUWtBQQxSoahAOxmWmbxRCsAkTECOFovsoY3jyvzwwMgDOMDIAZDAXQLMwJYEIMDhC5zDz2VsxQ42NMNQBxDAywRkwN0BRMCkBYDCYDFYwxMFiMItCMDBXAOkwE0AlMBTBIzCwQYYwFcB2MCSAkyIB9BwAQYBGCCmCCgAxgG4ANQCACAI6XLMVKmkgIPLLAQaNYPDiUogEC6oYRlQZNHITShIiBmGV0kQUmBh03ZXA4EmXlq9ioHNvIhQgNiRjIQsiHTPFMHGoVJzKAsHGYNIhoySNL+BxA4zP30X2AQtRRPtd6Z1UwcNFgcDGhlQKKCIyem6oIsomPhQiAgEMmGjpYBC9r4LmUeW/JEXIYEYlwsPYOyZAYiuaCKGjpwKJIh0FhE0VHF+pHFUDJU7WUhwG/hsuuiun0MDYsnhm4qazUpTDNCzpWgu6sOjw7abzjIWtHQAMiLUDiQMMsk1QDHMjGJrhbcec4cGDSxIBQNYFMgCiVUhxbxZsWIqo/sFocke2SgpCa7LHXZ69wsBrhcJNUOAXbSgMyWJDrEXUlRJUCDKodIxg0KJwRMvw0IEVX2uhmkYTGABB9RkUJ3EtAQpqMAnGPhNJAela8KPhhSBygKgFoFwAAytwQkdGH8Cj08GGLSCJAtoGXBYFkODA34cAzEfzY00XMZlgExBGgqCKBsbbNOqMNsLkwUgHDASAXMNYEUx1RFTsyLSPvVZczoC2jE5CPMTMIQwohBzZzlXMysV4w0wxTCEDcMMEIowKQ+zLyNwMMcX8wDwXDBpALMFYHowbyTTGxApDAOggBswEKEYMYucQ+ZMPjAEJBRgwobuYHGBIwDjSaJF2BvS4HSACF1zBwAYQKnkIRhAIrXJAAFmBDZnYeCgoFFwXBDNDY3U/RJMrCACdkoYZAbEX+YkUJIgoDW8AFowQTFgd9jAQlWB6gcRuSrYrYhsMFwkRBwePAIEBBIpNTZjNAEABIOAholR4MqMAwMFhwUCmAAIjYgX/LaEW1VTY0LKQGOiBEltz1MIGgAVMAjgoAk9S6bVe/SgigiXCkGhOQsC5q0AFlHgasDhjSWslAWKprQw3AEBQ4KbI1sfe+nSEDBSRk6wzzoAUHpVTMnQvGCKZssTYXFCGgLuZLAbKGvooMqYqhgWWT1VyxBN//vixLED/E4RBg9vE4fLQiEB/eZwhhzvq7gJ00IGlq5bg27JF0MOLWBQygZe1B9aKXKi7GAuQlgDhIAVVBKQNKswSBLFgSRC1RIKWwVAQvB1EGQYFujJzQstwNRW8EVG1EKzOZtjG0KDBJh1AFEl+XPFQNORjJuGtYISCElrghAZsQlMaCIKmorBXqCj0wUNCSVYtEeGAqANxgZgBiYDGAsGAQgcJgEwZAYV4yqGPxkihhHQJmYCmBNGAxAOxgiYOiYq0BGmIQhKBgBoFcYHYAXmBlgyphW4OCYM+EsGFjgHBgCQACYFAA2GCcBaBhZATGYIMBiEQJqDgFcElZgIKYoCGIDC4C7CrgwGNuWxhPYoYcSAYUKCAFZZkgOhuYuNmXjYNWjYh8wMKMCHzHSAwgjCqqLXZjQYaYbGcpIVXjwLA4wWHFo5KKMWEzQT03g/TFL+L3XYZITAEcGgNCBXxcgyAEMMB1cAkdWCMEKgEAGSG5IOFZcYcDmug5jYMAAkEiQoHAYyTlJgVDFL5K1w2ThACMisI6QhzLpmMKZCAwQLmgdRgo5CZopgqgSZqq4RQFRQqHmmCzwBDsMtqZrpfFm7E0BiJarFBF1w3DkaLfMoWYsVOt91ov6hqXYSNUXZMrYn12XNPZoXZiTJGylwnZUzSSfFQ+AYxKWzPAsKs9I1LVYBSpD5wmrocSQKCxQRHJeC6nlWCGQEBDLU73sJn2hOpInkka20xWuAIFnRCOlgpk09nYsMOIsiQRN8oYFwwaKuJGBLsACsreROslHS/HAB0Ut8jiNAMJca6nVBTMQoILGJXqHmYARJGeSjmTDNNHvQ6OdVUDFEJIca4BbtGgDMkAcsqOdTVTAHAkMGIFAwVAYDBnA7MUgYI40y3j7yUwM4EH4QgaGA2EQYSQSJqe7tmxuSqYYYSojAwCwMpluG6mWEIKYbYTBhVATEgLhhJioGT6IQbn6K5iqg6mAUAUQjKRhlAkXtTFaS4y5zESsxZoQiBgQYCJExGPRhpIKgsYeKGDhBVWDZTY1QqQCO8YaNRoyVoN8Ti9xiQ+ZwgHT7hyRUaOBmck4IFzMAozYROlUSz6BgNCNVZk7CH5dBmwiAd4wknfXgBnjZIQiEpx9MS2MrkAEjRRwBpVAU5BMY4iRz3tySDKw0dC+q/XvWMDgUjDflBwxqpCSpMOmiYrBW4EeukgyDDwy1QoSedJBlgy6Wru0DRJIkvDz4N2YQkPOInSFWOCUiFnOA0OEOcpFNx2VVk7pakguuBExKrS0wXuaI36Wz8KecNnZELVZE4EHqnhpxG3VpVVSRUClS1m4IuqyI+INOEmasqRPxDYhHaOKBo7WocXK8L1OesdQKBCACOIDFgUWkvGGOKABVTvymAChXSf/74sTGA/naDwoPbzMPqEIhQf5mYEUQcR0TrTofwUDir6q2JkprlDoyCDl1RB1iRLgorFpBCEWif4lDJDS97XIYSwCplACgHzFiFb2goAwaQkU7bGnttijAXgJMaAijAVABIwDkBgMCOBkTCDUfcyuQHVMHHBeDAbQGswAYBSMCTAZTEsC1cy7cMFMCMA4DAHgGkwHQAqMFMAXzDshZswrwJQMCgAXTAbwE4wB4AwMC+DLTEWgMoxDUG9MA8AVjHI1MCgcEAoxDDzUZDBAIZoWAeIAiacSZioFLPTJCAyYRThpEApPBcDF5ZIYXApiw3gZPt4YFAiAwywDjbBoNLl0xiA0jQALzc9IPBpUzOOzAQLMSh0wQ6DQLsBhAGhqEJhxRVAVcsxji1CIMCspIwCmCOpl0QA8YbAEKAJIGRLMDAQY6sIjyy0oOoXLL2KYohIzl90umup9JoqlB2omEbhEBFtF5GUKB0CqKnMkI32aZY0u5KRl53plOhUI0OWlg1GtOFjjJ0BLZVlJMr9arUVyhsWYXu5reQIzpY6ci1px02Fv3MWV8PK7L6NfZuyluETTOamqgwNCtOqGFhmWMFL3sqgwqCDwF9lpeBOkAACARrK9C66Yz8yBci3lrsVUmECNOdZWVSujQkwpIgt/ElVGbKuR7TQeAs+rcgqvULAF7Uhg5pFJGgLhq7WEb1ZSIiWxhCpfJiggJCYFgQUMjGmY+6WyfqE8AipuGG7kBi0ELPwUSgFAxCCRA0sHpBtwgSJydMB/AijAcQFQwDAA9MADAPjAHwRkwTZRzMY0B6zAggUYwL0ARHADAwGEBWMBnFNjUNwtUwi0AaMAZAQzAKQM4wTEIYMD9CSTKIgpgwdoCPMAPAJjATQM0wCUFrME1FoDKcQfEiB3jA0EQcAwND8w9Rs2HAowSB5JpI8wHCUwlJwwgCUIAFJRWImD4wMG4FBQNA4FwDLtiQwmKyXGYYjhAdAILEERgoaBhLRRrSHw0cqFxjkTpmEFhhsrBmeIQsHi/DD8FzJoIDKsDwMThrNm4CaaZecFGGKGrUoesGlaXPCAVjEoJfxP40Ql6HOWCQEJYUDIEyUcwQqZMqSF4HsFjmmkhhcdTFDuhS7qIrYlLlDnsRQQlhUoIuYSoHckBekiba8wFccIa8IhXRftusWWEC5RFJeYk2d72KqAolNaVOsIiU/ayWZRJ549faS36cLYlLFWq4GQGZlyVNF0KZNMsqYvO3QsyuVhD2s+huSugnuySJrbUyVy4TW2fIDUwkcoHYMwlB1kz8sZTbWDVrXM3KBFaWYuSo8spHV6GmscQTOUPDNjjRgimOKX4QWcIeBLateCwaAxAYDDYZQrYklUUApzp0v8ViiwRctOUuYsp0UzBAEz/++LE6YP95hEKD/czB6XCIYH+4mhUYQMwZNgIvQeTCFR1F26jIKvQgIGENdVK5VNOGAGAMZgEoDAYByAPDoBQYC+A1mDcG85hbILaYBsAKmBvgLpgEIBKYCqAGmFcDpRpqIFUYECAOGA4gBJgFgACYFWAuGDgBeBldAIYYE0AQmA2gFAKA+jArAHAwHYT+MfJBbzASAB4xLDYwhFIxQBMwjX04LJUIDWXN6YCgOYPncTGswRly9QQAxhQJgkGiqhMDAjAEVCwwmYAyiE4qAiYCgMYIiOYEDIZ+rmCpPAgqFnDCQvjDUYjMGijTgxDBQBDBYBAANKZJjOsYcIYOAwKAiDAHKwFMVjkM0RdMJQGAwCiwBtLZ4WgQTPLJyIQ50XereYEpBixDdQlO5D/MtWFU2WuwZCWX9Tda0wFB1wHGV0nSqdXAyNTJ5C9SajAFopwIjIAHVct24FfgGETXgxmzro3mrIk+MKcqHsnBR6FxraQTB1ZWJrBrBQ1QT/XDX1DjftJxdh1HagJW2LQK8Cz35hpPRzGTKCJcrMcllaOI8VPNZqrmfs+aElW5MonlQNqv5L9AAKHd9NRxVoN0hKRCAdFp/UNJ4USpvL1BW3SSTRlKgDPlgErFkqWr9Rea86wkNfS7ldLUgRHN3Urm4R9sqAZQEDGX2zZu4gFDqplyoKqkTqQyQOQJvMAFodQKZW1IFKAMAFBprP5pUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVAAAGCsAuYF4DJgNgMCgC4OBGMWJvczJwQTBzBYIg0zAqAnMG0HYxVM1D8JHQMGQCEwYQPAMEAQhGGDoYgchQh4CEdMAgAcwUAZTA7AcMep1g0kxajAHBBMIgbCwEGBYhgFySlwzDoHktwoAgBCMQCoYrgmlMypV4yAhgyKgCDBkaNxKAiOJmOPJkgBpgWABEBqAMwXEkzJi8CBwDAKIARJhJMHAUM1XKNmhpMDAqMJgBC4uGB4WGAxlgJFjBAwz0EM3DjAxoweOPleFyMvRXMJCQcdPwvpgKKqLCUTYVK1EGtMEJhIiB3YjDoS8VGWkrudxZTMBUAX3HZhYaVpjEwFDzS40whmi1ZBQTj1K6et24Q2jcVLmQQh94aXQWBYeAnCTaZE0QOBHzhUPxd/KymlaQtXdd4m/fiAFTw4/MER2rEmBU7D2ISp2nvfJldBRLqVBDTfwM1plstvPC1SFw24MngNmUTcFs0llkIaBDTO2JJ3qmWOwlsa7VvsjhDDm1irXGnLwf5hDuNbZqy9LhzV6tPSoSQWypYmSXRfkeA4yWdeFPd//vixNKB+XoREK93cxdnQiJh7uagE4vG4C524KFOvTJ1qmWymgsE19MGNuY04ts4j01g4LRqQzh6lgfEQgwaQMTAXARMC0BUwCwBwKA0AUjzKVCTMBoCcwNQATAmAxMBsDIwStSjr1FqMMoCMlACMBoBEwOQGjCYZgNrYQkwrwqR0FMwTQGzA1DHMUmkgyYBXDDiANMFMAsGgeGCcCcY3gRBo0iomDoDmEYIkASGBgHmJBLGOISGBgAJQJDpwGC4LgIPXqRVkRckyeO8xVDcwBAUeAICASYFAyZ/B8ZeDIYDCsYTAaYhhsZFCMaoU+ZWmeY0iGBjHMJCUMiBVMuTAMAwiBQMCMCQKFhiEHhhwkJm6MphKEpiKHsLC4imKYMCwmFxwCAoscZwhwxmGAhitpqSnjcXBRiwBdBa65C6CwkVTaIh1AUOIYepuDh6WHyKRUcrkLtKyRmH5xRyyosmDKnPgmKQ+xFuLPZAz52C0qk8GTI6J/DDphgtxiL/1nVkLS2kw41KrF1pRmFS+B6jAX2r0D+xeK0TvxqA6aEQTTu4uZ9H9euDpGrc0pm81QMkZlCqF3pRMzr8S6ae1pz/SKPPsu59oEbG/qdUN0DLGSMTe+B1ysVd5pj3M3TSYg/ygccUTa8yZqrxtFa08S6FoOV1drC1opREwCFyfDmKwwQgw70COMwUvIzptWuqFuI2zB4TNU+1TEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVcIAAADBIA7AIEZIBIYGAEgEAvMHM50xXQIhoDkeAjMCAFUwCQljEwswN+EAIGBRlgBAKgIhcDIwVG4jXOBWMDQE4wYQKzA4B6Mhwlg09p3DK0E1MTUDMaCEKAcTCpBQMGoK00Zw6jH4QjFECwAIBj4WBpAURhORgwHJABAqA4XBowhAkRhgMhwYJAEFAaMJAWMKA+MEwICgYmEYAmCAkGTRCGZB1ApbDDEPQ42REJ5j2LxirOpjScgjPExFDoFD+YpkeYHhiLE6cTTmAABmwwa4VGIXxjwuHBI8pCMBMiJTUmZDc0o+MdJTXko0gcHn8BERkgiGBTWFoGDCgCCTJwEIGA4QZoYOBA48jCvEfWjkQKDgIRCYYjhAWnkzgSAlV2T7aNSsccncJplbqe/KaWCWcPpHZTm8jYhIqo4fRQRUBoCj9DzE2vvs1BZrX30lzOIMaxLqWk3GofmJhnlLNOJGWXwuZlmEah1+YrDEzRy9uj3tYdqcuOE/Usib0Oq1qW0bh1GUx16J6GXVq27bsvsyt244xh02UP49yyKqw7JsWRzMlfv/74sTSgfseERcPd3THMsIjIe5umKQsCYmueWyKKM+XEx1rUha5HpS1h72oqeTpcCGZmkYuu16ppznZZBADprhaRORGA3nj9/phBgIgAkwHZgGgOmBUA4BQCzDCM9MwMMdSasIMBbEQXBhz0iGM2NAYO4LYEA0MBUDMwRAHDBcawMB8bMwJQBBgGYwgwgDBAN8N5dmkytAKDFHA0MBsHwwAALDDTCOMeVOgydhgDPgjM2i4VORiFOGtMGBryLBkwuGQqGAoQjJJNM2h8CjAAhsEhowyAzOo7MZhswmDTAQAMVioCjo0sKDUQaBQ5MzAkwsXATkDcObM2qNZpqwmoDT+9DMHlszUHTJFwypWDIIywmNRWDFTo1AHFpA081MUdwqrGkHBhJ2ZkamhI4GSTFaY0BMMxGFxB0SYgEmcgQCCRIMFQAKjsBgoXIhxUSiphQmkUsCWTT0Ih8EDQsHDyQYaCuS91aCH5fFtHUoocgnB87MucFmdhvWUuCwsYAFnx2G0JqjRMENAYcn7eQSyukUwWFl0MwzB16zJ3bgl4pmUX6CYfN5VcN878MyibsZw1NU0Zf7TrU0jryd1Ytk+MOQlxMYMyYbOx6nlEM1odgB77u2JO1Ipp/X7o4zLn/f9Z1K5LuxeOwRI8r0Qfh15h9ncgqMtrBD8uC7sMQmAYvi+j6UW5E0/B9KCH2guM6DAn8gGISy1xUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTAKAAAAgXACAKAgIAcBaOgBGB0KyZeoEwKCTHQKTAdBTMA4CYxR19jQoAwCoHJgaAOGBWBOYHQUhghkTGo6F0EBFBgIJgqBSGFYC8ZresJk2EPmKCA0Ag5TABAoMD4HUyFwVDL2E7FqSSBQwaGjBbCMQyQwUMDGgcFAKIAiQDAQlczqbjDQKaEBgQIxaNNQwcJhkNtIJRAYlHwphAYdzAopEgYYUBRhMuB1RGpUZGRpkUemNR2ZehpgeRmbYuYgIaJZiApGBycZFR5FtgcTBANBkDGSlYLEs1UBDM4FMOh8yiITMoFMwosxaHyAXoqBw4MIhow4Dy6QQByoFHLL+hcFIiyBtAsCFkKJpCGAAAigJCtFIwqDQqACwBmgI11G7tOa3QS+9Zg6HIMnJXDMulUsh9nS+UuHBjLS1LoGKASkxKJpf+xRlKwGwo4CMZICmkY2decm5kOJPoEnSOOlWG634OJOM8yNU8Frb2XTnO9NFljJ9hhRUMSzmcJf2KOfp0wnaUOlOJBgOt4zQ2f/++DExoH33g8aj3H1xzfCIxHuaqCRuYI0tXp0n5CVi5UCmOdJTIYzLFIjTMoIC9ZzSJPzwYnaoZoyfOtCmXLOq1FBX1I4TlgQGCWA8YBwHIyAMYAQEY4BQYHAHJmCgbmBaAOYDgFj+vSYHCfxuwAvGCUAiNAEmAIAEYCgD5iYjEm1WDMQAGgoCYwWQETGHJyMxijswLB6jA6AVMGcBIwawVzBpCFMJ8101MBuD5hoLYmFBiYJBBl8pGqg8YoEo8VwIADD4eCoZMYGMHAExOHTAguMND4waeDQ5fMPgswMEguBoKS2MNGQ0oCAAATAZuMliAwPIDLp/KBsYxCBjhcHC+wavXhmA3GmUEZTMZhsqmcGGbaVhzQlAQPGDAiZWOJisrAgrmtQiY6LRjAhmt4nkXmYrC1g2kYusnwLCwC0JlprBRjigOFAJMYUGaECuVHRaaoDHmghA5Ce4oJQ5kIQ2ggFBVD1g3kXe7y0Iw79a20GejEon7THoYYBDjtoFO6wa4+yxmkQGydnkAMkaQXiZs0x4mnRCK1Zu1G33l0Xj+fH5mbzR5ieiEPRp7m5w5Fbsgeq9STt6/KHyno6zifcJ1LrtSWVW3caJDziyaoyukguxKZh2Ybh19IsymBLULj0/q9XiEYftv41GoOa3Dk/DMGRyw67KJdJLV6ei7uOu2CIOpDsujeF5rb+sxhLgO0wG3nPcUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVRDAAAAwLAEDATAAAgEhbURgWGBWFqYsIdBgWADmBKBwBQWgqDuYT6NBu8FOmDOAQYAAF4jAyMFEHkxHAKzZVLkMH4GMDCZGEUE2YNBCBhJK4HB4s+YXIYBlOgJgICpnMFZm5qJxj/5o0JZmGCxg8GJk+RRiwRpMHAsH4cMBh+AoYBBg6CpeQgAoMHQwMAsOFswBEMwODERAyYGguYDA2MAyDgnMLx4NLA9RLKAfEAfGECIGCwUmugaGQIcmIZTDxzDxYmI4JHQhMGPBOGGAFhBKmU41GfgckgbGAAkjwvGFg/mJhPGHQcCIrzAElzIXAOFTJjY1VzGOMz8HMYCQEWggtGTAaHBIwDAoFAphAkaaAAYGL8JGll0XnEJRwar0dVOlBhYgMRADEwRDedaOnisKpm1eL5u60ZSt/JRhcbIzaOwfGbbhpuqfcxhcvghGpikbialbgMibrM1ZBdyicofPtS3Mu89D/Q1LqeLyC9VfyMOFXjv0mOcWfiOztn23h+bei5epI1ZnWt4VYbiklsx99IenICo6SMRB7q0Kqwz/++LEz4H6Xg8ZD3dzRzHBoyHuZqlXqck0vl8ZaNXcKbkz9O3XiEJpo3TwS77dKkMuLP3IPdnKWxtoz7QbBs1Azl0s7KX+itaywIBgTg4BowAgEVzkABhgwiShh6hgYAGmA6A8YDIIhgHBOmDgikZfI2JhEgeAgCskAIFAHDBpIONCYQAwwgUx4NowsQ+zCkB+MmE/Q88x8jG7EsMAkEEwNgATC8BJMCwRUy/CVjeJPFwEYAL5pAQmVT4bAS5ioKGMgQPHIiBTFzJoIMGgQwuCTAw4By1MGJg2IpjBQDMFiodAJh4BmFC4a/ABpoQiQlTCGgkYfFRkEbGwieYsDZkYpGXzWYqQRiC6HmUSaZTBi4nGDj4YLMZMNzGY8HCgX8MVA8QiwxkFzHJCMKiQueYEKRkJRmuWCZqWRikKhB6MLB0wQOzHhOAgpVTMFBAwSAAAFgwHpbh2hFdHE9zFHJKjbKAzxeUaYBZZmGMvKoDvxllbAos15/GeRh93Q1LXCe2Jshe2XYx6HWZtLjFiLRkEEtNf6MDz7fDgrb4RCleqWxSo/8XjV2Aqa1G39q3p/cTqRnOI2m7yZrMbc+G8pl7X0sVZHZljsVZe9dBC+U8hjcQwxlkruSyHHSfWWy6O0T3vvG3UlcMPxHK1JM01uKxqUWKemqTNBhEGvxCYgmdgjB5oGir8tbqWJFJn1sw5HY25UrlFhZVMQU1FMy4xMDBVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUgAAYC4ARgAgHhADRgWgBhcAUwBhzTHiBiAQAohAOMCsCQwMAEzCXLMN98VcwuQBQEB6YIoCZgiAbGISOWbkAHhhVAHmDmAmYEoV5gAjeGCOXqbFqNRgcgKmBSD4YGAARgWAlmCqEGZ7wSZi5OmsRGYiQ5lAVGeCgafLphAcGGA4CiGXPMEEkwKFlBwUTlVTBoIMfjA0iuwcJjHgwMFgtIkwiQTPDUMuBQwiMTGQKBADCwNMKLoyEODFJjMJiQzqazBa7NQ2kwEgjVAmNhDEwACDIQmNppwLC4xWGwwgQ2oaYCPJoYlggFmEgaYWPwJAZ1Admu1mYDFBgQLGCREYICBmNEkxOBwFMPAkSCoJBoGEAAAqhIcEYdHQCYWC4kWyIPhwlEYCWoYWA6zAMBk3ygA1SYKJk3odhLkhqVVT9uVytZC2F7jsaTLoWwnDfBI0qwJNFFtFOCGC6A2i6oecixBZFC1yxFmMknBJqtXFxE5OJ+yFOyPUMOZy3l7VW2jFyVykSCgYGI7MIubbNDh2fqJGQ29DoCIc7suFTpVNDMeLG8cICoclcxtShZT+UqjMpON//vixNkB+i4PGK9x9ZeDweLh7vJgz9zZ4p/sp1wrIBGIgyV1Q9lacBlm+oSiWTNgR2VoksQYUA8mA+AgRAugwBQwBwATB6DFMz4JQHAkmBMAGYCYIJgNA6GFSNGcU44Bh0ghmA8AlEzAKAeMMc6Uzmz4TDHB4MCAEEwSQYjC1BlMJkWU8kiCzBaAeMJREDBFFQiMkjlPxWgMxCDCgimFwRmGIImPI4mZBbGKoHGCIkJHGCAFjoWCAOwcGgQHRgYAJhUDJggJphaTxiuEJhoB5dILgGYciiZDsQaaC4YXg6YChmYKBoYEBsYwsgYtkCYniqZAEsBiLMNhOMQLpOwsw2OljTzYMCjcx6IQglGjjQYNIBhAlGKxGNF8wWADcprMRDMwoTzDJ6MaEI1W2DatsMFE0zIDzBwlBgJMKhEx4GxkKAYLAEEAwkmMAeY3HICBbzrpIAmKAUx0EQhfjQbMBAxAaQAgwkNYMT2TqepczFEcYZaBafZ3mavLUsQzDyk4An5fTRFGuHaXseoAECIg+b5p/yhGVI6HnHa1A0NwmNU1E+b8y6vGYra6wF7vprkNS6OanYvYl9fUWg+VxC/KJ908aWBYs8cAR2A4ZYGwCVWoEguhg6O5UsPPxTRZvJx4ZU/tZ/KCJOhYmXvhEq29TXH9hL5QPJ+z8uvPw06NOxffx2IByxsSl3mouPD8vdGG6R7pq9dVTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUWBzBwFYsBWSgBA4BMwxCNjMmDlQ3AADpgGAdmAuF4YDRqJgXFMGEOG2CgSzAgAAME0LEOMcN/s2IxGQfzBgAnMAkFAwPBLTMLeFO88fcxXwRDEoADHgSTA6B5MKgaY01i7TcjADE8YLHhlYUHBimbJhxmofmFyOYXBJQCTF4kCwWMKhgSGa1i/xloDGslsZiFRiQXlvAsAACDxFajah/DikZJBABCAqBjTGSPFqo0gHQcRRoMGUQWZ2ep/4bZmIsBiUVJhkM5hyIRg2VplUG5g0IJjqAQqGxgmEhgsMZnAXBiGRxiKDhg8QRgoExikVRo0wYAMtKMGhoTASYRhqYACuYWiYYDAaYDAWYGCaPA+YMCiYTgKCgcU2fYYBAwiGQIOItSCAJMJQJC4NkwpgoB3UhS1BADaSTBWwM15AMBQ/EXul74sr3DUGylLVlapV+2MkyHJMBwEToWowJfKlQqBDEp2LwXA191Vn0uoXdob9K/rozr7vzKoVjWhqYzlU/ZxhmRWKV7K+NPHHLfB7txuG+vREYk8csdF/LMNRzKB34h2+0WR4QK/rrvw8cMV38gSmkTSIxADtNq4safSfU9R3qsOv/74sTiAfxeDxQPc7THh0Eioe7ymNHhy47clbNEHzbBE7r7U7NZZJmzv01pQeikTww7TUYhBgKAhmBWBsJAAgEAIlAXMCU2Ax+gGTBSA+MCEFcKgRmBWAMYWQgh0YHZGLoCkNBLBwDIgAiMEkxI2MkTDGsBmMDwB8wGgWwSDmZJDvJspS0GZsB6YToExgIAfBwFgoUYaa5whzUfBi6PpgKBhi+MyJRqc+ZjGNBhcNAJAJQgLiEYcgAYDgyFQBBwOmBwNBYGzLU4zD4RwgTEJIQBYQIxmafJsQdRjMISA8Ag2YRhwZLu4ZsoyZYkWYFEiYWgGYWC6Y/XmaYaxkMXgwaBYDGUUiahwBjs0GEBwCQgGFQwsXDIpUN5JUyGeTJhiMKIoxKQjCEmN/ooy6XjGhOMPAoBAwxwXTIgGAwmAQXVQFBCBg6YNDJikFBgfV2hxoBUcmCw4IwMJBMkCJg8iEzPDCOIwIowo8FwYDhMqJsDUbS6WXPhhG6WUzbFmUP5WcVaJUAj9QJ6Hz4mBwKnBUUwYxHUrWGy+RvvDsUksa1fh2IT9FUjE3LqK3k7NqHH7wlcPxd4n9j0ujV6UQ2+0eh7U80F/cJeymklNqWOA48CwbBkdjWLvvq6LcI/OyGSyFnzw0kNP9CZ9wWay+UvpEG9Zy4eERd6mqR9qjRKjpxCAIiz+RO6w594YZRAM7PTLS5HTyq7ekxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqowAQXDAdAKBADoWAKMA4DkwqyCjR7IhBABTWDARAmMCIHMwXzMjKDXbMQwDIwIgIQ4C4CAxGH2AaYl5a5jbAIGAABsYKAFJgqhbGQsNqayJfZpJAxGq5FmCpKmDpoGKJJGR9Qn6A5AZijCkRDCAQBGPBqqVJoKGhimGZbhCARgYEDgDhFBwkhADGA4GmEYRmBArme5+AYWQaCRVBgxACYzCIE17H8efwHAgDAEFgaMODeMBydOfwAMSAIMFQtMUwANIHrORoTNg1aMAiDMPRyMYwGMGReMwyoMayRMAxGCBkMGwAMUReAISmiBOGhQAGEInBBfmcouGE4gmb6CGRQEGSISmDYAmF4fmIAdmGpNmAoGCIES7wKFEwEAkxOh4GAhQiHjM3EqTjLlpK0TTgyU3KhaFUr+A4p+YcTfYLQTrsuH8FTTYJ6nYZAvHnbjLWFMzo4IbGsK5KtTNmiqwNPXpNPJG5vsTh+QTTj/BUhgDOmp6Oeuzk43CkmYLkdZ+I1Nu3SXpVZjTpRmD4U/USdx9H3dqhZpC4fgWgg+Wu078go33ksugGGYk198YGhTtuvBdK6kNNP/++LE2wH82hEUD3czhz5CItXuvngcF1nuopS+q0IkzqO1meOlLJNHWnNDcqMxhwr7YnZgR1IKae47D3Ra24cNtNaxDlN1IWA9C4BqWxgKgRmBAA0YRo85qWhjGDeAuEA4GAMAEWgMIkOU02TKjAWB3BgCyIRVABMDAO8x2hETBPAnBQQJgPAwmAYCMYeYKxjkPKmAkD6ZUg4YIAQYig4YYm6ZlTycTD4ZZggBQcMAQNMGhUMrknMvBaMPRUAQyCwLAQGTB8FjBgHh4LxAAQ4C4ABIxYDQzmK8xBCIUAVRUcC0wCEMyMiEx9Bsu+hKQ2MGTCMMm0NaQlMRR1MBQzMNRyMNjfNVnbMrmLMdi0MGwyMLhPMEhZMEi0M/REMWyXBwaigFmCAPGAQ/GRZomcwQkgXGKYJDRcmIJFGVCagY6i8RgICJhgGhguBBh4BJWI5gQBDD8muGAgsEwnuI7SRwUCYwWAMMHohBsICIlAgeChrxguBahql0+26Uiw1E7eSlG3JpvlbSfN6p1GPlEpUbaeYGt4XcYhjphLosdytRLIzvYqEOTdDw7jw4bmuLvpEJYp2zarLFBXCjiPlZAPOZhaVI9cGdqiHmqzuOtlO9YZX75EKi6eNFFtadUTOytjknlM2o08zqJQuywyKZIGwWx+nllWH6ikKS7QpjwXVVAcC2/VBtGWXaU+1hdnGro2SDm1BtJupMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqogwAAAAoGQcCOLApgQC8lBUMCQyUxriHAQCmAQPjAyAEMCUAowtgSzYaGfML4EQeBLDgBIQYMdAjOO5kMDg3GhIJhlFQqMc20OYJfO9x3TVMBgeMIyBMRBpMp45NtBrCCzAoMiwcGKQNmIAbG4gZGSAFmDgLigDmAAIiwOGH4OhgOJ0sxMJAuAIPmbK3A4XxECpQAIFBQxbKAzocwzTHQqgIW6lZgsDgXxwzvDYyLDswrBswFBcwrEQ/VtTOkYMJJsxMCzUidMVAEzsAzH6yM5G4QB8MEZjEJGWRSZPchn4VIBjGoSMKlcx8TzY2aNIqgBIIEh0wuUwKJjNCCMlhZGsvgFQapsYuIENz91OwwCECUKmJAEYSE0PhcGA4WgYNmCgkYACTdH1YdkMgVltSXO44j8w7Zux+IyK46kZmsnlSae+B5uTvgoLAMesaX40Zx4/Lott2qDCHJqP7rw3bldLNbgZ35rlA+kLyn5HnGYxhGJ2GpRDtR4br8wJRS+xi7+cpdWRvq1SMRqVxtlsDRWBqao4LsxqcnY//vixMyB+XYPFw93jcc4waLh7r54bjr3s4h1ucBu9i3CPxCZj7sUeoKYdAr30lWmhK/H/uT0qkUaguEy+igh5HvgSD6r6xboBhMBWYBgCaZQcDQNApmGgB0bFALQKEBBwS5gZgKhwChgti6Gf6UOYUIBwOA5GQBAwAcwawdDGyLLMAoBFkwQBeYGwR5gRipGGm6UYo4kxkyHZCBAQNhjgURmXq5p0UJh6AxgwFyKRjkYxm4YBE9hiIEMCL3BwOGFwPhUIDA8AUZxIDzAMNTGcCDEBfTB4FwqBRgiGiDRhwK5ja4hk4QymsrTTMUQGMEL6GlZMixOMLwcMGCHMjCwOWobNcjwM3wfMFwHMRRfFC5MWgFMdg+MVCpMBwPMJgMHBOMWxvMPztAgbiAGDAsPTJpgjBkrjI0JzBgjjCoHjCALxYJDDUMDCgZgADQQBYgABMgYBUChYFQWCAXUehwvEnKLFSYIBiCg3VjZuYJAaCARMDQVSoicZbulI/jPslSFqhmQ5xZ0+wGEc75XHEK6EAUhAFYJ4wClAGR5sy7LmCjJsuFtiftqtSrCwpR7OnkoyjUSNVchlmMykAon0I6F9tlyqJYUBWo1sntAdO255Nqc6z9ZHamWle2x1HAhPCNjhY1Of7iYLGlHiGK43na5J8+PNkO1OM7kpFdcvKePAth7tx1Fo5LSM5jqWYzD9ZzrgImc6FYmTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpIAAGAwAjwYjQpgAIgaJZg5cB1o8JjwJRhGIJhiEIOCQxVEM0u0QysAgcAceAIOEQABqZWZ0ZvE0EAyYNhCAAAMCDPPhRcPIjsKAjMOBKMEgIMjTWMnHzOolUMoAbMOwILvGBY0mOqGHEqQmOYAF3B4DAgNigAAMSgsAQCANKoUAIwcAsxCWYEAUgYNBEIgNBwHmIZRmuA1DwgCwVgoCzC4PzF2MDNI2wwtDGUAjDAGTEwYA4AzmBfDQAxgYKpgYUZiKORiKLxiSChhqQwMAJLYQBCAhsMkUSMTDwYKAGH5nIGGfgmZslJmIKA5QkoLMOhIIBxiMcEQuMCgJCetEmARgIKDxJY8sVP5iJgEFGCRYYcGAyBC1rhKwCEUg4du2/DzszIQQuB87nwLLpRawkkZoGiTEYn4VFS+KXje08cl6KAsDC/cUicOLoTjYpjF4i+MO5Us/Dtu7L4dcZwYjAL23ZQsRl7DpLEPScmXhKRmcR2ofJHytJwUhAPDA6NztS0BYNQKHZqMP/74sTEA/deCxiu8Z7fNkFjAe4+8SgNFiSeh4rb3x6ZJDpMOTFWbthyI5vGA4Qg/VFRSSbFovqDh8KTosVTLx5HdClCNB/jjkgCIGABMAEAoFAnGBMAaYYIiRsxkSmGmB0YIQAxgRAABwCZgIBumX+WGYhwGJgUgSGAAAOYCARQCAzMF09wzhgMDBjALEIBJABMYFgfJlCECGheR6YQQQBgDgQmC6A4YIoC5iABVGXcZCFQGDAvAiUsME8BIQAamHisbhCRQcGAmAA+YRBxhMwGMwCYGAQGG5eIweCjEpeN9lMwmMwuA0cTAQGMbM0yMDjUABLTI7ignMs1g5H9DahkKgWFRsCAcZLJB33nGFIOKBIwUPTJARMGFY1QgDyZtMCB8xGAjGgxCoUMlJozyrDRgGMnjQ1yVzDwYMak4wI9jCwlEgCIQ6YFEocTwAEzEgALeK/lzLgaFAAChoEJrpjQ4YVDhkUzCRtMGgEEgpY4KCAQOQgSLidROtRxmiXkcpI9fpJREJFOy6HIOBQDgZ8441p3E7XHcd+lxAYFiBm2cbCJ8ex/oBrnam1QulnTYr1tewiG16wqVUOTkmMsB8yJiEqutxlHtigPk4rmZnX2c821Fo1C2dcv1JCXMjkytb1pekJVKTUiw8ZYjMiVNhEoyZ4rY5vJd8mUsbzEomR2ZTMpCiSTSo46oVOjnbKq44nJQMVhVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVAAAIJzAIARGgSDAJBRFAZDAfMNMfdJwwEQhzAoA4EQAAqAEYAwe5naLPmVaB2YPAEBgTgRmAwGwYHILRitirmrkDmBg+y/Rg5hBmBkDMYiAfph8pTGYqCgoJzMIMjJoPTSVFjSnuDF0hDFAPigKDAIHzAwHjEwZDSkPAgSmtGAoEhAQl1jFsDioB4IABHQFBqYIHUZDBuCjKIAES7HhKMNCBMSW7NEAIGhMJAkEQymFY4GdJWHQxGGBAJhYDQ4XjAEsjWBOjNmCDDA7jAoYjCoQjFQoDGYvTOhczF0QxGGzODDcLDIILjH5HDLA7zBUSTJoEBwDSqKJhIYxiaXAGGACAIAg8BQ7GAwLJXl1oCRYWMBXTJIASrUWWqGgKobCMcwCnFloDBVzRTEeLcyW4v2y6K9IZl8lgOkaPJvklmH4GLXSe3cViQeSoTjrv+r0UJbyHtshzU7bM6ruxiX2oafqrOzeFFuXvZTP7JZ6Su7AdZ/KS5GrcByveMDOnRT7/SmxRP7O2Y7GXRrU1mFSaLPC7UNQSyCXxp3r8OwO/12EbvNcl91+XEdeD/++LE1QH6VgsWr3czn15B4uHu6nCmzvPFXfrx1rtyEQVEYlXd6HHbeRlcCQDAjAYjGOPFI33h2RvXPQNtKwIAANjBCALMB0DYBBaGB6AiYeAXBxKDFmJIB4YLYGJgTgGmAMAGYBIeBj8SAGGuEEYAAFYiACC4RRgkAiGB0dyaMwPJgDAoGAYBGYDoApgtikGGKBQcdAyZoYeRawwgDIwYBUzELo4DiUwyFkLCeYaAyYuCwRJWY/AOZ7j4GDuDgGMEAZKATEIKg4DACCQBAEVAAwPBMwTFEzpOAxLE4twpcTBCPAYY9vuZGCKJCSAgTMCgvMHQAMo1tM7CPBAGEIPl9jBJKDDF2zKy8zFMVTH0LEWgcBRmma4Bas0tB0wyFwIBoxNB4yDPYxHEA1VIAw+CIzEBYwTD4whBEwhBoKHOjSTDmJB+YBgYRDEYCCqTDIwIsmZIGIgBcQMdKbMVJBYXFGYNHiIuOtmUmCCITRQo3rbO4o41dyn7uUUemZmPT8nj0qcJaCRTfQffjq611xyXQGX8ZwUFpZKX9gFkM/TT0upKOAX6gOekcFPBqZvXYu925bG5HSzcSoKbc1KZC68YpJXajFLPbu1KLCH6jv1rcOw++8hlMqktuUSiek8Bw+5MZgSJOdF51hrE3uiUD0dDhhVeCdl7pOVB9BGoTKpyBnxdCTMsdurBsw/b4Uz9SyvLrkBy/ipMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqEIAAADAdAxHgbDBaAjMCsAIwMgZzC1MuN2FYEw8QgjBkBBDAFDAJADMCwDw14XPzHqD1MFcBwiA5CgYRhaAgGH6YabAQXRhIADGBYASYLgMBgViYmRizmYV6WZ1k1mmziblawgRBjkhH7rsfbO5g8MsYMrjQ0ERTL+8O5hUw2FlGISxkgFY0YWsmCAEFgCAC0YpHhlqBmSSqYRF4FBIsKkjjIp1TVkYyYJjAkIyUCjDMfTCV0ztlUTDUAjEwIg43BwwDj8ITdXJDFItzHQwzCIETBsMTFwBTPaojWkEQAIxYAAwAA4GFMY0FIdapeQCaDjeCgcGGgJg4DDWtTjEQBCoARhAAIYAoOB0wsHMKgEhqp4MAIoBoAgIYmge4LYG5mCwIiMIhYskZGhRJEhxx0FVwv1EFHm+WVMSytDsqjUmfN7s8W6KnZg/sigmeUBVM4Fl6WVtzY80BwIk89G2J8aChtsAdxM+O170rgl+Kr8OxFr+2uSqfgWEPhTSOrTxuIvi8r9MNdpidNEGwwl+oZjbXIg5LcoW/FAymGIddWXVY7XkTkzb+s4dmVwTAMoZPDKpHiZ+15udJSv0xFw27y2MS//vixOEBvEoNEw9zsseBwiJh7r7o1aUKZe1iD2nt+yuKULEJIpXFpe7UPu+7iunVcHJhrvJMEIYGgEz8mEICEYPoHpgIA5GEeW6aybPhh6hamAYCkYBwBRgBgNGAED+aYStJoBgsmFABsGAtmBMGMYIAHxgMEDm9sCqYPwAJgUghmBSCKYHAZ5msNBmx088YBoHRgSAamHUDMYEAQ5gLgzGQkr8YOIcBgeAfGEeCqYKwKZgqg3mEQqm44CgIt1qlngcChggHaEshAFZIwAYoFhgiDJiwRZn2Kpg6EJgCAyIpgCGhiMAxluZBgkDpdN2gaQJnIWpoHIhMbJgiIw8cBgoEpiyNJt1cYAEEwfDcABCYLgYYTAoZDhUZwkUYSAMYYiSYCCuYLgQGFoYyI4aqhmYTC6YABMtgwsBcwzJsyyBEQgIYAgKjChaYBBoZTjOgPZAjQkICgaAgLEQXQ0uYtKXIMFwTMUQRg2UIBnRY4LALMwJckQ+BpI1ucmSLkcU55OzTMRVKU6HJ2bZACEnbDSpWilDrXzCdqMes/1BEfw3Re7o1yQlVmQXVjZ1c5K9CV0brJFXaiOZPtzYSVYaCEyNKuwkdrxK0+ckqXVpfUAgkSu1FD2r0PXkLgG6ryqTDAvJc5IhyuSGHa8Vq0zlgPRxOct6pL9HOOIfCGKMxxbixopwJ0jIhbpUOValYE+fqeO1Lt7vVTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTBZAKMBQBowBgITAuAcMF0CkxGAaD4KN3MbIH4wfwCwgO4wcAdTDPMINZzuwymyLDDmChMCMGowRQQDCrB/MkQn04TBaTDyAmMKcAwwPwojBRCNMTkk40xrvzBABeMGIBkxrwXyQG8wMRCjH/ZaM/YNYwBAdDBJCWMCkBskCJMXBpNOUsDgoMBgRJgEEQCgYLwcIDB4ELkmBAHgARzMIijZUJBYR1VEbwaHRgcEhrshqIwOAaFmBwaGZaNGD5cBE+GEoXGBoZmBBDmSJQGAEYmtoMGB4HGJ4bGMAGGIIYGN7vGJqzmLIfmDA3jIFmGJFGFYeGqtOG0Y7mBYtg4jTA4VzCcLQsIBjyHZhQFggA1G4wBAcFEcYnCERD+g6w9XUiMHwaMMQHj6YJMAZgeCw6EBhaDzDJMXNaSo6XWgqXvxL1UwIewLCYo3DdjMLida0A/g/GxWoA9TKUbGlBYRoGqghEji2/OQrzZS6vYle1skxul7Wz06RVc5BFKr0AordUOR2Kk+lSimxlPYYBol2LqpGAcxKSkPwnppjtcy+uSLQhD12QpDy5NODkOYaU6fawjR0H4S4uSpWyHF0PASAm5klMxth+IIQ0UB3n2ykLFaEmesRJ1gTsW8NP/74sTtAf1OEQ4PdfdHwcHhlf91oMNlNmw0HUIWK+Mc5ybP7wdpBgFoYAoALGALAERgEoBsYCYAgmB5hEhm6ot2YKSAcCIABMAIAYDAPwLMwEwKaMlrRZjLIAcYwTsCzMIYEowyQKjAHAbMd1NQElVmAwDoIgTDBtBWMJQE8xPiaTvXjYMrsBAZDvDCkDAEAUMEIG8x7EnjXYCrMCcAQwQgizABBUME8BoxIPUzgU0OFIRgSTAcGAGIAEFgXLTpgq7MOwWMCxOMRQXCxNLvJgEMDgAEQaGNYXGKJMGJIuMpAQbGCQ6GT5KGz2lmzBAGGIWmEIVGDhWmTBKGby1mSRmJ1lyAaBwIEQtYZjDIZUhwGAQSAeHHYYyiyY5LMbIokRBEIgBMAAWMKwxAJAGGRdiSWtQawwwwMDswfJAFCEqKge1UojAkwcAoSBdrSbocCKAAtWvWBUZnHVkeFTVuU7f278+29M+0ndqHVNJHT5xJeIoAPyaMwCztTpkruKbMwct+GIPVLXtwjsZqz0tkD7Q5AkHwxea82JVV+3Oed72tJqNddRu0w+GDYnDaUrdJIYZU19LBm0rcp76eDIvPwy7zB7LnQlQaQriZSlembJ4XQKbuujw2KH1A6Fuqokw51KRtIDUzsNed+FxB1XBdiPtXZaw4IAKgS8SFTkZDL2CpYMpRNf6UtPZnMO6hcsRQV5lM3ajMXUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVAACGBBgLJgCQAuYB0AdGACAJpgBYEAYEAEYmP4EuxgMwCiliYDEAymBagaxg/ATCY22oCmUbBY5gr4GMYPgPpgggJGDGFwYtqb5oXhvGHmAMYBwJphCAbmBIB+Ye4+hrbIEGPUAiYPAThg1AykQUpgAAvmOabsaTgHpEDWHBEg0EYwFAKzKx0MtsIxuCGDrkVEgSMFA4WEUiJAADgYDR2YwAgG1o8SUVBUHmAQ8Ih+aBQZAAEBCAsEDox4QTMCfP8AkQD0SHBggiiVcIaic5E5lQIGDgeSgwwKBzCZPMwgccFRgINJwgoFGPCkYqB5zMlkQ3TkMMhcGigwwmwYQhYOJBlvU1C46D5nUF1ZKncWqCAyPApFb4jHnRRqWFsXasDt1tQZ8RgLJYSIw1AW2xw29WEQgGUuux19qSXwDI0emOP5I+R52FT25hzXBoIbgaD8qWG3ejcPSmbpItC4PvsehiMulPS/k5GZXBLMo2uNz6drz9vquRR6JKB2YUxODlbocSOd1+m5oD4BdiG1gG1fQtwrxczbw40tcsvdxLZUUoVhTLf9FJmihKvopFkcGHNIjiymrAIDqLt1hiTMFJgFdkQcC0v1yD/++DE5AG7xhEMr/uNB6VCIWH+8mDoAlC3wcIXvZ2rWxFMZjaCjU2uQ5dsGAMMA2A9TAcAFIwOoBnBAGoYBSBUmBBBzxiWRb6YIsBuCgDaYBuA3mBKAdhg94VuY1cwgmPhhcpgjwHUYEGA8mAvABJgaQCsYMUH2mJqgQwKBTxAAMGAWgBBgCABEYL4FvGJljsJksGBg4BRneJw8P5k0Fph9P5/AXYkRSKJg4KJgECAOJ4qB2KAQHAEuIGgAGBMDAFnVLEHiABzAcODE0xDEEYygJFvQYCQlIAHMjBMCBEShHAJMDQ0CoMG2tFh2clABlAqmGAoaGKpkazm1g8ZSCoCDRMCDAwhMuNcw0KQciB4YDomBQCMYnI0zfTAiAMEgkkASerlhgCMZCMIH7ezjWjBoSMPG4x6FnFYK6STgQBlOFewmT2wMBEql+0nytZzBHLi1LBUiXYgvDcMSmK2SEBqYwRXlDvv+hQvaU3a08gIaTALtvq01R6GH1wh9wtP6yx25bLIMdaTMGo4YhtxqR+m4ahtlzyQKl6yuOzy2FSO84juxZiDoN2cdiJeRgbuMFRlikMSllTYJFZTlSYXOz1pLXbyY6mQiArX11q3F4H3C4EzhlSoOAU43zDHbYa5yYiY7+LEgPIuKqmk4s1zRCA0z2dprL1CgBBQbhpK1rrEZcXVQQcStRmSETfagqoiQCgCoFHLykxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqjAkgKAwN0AaMBdABzAkwFEwIYCaMGfDrTRoyK4wdcELMCWAsDAPQKYwH4EbMEjCrDMFji4zXUIEMH8AfTAswBIwI4AbMECAFDCVR6UxC0FkMCLATXEEQAKYB8ARGCrhDxhVg60Ix5CoqmkgahYIzBMXDF/VzkobzA8BjBQCx0AQYDhgeRAKC0MBV/mmweBgIDgVUgzuaGQMHRhBJNGaoSSuVDQGjAMoTzJUkSAAkzRQHDAsDzDgODWKrwSM4CFgwKA0RAMYWgqYDAMZ8EGpAGAMhWX4CAMMPjFAIHqKmFQFkoGA4DjJF+TVQNzFwDkzDA8EowOh2YphUAgKWGg5p6dJiyNy4Um6OXuwk0VDPDEYpEnPXA7eUCwAsKWwk/XYi0TUXItWli5WHaVxDUpkbxV5hmt6HHEa+zhqrQ7TEIcarAEGvRKndj7UG6Q+9bjUEfo3PhD+QZC2vMuZm1Gw3B/ph4Ik76nLXnQWDX7SEAYfQXlC8XhbxfkNqmcRJFNJrCRdogHpr6EEOW1EFPQy9KsgqdkasakW8SlcBhqcgKM6qo3+WoXAaoqgqMlDElMFFyRyZK0izaqyI02kIaH/++LE3oP8Gg8ID/cTj3RCIMH+YuCzQ0BCFkiFKRIsAKmIlNPRiTIBh0AYskuGAxCEkfRXUUbyH1jAvwPUKANBgFYBOYBkAVFAKmYOIEmmvaC6RQNqGB9gGpgPIAgYAKBlmB4B9xker6MYuYIkGBsguZgJgGAYAaAyiQeCYG0XemEwgSTzjIA4gPMADAbTAqAdIw84YlMEeAfCoAuGCSgGhgI4B6YCSAaGBqCH5gdQDC1EiAKjACAANloYKxZGo8tcgZlSCAZFiSKTlIvgwAADBSWMQhxOUteFwUQAwwMiTjaOLtBBMSlVsMODMyF1jL4UFioAjUYCFDMzEqIBw1Ij0BgSsMpUYGIRl1JGIQcLC8wYBaQwKSTI3zEB/VlAoKRFVyYABJgQPiQLVxafVnpiBVuKua6885ITIt1LDivRTo/wPT0F9mBfNFBqMjdZab+l22TMsnHLYEm+r9gcYVe7q+3tXtBTCYy9DO4HiMMRNL9jDlqmXSueD3bmnIZ3GmfOq3VpjW4fXZbiDVZYydajEWAMFbC6TXYXK22ZTUbBC2kMOd9ha2SoFpjMmhKbrTX60NToUExlkzJuN6kOn0hEzxPRlRAIQlS5RyBgQINSQMEstPN/VPqgak4igymiOxEVlpnAuxlgYgXGvAKhZQxcEIDuKGCGLF1eJ7PwFnP4nqXfa8DroDVowchQiWhY3UwjUk3Fp/ZMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpgUABAHQwEAXDAXAYJQSTCIBMMCwGcweywjyjxRMWULowlgTTB8AhMLcC0xGgWzgpbRPjwMwx7QIzDUBKMGcNsxJgJTD0UvNBATAwggUDAgAjMDoBYwFAPTA/BsMwc4AxIAWi8BgsAPmAaAiFwdDAgHTReR0MAoAFDsYAwCRUyDFGUiSl2uQl6giMVTw4QUgy9qBc8yw2PDZgFWgJXHgkVAiATPSmzkmAlBUAyaRhoAdKYnKAxVBkECUD7mRkZjB4AjJdaQlMYeSGhAaqsPp0v2BQUceQuemthKmSaDKiwCmQi5qJCxd3rjdhQkHhaDpfA7MI2hpIp5/MoJcJKFRns1SlzUvwExrcneRpK8zRRzkxKGuz8SQrGuqMzypTcN10RVbE+wKYaEq9FcRhZpAi+GVuSvtlLFI3cXw/KfD2RJ+IEZQnLBzbPokQwZrEpblA8QbyVPo47DKN32vr3UochcbJUqVnPu8zsMUamydn83E4LdtrojFJUT0ELV25P/xLtIVTGzNL1aytJfSA5aKsC54kqkrHHnYNBUAz/vQqkjQt5yRJywgOCoIFgIUp5qbqw//vixNiBOcoRCy9vFweMwmDV/u5irQgJQ4RmcxQRrixghrFm2LrJANZkyqjFQIVDateQAAwIYBABoAyYA2APGBWgcJgDID8KhEJkQCRgYCEBdjQEgYDsBEmBkgkBhOQa6YunKKmVPCE5gsIJwYEEBPmBwgKxgYQBKIBCEyGUQlMAgAPAMASl7DAEQBMwBkL1MRpByTtomRUlDGwogMWpgGJxl9J5jOKYKDgaBZwSUAzBUYDEZBAwKoFZ4ylgwcAJlmJaJzvioBmAwJCERjRWpTDMeTCsBAgMy0RgWGRl6bBtMNoYMiLCfpUDYyUGUw/A4wkA4MAkLhhEXkKcecigZ6Zc7zaPgUARhZgFAoqBQQEEAMZQ6jyWcGHQ5A8oKg2GGIAWm1U/CJgx8SKxV34xNUDSorGIhE9RJejTEznWn4WvijMBA40uufikMlUIWpLa1ShXs4EXijuVIzLmGz1hdy5XairMWut1Yq8bjSd+Y00F1VTNvBUSUAcJgqy1VnGzgZyGlKDQfxWxT6cLX4w3dImHFgIwtVxy8jJI9mxBSp+WQuwn0u1mKOg8BLaXg8xbqJLiTdTiTadl+1O1Wv6IAULAKVBfUUBwUKKvbOu5d7WVlyBJciABgJHAEsgRABeAaA13piLGLpBgAFQFIsvwWWXIqiOAqoGVuBDQ0jquTIEYCYOKsEWgFw5LIVCSIQR7WY8ED3O1TEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUAAAEBgOYH6JAU5gOIB+MAPhgDIFSYBQDKGA3n+JglgGEYBKA6mAGgQJgTQJMYRCHemEiQO5mXoa+YKQCOGBagSZgdABgYGoBnmACCpphGIhgYCCBDmASgGwXACTAAAG0wPYGfMXaFSTAZpMNh0LE0IIhiUDmXECbXAwODggAo0ADAAIMXDAxKVCIuLf46VowEQDK5cVDAzdwIGjGorOsI02CEzIYcMRBwwKLxQfmPz4arNo8QTBwPRJAICGEQYhDpgwDkQQFgOi0YIMYjFYGABECFDnfWSYOBhgcQgALMlYQGAIKCk0cFS7ZQA1oSlMwcAYyI1NJ6JNHQQqssUsRvxeHY9efqWQ6mOWqiUzLWEJlNBR+bWXQCs9CwBfbCw9nEBsLQflK9HySIU7XTKWGrsft+nTjEOsGjTVH8yay80EPfGWTMQfqAmxQTYbu78ssui8cBNyacoCvpndO19NdURayB3lXaWdYI9i3IZc2MIDUkGSpvJtMza2slcyLDeMdW8ytXr1uLixZWxOdlK+FsLIXywJbgch6GgrkUYLpxZZyPCHIRLaqnESv/74sTVATtuEQjP8xOHPcIhMf5mYAW2zlHl9V+OaRVnEkCqBXSzB7ieK5ggZFNJwzgL8ppBAQiScsLaQhTGEYS3afWOUptigICAeBgQAEAAgEkwKACeMGEBGTAXAMwwKETZM4nL5DCBQVswLAFMAIHoYEIA9mCUghpm4wRWafqBwGESAEZgfYAQYCUAgmBCALpgLIlKYmYC2mBJADxgGoAi3IwBcAdMAHBKDCFwCc8+ADGZdREMAgoUAxnZ9G9Qq8rKhCAy2xgsUGgB2Ch687YWcpcmA3IEKFSM+ysQAExmjTXlWMJjoiMSAwHCAgCpioamvRURDZnxeQICRmkKAkGL+L7x0zgRHscAS1ErFqOK0kOyfkBAypuIyGc8ID9E6nJdmMDgAMBNUB1Z13+qaOVDMbjd56FSK2O/PS8YSBBgqOkguR3xwYjLAAAjBLvI+OKCAgUWmOMBoCUUEGZeAA3QTqfsswDhnMR4VAkomI2jMljw8MBLBQhnMy1Z/WEUjtOO/7c0j4mlO+jBYqw9xnQau11pEt41FqEfnlrIuNq/iwVRVDNeawkuge+5S8J9Zj7s4etOuPQW2rwL2UOQ/h5gzOnnaxB7xrNSvbtGPb1CtW9h7shUFNRrqMC7EHGSF4EHSUZaBfBCQwBuTFUZGsphvI37ygkBHXcgX01NCW+xfsRJId2IETgMHUGZ8mGARG/Xe79edUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVYAAAYHCCemAzAQZgY4BKYFAATGBzgG5hewlMb28D2mIYALRgsoCeYE6AOGAxAjJgPwtYYx5ViGW5iphgB4M6YAwB0GAwgF5gXQEIYFEIumLuhO5gK4DUBgBowHAYBBSZPgmYGZkAlGMCANDidDACMJACMUYsMnxGEYErIU+6g4IAKECNt6v6VgkHzFcmwcCsQWesICA/MGUpMYCTMOAqMHQHdQOAIwiDYwsGUxABxIhylBguDRgQZJgoC40DTM0wIYMGh1MGAFTna/DCA4ZA8KAeIQBWIk/DAgB0w3FsxCCgiEpmsvS9VqIgrCwEvDDr8srFgKlUpqO/SPwoPKLUVkbWQ5L/w3C1MBA46BTTZE0xg6aaWyayNTE2EOAnU03JdEbU6XRG4Jbi8bXpU6rWXCrzTAnHbs8T1JNfUTgZq2FXDltjavWhpAMNFW4umUtIY+ic/6EtliwTE2AJYBDgxy9w5TDV7MSQZWEUqflXLcmNohqncNBtrKCRMUiaNTFStPcpBEWiZUXua6LCTUQqiw+UCBL6qDKKB6AlyNyyAukuaUNQYSsLxpEpFJ0lpTO4twydrq/QRUcAw59EMi6SC5fhh6/5In/++LE4wH7/hEEr/cRx5lCIEH+ZmgKnM+qdAOOLICLqxjB0REUkFCA5eNebrv3RmAFARhgTYAsYDMAcmAOAYRgaQPGYXGXgGyLpwJhkoQoYD8BumAMAE5gCYEOYDODKGrhg1ZlbgO8YQGA+mBwADhgGIICYKwBQGDtkmJip4QQGAChgBwAiAgAgZAOTAOgGswGELPEYeBw8MohghAoEB4FexnYNI1poLjR6MJjgiLbxNrFWlmBTeY0Jxd5FhIQkAQQOTqBiMJm8wqBzCIIEAYMDBIxOoDBRnAzlU1VcjOBAsaqGplUFMjTlL+iQAHAoEIouUyRY6gBiQJGCwyCQsraki35p8mlqNclgJNiPDApqAM+WM1GrKwwVhsmfuvGWxOpBkNPQvNP4IOWW38SXyFyAIuXATTZAvB5hsCPq6f1mrfStiarWur5gRHZOpWuEp1Q/GVb4bSEVvYaxEeDddk8OMvlq6VD4fXG4CH661lJbMwgeYgNW1MFIgucGBhUVXLA5hVyPbpRNhosWXzSYBIpUCSKVjXiXmQPLuI1l0yqUyx4GzjDrOEd1fKSBgIWHctZIc6jKIwC97UEwlLECJdFKcIiMcUaCEuU40EqeyChZcuoYZCElGYWWQDAFUAhF0C1icDiAFcHADg5eAIwTZMUQRFBZFM1UYQYWeMMBpbAUWiicZCABwGNVcncApk+xCWlszVi+apMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqACABgEwJ2CQJkwFABWMC1BOzBEgjAwuMvpNr5TFDDNwiEwTYEGMDSAnDAnQJMwWoG/M8wH2zIOgfkwJcCGIgCwwIkElMGIAtDAPCsMySMLRMA2AMiYAABQzMQkszKrzM2iMjEIuiZOCoWACdpnktGggipkvVKxWkKAURiIeAqmDRQoADAB3Dka3NTpWEVARg8IG55yYgFgGZ5gcGAABAQlmcYmZWFZnQGBwHnVAQwRGOCsPLNRVNhF8ecFLTlQJkY2yJACcZxCMIyUKZkyhTIbOgc3+BoUuMwMqliTLqogvQ8Slytz1ttZsSlbMVuTsqTbTjRzTPYFFSEAECHi8yh60qGEIjGGItXaJKl6ji9WlJpw1DqnEPsnT/jDNmjtCcWLqQzkCeit7L2bS5x3KdJc8zxdzprCsFcN0U5FBBoFYdp6VCRT3KWxJAMsIrhMWMMnRqZtKEuqjmywtZBpRNEy1hWEssZPEl0pmKvGnsyOHWbAhNHlr8hQqLvCxQEBYM/A0MPEkwLGQSQEBLOQ0cQtIXQMENAfiY6C8RkxM9HoygSB8YFGRm+MAtIVJMOFGSlfmeCsVUDsqVJgl0//vixN4B+x4RAq/zMVeNwiBV/mZgx0qTGSaPNlBZRWMkOYDFSwADiyIJGsSAU3a3DGaBgRQB4YD8AamBRgMxgXADGYMWBaGHvC/J0PQ5QY0UAhmCygPZgCoGSYEWCWGDbAbZopoE6Yu8CRmCQgFAcBSGAcAhJg0QDuYbUPlmSchIBgEICKYAyAENyMAwAHTAtgAMwNcJRM2kUFAAoQTlhYAGKiWGBstHAJaAQgYwQEDEora0oej8/gJHJnwXCMOF0AIIE/TApnMnwAyMFBotmMjwAk+CkSaMTZq81jUhL8GFgQLBFfpQHRI7q3EQDQDoSAx0e1U4eZ6wC4dS5lBoFNNIjBCMBBisMLLLjmC9AUIb1OJrrTHKQAr4ZbQy976BbKtc5F7aZKPBjhlxFSNdiYNdPARHF9VJqqCFQElrVabEXRg9VWXFtFAGyM4hlFZ8XRdVWyGUxV+Oelwg41lTBd7Akr4w7DoL2sM4ctQCdHQHGKCC9gkGi+wVnTcVVUxkECwoVHL+PgiymYhJU7CARAAuoWMjCrlpMOZUho6DjgwBLpEtzVJgaVEdToWCfMWCGRi7zGkpB4cu2IiwMHKV0mSYkVCEa4JRnROZ6nGXsQbKyRYIFFKqsbg4Whb8IyYCtEAAF0k7422dAAYgJimOaTCCQSkQi0LnpwiTCEw2T1bQgkrGMxhDq0MFKJ/kWCm4URFgpfcqTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqoAAA4AMDvAXTAGACkwCQB3MBOA+jACAkcwLAuYMWPToTBRAiYwBkDPMBXAbzBAgOowp8P3MTyacTGQwf0wJgCoMBtAMTANALMwMIFXMA1EbTCVwc4wHoBFSaMAgAH11mAmgQxhQgJ8b9Chh0FmAjeMDMxMQTCqhMiAAYA6oETUBgOB5g4IJ5OSFwQVg0BDQz0bw4oILqtT1ARPNBXMxcBjBQZAgaLijQ0MmNQ2CCAEEXkBgLC4IMAgMwEGigPtKm5Cmik0XXkCMzxlahitKpFVFP0cKEJxoqm2EKLIthUEvym4HCORE6XTpCgDvRKMxm1Rr+hutGmThQAW9b1c1ElSygzvGoRJI5Uhf4u05bYGZw61SmUtZdSQCwGZxfp7kr0+19RpTp2lYV9wlVSGHEg6cbeNMOWyrC+TSqJl7hPYoOygu4tVFeUtJQQJNLwc5fKwCn5CqVMiNxxEyDEclWQAjKnQnio1XZHAjhKQViaaXtTMYsnogyoLAwwUqki7KBQSGWBKMO6p2oYKjvLAShKd6DKE0LgjR1CrfDqVoiFMcEGFkRa0UMXod5/QYKJCFAQ8sLLFYiHg8M18IBVaIBhpYf/74sTggns6EQUP8zMHoEHgAf5mOSWLbNOFkQSakyDRUmB0MuC3FHA1XzNDjHTBTAOEkAGTA7ANQwK8CPMGOBujDzxnk60stkMapC+TBygaowGAGaMAOCBTBpwisych2KMYlFjjC0AR8wN0B0MAuA/zAKwGMwOwM2MNpDTTATQAsEACoOEAwbTBhXO+nAxMLjCQOMSj4kB5hMBGRCSYSALuQYEBJTYwKDTOYfEg8zYsqsKAEUZNBwcIQEHnXbmYaERrPWGhDCAkiYADqV5gITGgbAZgBQkIklF0KyCIChcVEoKgtrTjGAAMYoA5gcKKuvu49pkkEAAJK3JEgoEuUMpMxcFjBAQKw49regwIkRMZVOtAeZ9En1qOmsh9HAbCrdEKdViCgJMDHxpQ1UXERsHcDYtgctgg4OFGYAbBqdDvoT0wmuF52CIhPyzlu7iy0VDmHlVIgIJA6IWLR2Hg3+aYEBuumnDKjrHF7OaXYd5eIQIIyl8rSQdawqk1J9KBYcQkp6tPWHUahWmLCEMefY2XxoS4oVAIkIoYoCfRb4tOvBoReeQrua0ztAM8jBEHhxBkxUJJnUZUtV2meWBFDLDUHUvLmvsDjVFVlK6UWDA096AhFTlHQCsM1xEMZEUMA1dYdUoKVAQDySFBAMCBUxTzDlZE00njNEMUUOmXgg+oIVS0EoXIMQWWlqSQQhNUkzRBMwWoLkxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqowN8DiMCIAmDALgJQwI4ArMDXArDCKhKE5SY2eML6AizBZwCMkAJgoBEmEYAmBhJsDkahsH4GBNAqZgDQFIFAR0wN8B0MEcC1jFoQlYsAWACAhSgACMBIANxICjMFQAZTZTkwUZMLGwMSFsjIUEwoEHgxOFcSxQAgm8G4Kl1NHfXoYOTGDvBFvpCCEBvNqYiWmychyQ8YIDGDCoCETJSYFQAGElQl6qR3wUPo8w2yheJhhCxRjJjUUWUWRBOANdYABSQSCGASyonSFlAUyZICF6eJWCyn4Yp0LyzbcXUtJAtdYe5LZxEIhoCRnoEiTFCNMAJGIBGHFswYCgsQmBj6NpigDAtIsExItdLG+e4UVWsXXcVIBatdG1XEbQcWg0Rpyg5ZpP9eqY7sytEeFMIX2mYtFFKGodGQkAZEikysWy0y+MAIWrfRwQEq5S0GgXTjL/rCIVNbQ4JhFswwBNFRQdDcpLRA9fIQEtAChO+IQDFDXgVpg4ZMJCdFS7hjtpVrDF3WKp/BxDLnFRMNwoAjr4Zyl8W/cUaFSiRQHgFBaw0GGFBgLRizBmAAIEKOI2CAuPltWYP8pSl4mKmohSu8vIMJITzH/++LE4oP7Sg8CD+8zD6zB4EH95mGLUDLQokBU0UFXsIpF2CIciUTsaEIMAcBRzAvQKkwHAC2ME8AITBcwRsxEYrINYlQWTAKg0cwv0B/MD3BsTA5A14whwNfNApCIDXGg28wV8D8FgZkwCUBCMCqA2jCvQ6MytsG/MAsBJTCJQqEOC3jAXgFcwLkB7EAYwc0+DhEaQ2GvLAKSCJAMuKxAEEgCmWgoEBRjD4EdwhB0Hy6AXKTSRU8QHTLYeIQEiCzD3YxtvNyAExy3whAAAtiRSXdVRfl6oSYILs2cxrLnoE77xkwECJySp1hkkwgwEoFBEOQyWQvgwMDJAmA5jkTCYxpb+hCcBJtscKC09y1aQT4N0YQrc0ZtC4CQgFQOkUHUirBnHAJUYVHmERxCOSCHY00xHVLZaqEyJrvY6nSs0lBMkd4kNVAlgQcQpEGqIsl31gwcAPAjgI1CsRER1QgdOhMRCSYgRdgwCBCWqunE1VeI8kytvhwRHl32TFhFDYSAZI6DitOUOXY0hHaD3iEmE+WHCRAsMWrJmmDpqBUhK2o4yLQBLWe4Yogh1LTtDYYRGIfpXDq4VLIQgaEiiXTLmDQgMKTBMVOBBlMuA0lNVH5YYsFLsTzAIgwI0RAUwYyRVTjybIiFVMISQC5ZgEIyKPmIoX/ERpEesdi6Vyw0Pp1gEcRhAwctmkYZZKNIIZMUJB1OIbVMQU1FMy4xMDBVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTAogQgwFkBhMAMBcTAwQEQwDoASMNNK1DPaFUM0HwIPMIsAQTAygMkwGABoMCcElTEdEuUxtgGlMKGATjAYAKUwP8BhME4A5zBCxfkxC8FiMEmCHRoGRHAEMSxOMXEROa3tNCA5CwBioWGAIMggDzBMBgMs4IAheBgmCD1gUGzBgRBYLjAkFzBsJDCEKTDYAhoIhI9sjPDBJA3xkaO0YxSGysygwweKKQHG1sPqs5Mlb8fgKlgdpRQS7hbF+yIYZAIj2bLPZwJAjpYikeEzihBQnaX5VIVhB1JC6qEwgB0JTZaif7sJILibHGWgpjhVIIGHKjDWTUDijcQHFDWKOYwEDCMsymQrUawRfgvMQgFArOGTocC0EBrE67IcYhOQCg4pkxjAOy1ssuKjrQXWtEeOQ2CgKZyhaVSZAQajkTKMWZIsowy0J6Va+i9i+EvW9TjYiks10iJS2LOL9SsdJXZdsCionLuEkizKO7LUrE+jGIiwADEqHFXQskrASHWmjWm60lQMuSoyELIPI6oyII0fZaHQmIQgoQhFvTCARIGh2BgYcOQUDDFGAmIChQssuuvYcAQ4w6W7ASgYKj+n2qqWtQ1M//vixOID/SYRBA/3MMduQiBB7WZYJYCksZbdH6Ei0YClDgBg4HNo4loGpg6s4QRCMs1QQSMT7bm+mBhViXmGABWYZgRgACEMHwMsCMImQvLwciCY5gVBUKLg4VowLAyzDLYpMjQj0mbRMX0Mcw0AODDiDnMWYo8zgi1jB2DVMF8HwwTANzARBYMKwK0xlAbD3pzBjTSWTCDzGBTfXjyljAKwhSBpKkjCJwyqLD0rS3KX5lShpB4KlUoXGOGYYCZ/wERg6EYcAo2ounCrEXeT5Yg0h3CQNHJrcFRJKULqFr2qR5KJ9EhGXWizJewGAJ0g04AOmguX6BCqMSfzCHbMosSoGqSRaQCoRdlySYktyqaNP8KkFQUmrMS4ymR5ErJNoEWCHSSaEHRGi6piCixY2AgoTOuKhlVp4FQ+BIia8Njy5VDIgX8LRkIIckOArkGQHRJQC6ok4hA1JrCNICeEgREQwoRisPBQKQKZKKl0xwzEEcQHFNYQhLTrLJB2eoC1yo4E2AcsZRpQVGWCJQl22BI9p8kDDODIMHgQgtKpC4WGJintMs1RgkCIhUzBJZIQAgpBBUgBAKuTOMgeTrLLmEAaZiChdsWQQyL8DASiAMDGjCEkUSQUDoVGxGeTBCSYAITRIhhotvgCYZIYQQnYzyyqRgA2UpYBgk1THoQHApsUCNJoFFhUwzyjGOUChsEDGEKg8yTqTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqjBECMMFIHgxdQehYVUwWwVTEpTdMXFf82IBujDvAMMBoJ0wEgmjB1DBMESM8y2A0jEtFNMKzGMlixMbQhMD3UNPtFMEjCBxSmHACgISDNszjSsNDKEFgSDRQLYXBtXJh6JgGGILAaIAEMAwDQ9TWAxQiBVURQBAcDipi6X3UBYKLIGNyDxDjISpCB2yltUH2nI/OUrcnugkDilxt1glr7EgKQq5raYrIxkxRhjUClYasKCVBMIjUmU1SyZMmnsCRi3KQClhb0dOR5GBQ4EvSFwGVPq7ShgFGBIAoODoWmAIUzAUMkExds3F1LElgK0lusA1JWUSxQUVtWMoA5IYKXRgGNocoHUxRMTHLqJXAURFIrBGCH8T9MsgChCggKFKyqVMgueokFAizSRaRxCYOgiwwBEThBAau00s3EAr66kti4pFAYY5MWj3HAYAHBIGs3TCLomMChkDAyqUGCock2yzZbkmEFgjLKDFwaUNAoKLKIFy3qlBAqcgKJzhrAgQQuecbIqEUSkxSVQ1eYoq5jTJMQVREySE+4FYIZAJYEIgi0auRq4sy0IDpBU0RJgZZbZsiLHGH//74sTbA/ueEQAPdy0HZsIfge7loB5cYWXuODCAMBYBQ49UAMSFiE+BgsorDvQsWY0gCCIsiJZUDdHpumDyA6YToRBgDAGmIsC+YWAH5liKJmk0imYlov5iAA7GC2DQYU4JZhGg3Ghw6UY84OpjvA1GSJLmNYQmao3GAcdH/p3GXo1GbhdhhFLRMbCZMRawFQqRwIgEAQFBABGBghhg8oiIByUA2JA4FC1GseDkpEEQtmKuHEQLJmCAUA3wjLBLMAUJkMGKWFyFakqaN7F/BcAomjU3GoMkxmAwcqsutS1+kKYnBDYUDC1pQcpFkiE5ubSnRVyytczSVNTKLa6vRcid6ZyQidTHGZpAqZLmQaUUUATTQ0hpOqEr6RXREUktkaCRYTpLoMmDClh12MAaaAgkVCINO9XSSiQZf1gBZxijuuqChmnsbQHOwXrdJ+W6qxIYuaiWEBCgL+ipa3U9gIWCkl3AYAKAIyJAJYF3BZcDDK4HSQcoHFMqSIAQagIIICzY80MggEwWEMY0eVNKI1wzODEyzIDlIrSABwKiYhBYNX4TvgUsSIMRwxBjTiLwhjAMBIDzAPNmV7jIVPxhPWQArUwhAsKYfJpxmBwCCysRBKGMG5QI3TAxTlDxDEVBXRiNA4w2VxEGEspXBBRhzG8Ce6ZhugQ0yiBVM6xQu0IQjMUAALIgWWCHwcidFoMZAUoVATidakxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqIDDSB+MJ8KAw+wkTB4AmMGENIxsyDDR5MHA1sRiaAomB6AkYEAWJhRBWGfSoUYpAehjYgwGBOCUYB4Z5hCgImByRgZ3oR5gPhNmDiCAVQIBIBcwbwdjGAEFDBLDAMAmKAVmtuyDgIhoIEtQkGiEW1TpUGgZJlg7IkNy1wRCzhN8v604ySAtKLGr1alHgSUIBy9T61ngftYVPKRu+pVSIdm5P2vR/GWsoSNglxXuX/K0+2kgkhXyzkmaOBn6jdZ6EBzZGvQI9aVbsLlX0s4lFdNy4GZ8sFGmstljkWVtecMCSOh5j6gS0lOlEYQ3YRiL5h5BtCWkeXdYIFAihBM5Z48O4QCFAJQOEXmQhuegIXsoGiIyxA5nhfZWZiS6XKEBwoubYBvHEBBlslyg6VNgMZRuCiZEsGDrNAUwwGIhAAGACiageBAIZllixgKSMxJEQOJNIMyi1vAqBioY0USCpaewJJMEQITSYDAQTEYKB7QBQAcHLaltQCGTdBpUxgkvWQCCwKMWYEgxeoyIhAgIiY4BMKGKpUoZGQJAamGPQKMER00wxMda4MLCzMxRcKmAugCqcLoShaRTwuJEAgHPQw0Qr/++DE4QI8IhL8L2dZx4LCXxXPaLAzRqRCBLbBCtK8xQMBORAIKFZwgAFQmZep+NQEi8LwCGACsRmwwmCgQYzNRjMImyYsaMwlZltjcGLcFqYJYFBhBBGmHYKuYoQrhjtB/GACFYYBIJpgUg8mAWBYYIRHRrWiwGAsHEYDgNaEQQCsYOID5jygIi4kOCmNdKTRsKgMyRdqCNUwyoAD0Zlquyz5PUVRiwWRQMlLAiGYWKFrFN21pXDQ/LnyyZtO8utFej07TLJcXvfhOqBVoOG2RurU4qnIvkqg0Bz5sDW3Nvyzh955hnUQGwOwrxqcRa8uUmFuyowtWCH+SFZNIHURRX83Jj1ZGeVJINkUdmEMqddJgwBekKhh4G2jW0uEEy1kBqlAkES2ZvL3USWReLWrtHRhdpdCmYKQggEXVkIYPT3EAcLky9KEAyELXmNLLGVmYM0gxIoiJEQ1koYhEiJCdAQ5CgSGFoV7Co5YczhEaOOKYMcNJAcjAIB2QqdGkZhCbiGGFmGKGBHgZAABgUNApmbRGBkZjBJgRJVOpmm3TAJEyEORFQKHBgYiAUUsqY0AbhGFQMGGyFGDJGFOCM+YBQFYZjFacBmgxMgNIWMWkNkcMAMKgUqDg5it80hBM0SHBIky4EwCEDJkNzKETAlQVLCxYHVTmHTFiUEYJlmuXhdQIYRlzRtwZjGwCnGdOmLDqUt5nUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTBgDfMVADAIBjKANzAcCFMAETg0zQcTGkDrNFhHMAwAUEMhjJMpSmNWCdMuwrKBkMZBTMGgVZMePh0Yli8YVjGYAg+AgAMKTLNSALBqMMBggeCmBKHJlYRCVzCwSIfQLiCYmgEZGl6pcIj6YIGHPvKF7MzUXMSKHgTO2suoOBwYIno43KeR8FQqxmISp/lLi4rDnnWi0vSlqti6pY0NS5BCv5JtV6a7WmdQVFHBX+pTOJ8uc0xp0uTjZXTM2TxHgChcMOamw9zTJlQFIYuui2h3EgJgwimaEBUAVxISmMx0ODr1DjSsaCMzAoHEGcongYOYMoPHQ4+OBlxjxBOkMXorKrQGFSZEGMiGLIGBLhA4xptLRxAcsCEYIEAlCRMAclFk6BjhgQsnoZMcWnMYDMUVT3JEhhAwjLAJ2kaXAFjSHFuogDN+7xiR4VSmEKCNaJVFDzaFTChjHkRAFNE6KxQABlZ04rQfECVQSFmrCmhQBkdBw1AU4BMlplC4AAhJ0b4cY0KYy6IEICGAIyLJh1SFCZDJNchJIZckEjjFkiJuW1OnYNegABA4A8xQ8xbQ16UWamIDh1wAODUojWGjBljJITUxQ4qZgGZ1QSr/++LE5gA9VhL0D3dHR4dCHuHd6ZBmSGSbmCBEw4ygo4yAGTwNBMITHiBmgZs1hlCqw1ToAgB/gDjrMrCgMpibMgSBMQwrMTYZNCF4NihlM+gIGQPEYiGDRYmO/JmbYgBh9mBj4oEmQCJnP8cqfBQLOTDggzWBHkk8IaOiSVgMSIEQMwYw0R6WQC6LJW5CgQOBOgsZDULAkQYJVicxN5UywIUOPepk6LyUQgECRFTmGmpx9pgiCJBrQgqYVjLpq2O0zuMS9qjU2lTD1hYC/KdCzlntUm0zlcQG3y9WsOvdfZrSHBmixYIRubdzmKCgFzUbnLWM/qe0qn2+S9ajEFfQEzZRYeEtKHACIoWBMxZ4WBo6PJgCDYWGIcC2qY4XGiMCXaIAKbYCAtqVA4QReFJEiKAQUDQAGXrDgUCUA01iEUZkUIBKyjClFXmgJAkTF1AgwkFhJgSAJHEIJIlAKaoCBRoQfNODM6UM8QDhBkxxpxRhFoUFCMOZcOQlGEgxg6SLZswRhCYKLDAEzAoyc0tQiaZAODk4JXgweYtOAD5iEJg4DLiAaBj5gyJMoNsMMQBMfBNSGFnZhAKAk0oAEhTVIwGSMygMkhNoaN6ZNgvMUDNIAEBU0pA2JUdJCRMwjIDFAAPJRBmRpoEIBRChkgfqAGaDDsAAnkAhkQzMzqGRQuCEBozQMCDR4onmHQmROBj4UEpIwOpMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqjHNhTz4VTOwwTYYwDKIYTTI8j07mzEgXTJ4PSIDzBYYjFkCTsyGA8szHoJzBUDgcKBg+DphAMhxQKxhKE4sQzLwcCoWMgWGQVABSht0o0XjA8Ag4I2tSSMKyo7K+aO5EzDTJhKwIJgeClVmmETA9knhZnaNYJQJvHUkzWlDk8IOkEFMGhsDCoOqqspd7sTmHSVsijlr7Zy58ZghjSunXlMhfBrTKYLhTRYLWkWyQFgQFUj7JpLTf5DthGlVWSL0d9SBgkhYF2wUAyAqkI/AVocCT3EI4jHEhC+Zihp9C4JbNKmWJnJXAaousHEiA8aAXUj4xU0FgvAFERqsyDjOEMEZJktQF3Qc4DQQFYggQrJvTDSEcRmolMZrhm++ZwYiUOU5m4MNiRILFzAAgFIFmxwiRrzoKomYikgEyhM5w4xKQ0RJc4RIAygzYQhShU+FaJAdMg6HCZiAZl5RpGBFcCzEwS42XEyIMyEML0jMtANIBXcz6oz7kmkGVBGFQjy8DPjEozVKjLLgQlEB0QEjoPQdkNbuMiuNTROUtA3E1UgyBo3TEGqjGDjI1BVaZYCZZsJIgsHFv5RPHDx1kIBGGADArYaUgCiZohg0rP0n//vixOaD/L4S8A7nV8edwl3B7ujgOeyMcVEzRrExo7RhsB3ywoAMGQCAreODRGRURUYzAuJgoDDmHUGuGDimCsCKaCJERiZBuGOgdgICTAIDjEIKDoHGDH4vDHANjCAAzB8EgqG5giaQXH0weFcxDBl8AsbNWRH9REAYSjY4ylBVCGRBOzMqYzAQATuS3ai2RWVNROVg72+ztYxqRBiSKmsedi+XVUWTgaA7aEVIv1XsH7dWHRwIpc09StlNRtIgtFvWSrre+H0x1MW/Uvgh9JSypxX6ZMt2BmJMrwWBTqn0skpowmmyqKIqIAkKiqISoropsRlalBe1irGzHBGElmTAgBwaFEKdIkTHQ6bqJphwAoBMSGCoYvYSBhgCgIMcIMIRHRoOQDQcqBhEDCGMrHSLcSEqquiuXodgWPAEQvYUCgVMaFKBSQKLmKZBVGYcs/ErAIIFBDUnkKgUsFU4OjhyAWHgkQrEY1YFDxjgAMAjx0zA0xb8ApFXGHOGQDmyJmdVAp+VTZygJnQRoi4JLq9LWGkEGg2HCWmonhxIAGghOBWpI3AhlHQ0po85ExK8yTUeCmLYgRQWBIduOmHNOXNYbMq3TEMyxCwExqQx7Q5ysZLHUiGZuBtg2pYbpmSOmWxnEZgsYBao8kH5YcvMdBM6UKhYGnwMvM6TcUy1oKSzuTjMpSxxM6SNc5MDeH3RAvHmLbcqTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo3dGwwVH00TMswmNoWJA05NoyCJM2iIEwNCYAAeYJhQYMAyZwS2aLA6IRKFh0L2opAkdDMMNjCUEhEJxEEyGRhwCIECdzuII3kiBMCaTMsfdxYisMhPrOyypz2VIlprPvAsUWHAwrbMYToxg9mREAhZJHmf+Hk51FWPMLdJzQuC4sEQal9MQGgbJ8HxT4e9tr9ApsXcX8opOOm+6yHxfZU6tqQiFLAkk1HB49AIJISlOYxCEXYeTFdpM5chiCqTR4HRTOJUWHCxwBVYqkmGUk6gqEpB14RiUjK2ocCqkUcNKL0mEdUNNZBoKqN4mG2MBBjIIjUAsjXlCAYUzY4xwsmYTadBorBig06Z4BZJCafYwOYMsxS4zYF7nqCMxphGUKAlab8oTHzMZDKnjVtk3BkwEYRp4OsDIgTCnVMjWHoENMMQFGKOmlLo6ovmRCmIpgYCs80Y0EmgiWO1QVrBioMLAA8bewXTDxRgwxrz5rCYFMhrULGzljxSkd5mIywFOHUUmfDDWUXRDzYwdE4gYyFI3rUDTjAogdEOuYaEZpeFSZnlZlCJCFAg0wIAQGSqP/74sTXg3s2EuwO51fHV8Jdidzq+FDKZmEIcHO+fOVxM7DMkiMaoOpEPlrNcSOIgMYLPUFAoYyRUwgBCQldO5DIYeIiZ9jMacncZrFGZLjgZJHScnA6DRgMIQiMJwJLVqFmE4PA4pQMIQXBcAACOAgYYkKZzh8IwfEgIIgHdswjEoybBxNB/lNY4v6opxNy+CZOKhrGToiLkp8OqRDIqLCtLcqRITgcG0plktfcdGLhxpTp2n2cdSiVpooUsSlSZkPsVbC3Z3IfZopRErC6Zc5D/UjNo44c1FlfrddJ/WaNITInBIFxFUA4J7lkr9e1hrA3BZiouOENfh0ZQUcT4QlISVfgI0wAHVXmEYJzW0hh4ZZ7/R4GAFzyqKqNfBIcASy549ahe8ptPgYRdzamYUPAiFoSZCoadxE6I2gC6gPDiAiYzgATWmuZYC8DAHNtQiEN98KoFt1HzTjTJBxEqWgLIBZOCVhgzzWRhqX4A0YbHhB8UIA5eOBjLoDUlDEBCJia4CZ0WBjptyxsjJCaEJAmdGBXGxTGZZmASjSUwrMZAAoAa8sZNyW1MwNDpYMZF0TXQzBlhgCVvzAHAsCPQzABoLBG5DSExMYwtA2y4yho0ZRKU16YdLBdQG4hcOAthziJhYxnwoOPjJ0W5mEFGEAURqUBmDZgGw2BOIJMgKPSSAVMvWZRMec4bpmZgybQYYAsjk07GkxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqhAOEnQyMfTZbKMito2ONDdsCPxqYzyzk5QMCwoJGXGg4CeOKRgobFY3EQHAwcMXQMzADAwIGCxYrtjoqDzCpDKgBWe/rmJ8kADsuLDrptjpWBKO4VWYLDriWiul2ok8cMS3rwu1DZAOXcW+z9DknU3JDJfs2ttrbKl1wEklLXFjG3JZhAEZjrhrZeGBWz0rrKeaitV1YBUYgG66kvgBc6mSEtx2xCIUgCQfW66EQRtVap9xC6iAllzPlrAY4vejq1IqmBVZdDjFgVgpYIL/o7qGmUuZxL0EgSaYtUuwHHIDAS2ZJBYdMhdcsyUoFBArAL5ggsI3HlQdyXIOcsoiMg8cxAJwkwY5wJNAApEmboQcEZNAY+FA5UFrRMCCMcRJnyCAS8miEgxWZ4gaesOozMIjFzjHlTJlTEHCJSDWBoCZ0BKAsHTTLJFNBlaCn4iCGjRg5GChACTmkCu2ZBeZMAZtYZWMowCiggAAg8YAmd1iCkpvR4jBpznGhkUUwrlpZl0xmSRkjBgEQY1MJWDZZsnzqmXnGfghVKdgWZhGEbRIwbdUcl+bFgadAbVwfFgdhMbVAcGEY+kaXWAUYWLCMEf/++LE4AN6lhLoLmdXx65CXIHdbzgAuaFcYNoZ0WB3AjZGfLmHEkwl4Om91Gmi6VHCROm/RHmUIfGUSSmohsmmBOGEgVBgWCMMjBMBTHR+zfoSzAwCwEExABZgkEJhEFZlOI4wBQOAZNZZoID8xWCoiBuGVeuopuNAU0t/G5QSmMnA+7zNoyduqbrQX2h6HVanxVhTmYrBs1I0OIiCqcMybo3BTSVsvkkLfpxnwdaKI4xSUSnrjNKflvGAq3xhYScjSi8oUefKC2uvC4zTousGnpSsKZJD8DIZlrGYN2X6xEmIo0oJlyF0AUPUdHCDX2bggaYIMPC2ligqG0OocNZ+g28piwuyoZZKxEWPgYEKExYCKFhwOhCZwaCnSd4NFlBoZMGENkw0mdGWAA18GGyEeZs4ITRJINKjNcYCxoxYgzYgwYlRgwxoCoSBcTdlgxIwYVQOAxoiAhoqFMYUMEDMgqM0NMgPNkbBzkUMGxeEVUs2YCabUWBRrJDVHTJuEB5k9BYJjXAMMGfJhRU/gXJGHDlDoDJzAgTCOQCVCE4iEA42MHKjCwZlQKAQslGKuRn4gYgXp0mADwKKm+FkQwcPM6TiyxqySCg4w07NmJwQJmKBZgRqBgYVZzjiwea4+Ii8hGDbFkwdRNiHjRjUAHBsIgZEgmxIppCckCYSuhYOMxRjCVIypFBAwNWAIGzPBEwMaTigjlVMQU1FMy4xMDBVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUwDrOEPZFI2QgDsI5R4MToA0aHTmxTAxqMDAgweDDCodMYIU14aQaDgYCzCwTCwDKhkMrjoOBygjtPWOCM0MEUMF8JFO0zMDAwrAcWfRry81VG/kT8yugdllKLUQR+bHTGInDqnSDrVV8KDNYYmXpjkTWqw5f0nLjOk/LTa/KkPYwiCXUWNB7uNEa3Mr5ZwxJ9mkxGMp6vq3WGSsIUJnkPFZ2aqEM8cRDRKNVQAiMpStaahmgWqxoRghM2aWKBpymcyq0HNzqt4YEAQiySIjQwJCXsHTTORACIK2GSxEgwcym0A5bpQEQnOsaRZhoIWtNQ5AGYRHrkXecxjcjYlNgAwqRAMDCSxsNoICizzIA4cwQCEBsIwwDlDLGMOsRnmoGqdRUqFmggLKlrjXyXqKAnG6KuGM+YB5uhGsYCHDW/PAQ5BDAjMAoClmvwaWYqKZjJ0nDs5qaGmcoARalAoDfKqFgIRFwcVT0MoaA7I3g8OmiMEZNkbOoIlR0Xhoxxh2iWoMHCzo3i4IRJyGbIAFCY1EEBwAaAwM2607FMTAgIGY84NRjvJTDLDbogExN4rA3kygA45Q0Z//vixNuDec4S3i5nWcekwloB3O7409gM3I4DjzVCRM4bWSCrJuIhpDCqy99Gol1nVREmVYqGNodGMRMmQgQmTpoGJIAGI4OJ5mAoEBUAQwWDGMVDBEAECaqQOAYxBNgztGJLkwBAJtk5zAENjAkHQgCJYXmRGZqYNhwDhGmpW6rKWSuVrsPOTAVPHXZeWnbAtZaKzX6q0LEXZfl0mywJH3adZrK5UiXgROXEu1nUFsRlFqAlhnmgJpLJZU+zrRFlLyr5YMraxhm6grMq6HFEQtizRE5p60DFAa+xFYIqACxT2ruTJRxYUXKSGVsMcZEpzHGT/ATqqyR6FyngKA34VMDiy4BnjF/zJQNU5V4qMHHA0pPNsoWKOBdulJVJSTstFpSzSVplOkSCA5gV9YMGEB2RUaCLQqgcKhlpCRwXON0QyGzIUM2NRIdamEAhmZsLDymxgwisOZaXGBhhj4Ii8YuFMBMJMDQTwy8wMoNTLisyQLV0ZIkjSgXrMIBwIImVtBy8gDp4woTMsQRZFMOLTCgIAhpjpMAicyIbMUB0vUCDfIejBgaYxmlEplSua4emVFJjAqZMYhB6VQMxMQMDJDQyoBARhIEYCJGPjQcRmaK5np8Ajcx4VSUEAiCAwycmDi4wohMBCR45MTDgqAmLApiB+Y4WCTeY8DggZM2UzYF82p9CLkzMmMCRTPhY3eCNQPy4DUsVTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/74sQAA/2KEqQO70lAAAA0gAAABDk79zoZZjr1dDTprzDpQDPMnzTwbTQVIDCxPTJMdTxGcCEhtbkOvZsBwRg52UCdH/GQ/h1bedscmephnI0ZA1mlGBwaIaFAmOnZrw2ZCYGAh5MpMeGCw0vAXqjiDyMqlCr0FUbmdtNiygLCmRsMW+laj0rKzterSnnWK0ZqS7XwnMo1VoXlSGTJWEaC/0if2pVkkKXayF4H7kNV0njeyHq0+5KRyAsOMmLJDo0eEMtWKlU0t1ZAkUFAIqEKoRCWlCoNDbywenSCQw6KEh5jhIqQHj5kiJUIDSYxhMqCSIgGBkJJfYsBS0ACTGKPiosSMw0ARwXLlEg1p4yzEKsAq0MGxNMKNeAMwbGSxhQYGYmTRDBIDMgQVCEBoxBlDZgTgIVlR0ZAsa8UYQ6LIDHilbwQHJjBp0Ri3RlUY1pNSaBBFeo0ENyuN1rMdzNZGOGBA1kWDKkRiStxiNZW0lBCQcyQUwJQKhSgK4ib4YVMiiC6UaqGvOGMSkJYEqAKxK2xuXAjYgLiaFQBRY8hAw0wpIYQgpgaEcIBIcJL3QAZIaZlsFVZnAAQbMAKFoZtk5m5AAVEWIzQ0ZCJZFuUUAMeMQPACMAKjbgzpKzb2BWaaxALajKExokaZaF2BlRoCWGXCm6BnTyDnEnDGaBw11MQU1FMy4xMDBVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUQUdLaXR0ZW4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUZWxlZ3JhbSBNZXNzZW5nZXIAAAAAAAAAAAAAAABOb3RpZmljYXRpb24gU291bmRzIFZvbC4gMQAAAAAyMDIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/w=='
img_jpg = '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'


# endregion


# region db
def sqlite_lower(value_):
    return value_.lower() if value_ else None


def sqlite_upper(value_):
    return value_.upper() if value_ else None


def ignore_case_collation(value1_, value2_):
    if value1_ is None or value2_ is None:
        return 1
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


async def db_select(sql, param=None, db=None):
    retry = 2
    while retry > 0:
        try:
            async with aiosqlite.connect(db, timeout=15) as con:
                await con.execute('PRAGMA foreign_keys=ON;')
                # con.create_collation("NOCASE", ignore_case_collation)
                # con.create_function("LOWER", 1, sqlite_lower)
                # con.create_function("UPPER", 1, sqlite_upper)

                if param:
                    async with con.execute(sql, param) as cur:
                        return await cur.fetchall()
                else:
                    async with con.execute(sql) as cur:
                        return await cur.fetchall()
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))
            await db_change("VACUUM", (), db)
            retry -= 1
    return []


async def db_change(sql, param=None, db=None):
    retry = 2
    while retry > 0:
        try:
            async with aiosqlite.connect(db, timeout=15) as con:
                await con.execute('PRAGMA foreign_keys=ON;')
                async with con.cursor() as cur:
                    if param:
                        await cur.execute(sql, param)
                    else:
                        await cur.execute(sql)

                    await con.commit()
                    return cur.lastrowid
        except Exception as e:
            logger.info(log_ % f"{db}: {str(e)}")
            await asyncio.sleep(round(random.uniform(1, 2), 2))
            await db_change("VACUUM", (), db)
            retry -= 1
    return -1


# async def db_select(sql, param=None, db=None):
#     retry = 2
#     while retry > 0:
#         try:
#             with closing(sqlite3.connect(db, timeout=15)) as con:
#                 con.execute('PRAGMA foreign_keys=ON;')
#                 # con.create_collation("NOCASE", ignore_case_collation)
#                 # con.create_function("LOWER", 1, sqlite_lower)
#                 # con.create_function("UPPER", 1, sqlite_upper)
#                 with closing(con.cursor()) as cur:
#                     if param:
#                         cur.execute(sql, param)
#                     else:
#                         cur.execute(sql)
#
#                     return cur.fetchall()
#         except Exception as e:
#             logger.info(log_ % str(e))
#             await asyncio.sleep(round(random.uniform(1, 2), 2))
#             retry -= 1
#     return []


# async def db_change(sql, param=None, db=None):
#     retry = 2
#     while retry > 0:
#         try:
#             with closing(sqlite3.connect(db, timeout=15)) as con:
#                 con.execute('PRAGMA foreign_keys=ON;')
#                 with closing(con.cursor()) as cur:
#                     if param:
#                         cur.execute(sql, param)
#                     else:
#                         cur.execute(sql)
#
#                     con.commit()
#                     return cur.lastrowid
#         except Exception as e:
#             logger.info(log_ % str(e))
#             await asyncio.sleep(round(random.uniform(1, 2), 2))
#             retry -= 1
#     return -1


async def db_bot_create(db):
    con = sqlite3.connect(db, timeout=10)
    try:
        cur = con.cursor()

        # TRG
        cur.execute('''CREATE TABLE IF NOT EXISTS TRG ( 
            TRG_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            TRG_VID         VARCHAR     UNIQUE NOT NULL,
            TRG_TYPE        VARCHAR,
            TRG_CONTENT     VARCHAR,

            TRG_RIGHTID     VARCHAR,
            TRG_RIGHTTYPE   VARCHAR,
            TRG_LEFTID      VARCHAR,
            TRG_LEFTTYPE    VARCHAR
        )''')

        # ACT
        cur.execute('''CREATE TABLE IF NOT EXISTS ACT ( 
            ACT_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            ACT_VID         VARCHAR     UNIQUE NOT NULL,
            ACT_TYPE        VARCHAR,
            ACT_CONTENT     VARCHAR,

            ACT_NEXTID      VARCHAR,
            ACT_NEXTTYPE    VARCHAR
        )''')

        # MSG
        cur.execute('''CREATE TABLE IF NOT EXISTS MSG ( 
            MSG_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            MSG_VID         VARCHAR     UNIQUE NOT NULL,
            MSG_TYPE        VARCHAR,
            MSG_TEXT        VARCHAR,
            MSG_MEDIA       VARCHAR,
            MSG_BUTTONS     VARCHAR,
            
            MSG_CHKBOX      VARCHAR,
            MSG_TEXTF       VARCHAR,  
            MSG_BUTTONSF    VARCHAR,
            MSG_LC          VARCHAR,
            MSG_TRANSLATED  INTEGER     DEFAULT 0,

            MSG_NEXTID      VARCHAR,
            MSG_NEXTTYPE    VARCHAR
        )''')

        # VIEW
        cur.execute('''CREATE TABLE IF NOT EXISTS VIEW ( 
            VIEW_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            ENT_VID         VARCHAR     NOT NULL,
            ENT_TYPE        VARCHAR     NOT NULL,
            CHAT_TID        BIGINT      NOT NULL,
            UNIQUE (ENT_VID, ENT_TYPE, CHAT_TID)
        )''')

        # LANG
        cur.execute('''CREATE TABLE IF NOT EXISTS LANG ( 
            LANG_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            MSG_ID          INTEGER,
            MSG_LC          VARCHAR,
            
            MSG_TEXT        VARCHAR,
            MSG_BUTTONS     VARCHAR,
            MSG_TEXTF       VARCHAR,
            MSG_BUTTONSF    VARCHAR,
            UNIQUE (MSG_ID, MSG_LC)
        )''')

        # POST
        cur.execute('''CREATE TABLE IF NOT EXISTS POST ( 
            POST_ID            INTEGER      PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            POST_CHATTID       BIGINT       NOT NULL,
            POST_USERTID       BIGINT       NOT NULL,
            POST_TARGET        VARCHAR,
            POST_TYPE          VARCHAR,
            POST_TEXT          VARCHAR,
            POST_TEXTF         VARCHAR,
            POST_MSGID         VARCHAR,
            POST_TELESCOPE     VARCHAR,
            
            POST_BUTTON        VARCHAR,
            POST_BUTTONF       VARCHAR,
            POST_BLOG          VARCHAR,
            POST_WEB           VARCHAR,
            POST_TZ            VARCHAR,
            POST_DT            VARCHAR,
            POST_TR            VARCHAR,
            POST_STATUS        BOOLEAN     DEFAULT 0,
            
            POST_ISBUTTON      BOOLEAN     DEFAULT 0,
            POST_ISDYNAMIC     BOOLEAN     DEFAULT 0,
            POST_ISSOUND       BOOLEAN     DEFAULT 1,
            POST_ISSILENCE     BOOLEAN     DEFAULT 0,
            POST_ISPIN         BOOLEAN     DEFAULT 0,
            POST_ISPREVIEW     BOOLEAN     DEFAULT 0,
            POST_ISSPOILER     BOOLEAN     DEFAULT 0,
            POST_ISGALLERY     BOOLEAN     DEFAULT 0,
            POST_ISFORMAT      BOOLEAN     DEFAULT 0,
            POST_ISTAG         BOOLEAN     DEFAULT 0,
            POST_ISREACTION    BOOLEAN     DEFAULT 0,
            POST_ISPODCAST     BOOLEAN     DEFAULT 0,
            POST_ISWINDOW      BOOLEAN     DEFAULT 0,
            
            POST_LNK           VARCHAR,
            POST_FILENAME      VARCHAR,
            POST_FID           VARCHAR,
            POST_FIDNOTE       VARCHAR,
            POSTB_FID          VARCHAR,
            POSTB_FIDNOTE      VARCHAR
        )''')

        # PUSH
        cur.execute('''CREATE TABLE IF NOT EXISTS PUSH ( 
            PUSH_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            CHAT_TID        BIGINT      NOT NULL,
            CHAT_FULLNAME   VARCHAR,
            CHAT_USERNAME   VARCHAR,
            CHAT_ISPREMIUM  BOOLEAN,
            CHAT_LC         VARCHAR,
            POST_ID         INTEGER     NOT NULL,
            BUTTON_ID       INTEGER     NOT NULL,
            UNIQUE (CHAT_TID, POST_ID, BUTTON_ID)
        )''')

        # USER
        cur.execute(f'''CREATE TABLE IF NOT EXISTS USER ( 
            USER_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            USER_TID        BIGINT      UNIQUE
                                        NOT NULL,
            USER_USERNAME   VARCHAR,
            USER_FULLNAME   VARCHAR,

            USER_VARS       VARCHAR     DEFAULT '{USER_VARS_}',
            USER_LSTS       VARCHAR     DEFAULT '{USER_LSTS_}'
        )''')

        # USERBAN
        cur.execute('''CREATE TABLE IF NOT EXISTS USERBAN ( 
            USERBAN_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            USERBAN_TID         BIGINT      UNIQUE,
            USERBAN_USERNAME    VARCHAR     UNIQUE,
            USERBAN_FULLNAME    VARCHAR,
            USERBAN_BAN         VARCHAR, 
            USERBAN_DT          VARCHAR
        )''')

        # NOTICE
        cur.execute('''CREATE TABLE IF NOT EXISTS NOTICE ( 
            NOTICE_ID           INTEGER     PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            NOTICE_TID          BIGINT,
            NOTICE_TXT          VARCHAR,
            UNIQUE (NOTICE_TID, NOTICE_TXT)
        )''')

        con.commit()
        cur.close()
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        con.close()


async def db_usr_create(db):
    con = sqlite3.connect(db, timeout=10)
    try:
        cur = con.cursor()

        # TRG
        cur.execute('''CREATE TABLE IF NOT EXISTS TRG ( 
            TRG_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            TRG_VID         VARCHAR     UNIQUE NOT NULL,
            TRG_TYPE        VARCHAR,
            TRG_CONTENT     VARCHAR,

            TRG_RIGHTID     VARCHAR,
            TRG_RIGHTTYPE   VARCHAR,
            TRG_LEFTID      VARCHAR,
            TRG_LEFTTYPE    VARCHAR
        )''')

        # ACT
        cur.execute('''CREATE TABLE IF NOT EXISTS ACT ( 
            ACT_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            ACT_VID         VARCHAR     UNIQUE NOT NULL,
            ACT_TYPE        VARCHAR,
            ACT_CONTENT     VARCHAR,

            ACT_NEXTID      VARCHAR,
            ACT_NEXTTYPE    VARCHAR
        )''')

        # MSG
        cur.execute('''CREATE TABLE IF NOT EXISTS MSG ( 
            MSG_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            MSG_VID         VARCHAR     UNIQUE NOT NULL,
            MSG_TYPE        VARCHAR,
            MSG_TEXT        VARCHAR,
            MSG_MEDIA       VARCHAR,
            MSG_BUTTONS     VARCHAR,

            MSG_CHKBOX      VARCHAR,
            MSG_TEXTF       VARCHAR,  
            MSG_BUTTONSF    VARCHAR,
            MSG_LC          VARCHAR,
            MSG_TRANSLATED  INTEGER     DEFAULT 0,

            MSG_NEXTID      VARCHAR,
            MSG_NEXTTYPE    VARCHAR
        )''')

        # VIEW
        cur.execute('''CREATE TABLE IF NOT EXISTS VIEW ( 
            VIEW_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            ENT_VID         VARCHAR     NOT NULL,
            ENT_TYPE        VARCHAR     NOT NULL,
            CHAT_TID        BIGINT      NOT NULL,
            UNIQUE (ENT_VID, ENT_TYPE, CHAT_TID)
        )''')

        # LANG
        cur.execute('''CREATE TABLE IF NOT EXISTS LANG ( 
            LANG_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            MSG_ID          INTEGER,
            MSG_LC          VARCHAR,

            MSG_TEXT        VARCHAR,
            MSG_BUTTONS     VARCHAR,
            MSG_TEXTF       VARCHAR,
            MSG_BUTTONSF    VARCHAR,
            UNIQUE (MSG_ID, MSG_LC)
        )''')

        # POST
        cur.execute('''CREATE TABLE IF NOT EXISTS POST ( 
            POST_ID            INTEGER      PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            POST_CHATTID       BIGINT       NOT NULL,
            POST_USERTID       BIGINT       NOT NULL,
            POST_TARGET        VARCHAR,
            POST_TYPE          VARCHAR,
            POST_TEXT          VARCHAR,
            POST_TEXTF         VARCHAR,
            POST_MSGID         VARCHAR,
            POST_TELESCOPE     VARCHAR,

            POST_BUTTON        VARCHAR,
            POST_BUTTONF       VARCHAR,
            POST_BLOG          VARCHAR,
            POST_WEB           VARCHAR,
            POST_TZ            VARCHAR,
            POST_DT            VARCHAR,
            POST_TR            VARCHAR,
            POST_STATUS        BOOLEAN     DEFAULT 0,

            POST_ISBUTTON      BOOLEAN     DEFAULT 0,
            POST_ISDYNAMIC     BOOLEAN     DEFAULT 0,
            POST_ISSOUND       BOOLEAN     DEFAULT 1,
            POST_ISSILENCE     BOOLEAN     DEFAULT 0,
            POST_ISPIN         BOOLEAN     DEFAULT 0,
            POST_ISPREVIEW     BOOLEAN     DEFAULT 0,
            POST_ISSPOILER     BOOLEAN     DEFAULT 0,
            POST_ISGALLERY     BOOLEAN     DEFAULT 0,
            POST_ISFORMAT      BOOLEAN     DEFAULT 0,
            POST_ISTAG         BOOLEAN     DEFAULT 0,
            POST_ISVIA         BOOLEAN     DEFAULT 0,
            POST_ISREACTION    BOOLEAN     DEFAULT 0,
            POST_ISPODCAST     BOOLEAN     DEFAULT 0,
            POST_ISWINDOW      BOOLEAN     DEFAULT 0,
            
            POST_REMOJI        VARCHAR,
            POST_TIMER         VARCHAR,
            POST_THEME         VARCHAR,
            POST_WALL          VARCHAR,
            POST_ISDESTRUCT    BOOLEAN     DEFAULT 0,

            POST_LNK           VARCHAR,
            POST_FILENAME      VARCHAR,
            POST_FID           VARCHAR,
            POST_FIDNOTE       VARCHAR,
            POSTB_FID          VARCHAR,
            POSTB_FIDNOTE      VARCHAR
        )''')

        # PUSH
        cur.execute('''CREATE TABLE IF NOT EXISTS PUSH ( 
            PUSH_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            CHAT_TID        BIGINT      NOT NULL,
            CHAT_FULLNAME   VARCHAR,
            CHAT_USERNAME   VARCHAR,
            CHAT_ISPREMIUM  BOOLEAN,
            CHAT_LC         VARCHAR,
            POST_ID         INTEGER     NOT NULL,
            BUTTON_ID       INTEGER     NOT NULL,
            UNIQUE (CHAT_TID, POST_ID, BUTTON_ID)
        )''')

        # GEO
        cur.execute('''CREATE TABLE IF NOT EXISTS GEO ( 
            GEO_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            USER_TID        BIGINT      UNIQUE
                                        NOT NULL,
            USER_FULLNAME   VARCHAR,
            USER_USERNAME   VARCHAR,
            USER_ISPREMIUM  INTEGER,
            USER_PHOTO      VARCHAR,

            GEO_ISPRIORITY  INTEGER     DEFAULT 0
        )''')

        # JOIN
        cur.execute('''CREATE TABLE IF NOT EXISTS INVITE ( 
            INVITE_ID           INTEGER     PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            INVITE_CHATTID      BIGINT      NOT NULL,
            INVITE_USERTID      BIGINT      NOT NULL,
            INVITE_MSGID        INTEGER,
            INVITE_TYPE         VARCHAR,
            INVITE_DATETIME     DATETIME,
            UNIQUE (INVITE_CHATTID, INVITE_USERTID)
        )''')

        # USER
        cur.execute(f'''CREATE TABLE IF NOT EXISTS USER ( 
            USER_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
            USER_TID        BIGINT      UNIQUE
                                        NOT NULL,
            USER_USERNAME   VARCHAR,
            USER_FULLNAME   VARCHAR,

            USER_VARS       VARCHAR     DEFAULT '{USER_VARS_}',
            USER_LSTS       VARCHAR     DEFAULT '{USER_LSTS_}'
        )''')

        # USERB
        cur.execute(f'''CREATE TABLE IF NOT EXISTS USERB ( 
            USERB_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                         UNIQUE
                                         NOT NULL,
            USERB_TID        BIGINT      UNIQUE
                                         NOT NULL,
            USERB_USERNAME   VARCHAR,
            USERB_FULLNAME   VARCHAR,

            USERB_VARS       VARCHAR     DEFAULT '{USER_VARS_}',
            USERB_LSTS       VARCHAR     DEFAULT '{USER_LSTS_}'
        )''')

        # USERG
        cur.execute(f'''CREATE TABLE IF NOT EXISTS USERG ( 
            USERG_ID            INTEGER     PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            USERG_TID           BIGINT      UNIQUE
                                            NOT NULL,
            USERG_USERNAME      VARCHAR,
            USERG_FULLNAME      VARCHAR,
            USERG_PHONE         VARCHAR,
            USERG_PHOTO         VARCHAR,
            USERG_PHOTOCNT      INTEGER     DEFAULT 0,
            USERG_ISPREMIUM     BOOLEAN     DEFAULT 0,
            
            USERG_RANK          INTEGER     DEFAULT 0,
            USERG_COORDINATES   VARCHAR
        )''')

        # USERBAN
        cur.execute('''CREATE TABLE IF NOT EXISTS USERBAN ( 
            USERBAN_ID          INTEGER     PRIMARY KEY AUTOINCREMENT
                                            UNIQUE
                                            NOT NULL,
            USERBAN_TID         BIGINT      UNIQUE,
            USERBAN_USERNAME    VARCHAR     UNIQUE,
            USERBAN_FULLNAME    VARCHAR,
            USERBAN_BAN         VARCHAR, 
            USERBAN_DT          VARCHAR
        )''')

        con.commit()
        cur.close()
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        con.close()


async def db_bot_create_extra(db):
    con = sqlite3.connect(db, timeout=10)
    con.execute('PRAGMA foreign_keys=ON;')
    cur = con.cursor()

    # USER
    cur.execute('''CREATE TABLE IF NOT EXISTS USER ( 
        USER_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
        USER_TID        BIGINT      UNIQUE
                                    NOT NULL,
        USER_USERNAME   VARCHAR,
        USER_FULLNAME   VARCHAR,
        USER_ISPREMIUM  INTEGER,

        USER_UTM        VARCHAR,
        USER_PAY        VARCHAR,
        USER_GEO        VARCHAR,
        USER_PHONE      VARCHAR,
        USER_PROMO      VARCHAR,
        USER_EMAIL      VARCHAR,
        USER_TEXT       VARCHAR,

        USER_IP         VARCHAR,
        USER_PLATFORM   VARCHAR,
        USER_DEVICE     VARCHAR,

        USER_TESTSESSIONTID     BIGINT,
        USER_TESTBOTTID         BIGINT,
        USER_TESTBOTUSERNAME    VARCHAR,
        USER_TESTBOTTOKEN       VARCHAR,

        USER_DTPAID     VARCHAR, 
        USER_ISPAID     INTEGER     DEFAULT 0,

        USER_DT         VARCHAR,
        USER_TZ         VARCHAR,
        USER_LZ         VARCHAR,
        USER_LC         VARCHAR
    )''')

    # FILE
    cur.execute('''CREATE TABLE IF NOT EXISTS FILE (
        FILE_ID             INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
        FILE_FILEID         VARCHAR     NOT NULL,
        FILE_FILENAME       VARCHAR,
        UNIQUE (FILE_FILEID, FILE_FILENAME)
    );''')

    # LIKE
    cur.execute('''CREATE TABLE IF NOT EXISTS LIKE ( 
        LIKE_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
        USER_ID         INTEGER     NOT NULL,
        POST_ID         INTEGER     NOT NULL
        )''')

    # OFFER
    cur.execute('''CREATE TABLE IF NOT EXISTS OFFER ( 
        OFFER_ID            INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
        OFFER_USERTID       BIGINT      NOT NULL,
        OFFER_TEXT          VARCHAR,
        OFFER_MEDIATYPE     VARCHAR,
        OFFER_FILEID        VARCHAR,
        OFFER_FILEIDNOTE    VARCHAR,
        OFFER_FILENAME      VARCHAR,

        OFFER_TGPHLINK      VARCHAR,
        OFFER_ISTGPH        BOOLEAN     DEFAULT 0,
        OFFER_BUTTON        VARCHAR,
        OFFER_ISBUTTON      BOOLEAN     DEFAULT 0,
        OFFER_ISSPOILER     BOOLEAN     DEFAULT 0,
        OFFER_ISPIN         BOOLEAN     DEFAULT 0,
        OFFER_ISSILENCE     BOOLEAN     DEFAULT 0,
        OFFER_ISGALLERY     BOOLEAN     DEFAULT 0,

        OFFER_STATUS        BOOLEAN     DEFAULT 0,
        OFFER_TZ            VARCHAR,
        OFFER_DT            VARCHAR
    );''')

    # BOT
    cur.execute(f"""CREATE TABLE IF NOT EXISTS BOT ( 
        BOT_ID              INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
        BOT_TID             BIGINT      UNIQUE
                                        NOT NULL,
        OWNER_TID           BIGINT,
        SESSION_TID         BIGINT,
        BOT_STATUS          VARCHAR,
        BOT_PID             VARCHAR,
        BOT_USERNAME        VARCHAR,
        BOT_FIRSTNAME       VARCHAR,

        BOT_TOKEN           VARCHAR     UNIQUE,
        BOT_TOKENPAY        VARCHAR,
        BOT_ISPAID          INTEGER     DEFAULT 0,
        BOT_TOKENTGPH       VARCHAR,
        BOT_PAGETGPH        VARCHAR,
        BOT_JSONTGPH        VARCHAR,

        BOT_CONFIG          VARCHAR     DEFAULT '{BOT_CONFIG_}',
        BOT_CBAN            VARCHAR     DEFAULT '{BOT_CBAN_}',
        BOT_CNEURO          VARCHAR     DEFAULT '{BOT_CNEURO_}',
        BOT_CINTEGRATION    VARCHAR     DEFAULT '{BOT_CINTEGRATION_}',
        BOT_GOOGLETABLE     VARCHAR,
        BOT_AIRTABLE        VARCHAR,
        BOT_CNOTIFICATION   VARCHAR     DEFAULT '{BOT_CNOTIFICATION_}',
        BOT_CUSER           VARCHAR     DEFAULT '{BOT_CUSER_}',

        BOT_VARS            VARCHAR     DEFAULT '{BOT_VARS_}',
        BOT_LSTS            VARCHAR     DEFAULT '{BOT_LSTS_}',

        BOT_USERCNT         INTEGER     DEFAULT 0,
        BOT_IP              VARCHAR,
        BOT_PORT            INTEGER,
        BOT_ISACTIVE        BOOLEAN     DEFAULT 1,
        BOT_ISTRANSFERED    BOOLEAN     DEFAULT 0
    )""")

    con.commit()
    cur.close()
    con.close()


async def db_usr_create_extra(db):
    con = sqlite3.connect(db, timeout=10)
    con.execute('PRAGMA foreign_keys=ON;')
    cur = con.cursor()

    # USER
    cur.execute('''CREATE TABLE IF NOT EXISTS USER ( 
        USER_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
        USER_TID        BIGINT      UNIQUE
                                    NOT NULL,
        USER_USERNAME   VARCHAR,
        USER_FULLNAME   VARCHAR,
        USER_ISPREMIUM  INTEGER,

        USER_UTM        VARCHAR,
        USER_PAY        VARCHAR,
        USER_GEO        VARCHAR,
        USER_PHONE      VARCHAR,
        USER_PROMO      VARCHAR,
        USER_EMAIL      VARCHAR,
        USER_TEXT       VARCHAR,
 
        USER_IP         VARCHAR,
        USER_PLATFORM   VARCHAR,
        USER_DEVICE     VARCHAR,

        USER_DTPAID     VARCHAR, 
        USER_ISPAID     INTEGER     DEFAULT 0,

        USER_DT         VARCHAR,
        USER_TZ         VARCHAR,
        USER_LZ         VARCHAR,
        USER_LC         VARCHAR
    )''')

    # FILE
    cur.execute('''CREATE TABLE IF NOT EXISTS FILE (
        FILE_ID             INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
        FILE_FILEID         VARCHAR     NOT NULL,
        FILE_FILENAME       VARCHAR,
        UNIQUE (FILE_FILEID, FILE_FILENAME)
    )''')

    # LIKE
    cur.execute('''CREATE TABLE IF NOT EXISTS LIKE ( 
        LIKE_ID         INTEGER     PRIMARY KEY AUTOINCREMENT
                                    UNIQUE
                                    NOT NULL,
        USER_ID         INTEGER     NOT NULL,
        POST_ID         INTEGER     NOT NULL
        )''')

    # OFFER
    cur.execute('''CREATE TABLE IF NOT EXISTS OFFER ( 
        OFFER_ID            INTEGER     PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
        OFFER_USERTID       BIGINT      NOT NULL,
        OFFER_TEXT          VARCHAR,
        OFFER_MEDIATYPE     VARCHAR,
        OFFER_FILEID        VARCHAR,
        OFFER_FILEIDNOTE    VARCHAR,
        OFFER_FILENAME      VARCHAR,

        OFFER_TGPHLINK      VARCHAR,
        OFFER_ISTGPH        BOOLEAN     DEFAULT 0,
        OFFER_BUTTON        VARCHAR,
        OFFER_ISBUTTON      BOOLEAN     DEFAULT 0,
        OFFER_ISSPOILER     BOOLEAN     DEFAULT 0,
        OFFER_ISPIN         BOOLEAN     DEFAULT 0,
        OFFER_ISSILENCE     BOOLEAN     DEFAULT 0,
        OFFER_ISGALLERY     BOOLEAN     DEFAULT 0,

        OFFER_STATUS        BOOLEAN     DEFAULT 0,
        OFFER_TZ            VARCHAR,
        OFFER_DT            VARCHAR
    )''')

    # UB
    cur.execute(f"""CREATE TABLE IF NOT EXISTS UB ( 
        UB_ID              INTEGER     PRIMARY KEY AUTOINCREMENT
                                       UNIQUE
                                       NOT NULL,
        UB_TID             BIGINT      UNIQUE
                                       NOT NULL,
        OWNER_TID          BIGINT,

        UB_APIID           VARCHAR,
        UB_APIHASH         VARCHAR,
        UB_PATH            VARCHAR,
        UB_CLOUD           VARCHAR,
        UB_PHONE           VARCHAR,
        UB_USERNAME        VARCHAR,
        UB_FIRSTNAME       VARCHAR,
        UB_LASTNAME        VARCHAR,
        UB_BIO             VARCHAR,
        UB_ISPREMIUM       BOOLEAN     DEFAULT 0,
        UB_ISMUTUAL        BOOLEAN     DEFAULT 0,
        UB_PHOTO           VARCHAR,
        UB_PHOTOHASH       VARCHAR,
        UB_ADDLIST         VARCHAR,

        UB_STATUS          VARCHAR,
        UB_PID             VARCHAR,
        UB_CMD             VARCHAR,
        UB_RES             VARCHAR,
        UB_UPDATE          VARCHAR,
        UB_INFO            VARCHAR,
        UB_STAT            VARCHAR,
        UB_WAIT            VARCHAR,
        UB_SPAMBOT         VARCHAR,
        UB_LOGIN           VARCHAR,
        UB_AUTODEL         INTEGER     DEFAULT 0,
        UB_DELAY           INTEGER     DEFAULT 0,
        UB_SPOILER         VARCHAR,
        UB_VOTE            VARCHAR,
        UB_FIRSTMSG        VARCHAR,
        UB_SPAMBOTCNT      INTEGER     DEFAULT 0,
        UB_DELTATIME       VARCHAR,
        UB_USERCNT         INTEGER     DEFAULT 0,

        UB_CHANNELTID      BIGINT,
        UB_CHANNELLINK     VARCHAR,
        UB_BOTUSERNAME     VARCHAR,
        UB_BOTTOKEN        VARCHAR,
        UB_BOTQUERY        VARCHAR,
        UB_BOTMARKUP       VARCHAR,
        UB_BOTISPAID       VARCHAR,
        UB_TOKENTGPH       VARCHAR,
        UB_JSONTGPH        VARCHAR,
        UB_PAGETGPH        VARCHAR,

        UB_CONFIG          VARCHAR     DEFAULT '{UB_CONFIG_}',
        UB_CFORMAT         VARCHAR     DEFAULT '{UB_CFORMAT_}',
        UB_CBAN            VARCHAR     DEFAULT '{UB_CBAN_}',
        UB_CNEURO          VARCHAR     DEFAULT '{UB_CNEURO_}',
        UB_CSENDCNT        INTEGER     DEFAULT {UB_CSENDCNT_},
        UB_CSENDPID        INTEGER,
        UB_CSENDSRC        VARCHAR,
        UB_CSERVICE        VARCHAR     DEFAULT '{UB_CSERVICE_}',
        UB_CREACTION       VARCHAR     DEFAULT '{UB_CREACTION_}',
        UB_CTRANSCRIBE     VARCHAR     DEFAULT '{UB_CTRANSCRIBE_}',
        UB_CPODCAST        VARCHAR     DEFAULT '{UB_CPODCAST_}',
        UB_CPODCASTSRC     VARCHAR,
        UB_CPODCASTDST     VARCHAR,
        UB_CGEO            VARCHAR     DEFAULT '{UB_CGEO_}',
        UB_CGEOCURID       INTEGER     DEFAULT 0,
        UB_CGEOMSGID       INTEGER,
        UB_CWORDWRD        VARCHAR,
        UB_CWORDSRC        VARCHAR,

        UB_VARS            VARCHAR     DEFAULT '{UB_VARS_}',
        UB_LSTS            VARCHAR     DEFAULT '{UB_LSTS_}',
        UB_LZ              VARCHAR     DEFAULT 'en',
        UB_LC              VARCHAR     DEFAULT 'en',
        UB_DT              VARCHAR,
        UB_IP              VARCHAR,
        UB_PORT            INTEGER,
        UB_ISACTIVE        BOOLEAN     DEFAULT 1,
        UB_ISVERIFIED      INTEGER
    )""")

    con.commit()
    cur.close()
    con.close()


# endregion


# region menu
async def post_offer(bot, data, BASE_D):
    try:
        for item in data:
            try:
                OFFER_ID, OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT, OFFER_TZ = item

                sign_ = OFFER_TZ[0]
                h_, m_ = OFFER_TZ.strip(sign_).split(':')
                dt_now = datetime.datetime.utcnow()
                if sign_ == "+":
                    dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
                else:
                    dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))
                timedelta_ = (dt_cur - datetime.datetime.strptime(OFFER_DT, "%d-%m-%Y %H:%M"))

                if timedelta_.days >= 0 and timedelta_.seconds >= 0:
                    sql = "UPDATE OFFER SET OFFER_DT=NULL, OFFER_STATUS=0 WHERE OFFER_ID=?"
                    await db_change(sql, (OFFER_ID,), BASE_D)

                    loop_minute = asyncio.get_event_loop()
                    loop_minute.create_task(broadcast_send_admin(bot, OFFER_USERTID, 'en', OFFER_ID, BASE_D, []))
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def bots_by_inline(chat_id, message, BASE_D):
    result = []
    try:
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        data = [['👩🏽‍💻 @FereyDemoBot', l_inline_demo[lz],
                 "<a href='https://t.me/FereyDemoBot?start=inline'>@FereyDemoBot</a>"],
                ['👩🏽‍💻 @FereyBotBot', l_inline_bot[lz],
                 "<a href='https://t.me/FereyBotBot?start=inline'>@FereyBotBot</a>"],
                ['👩🏽‍💻 @FereyPostBot', l_inline_post[lz],
                 "<a href='https://t.me/FereyPostBot?start=inline'>@FereyPostBot</a>"],
                ['👩🏽‍💻 @FereyMediaBot', l_inline_media[lz],
                 "<a href='https://t.me/FereyMediaBot?start=inline'>@FereyMediaBot</a>"],
                ['👩🏽‍💻 @FereyChannelBot', l_inline_channel[lz],
                 "<a href='https://t.me/FereyChannelBot?start=inline'>@FereyChannelBot</a>"],
                ['👩🏽‍💻 @FereyGroupBot', l_inline_group[lz],
                 "<a href='https://t.me/FereyGroupBot?start=inline'>@FereyGroupBot</a>"],
                ['👩🏽‍💻 @FereyFindBot', l_inline_find[lz],
                 "<a href='https://t.me/FereyFindBot?start=inline'>@FereyFindBot</a>"],
                ['👩🏽‍💻 @FereyAIBot', l_inline_ai[lz], "<a href='https://t.me/FereyAIBot?start=inline'>@FereyAIBot</a>"],
                ['👩🏽‍💻 @FereyStickerBot', l_inline_sticker[lz],
                 "<a href='https://t.me/FereyStickerBot?start=inline'>@FereyStickerBot</a>"],
                ['👩🏽‍💻 @FereyTargetBot', l_inline_target[lz],
                 "<a href='https://t.me/FereyTargetBot?start=inline'>@FereyTargetBot</a>"],
                ['👩🏽‍💻 @FereyUserBot', l_inline_user[lz],
                 "<a href='https://t.me/FereyUserBot?start=inline'>@FereyUserBot</a>"],
                ['👩🏽‍💻 @FereyToolsBot', l_inline_tools[lz],
                 "<a href='https://t.me/FereyToolsBot?start=inline'>@FereyToolsBot</a>"],
                ['👩🏽‍💻 @FereyWorkBot', l_inline_work[lz],
                 "<a href='https://t.me/FereyWorkBot?start=inline'>@FereyWorkBot</a>"], ]

        for i in range(0, len(data)):
            title, desc, text = data[i]

            input_message_content = types.InputTextMessageContent(message_text=text, disable_web_page_preview=False)
            result.append(
                types.InlineQueryResultArticle(id=str(uuid4()), title=title, description=desc, thumb_url=bot_logo_jpeg,
                                               input_message_content=input_message_content))
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_buttons_main(lz, bot_un, BASE_D):
    result = []
    try:
        result = [types.InlineKeyboardButton(text="👩🏽‍💼Acc", url=f"tg://user?id={my_tid}"),
                  types.InlineKeyboardButton(text="🙌🏽Tgph",
                                             web_app=types.WebAppInfo(url='https://telegra.ph/Links-07-05-462')),
                  types.InlineKeyboardButton(text="🔗Share",
                                             url=f'https://t.me/share/url?url=https%3A%2F%2Ft.me%2F{bot_un}&text=%40{bot_un}'),
                  types.InlineKeyboardButton(text=f"{(await read_likes(BASE_D))}♥️Like", callback_data=f"like"),
                  types.InlineKeyboardButton(text="🦋Chan", url=f"https://t.me/{get_tg_channel(lz)}"),
                  types.InlineKeyboardButton(text="🫥Bots", switch_inline_query_current_chat=f"~"), ]
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def send_request_chat(bot, chat_id, lz, is_group=False):
    result = []
    try:
        reply_markup = ReplyKeyboardBuilder()
        user_administrator_rights = ChatAdministratorRights(is_anonymous=True, can_manage_chat=True,
                                                            can_delete_messages=True, can_manage_video_chats=True,
                                                            can_restrict_members=True, can_promote_members=True,
                                                            can_change_info=False,  # can_change_info
                                                            can_invite_users=True, can_post_messages=True,
                                                            can_edit_messages=True, can_pin_messages=True,
                                                            can_post_stories=True, can_edit_stories=True,
                                                            can_delete_stories=True, can_manage_topics=True)

        if is_group:
            # print(f"{is_group=}")
            kb_entity = KeyboardButtonRequestChat(request_id=1, chat_is_channel=False, chat_has_username=None,
                                                  chat_is_created=None,
                                                  user_administrator_rights=user_administrator_rights,
                                                  bot_administrator_rights=user_administrator_rights,
                                                  bot_is_member=True)

            reply_markup.add(*[types.KeyboardButton(text=l_grp_btn1[lz], request_chat=kb_entity),
                               types.KeyboardButton(text=l_grp_btn2[lz])])
        else:
            kb_entity = KeyboardButtonRequestChat(request_id=1, chat_is_channel=True, chat_is_forum=False,
                                                  chat_has_username=None, chat_is_created=None,
                                                  user_administrator_rights=user_administrator_rights,
                                                  bot_administrator_rights=user_administrator_rights,
                                                  bot_is_member=True)

            reply_markup.add(*[types.KeyboardButton(text=l_chn_btn1[lz], request_chat=kb_entity),
                               types.KeyboardButton(text=l_chn_btn2[lz])])

        reply_markup = reply_markup.as_markup(resize_keyboard=True, is_persistent=True,
                                              input_field_placeholder=placeholder)
        await bot.send_message(chat_id=chat_id, text=l_choose_direction[lz], reply_markup=reply_markup)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result
# endregion


# region post

# endregion


# region blocks
async def recursion_blocks(app, tgr_cmd, BOT_TID_TMP, BOT_USERNAME, BASE_ENT, BASE_D, EXTRA_D, MEDIA_D, msg_lst, lc,
                           deep_cnt=0, next_items=None, target_click=None):
    if next_items is None:
        next_items = {}
    out_vid = None
    try:
        if deep_cnt > 7: return
        await asyncio.sleep(round(random.uniform(3, 4), 2))
        print(f'{deep_cnt}. recursion_blocks, {msg_lst=}')
        clicks = {}
        deep_cnt += 1

        msg_lst, next_items, clicks, messages, out_vid = await bypass_messages(app, lc, BOT_USERNAME, BASE_ENT, BASE_D,
                                                                               EXTRA_D, MEDIA_D, msg_lst, next_items,
                                                                               clicks, out_vid)
        msg_lst, next_items, clicks, messages, out_vid = await bypass_messages(app, lc, BOT_USERNAME, BASE_ENT, BASE_D,
                                                                               EXTRA_D, MEDIA_D, msg_lst, next_items,
                                                                               clicks, out_vid)
        if len(msg_lst): messages = [message for message in messages if message.id in msg_lst and msg_lst[message.id]]
        if target_click:
            clicks = {key: [elem for elem in value if elem == target_click] for key, value in clicks.items() if
                      any(elem == target_click for elem in value)}
            print(f'if target_click => {clicks}')

        for message in messages:
            try:
                for click in clicks.get(message.id, []):
                    cnt = 3
                    while True:
                        try:
                            x, y, ix, knd, lbl, query = click
                            next_items['type'] = 'btn'
                            next_items['MSG_VID'] = msg_lst[message.id]
                            next_items['click'] = click
                            print(f'clicks[i] {click}')

                            if knd == 'button_kb':
                                # continue
                                await app.send_message(chat_id=BOT_USERNAME, text=lbl)
                            elif knd == 'search':
                                bot_results = await app.get_inline_bot_results(bot=BOT_USERNAME, query=query)
                                await app.send_inline_bot_result(chat_id=BOT_USERNAME, query_id=bot_results.query_id,
                                                                 result_id=bot_results.results[
                                                                     0].id)  # clicks[message.id].remove(click)  # print()
                            elif message.via_bot:
                                print('via_bot')
                                break
                            else:
                                await message.click(ix)  # await message.click(x=x, y=y)

                            await recursion_blocks(app, tgr_cmd, BOT_TID_TMP, BOT_USERNAME, BASE_ENT, BASE_D, EXTRA_D,
                                                   MEDIA_D, msg_lst, lc, deep_cnt, next_items)
                            deep_cnt -= 1
                            print(f'{deep_cnt}. end {click}')
                            break
                        except Exception as e:
                            logger.info(log_ % str(e))
                            await asyncio.sleep(round(random.uniform(0, 1), 2))

                            if 'Request timed out' in str(e) and cnt >= 0:
                                await asyncio.sleep(round(random.uniform(2, 3), 2))
                                cnt -= 1
                                continue
                            elif 'MESSAGE_ID_INVALID' in str(e):
                                try:
                                    if isinstance(tgr_cmd, list):
                                        _, msg_id, emj = tgr_cmd
                                        peer = await app.resolve_peer(BOT_USERNAME)
                                        ReactionEmoji_ = ReactionEmoji(emoticon=emj)
                                        await app.invoke(
                                            SendReaction(peer=peer, msg_id=msg_id, big=True, add_to_recent=True,
                                                         reaction=[ReactionEmoji_]))
                                    else:
                                        await app.send_message(BOT_USERNAME, tgr_cmd)

                                    await recursion_blocks(app, tgr_cmd, BOT_TID_TMP, BOT_USERNAME, BASE_ENT, BASE_D,
                                                           EXTRA_D, MEDIA_D, msg_lst, lc, deep_cnt, next_items, click)
                                    deep_cnt -= 1
                                    print('end2')
                                    break
                                except Exception as e:
                                    logger.info(log_ % str(e))
                                    await asyncio.sleep(round(random.uniform(0, 1), 2))
                            else:
                                break
            except (SlowmodeWait, FloodWait) as e:
                logger.info(log_ % f"SlowmodeWait {e.retry_after}")
                await asyncio.sleep(e.value + 1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except (SlowmodeWait, FloodWait) as e:
        logger.info(log_ % f"SlowmodeWait {e.retry_after}")
        await asyncio.sleep(e.value + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return out_vid


async def bypass_messages(app, lc, BOT_USERNAME, BASE_ENT, BASE_D, EXTRA_D, MEDIA_D, msg_lst, next_items, clicks,
                          out_vid):
    messages = []
    try:
        messages = [msg async for msg in app.get_chat_history(BOT_USERNAME)]
        messages.reverse()
        IS_LINK = False
        for message in messages:
            try:
                # region data
                if message.id in msg_lst: continue
                logger.info(log_ % f"{next_items=}, {message.text[:64]}")
                msg_lst[message.id] = 0
                if message.service: continue
                if message.from_user and message.from_user.is_self and not message.via_bot:
                    continue

                btns = []
                MSG_VID = MSG_TYPE = MSG_TEXT = MSG_MEDIA = MSG_BUTTONS = None
                chkPin = True if message.pinned_message else False
                chkProtect = True if message.has_protected_content else False
                chkSpoiler = True if message.has_media_spoiler else False
                MSG_CHKBOX = {'chkPin': chkPin, 'chkProtect': chkProtect, 'chkEdit': False, 'chkFormat': False,
                              'chkTyping': False, 'chkPreview': False, 'chkSpoiler': chkSpoiler, 'chkSilence': False}
                # endregion

                # region type
                if message.text:
                    MSG_TYPE = 'text'
                    MSG_TEXT = message.text
                elif message.photo:
                    MSG_TYPE = 'photo'
                    MSG_TEXT = message.caption
                    # message.photo.ttl_seconds # chkdDestroy
                    file_id = message.photo.file_id
                    file_name = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpg')}"
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.animation:
                    MSG_TYPE = 'gif'
                    MSG_TEXT = message.caption
                    file_id = message.animation.file_id
                    file_name = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.gif')}"
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.video:
                    MSG_TYPE = 'video'
                    MSG_TEXT = message.caption
                    # file_id = message.video.file_id
                    # file_name = message.video.file_name
                    # dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    # await app.download_media(file_id, dst)

                    # tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    tmp_json = {'file_id': 'BAACAgQAAxkDAAOZZbz1zKWuj-6oAwo8y9IqgVOVTo8AArQTAAI36OhRkhobPNQiYMg0BA',
                                'file_id_note': 'None', 'file_type': 'video', 'file_name': 'telegram_video.mp4',
                                'tgph_link': 'https://telegra.ph/file/c6776f68485dbac7bdfa4.mp4',
                                'tgph_link2': 'https://telegra.ph/file/99b5073047bca81695ad7.jpg'}

                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.video_note:
                    MSG_TYPE = 'video_note'
                    file_id = message.video_note.file_id
                    file_name = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')}"
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.audio:
                    MSG_TYPE = 'audio'
                    MSG_TEXT = message.caption
                    file_id = message.audio.file_id
                    file_name = message.audio.file_name
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.voice:
                    MSG_TYPE = 'voice'
                    MSG_TEXT = message.caption
                    file_id = message.voice.file_id
                    file_name = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.ogg')
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.sticker:
                    MSG_TYPE = 'sticker'
                    file_id = message.sticker.file_id
                    file_name = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.webp')
                    if message.sticker.is_video:
                        file_name = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.webm')
                    elif message.sticker.is_animated:
                        file_name = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.tgs')
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.document:
                    MSG_TYPE = 'document'
                    MSG_TEXT = message.caption
                    file_id = message.document.file_id
                    file_name = message.document.file_name
                    dst = os.path.join(MEDIA_D, str(BOT_TID_TEST), file_name)
                    await app.download_media(file_id, dst)

                    tmp_json = await facade_get_fid(BOT_TID_TEST, dst, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D)
                    MSG_MEDIA = [tmp_json]
                    MSG_MEDIA = json.dumps(MSG_MEDIA, ensure_ascii=False)
                elif message.location:
                    MSG_TYPE = 'text'
                    MSG_TEXT = f"{message.location.latitude}\n{message.location.longitude}"
                elif message.venue:
                    MSG_TYPE = 'text'
                    MSG_TEXT = f"{message.venue.location.latitude}\n{message.venue.location.longitude}\n{message.venue.title}\n{message.venue.address}"
                elif message.poll:
                    MSG_TYPE = 'quiz'
                    MSG_TEXT = f"{message.poll.question}"

                    options = ''
                    for i in range(len(message.poll.options)):
                        if i == message.poll.correct_option_id:
                            expl = f"({message.poll.explanation})" or ''
                            options = f"{options}\n*{message.poll.options[i]}{expl}"
                        else:
                            options = f"{options}\n{message.poll.options[i]}"

                    MSG_TEXT = f"{MSG_TEXT}\n{options.strip()}"
                elif message.dice:
                    MSG_TYPE = 'dice'
                    MSG_MEDIA = message.dice
                # endregion

                # region MSG_BUTTONS
                if message.reply_markup:
                    ix = 0
                    query = ''
                    if getattr(message.reply_markup, 'inline_keyboard', None):
                        rows = message.reply_markup.inline_keyboard

                        for i in range(len(rows)):
                            cells = rows[i]
                            for j in range(len(cells)):
                                if cells[j].url:
                                    knd = 'link'
                                    text = cells[j].text
                                elif cells[j].switch_inline_query or cells[j].switch_inline_query_current_chat:
                                    knd = 'search'
                                    text = cells[j].text
                                    query = cells[j].switch_inline_query or cells[j].switch_inline_query_current_chat
                                    if message.id not in clicks:
                                        clicks[message.id] = [[i, j, ix, knd, cells[j].text, query]]
                                    else:
                                        clicks[message.id].append([i, j, ix, knd, cells[j].text, query])
                                else:
                                    knd = 'button_in'
                                    text = cells[j].text
                                    if message.id not in clicks:
                                        clicks[message.id] = [[i, j, ix, knd, cells[j].text, query]]
                                    else:
                                        clicks[message.id].append([i, j, ix, knd, cells[j].text, query])

                                lnk = await get_time_time(True)
                                lnk = cells[j].url if cells[j].url else lnk
                                row_i = i * 3
                                btns.append({"i": row_i + j, "lbl": text, "knd": knd, "lnk": lnk, "sort": 'inline'})
                                ix += 1
                    elif getattr(message.reply_markup, 'keyboard', None):
                        rows = message.reply_markup.keyboard
                        # if message.reply_markup.placeholder: print(f"{message.reply_markup.placeholder=} - просто вывести пользователю как фото/описание..")

                        for i in range(len(rows)):
                            cells = rows[i]
                            for j in range(len(cells)):
                                knd = text = None
                                if isinstance(cells[j], str):
                                    knd = 'button_kb'
                                    text = cells[j]
                                    if message.id not in clicks:
                                        clicks[message.id] = [[i, j, ix, knd, text, query]]
                                    else:
                                        clicks[message.id].append([i, j, ix, knd, text, query])
                                elif getattr(cells[j], 'request_contact', None):
                                    knd = 'phone'
                                    text = cells[j].text
                                elif getattr(cells[j], 'request_location', None):
                                    knd = 'geo'
                                    text = cells[j].text
                                ix += 1
                                if not knd: continue

                                lnk = await get_time_time(True)
                                row_i = i * 3
                                btns.append({"i": row_i + j, "lbl": text, "knd": knd, "lnk": lnk, "sort": 'keyboard'})

                    if len(btns): MSG_BUTTONS = json.dumps(btns, ensure_ascii=False)
                # endregion

                if MSG_TYPE:
                    MSG_VID = await get_time_time()
                    MSG_CHKBOX = json.dumps(MSG_CHKBOX, ensure_ascii=False)
                    MSG_TEXT = await replace_vars_msg_txt(app, MSG_TEXT)
                    MSG_TEXT = await replace_format_msg_txt(MSG_TEXT)

                    data_m = await select_exist_msg(MSG_TYPE, MSG_TEXT, MSG_CHKBOX, BASE_ENT)
                    if not len(data_m):
                        sql = "INSERT OR IGNORE INTO MSG (MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX, MSG_LC) VALUES (?, ?, ?, ?, ?, ?, ?)"
                        res = await db_change(sql,
                                              (MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX, lc,),
                                              BASE_ENT)
                    else:
                        res, MSG_VID = await check_exist_msg(data_m, MSG_MEDIA, MSG_BUTTONS)

                        if res == -1:
                            MSG_VID = await get_time_time()
                            sql = "INSERT OR IGNORE INTO MSG (MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX, MSG_LC) VALUES (?, ?, ?, ?, ?, ?, ?)"
                            res = await db_change(sql, (
                                MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX, lc,), BASE_ENT)
                        print(res, next_items)

                    if res != -1:
                        msg_lst[message.id] = MSG_VID
                        out_vid = MSG_VID if not out_vid else None
                    if len(next_items) and next_items['type'] == 'btn' and MSG_VID:
                        CLICK_MSG_VID = next_items['MSG_VID']
                        x, y, ix, knd, lbl, query = next_items['click']
                        row_i = x * 3 + y

                        sql = "SELECT MSG_VID, MSG_BUTTONS FROM MSG WHERE MSG_VID=?"
                        data_msg = await db_select(sql, (CLICK_MSG_VID,), BASE_ENT)
                        CLICK_MSG_VID, MSG_BUTTONS = data_msg[0]
                        MSG_BUTTONS = json.loads(MSG_BUTTONS)
                        MSG_BUTTON = {}
                        for it in MSG_BUTTONS:
                            if it['i'] == row_i:
                                MSG_BUTTON = it
                                break

                        if MSG_BUTTON['sort'] == 'inline':
                            trg_value = MSG_BUTTON['lnk']
                            trg_link = MSG_BUTTON['lbl']
                        else:
                            trg_value = MSG_BUTTON['lbl']
                            trg_link = ''

                        TRG_VID = await get_time_time()
                        TRG_CONTENT = [{"name": "btn", "value": trg_value, "utm": "_", "link": trg_link}]
                        TRG_CONTENT = json.dumps(TRG_CONTENT, ensure_ascii=False)

                        res = await check_exist_trg(TRG_CONTENT, MSG_VID, MSG_BUTTON['sort'], BASE_ENT)
                        if not res:
                            sql = f"INSERT OR IGNORE INTO TRG (TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE) VALUES (?, ?, ?, ?, ?)"
                            await db_change(sql, (TRG_VID, 'all', TRG_CONTENT, MSG_VID, 'MSG',), BASE_ENT)
                    elif len(next_items) and next_items['type'] == 'next' and MSG_VID:
                        sql = "UPDATE MSG SET MSG_NEXTID=?, MSG_NEXTTYPE=? WHERE MSG_VID=?"
                        await db_change(sql, (MSG_VID, 'MSG', next_items['MSG_VID'],), BASE_ENT)

                next_items = {}
                if MSG_VID:
                    next_items['type'] = 'next'
                    next_items['MSG_VID'] = MSG_VID
            except (SlowmodeWait, FloodWait) as e:
                logger.info(log_ % f"SlowmodeWait {e.retry_after}")
                await asyncio.sleep(e.value + 1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except (SlowmodeWait, FloodWait) as e:
        logger.info(log_ % f"SlowmodeWait {e.retry_after}")
        await asyncio.sleep(e.value + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return msg_lst, next_items, clicks, messages, out_vid


async def replace_vars_msg_txt(app, MSG_TEXT):
    try:
        if not MSG_TEXT: return
        get_me_ = await app.get_me()

        if get_me_.username and get_me_.username in MSG_TEXT:
            MSG_TEXT = MSG_TEXT.replace(get_me_.username, '{USER_USERNAME}')
        if get_me_.first_name and get_me_.first_name in MSG_TEXT:
            MSG_TEXT = MSG_TEXT.replace(get_me_.first_name, '{USER_FIRSTNAME}')
        if get_me_.last_name and get_me_.last_name in MSG_TEXT:
            MSG_TEXT = MSG_TEXT.replace(get_me_.last_name, '{USER_LASTNAME}')
        if get_me_.language_code and get_me_.language_code in MSG_TEXT:
            MSG_TEXT = MSG_TEXT.replace(get_me_.language_code, '{USER_LC}')
        if get_me_.phone_number and get_me_.phone_number in MSG_TEXT:
            MSG_TEXT = MSG_TEXT.replace(get_me_.phone_number, '{USER_PHONE}')
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return MSG_TEXT


async def replace_format_msg_txt(MSG_TEXT):
    result = MSG_TEXT
    try:
        if not MSG_TEXT or MSG_TEXT == MSG_TEXT.html: return

        result = MSG_TEXT.html
        result = result.replace('<spoiler>', '||').replace('</spoiler>', '||')
        result = result.replace('<b>', '*').replace('</b>', '*')
        result = result.replace('<s>', '~').replace('</s>', '~')
        result = result.replace('<i>', '_').replace('</i>', '_')
        result = result.replace('<u>', '__').replace('</u>', '__')
        result = result.replace('<code>', '`').replace('</code>', '`')
        result = result.replace('<pre>', '```').replace('</pre>', '```')

        if '<blockquote>' in result:
            result = result.replace('<blockquote>', '\n>').replace('</blockquote>', '\n')

        if '<a href=' in result:
            result = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)', result)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def select_exist_msg(MSG_TYPE, MSG_TEXT, MSG_CHKBOX, BASE_ENT):
    result = []
    try:
        if MSG_TEXT:
            sql = "SELECT MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX FROM MSG WHERE MSG_TYPE=? AND MSG_TEXT=? AND MSG_CHKBOX=?"
            result = await db_select(sql, (MSG_TYPE, MSG_TEXT, MSG_CHKBOX,), BASE_ENT)
        else:
            sql = "SELECT MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_CHKBOX FROM MSG WHERE MSG_TYPE=? AND MSG_TEXT is NULL AND MSG_CHKBOX=?"
            result = await db_select(sql, (MSG_TYPE, MSG_CHKBOX,), BASE_ENT)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def check_exist_msg(data_m, MSG_MEDIA, MSG_BUTTONS):
    MSG_VID = data_m[0][0]
    result = -1
    try:
        if MSG_MEDIA: MSG_MEDIA = json.loads(MSG_MEDIA)
        if MSG_BUTTONS: MSG_BUTTONS = json.loads(MSG_BUTTONS)

        for item in data_m:
            MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA_BASE, MSG_BUTTONS_BASE, MSG_CHKBOX = item

            try:
                # region MSG_MEDIA
                if MSG_MEDIA_BASE and not MSG_MEDIA:
                    continue
                elif not MSG_MEDIA_BASE and MSG_MEDIA:
                    continue

                if MSG_MEDIA_BASE and MSG_MEDIA:
                    MSG_MEDIA_BASE = json.loads(MSG_MEDIA_BASE)

                    if len(MSG_MEDIA_BASE) != len(MSG_MEDIA):
                        continue

                    tmp_res = 1
                    try:
                        for i in range(len(MSG_MEDIA_BASE)):
                            if MSG_MEDIA_BASE[i]['file_type'] == MSG_MEDIA[i]['file_type']: continue
                            tmp_res = -1
                            break
                    except:
                        tmp_res = -1
                    if tmp_res == -1: continue
                # endregion

                # region MSG_BUTTONS
                if MSG_BUTTONS_BASE and not MSG_BUTTONS:
                    continue
                elif not MSG_BUTTONS_BASE and MSG_BUTTONS:
                    continue

                if MSG_BUTTONS_BASE and MSG_BUTTONS:
                    MSG_BUTTONS_BASE = json.loads(MSG_BUTTONS_BASE)

                    if len(MSG_BUTTONS_BASE) != len(MSG_BUTTONS):
                        continue

                    tmp_res = 1
                    try:
                        for i in range(len(MSG_BUTTONS_BASE)):
                            if MSG_BUTTONS_BASE[i]['i'] == MSG_BUTTONS[i]['i'] and MSG_BUTTONS_BASE[i]['lbl'] == \
                                    MSG_BUTTONS[i]['lbl'] and MSG_BUTTONS_BASE[i]['knd'] == MSG_BUTTONS[i]['knd'] and \
                                    MSG_BUTTONS_BASE[i]['sort'] == MSG_BUTTONS[i]['sort']: continue
                            tmp_res = -1
                            break
                    except:
                        tmp_res = -1
                    if tmp_res == -1: continue
                # endregion

                result = 1
                return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result, MSG_VID


async def check_exist_trg(TRG_CONTENT, MSG_VID, srt, BASE_ENT):
    result = False
    try:
        sql = "SELECT TRG_CONTENT, TRG_RIGHTID FROM TRG WHERE TRG_TYPE=? AND TRG_RIGHTID=? AND TRG_RIGHTTYPE=?"
        data_t = await db_select(sql, ('all', MSG_VID, 'MSG',), BASE_ENT)
        TRG_CONTENT = json.loads(TRG_CONTENT)

        for item in data_t:
            TRG_CONTENT_, TRG_RIGHTID_ = item
            if TRG_CONTENT == TRG_CONTENT_:
                result = True
                return
            TRG_CONTENT_ = json.loads(TRG_CONTENT_)

            for i in range(len(TRG_CONTENT)):
                if TRG_CONTENT[i]['name'] != TRG_CONTENT_[i]['name']: continue

                if srt == 'inline':
                    if TRG_CONTENT[i]['link'] == TRG_CONTENT_[i]['link']:
                        print(f"{TRG_CONTENT[i]['link']} != {TRG_CONTENT_[i]['link']} than => no need to add this TRG")
                        result = True
                        return
                else:
                    if TRG_CONTENT[i]['value'] == TRG_CONTENT_[i]['value']:
                        print(
                            f"{TRG_CONTENT[i]['value']} != {TRG_CONTENT_[i]['value']} than => no need to add this TRG")
                        result = True
                        return
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def export_template(bot, chat_id, lz, BOT_TID, BOT_USERNAME, EXTRA_D, MEDIA_D, keys, is_premium_owner_=False):
    result = None
    try:
        BOT_USERNAME = BOT_USERNAME.strip('@')
        os.makedirs(os.path.join(MEDIA_D, str(BOT_TID)), exist_ok=True, mode=0o777)
        BASE_ENT = os.path.join(MEDIA_D, str(BOT_TID), f"{BOT_TID}.db")
        await db_bot_create(BASE_ENT)

        zip_dir = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f_dir')
        zip_dir = os.path.join(MEDIA_D, str(BOT_TID), zip_dir)
        zip_name = datetime.datetime.utcnow().strftime(f'@{BOT_USERNAME}-%d-%m-%Y.bot')
        zip_name = os.path.join(MEDIA_D, str(BOT_TID), zip_name)
        os.makedirs(zip_dir, exist_ok=True, mode=0o777)
        BASE_BOT_COPY = os.path.join(zip_dir, f"{BOT_TID}.db")
        shutil.copyfile(BASE_ENT, BASE_BOT_COPY)

        # handle copy of base
        sql = "DROP TABLE POST"
        await db_change(sql, (), BASE_BOT_COPY)
        sql = "DROP TABLE USER"
        await db_change(sql, (), BASE_BOT_COPY)
        sql = "DROP TABLE USERBAN"
        await db_change(sql, (), BASE_BOT_COPY)
        await db_bot_create(BASE_BOT_COPY)
        sql = "VACUUM"
        await db_change(sql, (), BASE_BOT_COPY)

        STATE_D = os.path.join(MEDIA_D, str(BOT_TID), 'STATE')
        os.makedirs(STATE_D, exist_ok=True, mode=0o777)
        stage_json = ''.join([stage_ for stage_ in os.listdir(STATE_D) if '*stage.json' in stage_])
        if stage_json == '':  # if True:
            stage_json = os.path.join(STATE_D, "1_*stage.json")
            with open(stage_json, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
        else:
            stage_json = os.path.join(STATE_D, stage_json)

        stage_json_copy = os.path.join(zip_dir, "1_*stage.json")
        shutil.copyfile(stage_json, stage_json_copy)
        state_files = [stage_json_copy]

        sql = "SELECT ENT_VID, ENT_TYPE FROM VIEW"
        view_data = await db_select(sql, (), BASE_ENT)
        view_act = {}
        view_trg = {}
        view_msg = {}

        for view_item in view_data:
            ENT_VID, ENT_TYPE = view_item
            if ENT_TYPE == 'ACT':
                view_act[ENT_VID] = '0'
            elif ENT_TYPE == 'TRG':
                view_trg[ENT_VID] = '0'
            elif ENT_TYPE == 'MSG':
                view_msg[ENT_VID] = '0'

        for k_, v_ in view_act.items(): await update_views(k_, 'ACT', [], zip_dir, state_files)
        for k_, v_ in view_trg.items(): await update_views(k_, 'TRG', [], zip_dir, state_files)
        for k_, v_ in view_msg.items(): await update_views(k_, 'MSG', [], zip_dir, state_files)

        sql = "DROP TABLE VIEW"
        await db_change(sql, (), BASE_BOT_COPY)

        shutil.make_archive(zip_name, 'zip', zip_dir)
        shutil.move(f"{zip_name}.zip", zip_name.replace('.zip', ''))
        shutil.rmtree(zip_dir)

        # enc key = Fernet.generate_key()
        with open(zip_name, 'rb') as f:
            cont_orig = f.read()

        fernet_premium_key = fernet_common_key = None
        if isinstance(keys, list):
            fernet_premium_key, fernet_common_key = keys
        key_ = fernet_premium_key if is_premium_owner_ else fernet_common_key
        fernet_ = Fernet(key_)
        cont_enc = fernet_.encrypt(cont_orig)

        with open(zip_name, 'wb') as f:
            f.write(cont_enc)

        caption = l_template_is_ready[lz].format(BOT_USERNAME)
        thumb = types.FSInputFile(os.path.join(EXTRA_D, 'parse.jpg'))
        await bot.send_document(chat_id=chat_id, document=types.FSInputFile(zip_name), caption=caption, thumbnail=thumb)
        if os.path.exists(zip_name): os.remove(zip_name)
        result = zip_name
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def update_views(GROUP_VID, GROUP_VIEW, GROUP_USERS, STATE_D, state_files):
    try:
        for state_file in state_files:
            tmp_file = os.path.join(STATE_D, state_file)
            with open(tmp_file) as f:
                tmp_json = json.load(f)

            if GROUP_VID in tmp_json:
                v_attrs = json.loads(tmp_json[GROUP_VID])

                if GROUP_VIEW == 'TRG':
                    v_attrs['children'][4]['attrs']['text'] = '0'
                elif GROUP_VIEW == 'ACT':
                    v_attrs['children'][3]['attrs']['text'] = '0'
                elif GROUP_VIEW == 'MSG':
                    v_attrs['children'][3]['attrs']['text'] = '0'

                tmp_json[GROUP_VID] = json.dumps(v_attrs, ensure_ascii=False)
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    json.dump(tmp_json, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def block_chain(BASE_ENT):
    res_full_chain = {}
    res_unfull_chain = {}
    try:
        data_all = []
        data_trg = await get_trg_shape(BASE_ENT)
        data_all += [[it, 'TRG'] for it in data_trg]

        sql = "SELECT ACT_VID, ACT_NEXTID FROM ACT"
        data_act = await db_select(sql, (), BASE_ENT)
        data_all += [[it[0], 'ACT'] for it in data_act]

        sql = "SELECT MSG_VID, MSG_NEXTID FROM MSG WHERE MSG_TYPE!=?"
        data_msg = await db_select(sql, ('web',), BASE_ENT)
        data_all += [[it[0], 'MSG'] for it in data_msg]

        # random.shuffle(data_all)
        full_chain = {}
        unfull_chain = {}
        logger.info(log_ % f"Обход ({len(data_all)}): {len(data_msg)}-MSG, {len(data_act)}-ACT, {len(data_trg)}-TRG")

        i = 0
        while len(data_all):
            # logger.info(log_ % f"{i=}")
            has_start, lst = await find_out_trg(data_all[i], BASE_ENT)

            if has_start:
                full_chain[len(full_chain)] = lst
            else:
                unfull_chain[len(unfull_chain)] = lst

            for item in lst:
                if item in data_all:
                    data_all.remove(item)
                    i -= 1
            i += 1
            i = max(0, i)

        # region убираем дубли (не раньше, иначе затрутся)
        logger.info(log_ % f"Убираем дубли")

        for key, chain in full_chain.items():
            last_element = tuple(chain[-1])
            if last_element not in res_full_chain or len(chain) > len(res_full_chain[last_element]):
                res_full_chain[last_element] = chain

        for key, chain in unfull_chain.items():
            last_element = tuple(chain[-1])
            if last_element not in res_unfull_chain or len(chain) > len(res_unfull_chain[last_element]):
                res_unfull_chain[last_element] = chain
        # endregion

        # region добиваем цепочки
        for unkey, unchain in res_unfull_chain.items():
            chains_with_lengths = list(res_full_chain.items())
            key = random.choices(chains_with_lengths, weights=[1 / len(l[1]) for l in chains_with_lengths])[0][0]
            # key = random.choice(list(res_full_chain.keys()))

            first_element_full = res_full_chain[key][0]
            last_element_unfull = unchain[-1]

            res_full_chain[key] = unchain + res_full_chain[key]
            ENT_VID, ENT_TYPE = first_element_full
            ENT_NEXTID, ENT_NEXTTYPE = last_element_unfull

            if ENT_TYPE == 'ACT':
                sql = "UPDATE ACT SET ACT_NEXTID=?, ACT_NEXTTYPE=? WHERE ACT_VID=?"
                await db_change(sql, (ENT_NEXTID, ENT_NEXTTYPE, ENT_VID,), BASE_ENT)
            elif ENT_TYPE == 'MSG':
                is_linked = await link_msg_by_btn(ENT_VID, ENT_NEXTID, ENT_NEXTTYPE, BASE_ENT)

                if not is_linked:
                    sql = "UPDATE MSG SET MSG_NEXTID=?, MSG_NEXTTYPE=? WHERE MSG_VID=?"
                    await db_change(sql, (ENT_NEXTID, ENT_NEXTTYPE, ENT_VID,), BASE_ENT)
            elif ENT_TYPE == 'TRG':
                sql = "UPDATE TRG SET TRG_RIGHTID=?, TRG_RIGHTTYPE=? WHERE TRG_VID=?"
                await db_change(sql, (ENT_NEXTID, ENT_NEXTTYPE, ENT_VID,), BASE_ENT)

        logger.info(log_ % f"{res_full_chain=}")
        logger.info(log_ % f"{res_unfull_chain=}")  # endregion
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))
    finally:
        return res_full_chain, res_unfull_chain


async def block_json(order_trgs, res_full_chain, lz, BASE_ENT, state_file, width, height):
    try:
        # region blocks json
        sql = "SELECT TRG_VID, TRG_CONTENT FROM TRG WHERE TRG_RIGHTID IS NOT NULL"
        d_trgs = await db_select(sql, (), BASE_ENT)
        for item in d_trgs:
            TRG_VID, TRG_CONTENT = item
            TRG_CONTENT = ast.literal_eval(TRG_CONTENT)

            if len([it for it in TRG_CONTENT if
                    it.get('name') == 'cmd' and it.get('value') == '/start' and it.get('utm') == '' and it.get(
                        'link') == '']):
                tmp = [TRG_VID, 'TRG', 'start']
                if tmp not in order_trgs:
                    order_trgs.append(tmp)
            elif any(item["name"] == "cmd" for item in TRG_CONTENT):
                tmp = [TRG_VID, 'TRG', 'out']
                if tmp not in order_trgs:
                    order_trgs.append(tmp)
            elif any(item["name"] == "rct" for item in TRG_CONTENT):
                tmp = [TRG_VID, 'TRG', 'out']
                if tmp not in order_trgs:
                    order_trgs.append(tmp)
            elif any(item["name"] == "txt" and 'utm' in item and item['utm'] == "" for item in TRG_CONTENT):
                tmp = [TRG_VID, 'TRG', 'out']
                if tmp not in order_trgs:
                    order_trgs.append(tmp)
            elif isinstance(TRG_CONTENT[0]['value'], dict) and TRG_CONTENT[0]['value']['left'] == 'DATE_TIME':
                tmp = [TRG_VID, 'TRG', 'out']
                if tmp not in order_trgs:
                    order_trgs.append(tmp)
            elif len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_':
                tmp = [TRG_VID, 'TRG', TRG_CONTENT[0]['value']]
                if tmp not in order_trgs:
                    order_trgs.append(tmp)

        i = from_x_out = from_y_out = 0
        logger.info(log_ % f"{order_trgs=}")
        while i < len(order_trgs):
            try:
                ENT_VID, ENT_TYPE, ENT_SUB = order_trgs[i]
                ENT_OUT = ENT_VID

                sql = "SELECT TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE FROM TRG WHERE TRG_VID=?"
                data_trg = await db_select(sql, (ENT_VID,), BASE_ENT)
                if not len(data_trg): continue
                TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE = data_trg[0]
                print(f"{ENT_SUB=} ({ENT_VID})")
                if not TRG_RIGHTID: continue

                ENT_VID = TRG_RIGHTID
                ENT_TYPE = TRG_RIGHTTYPE
                from_w = 140
                from_h = 50
                from_x = int(kjs + width / 2)
                from_y = kjs + 75

                if ENT_SUB == 'start':
                    from_x, from_y = await get_x_y_for_vid(state_file, width, height)
                    await upd_trg_json(state_file, lz, TRG_VID, TRG_TYPE, TRG_CONTENT, from_x, from_y)
                elif ENT_SUB == 'out':
                    if from_x_out and from_y_out:
                        from_x = from_x_out
                        from_y = from_y_out

                    from_x, from_y = await get_x_y_for_trg(state_file, width, height, from_x, from_y, from_w, from_h,
                                                           TRG_VID)
                    await upd_trg_json(state_file, lz, TRG_VID, TRG_TYPE, TRG_CONTENT, from_x, from_y)
                    from_x_out = from_x
                    from_y_out = from_y
                else:
                    # region data
                    TRG_CONTENT = ast.literal_eval(TRG_CONTENT)
                    like_st = f'%\"lbl\": \"{ENT_SUB}\",%' if TRG_CONTENT[0][
                                                                  'link'] == '' else f'%\"lnk\": \"{ENT_SUB}\",%'

                    sql = f"SELECT MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE FROM MSG WHERE MSG_BUTTONS LIKE '{like_st}'"
                    data_msg = await db_select(sql, (), BASE_ENT)
                    if not len(data_msg): continue
                    MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE = data_msg[0]

                    try:
                        with open(state_file) as f:
                            vids = json.load(f)
                    except:
                        vids = {}

                    if MSG_VID not in vids:
                        print(f"{MSG_VID} not in {vids.keys()}")
                        order_trgs.append(order_trgs[i])
                        continue
                    if not len(vids) or MSG_VID not in vids or TRG_RIGHTID in vids: continue

                    if TRG_RIGHTTYPE == "TRG":
                        to_w = 140
                        to_h = 50
                    elif TRG_RIGHTTYPE == "ACT":
                        to_w = 120
                        to_h = 50
                    else:
                        sql = "SELECT MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE FROM MSG WHERE MSG_VID=?"
                        data = await db_select(sql, (TRG_RIGHTID,), BASE_ENT)
                        if not len(data): continue
                        MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE = data[0]

                        to_w = 100
                        to_h = 50

                        MSG_TEXT = MSG_MEDIA if MSG_TYPE == 'dice' else MSG_TEXT
                        try:
                            MSG_MEDIA = ast.literal_eval(MSG_MEDIA)[0]['tgph_link2']
                        except:
                            MSG_MEDIA = None
                        to_h = to_h + 60 if MSG_MEDIA else to_h

                        if MSG_BUTTONS:
                            msg_btns = ast.literal_eval(MSG_BUTTONS)
                            row_cnt = await get_count_of_rows(msg_btns)
                            if len(row_cnt) == 1:
                                to_h = to_h + 14
                            elif len(row_cnt) == 2:
                                to_h = to_h + 14 * 2
                            elif len(row_cnt) == 3:
                                to_h = to_h + 14 * 3
                    # endregion

                    to_x, to_y = await get_x_y_for_btn(width, height, vids, MSG_VID, TRG_RIGHTID, to_w, to_h)
                    await upd_msg_json(state_file, lz, TRG_RIGHTID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS,
                                       BASE_ENT, to_x, to_y)

                    ENT_VID = MSG_NEXTID
                    ENT_TYPE = MSG_NEXTTYPE
                    from_w = to_w
                    from_h = to_h
                    from_x = to_x
                    from_y = to_y

                while ENT_VID and ENT_TYPE:
                    if ENT_TYPE == 'TRG':
                        sql = "SELECT TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE FROM TRG WHERE TRG_VID=?"
                        data_trg = await db_select(sql, (ENT_VID,), BASE_ENT)
                        if not len(data_trg): break
                        TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE = data_trg[0]

                        to_w = 140
                        to_h = 50
                        to_x, to_y = await get_x_y_for_vid(state_file, width, height, from_x, from_y, from_w, from_h,
                                                           TRG_VID, to_w, to_h)
                        await upd_trg_json(state_file, lz, TRG_VID, TRG_TYPE, TRG_CONTENT, to_x, to_y)

                        ENT_VID = TRG_RIGHTID
                        ENT_TYPE = TRG_RIGHTTYPE
                        from_w = to_w
                        from_h = to_h
                        from_x = to_x
                        from_y = to_y
                    elif ENT_TYPE == 'ACT':
                        sql = "SELECT ACT_VID, ACT_TYPE, ACT_CONTENT, ACT_NEXTID, ACT_NEXTTYPE FROM ACT WHERE ACT_VID=?"
                        data_act = await db_select(sql, (ENT_VID,), BASE_ENT)
                        if not len(data_act): break
                        ACT_VID, ACT_TYPE, ACT_CONTENT, ACT_NEXTID, ACT_NEXTTYPE = data_act[0]

                        to_w = 120
                        to_h = 50
                        to_x, to_y = await get_x_y_for_vid(state_file, width, height, from_x, from_y, from_w, from_h,
                                                           ACT_VID, to_w, to_h)
                        await upd_act_json(state_file, lz, ACT_VID, ACT_TYPE, ACT_CONTENT, to_x, to_y)

                        ENT_VID = ACT_NEXTID
                        ENT_TYPE = ACT_NEXTTYPE
                        from_w = to_w
                        from_h = to_h
                        from_x = to_x
                        from_y = to_y
                    elif ENT_TYPE == 'MSG':
                        sql = "SELECT MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE FROM MSG WHERE MSG_VID=?"
                        data_msg = await db_select(sql, (ENT_VID,), BASE_ENT)
                        if not len(data_msg): break
                        MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE = data_msg[0]

                        to_w = 100
                        to_h = 50
                        # region data
                        MSG_TEXT = MSG_MEDIA if MSG_TYPE == 'dice' else MSG_TEXT
                        try:
                            MSG_MEDIA = ast.literal_eval(MSG_MEDIA)[0]['tgph_link2']
                        except:
                            MSG_MEDIA = None
                        to_h = to_h + 60 if MSG_MEDIA else to_h

                        if MSG_BUTTONS:
                            msg_btns = ast.literal_eval(MSG_BUTTONS)
                            row_cnt = await get_count_of_rows(msg_btns)
                            if len(row_cnt) == 1:
                                to_h = to_h + 14
                            elif len(row_cnt) == 2:
                                to_h = to_h + 14 * 2
                            elif len(row_cnt) == 3:
                                to_h = to_h + 14 * 3
                        # endregion
                        to_x, to_y = await get_x_y_for_vid(state_file, width, height, from_x, from_y, from_w, from_h,
                                                           MSG_VID, to_w, to_h)
                        await upd_msg_json(state_file, lz, MSG_VID, MSG_TYPE, MSG_TEXT, MSG_MEDIA, MSG_BUTTONS,
                                           BASE_ENT, to_x, to_y)

                        ENT_VID = MSG_NEXTID
                        ENT_TYPE = MSG_NEXTTYPE

                        if not MSG_NEXTID:
                            for k, v in res_full_chain.items():
                                if k[0] != ENT_OUT: continue
                                if MSG_VID in [it[0] for it in v]:
                                    ix = v.index([MSG_VID, 'MSG'])
                                    ENT_VID, ENT_TYPE = v[ix - 1] if ix - 1 >= 0 else [None, None]
                                    break
                        from_w = to_w
                        from_h = to_h
                        from_x = to_x
                        from_y = to_y
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
            finally:
                i += 1
                if i > 20: break
        print('---------- endregion blocks')
        # endregion

        # region lines json
        sql = "SELECT TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE, TRG_LEFTID, TRG_LEFTTYPE FROM TRG"
        data_trg = await db_select(sql, (), BASE_ENT)
        for item_trg in data_trg:
            TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE, TRG_LEFTID, TRG_LEFTTYPE = item_trg
            TRG_CONTENT = ast.literal_eval(TRG_CONTENT)
            if len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_': continue

            await lines_trg_json(state_file, TRG_VID, TRG_RIGHTID, TRG_RIGHTTYPE, TRG_LEFTID, TRG_LEFTTYPE)

        sql = "SELECT ACT_VID, ACT_TYPE, ACT_CONTENT, ACT_NEXTID, ACT_NEXTTYPE FROM ACT"
        data_act = await db_select(sql, (), BASE_ENT)
        for item_act in data_act:
            ACT_VID, ACT_TYPE, ACT_CONTENT, ACT_NEXTID, ACT_NEXTTYPE = item_act
            await lines_act_json(state_file, ACT_VID, ACT_NEXTID, ACT_NEXTTYPE)

        sql = "SELECT MSG_VID, MSG_TYPE, MSG_TEXT, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE FROM MSG"
        data_msg = await db_select(sql, (), BASE_ENT)
        for item_msg in data_msg:
            MSG_VID, MSG_TYPE, MSG_TEXT, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE = item_msg
            await lines_msg_json(state_file, MSG_VID, MSG_BUTTONS, MSG_NEXTID, MSG_NEXTTYPE, BASE_ENT)

        await in_lines_json(state_file, BASE_ENT)  # endregion
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))


async def link_msg_by_btn(ENT_VID, ENT_NEXTID, ENT_NEXTTYPE, BASE_ENT):
    result = False
    try:
        if ENT_NEXTTYPE not in ['MSG', 'TRG']: return
        sql = "SELECT MSG_NEXTID, MSG_BUTTONS FROM MSG WHERE MSG_VID=?"
        data_btn_msg = await db_select(sql, (ENT_VID,), BASE_ENT)
        if not len(data_btn_msg): return
        MSG_NEXTID, MSG_BUTTONS = data_btn_msg[0]
        if not MSG_BUTTONS: return

        btns = ast.literal_eval(MSG_BUTTONS)
        for btn in btns:
            if btn['knd'] in ['link', 'web', 'payment', 'search', 'like', 'phone', 'geo']: continue
            if btn['lnk'] in ['prev', 'current', 'next']: continue
            trg_type = 'txt' if btn['sort'] == 'keyboard' else 'btn'
            trg_value = btn['lbl'] if btn['sort'] == 'keyboard' else btn['lnk']
            trg_utm = '_'
            trg_link = ''
            if btn['knd'] == 'phone':
                trg_type = 'btn'
                trg_value = 'phone'
            elif btn['knd'] == 'geo':
                trg_type = 'btn'
                trg_value = 'geo'

            is_in_trgs = False
            sql = "SELECT TRG_VID, TRG_CONTENT FROM TRG WHERE TRG_RIGHTID IS NOT NULL"
            data_trg = await db_select(sql, (), BASE_ENT)
            for item in data_trg:
                TRG_VID, TRG_CONTENT = item
                TRG_CONTENT = ast.literal_eval(TRG_CONTENT)

                if len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_':
                    if TRG_CONTENT[0]['value'] == trg_value:
                        is_in_trgs = True
                        break
            if is_in_trgs: continue

            TRG_VID = await get_time_time()
            TRG_TYPE = 'all'
            TRG_CONTENT = [{"name": trg_type, "value": trg_value, "utm": trg_utm, "link": trg_link}]
            TRG_CONTENT = json.dumps(TRG_CONTENT, ensure_ascii=False)
            sql = "INSERT OR IGNORE INTO TRG (TRG_VID, TRG_TYPE, TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE) VALUES (?, ?, ?, ?, ?)"
            await db_change(sql, (TRG_VID, TRG_TYPE, TRG_CONTENT, ENT_NEXTID, ENT_NEXTTYPE,), BASE_ENT)

            result = True
            return
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))
    finally:
        return result


async def find_out_trg(item, BASE_ENT):
    result = [item]
    has_start = False
    try:
        item_id, ENT_TYPE = item
        print(f"find_out_trg {item_id=} ({ENT_TYPE})")

        while item_id:
            sql = "SELECT MSG_VID FROM MSG WHERE MSG_NEXTID=?"
            from_msg = await db_select(sql, (item_id,), BASE_ENT)
            if len(from_msg):
                item_id = from_msg[0][0]
                result.append([item_id, 'MSG'])
                continue

            sql = "SELECT ACT_VID FROM ACT WHERE ACT_NEXTID=?"
            from_act = await db_select(sql, (item_id,), BASE_ENT)
            if len(from_act):
                item_id = from_act[0][0]
                result.append([item_id, 'ACT'])
                continue

            if ENT_TYPE == 'TRG':
                trg_vid, trg_type = await get_trg_type(item_id, BASE_ENT, False)
                # logger.info(log_ % f"{trg_vid=}, {trg_type=}")
                tuple_ = [trg_vid, 'TRG' if trg_type and trg_type != 'btn' else 'MSG']
                if tuple_ in result and trg_type != 'out': return
                if trg_vid and tuple_ not in result: result.append(tuple_)
                if trg_vid and trg_type == 'out':
                    has_start = True
                    return

            trg_vid, trg_type = await get_trg_type(item_id, BASE_ENT)
            # logger.info(log_ % f"{trg_vid=}, {trg_type=}")
            item_id = trg_vid
            tuple_ = [trg_vid, 'TRG' if trg_type and trg_type != 'btn' else 'MSG']
            if tuple_ in result and trg_type != 'out': return
            if trg_vid and tuple_ not in result: result.append(tuple_)
            if trg_vid and trg_type == 'out':
                has_start = True
                return
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))
    finally:
        return has_start, result


async def get_trg_shape(BASE_ENT):
    result = []
    try:
        sql = "SELECT TRG_VID, TRG_CONTENT, TRG_RIGHTID FROM TRG"
        from_trg = await db_select(sql, (), BASE_ENT)

        for item in from_trg:
            TRG_VID, TRG_CONTENT, TRG_RIGHTID = item
            TRG_CONTENT = ast.literal_eval(TRG_CONTENT)
            if len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_': continue

            result.append(TRG_VID)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))
    finally:
        return result


async def get_all_act_blocks(BASE_ENT):
    all_blocks = []
    act_blocks = []
    trg_blocks = []
    out_trgs = []
    try:
        sql = "SELECT TRG_VID, TRG_CONTENT FROM TRG"
        data_trg = await db_select(sql, (), BASE_ENT)

        for item_trg in data_trg:
            TRG_VID, TRG_CONTENT = item_trg
            TRG_CONTENT = ast.literal_eval(TRG_CONTENT)
            if len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_': continue
            all_blocks.append(TRG_VID)
            trg_blocks.append(TRG_VID)

            if any(item["name"] == "cmd" for item in TRG_CONTENT):
                out_trgs.append(TRG_VID)
            elif any(item["name"] == "rct" for item in TRG_CONTENT):
                out_trgs.append(TRG_VID)
            elif any(item["name"] == "txt" and 'utm' in item and item['utm'] == "" for item in TRG_CONTENT):
                out_trgs.append(TRG_VID)
            if isinstance(TRG_CONTENT[0]['value'], dict) and TRG_CONTENT[0]['value']['left'] == 'DATE_TIME':
                out_trgs.append(TRG_VID)

        sql = "SELECT ACT_VID FROM ACT"
        data_acts = await db_select(sql, (), BASE_ENT)
        all_blocks += data_acts
        act_blocks = data_acts

        sql = "SELECT MSG_VID FROM MSG"
        data_msgs = await db_select(sql, (), BASE_ENT)
        all_blocks += data_msgs
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return all_blocks, act_blocks, trg_blocks, out_trgs


async def get_msg_nextid(k_MSG_VID, BASE_ENT):
    NEXT_ID = NEXT_TYPE = None
    try:
        sql = "SELECT MSG_VID, MSG_TYPE FROM MSG WHERE MSG_TYPE!=?"
        data_msg = await db_select(sql, ('web',), BASE_ENT)
        data_msg = [it for it in data_msg if it[0] != k_MSG_VID]
        random.shuffle(data_msg)

        for item_msg in data_msg:
            MSG_VID, MSG_TYPE = item_msg
            next_ids = await get_ent_nextid(MSG_VID, MSG_TYPE, BASE_ENT, True)

            if MSG_VID not in next_ids:
                NEXT_ID = MSG_VID
                NEXT_TYPE = 'MSG'
                return
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return NEXT_ID, NEXT_TYPE


async def get_ent_nextid(ENT_VID, ENT_TYPE, BASE_ENT, no_btns=False):
    result = []
    try:
        sql = "SELECT TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE FROM TRG WHERE TRG_RIGHTID IS NOT NULL"
        data_trg = await db_select(sql, (), BASE_ENT)

        for item_trg in data_trg:
            TRG_CONTENT, TRG_RIGHTID, TRG_RIGHTTYPE = item_trg
            TRG_CONTENT = ast.literal_eval(TRG_CONTENT)
            if no_btns and len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_': continue
            result.append(TRG_RIGHTID)

        sql = "SELECT TRG_LEFTID, TRG_LEFTTYPE FROM TRG WHERE TRG_LEFTID IS NOT NULL"
        data_trg = await db_select(sql, (), BASE_ENT)

        for item_trg in data_trg:
            TRG_LEFTID, TRG_LEFTTYPE = item_trg
            sql = "SELECT MSG_VID FROM MSG WHERE MSG_VID=?"
            data_tmp = await db_select(sql, (TRG_LEFTID,), BASE_ENT)
            if len(data_tmp): result.append(TRG_LEFTID)
        result = list(set(result))
    except Exception as e:
        logger.info(log_ % str(e) + f"{ENT_VID=}, {ENT_TYPE=}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_trg_type(item_id, BASE_ENT, is_next=True):
    trg_vid = None
    trg_type = None
    try:
        # await asyncio.sleep(0.1)
        if is_next:
            sql = "SELECT TRG_VID, TRG_CONTENT FROM TRG WHERE TRG_RIGHTID=?"
            from_trg = await db_select(sql, (item_id,), BASE_ENT)
        else:
            sql = "SELECT TRG_VID, TRG_CONTENT FROM TRG WHERE TRG_VID=?"
            from_trg = await db_select(sql, (item_id,), BASE_ENT)
        if not len(from_trg): return
        TRG_VID, TRG_CONTENT = from_trg[0]
        TRG_CONTENT = ast.literal_eval(TRG_CONTENT)

        if any(item["name"] == "cmd" for item in TRG_CONTENT):
            trg_vid = TRG_VID
            trg_type = 'out'
        elif any(item["name"] == "rct" for item in TRG_CONTENT):
            trg_vid = TRG_VID
            trg_type = 'out'
        elif any(item["name"] == "txt" and 'utm' in item and item['utm'] == "" for item in TRG_CONTENT):
            trg_vid = TRG_VID
            trg_type = 'out'
        elif isinstance(TRG_CONTENT[0]['value'], dict) and TRG_CONTENT[0]['value']['left'] == 'DATE_TIME':
            trg_vid = TRG_VID
            trg_type = 'out'
        elif len(TRG_CONTENT) == 1 and 'utm' in TRG_CONTENT[0] and TRG_CONTENT[0]['utm'] == '_':
            sql = f"SELECT MSG_VID, MSG_BUTTONS FROM MSG WHERE MSG_BUTTONS LIKE '%: \"{TRG_CONTENT[0]['value']}\",%'"
            data_msg = await db_select(sql, (), BASE_ENT)
            if not len(data_msg): return
            MSG_VID, MSG_BUTTONS = data_msg[0]
            trg_vid = MSG_VID
            trg_type = 'btn'
        elif any(item["name"] in ["var", 'lst'] for item in TRG_CONTENT):
            trg_vid = TRG_VID
            trg_type = 'in'
        else:
            logger.info(log_ % f"wtf: {TRG_VID, TRG_CONTENT} - к какому виду триггеров отнести?")
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))
    finally:
        return trg_vid, trg_type


async def upd_trg_json(state_file, lz, ent_vid, ent_type, content, x_, y_, views_=0):
    result = {}
    try:
        # region data
        ent_type = l_all_json[lz] if ent_type == 'all' else l_one_json[lz]
        txt_content = await get_txt_content(content, lz, 'trg')

        x_rect = x_
        y_rect = y_
        width_ = 140
        height_ = 50
        x_crl_right = x_rect + 10
        y_crl_right = y_rect + 31
        x_crl_left = x_rect - 10
        y_crl_left = y_crl_right
        x_trg_lbl_tag = x_rect - 4
        y_trg_lbl_tag = y_rect - 20
        x_views = x_rect + 55
        y_views = y_rect + 7

        w_inner_rect = width_ - 50
        h_inner_rect = height_ - 30
        x_inner_rect = x_rect
        y_inner_rect = y_rect
        x_txtContent = x_rect - 16
        y_txtContent = y_rect + 7
        x_image = x_rect - 57
        y_image = y_rect + 5
        # endregion

        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        result[ent_vid] = {
            "attrs": {"id": str(ent_vid), "name": "group", "sub_name": "TRG", "isStart": False, "isStartFalse": False,
                      "width": width_, "height": height_, "in_lines": [], "out_line": "", "out_false": "",
                      "right_id": "", "right_type": "", "left_id": "", "left_type": "", "draggable": True},
            "className": "Group", "children": [{"attrs": {"name": "rect", "points": [0, 35, 70, 0, 140, 35, 70, 70],
                                                          "x": x_rect, "y": y_rect, "height": height_,
                                                          "offsetX": int(width_ / 2), "offsetY": int(height_ / 2),
                                                          "fill": "rgba(254, 254, 254, 1.0)",
                                                          "stroke": "rgba(142, 152, 162, .99)",
                                                          "strokeScaleEnabled": False, "strokeWidth": 1,
                                                          "hitStrokeWidth": 10, "shadowBlur": 10,
                                                          "shadowColor": "rgba(0,0,0, 0.1)", "shadowOffsetX": -1,
                                                          "shadowOffsetY": 2, "cornerRadius": 4, "lineJoin": "round",
                                                          "lineCap": "round", "closed": True}, "className": "Line"}, {
                                                   "attrs": {"name": "circle", "radius": 4, "x": x_crl_right,
                                                             "y": y_crl_right, "fill": "rgba(254, 254, 254, 1.0)",
                                                             "stroke": "rgba(92, 199, 117, .99)",
                                                             "strokeScaleEnabled": False, "strokeWidth": 1,
                                                             "hitStrokeWidth": 25}, "className": "Circle"}, {
                                                   "attrs": {"name": "circle", "radius": 4, "x": x_crl_left,
                                                             "y": y_crl_left, "fill": "rgba(254, 254, 254, 1.0)",
                                                             "stroke": "rgba(217, 86, 60, 0.99)",
                                                             "strokeScaleEnabled": False, "strokeWidth": 1,
                                                             "hitStrokeWidth": 25}, "className": "Circle"},
                                               {"attrs": {"x": x_trg_lbl_tag, "y": y_trg_lbl_tag}, "className": "Label",
                                                "children": [{"attrs": {"fill": "rgba(238, 241, 244, .99)",
                                                                        "width": 6.61376953125, "height": 7},
                                                              "className": "Tag"}, {
                                                                 "attrs": {"text": f"{ent_type}", "fontSize": 7,
                                                                           "align": "center", "verticalAlign": "middle",
                                                                           "fill": "rgba(90, 100, 120, 0.99)"},
                                                                 "className": "Text"}]}, {
                                                   "attrs": {"x": x_views, "y": y_views, "text": f"{views_}",
                                                             "fontFamily": "Courier", "fontSize": 7, "align": "center",
                                                             "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"},
                                               {"attrs": {"x": x_inner_rect, "y": y_inner_rect, "width": w_inner_rect,
                                                          "height": h_inner_rect, "offsetX": int(w_inner_rect / 2),
                                                          "fill": "rgba(238, 241, 244, .99)",
                                                          "strokeScaleEnabled": False, "cornerRadius": 4,
                                                          "dash": [2, 1], "stroke": "rgba(200, 200, 200, .99)",
                                                          "strokeWidth": 1}, "className": "Rect"}, {
                                                   "attrs": {"name": "txtContent", "x": x_txtContent, "y": y_txtContent,
                                                             "text": f"{txt_content}", "fontSize": 7, "align": "center",
                                                             "verticalAlign": "middle",
                                                             "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"},
                                               {"attrs": {"x": x_image, "y": y_image, "scaleX": 0.2, "scaleY": 0.2},
                                                "className": "Image"}]}
        result[ent_vid] = json.dumps(result[ent_vid], ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def upd_act_json(state_file, lz, ent_vid, ent_type, content, x_, y_, views_=0):
    result = {}
    try:
        # region data
        ent_type = l_order_act[lz] if ent_type == 'order' else l_rand_act[lz]
        txt_content = await get_txt_content(content, lz, 'act')

        x_rect = x_
        y_rect = y_
        width_ = 120
        height_ = 50
        x_crl = x_rect
        y_crl = y_rect + 19
        x_trg_lbl_tag = x_rect - 20
        y_trg_lbl_tag = y_rect - 20
        x_views = x_rect + 40
        y_views = y_rect - 20

        w_inner_rect = width_ - 30
        h_inner_rect = height_ - 30
        x_inner_rect = x_rect
        y_inner_rect = y_rect
        x_txtContent = x_rect - 9
        y_txtContent = y_rect - 4
        x_image = x_rect - 45
        y_image = y_rect - 20
        # endregion

        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        result[ent_vid] = {
            "attrs": {"id": str(ent_vid), "name": "group", "sub_name": "ACT", "isStart": False, "isStartFalse": False,
                      "width": width_, "height": height_, "in_lines": [], "out_line": "", "out_false": "",
                      "next_id": "", "next_type": "", "draggable": True}, "className": "Group", "children": [{
                "attrs": {"name": "rect", "x": x_rect, "y": y_rect, "width": width_, "height": height_,
                          "offsetX": int(width_ / 2), "offsetY": int(height_ / 2), "fill": "rgba(254, 254, 254, 1.0)",
                          "stroke": "rgba(142, 152, 162, .99)", "strokeScaleEnabled": False, "strokeWidth": 1,
                          "hitStrokeWidth": 10, "shadowBlur": 10, "shadowColor": "rgba(0,0,0, 0.1)",
                          "shadowOffsetX": -1, "shadowOffsetY": 2, "cornerRadius": 30, "lineJoin": "round",
                          "lineCap": "round"}, "className": "Rect"}, {
                "attrs": {"x": x_crl, "y": y_crl, "radius": 4, "fill": "rgba(254, 254, 254, 1.0)",
                          "stroke": "rgba(113, 129, 151, .99)", "strokeScaleEnabled": False, "strokeWidth": 1,
                          "hitStrokeWidth": 25}, "className": "Circle"},
                {"attrs": {"x": x_trg_lbl_tag, "y": y_trg_lbl_tag}, "className": "Label", "children": [
                    {"attrs": {"fill": "rgba(238, 241, 244, .99)", "width": 39.5322265625, "height": 7},
                     "className": "Tag"}, {
                        "attrs": {"text": f"{ent_type}", "fontSize": 7, "align": "center", "verticalAlign": "middle",
                                  "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"}]}, {
                    "attrs": {"x": x_views, "y": y_views, "text": f"{views_}", "fontFamily": "Courier", "fontSize": 7,
                              "align": "center", "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"}, {
                    "attrs": {"x": x_inner_rect, "y": y_inner_rect, "width": w_inner_rect, "height": h_inner_rect,
                              "offsetX": int(w_inner_rect / 2), "offsetY": int(h_inner_rect / 2),
                              "fill": "rgba(238, 241, 244, .99)", "strokeScaleEnabled": False, "cornerRadius": 4,
                              "dash": [2, 1], "stroke": "rgba(200, 200, 200, .99)", "strokeWidth": 1},
                    "className": "Rect"}, {
                    "attrs": {"name": "txtContent", "x": x_txtContent, "y": y_txtContent, "text": f"{txt_content}",
                              "fontSize": 7, "align": "center", "verticalAlign": "middle",
                              "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"},
                {"attrs": {"x": x_image, "y": y_image, "scaleX": 0.2, "scaleY": 0.2}, "className": "Image"}]}
        result[ent_vid] = json.dumps(result[ent_vid], ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def upd_msg_json(state_file, lz, ent_vid, ent_type, msg_text, msg_media, msg_btns, BASE_ENT, x_, y_, views_=0):
    result = {}
    try:
        # region data
        if ent_type == 'photo':
            ent_type = l_msg_photo[lz]
        elif ent_type == 'gif':
            ent_type = l_msg_gif[lz]
        elif ent_type == 'video':
            ent_type = l_msg_video[lz]
        elif ent_type == 'video_note':
            ent_type = l_msg_video_note[lz]
        elif ent_type == 'audio':
            ent_type = l_msg_audio[lz]
        elif ent_type == 'voice':
            ent_type = l_msg_voice[lz]
        elif ent_type == 'document':
            ent_type = l_msg_document[lz]
        elif ent_type == 'sticker':
            ent_type = l_msg_sticker[lz]
        elif ent_type == 'quiz':
            ent_type = l_msg_quiz[lz]
        elif ent_type == 'dice':
            ent_type = l_msg_dice[lz]
        elif ent_type == 'web':
            ent_type = l_msg_web[lz]
        else:
            ent_type = l_msg_text[lz]
        msg_text = await get_txt_content(msg_text, lz, 'msg', ent_type)

        row_cnt = {}
        height_ = 50
        # max_i_value = 0
        if msg_btns:
            msg_btns = ast.literal_eval(msg_btns)
            # max_i_value = max(msg_btns, key=lambda x: x['i'])['i']
            row_cnt = await get_count_of_rows(msg_btns)

        if len(row_cnt) == 1:
            height_ = height_ + 14
        elif len(row_cnt) == 2:
            height_ = height_ + 14 * 2
        elif len(row_cnt) == 3:
            height_ = height_ + 14 * 3

        x_rect = x_
        y_rect = y_
        width_ = 100

        x_crl = x_rect
        y_crl = y_rect + 25
        x_trg_lbl_tag = x_rect - 10
        y_trg_lbl_tag = y_rect - 20
        x_views = x_rect + 38
        y_views = y_rect - 20

        w_inner_rect = width_ - 10
        # h_inner_rect = height_ - 30
        x_inner_rect = x_rect
        y_inner_rect = y_rect + 5
        x_txtContent = x_rect - 10
        y_txtContent = y_rect - 15
        x_image = x_rect - 45
        y_image = y_rect - 20

        if msg_btns:
            if len(row_cnt) == 1:
                y_crl = y_crl + 7
                y_trg_lbl_tag = y_trg_lbl_tag - 7
                y_views = y_views - 7
                y_inner_rect = y_inner_rect - 7
                y_txtContent = y_txtContent + 3
                y_image = y_image - 7
            elif len(row_cnt) == 2:
                y_crl = y_crl + 7 * 2
                y_trg_lbl_tag = y_trg_lbl_tag - 7 * 2
                y_views = y_views - 7 * 2
                y_inner_rect = y_inner_rect - 7 * 2
                y_txtContent = y_txtContent + 3 * 2
                y_image = y_image - 7 * 2
            elif len(row_cnt) == 3:
                y_crl = y_crl + 7 * 3
                y_trg_lbl_tag = y_trg_lbl_tag - 7 * 3
                y_views = y_views - 7 * 3
                y_inner_rect = y_inner_rect - 7 * 3
                y_txtContent = y_txtContent + 3 * 3
                y_image = y_image - 7 * 3  # logger.info(log_ % f"y_crl={y_crl}, y_trg_lbl_tag={y_trg_lbl_tag}, y_views={y_views}, y_inner_rect={y_inner_rect}, y_image={y_image}")

        if msg_media:
            height_ = height_ + 60
            y_crl = y_crl + 30
            y_trg_lbl_tag = y_trg_lbl_tag - 30
            y_views = y_views - 30
            y_inner_rect = y_inner_rect + 30
            y_txtContent = y_txtContent + 30
            y_image = y_image - 30
        # endregion

        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        result[ent_vid] = {
            "attrs": {"id": str(ent_vid), "name": "group", "sub_name": "MSG", "isStart": False, "isStartFalse": False,
                      "width": width_, "height": height_, "in_lines": [], "out_line": "", "out_false": "",
                      "next_id": "", "next_type": "", "draggable": True}, "className": "Group", "children": [{
                "attrs": {"name": "rect", "x": x_rect, "y": y_rect, "width": width_, "height": height_,
                          "offsetX": int(width_ / 2), "offsetY": int(height_ / 2), "fill": "rgba(254, 254, 254, 1.0)",
                          "stroke": "rgba(142, 152, 162, .99)", "strokeScaleEnabled": False, "strokeWidth": 1,
                          "hitStrokeWidth": 15, "shadowBlur": 10, "shadowColor": "rgba(0,0,0, 0.1)",
                          "shadowOffsetX": -1, "shadowOffsetY": 2, "cornerRadius": 8, "lineJoin": "round",
                          "lineCap": "round"}, "className": "Rect"}, {
                "attrs": {"name": "circle", "x": x_crl, "y": y_crl, "radius": 4, "fill": "rgba(254, 254, 254, 1.0)",
                          "stroke": "rgba(113, 129, 151, .99)", "strokeScaleEnabled": False, "strokeWidth": 1,
                          "hitStrokeWidth": 27}, "className": "Circle"},
                {"attrs": {"name": "lbl", "x": x_trg_lbl_tag, "y": y_trg_lbl_tag}, "className": "Label", "children": [
                    {"attrs": {"fill": "rgba(238, 241, 244, .99)", "width": 20.75732421875, "height": 7},
                     "className": "Tag"}, {
                        "attrs": {"text": f"{ent_type}", "fontSize": 7, "align": "center", "verticalAlign": "middle",
                                  "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"}]}, {
                    "attrs": {"name": "txtCounter", "x": x_views, "y": y_views, "text": f"{views_}",
                              "fontFamily": "Courier", "fontSize": 7, "align": "center",
                              "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"}, {
                    "attrs": {"name": "rectInner", "x": x_inner_rect, "y": y_inner_rect, "width": w_inner_rect,
                              "height": 20, "offsetX": int(w_inner_rect / 2), "offsetY": int(20 / 2),
                              "fill": "rgba(238, 241, 244, .99)", "strokeScaleEnabled": False, "cornerRadius": 4,
                              "dash": [2, 1], "stroke": "rgba(200, 200, 200, .99)", "strokeWidth": 1},
                    "className": "Rect"}, {
                    "attrs": {"name": "txtContent", "x": x_txtContent, "y": y_txtContent, "text": f"{msg_text}",
                              "fontSize": 7, "align": "center", "verticalAlign": "middle",
                              "fill": "rgba(90, 100, 120, 0.99)", "offsetY": 3.5}, "className": "Text"},
                {"attrs": {"name": "svgImage", "x": x_image, "y": y_image, "scaleX": 0.2, "scaleY": 0.2},
                 "className": "Image"}, ]}

        if msg_media:
            json_media = {"attrs": {"name": "groupImage", "x": x_rect, "y": y_rect - 17, "offsetX": 30, "offsetY": 30},
                          "className": "Group", "children": [
                    {"attrs": {"name": "imgJpg", "link": msg_media, "width": 60, "height": 60, "cornerRadius": 4},
                     "className": "Image"}]}
            result[ent_vid]['children'].append(json_media)

        if msg_btns:
            json_btns_children = []

            for msg_btn in msg_btns:
                if msg_btn['i'] in [0, 1, 2]:
                    y_rect_i = y_rect + 12
                    x_rect_txt = x_rect - 2
                    y_rect_txt = y_rect + 7

                    x_btn_crl, y_btn_crl = await x_y_iter_circle(x_rect, y_rect, msg_btn, msg_btns, msg_media)
                elif msg_btn['i'] in [3, 4, 5]:
                    y_rect_i = y_rect + 12 * 2
                    x_rect_txt = x_rect - 2
                    y_rect_txt = y_rect + 7 * 2

                    x_btn_crl, y_btn_crl = await x_y_iter_circle(x_rect, y_rect, msg_btn, msg_btns, msg_media)
                else:
                    y_rect_i = y_rect + 12 * 3
                    x_rect_txt = x_rect - 2
                    y_rect_txt = y_rect + 7 * 3

                    x_btn_crl, y_btn_crl = await x_y_iter_circle(x_rect, y_rect, msg_btn, msg_btns, msg_media)

                # if msg_btn['knd'] == 'web':
                #     logger.info(log_ % f"y_rect_i = {y_rect_i}, x_rect_txt={x_rect_txt}, y_rect_txt={y_rect_txt}, x_btn_crl={x_btn_crl}, y_btn_crl={y_btn_crl}")
                crl_vid = await get_time_time()

                lnk = msg_btn['lbl'] if msg_btn['sort'] == 'keyboard' else msg_btn['lnk']
                if msg_btn['knd'] == 'phone':
                    lnk = 'phone'
                elif msg_btn['knd'] == 'geo':
                    lnk = 'geo'

                sql = f"SELECT TRG_VID, TRG_RIGHTID, TRG_RIGHTTYPE FROM TRG WHERE TRG_CONTENT LIKE '%\"{lnk}\",%'"
                data_trg = await db_select(sql, (), BASE_ENT)
                if not len(data_trg):
                    TRG_VID = TRG_RIGHTID = TRG_RIGHTTYPE = 0
                else:
                    TRG_VID, TRG_RIGHTID, TRG_RIGHTTYPE = data_trg[0]

                out_line = ""
                if TRG_VID and TRG_RIGHTID:
                    x_dest, y_dest = await out_line_x_y(TRG_RIGHTID, result)

                    if x_dest and y_dest:
                        line_vid = await get_time_time()

                        out_line = {"attrs": {"id": line_vid, "name": "line",
                                              "points": [x_btn_crl, y_btn_crl + 4, x_btn_crl, y_dest, x_dest, y_btn_crl,
                                                         x_dest, y_dest], "bezier": True,
                                              "stroke": "rgba(142, 152, 162, .99)", "strokeWidth": 1,
                                              "hitStrokeWidth": 5}, "className": "Line"}
                        out_line = json.dumps(json.dumps(out_line, ensure_ascii=False), ensure_ascii=False)

                item_children = [{
                    "attrs": {"name": "btn", "x": x_rect, "y": y_rect_i, "width": int(w_inner_rect), "height": 10,
                              "offsetX": int(w_inner_rect / 2), "offsetY": 5, "fill": "rgba(238, 241, 244, .99)",
                              "strokeScaleEnabled": False, "cornerRadius": 4, "stroke": "rgba(200, 200, 200, .99)",
                              "strokeWidth": 1}, "className": "Rect"}, {
                    "attrs": {"name": "txt", "x": x_rect_txt, "y": y_rect_txt, "text": f"{msg_btn['lbl']}",
                              "fontSize": 7, "align": "center", "verticalAlign": "middle",
                              "fill": "rgba(90, 100, 120, 0.99)"}, "className": "Text"}, ]

                if msg_btn['knd'] != 'link':
                    # print(f"{out_line=}, {crl_vid=}")
                    # logger.info(log_ % f"sort={msg_btn['sort']}, lnk={msg_btn['lnk']}, lbl={msg_btn['lbl']}")

                    item_children.append({
                        "attrs": {"id": f"{crl_vid}", "name": "crl", "trg_vid": TRG_VID, "out_line": out_line,
                                  "btn_i": msg_btn['i'], "btn_value": f"{msg_btn['lnk']}",
                                  "btn_link": f"{msg_btn['lbl']}", "btn_kind": f"{msg_btn['knd']}",
                                  "btn_sort": f"{msg_btn['sort']}", "x": x_btn_crl, "y": y_btn_crl, "radius": 4,
                                  "fill": "rgba(254, 254, 254, 1.0)", "stroke": "rgba(113, 129, 151, .99)",
                                  "strokeScaleEnabled": False, "strokeWidth": 1, "hitStrokeWidth": 20,
                                  "next_id": f"{TRG_RIGHTID}", "next_type": f"{TRG_RIGHTTYPE}", },
                        "className": "Circle"})
                item = {"attrs": {"name": "button", "i": msg_btn['i'], "lbl": msg_btn['lbl'], "knd": msg_btn['knd'],
                                  "lnk": msg_btn['lnk'], "sort": msg_btn['sort'], }, "className": "Group",
                        "children": item_children}
                json_btns_children.append(item)

            json_btns = {"attrs": {"name": "groupButtons"}, "className": "Group", "children": json_btns_children}
            result[ent_vid]["children"].append(json_btns)

        result[ent_vid] = json.dumps(result[ent_vid], ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def lines_trg_json(state_file, ent_vid, TRG_RIGHTID, TRG_RIGHTTYPE, TRG_LEFTID, TRG_LEFTTYPE):
    result = {}
    try:
        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        out_line = ""
        out_false = ""
        result_vid = json.loads(result[ent_vid])

        if TRG_RIGHTID:
            x, y = await out_line_x_y(TRG_RIGHTID, result)

            if x and y:
                line_vid = await get_time_time()
                x_circle_src = result_vid['children'][1]['attrs']['x']  # 200
                y_circle_src = result_vid['children'][1]['attrs']['y']  # 126

                out_line = {"attrs": {"id": line_vid, "name": "line",
                                      "points": [x_circle_src, y_circle_src, x_circle_src, y, x, y_circle_src, x, y],
                                      "bezier": True, "stroke": "rgba(142, 152, 162, .99)", "strokeWidth": 1,
                                      "hitStrokeWidth": 5}, "className": "Line"}
                out_line = json.dumps(json.dumps(out_line, ensure_ascii=False), ensure_ascii=False)

        if TRG_LEFTID:
            x, y = await out_line_x_y(TRG_RIGHTID, result)

            if x and y:
                line_vid = await get_time_time()
                x_circle_src = result_vid['children'][2]['attrs']['x']
                y_circle_src = result_vid['children'][2]['attrs']['y']

                out_false = {"attrs": {"id": line_vid, "name": "line",
                                       "points": [x_circle_src, y_circle_src, x_circle_src, y, x, y_circle_src, x, y],
                                       "bezier": True, "stroke": "rgba(142, 152, 162, .99)", "strokeWidth": 1,
                                       "hitStrokeWidth": 5}, "className": "Line"}
                out_false = json.dumps(json.dumps(out_false, ensure_ascii=False), ensure_ascii=False)

        result_vid["attrs"]["in_lines"] = []
        result_vid["attrs"]["out_line"] = out_line
        result_vid["attrs"]["out_false"] = out_false
        result_vid["attrs"]["right_id"] = str(TRG_RIGHTID) if TRG_RIGHTID else ''
        result_vid["attrs"]["right_type"] = str(TRG_RIGHTTYPE) if TRG_RIGHTTYPE else ''
        result_vid["attrs"]["left_id"] = str(TRG_LEFTID) if TRG_LEFTID else ''
        result_vid["attrs"]["left_type"] = str(TRG_LEFTTYPE) if TRG_LEFTTYPE else ''
        result[ent_vid] = json.dumps(result_vid, ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def lines_act_json(state_file, ent_vid, ent_nextid, ent_nexttype):
    result = {}
    try:
        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        out_line = ""
        result_vid = json.loads(result[ent_vid])

        x_dst, y_dst = await out_line_x_y(ent_nextid, result)
        if x_dst and y_dst:
            line_vid = await get_time_time()
            x_circle_src = result_vid['children'][1]['attrs']['x']
            y_circle_src = result_vid['children'][1]['attrs']['y']

            out_line = {"attrs": {"id": line_vid, "name": "line",
                                  "points": [x_circle_src, y_circle_src, x_circle_src, y_dst, x_dst, y_circle_src,
                                             x_dst, y_dst], "bezier": True, "stroke": "rgba(142, 152, 162, .99)",
                                  "strokeWidth": 1, "hitStrokeWidth": 5}, "className": "Line"}
            out_line = json.dumps(json.dumps(out_line, ensure_ascii=False), ensure_ascii=False)

        result_vid["attrs"]["in_lines"] = []
        result_vid["attrs"]["out_line"] = out_line
        result_vid["attrs"]["next_id"] = str(ent_nextid) if ent_nextid else ''
        result_vid["attrs"]["next_type"] = str(ent_nexttype) if ent_nexttype else ''
        result[ent_vid] = json.dumps(result_vid, ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def lines_msg_json(state_file, ent_vid, MSG_BUTTONS, ent_nextid, ent_nexttype, BASE_ENT):
    result = {}
    try:
        try:
            with open(state_file) as f:
                result = json.load(f)
        except:
            result = {}

        out_line = ""
        result_vid = json.loads(result[ent_vid])

        x_dst, y_dst = await out_line_x_y(ent_nextid, result)
        if x_dst and y_dst:
            line_vid = await get_time_time()
            x_circle_src = result_vid['children'][1]['attrs']['x']
            y_circle_src = result_vid['children'][1]['attrs']['y']

            out_line = {"attrs": {"id": line_vid, "name": "line",
                                  "points": [x_circle_src, y_circle_src, x_circle_src, y_dst, x_dst, y_circle_src,
                                             x_dst, y_dst], "bezier": True, "stroke": "rgba(142, 152, 162, .99)",
                                  "strokeWidth": 1, "hitStrokeWidth": 5}, "className": "Line"}
            out_line = json.dumps(json.dumps(out_line, ensure_ascii=False), ensure_ascii=False)

        result_vid["attrs"]["in_lines"] = []
        result_vid["attrs"]["out_line"] = out_line
        result_vid["attrs"]["next_id"] = str(ent_nextid) if ent_nextid else ''
        result_vid["attrs"]["next_type"] = str(ent_nexttype) if ent_nexttype else ''

        if MSG_BUTTONS and result_vid["children"][-1]['className'] == 'Group':
            for btn in result_vid["children"][-1]['children']:
                if len(btn['children']) == 3:
                    lnk = btn['attrs']['lbl'] if btn['attrs']['sort'] == 'keyboard' else btn['attrs']['lnk']
                    if btn['attrs']['knd'] == 'phone':
                        lnk = 'phone'
                    elif btn['attrs']['knd'] == 'geo':
                        lnk = 'geo'

                    sql = f"SELECT TRG_VID, TRG_RIGHTID, TRG_RIGHTTYPE FROM TRG WHERE TRG_CONTENT LIKE '%\"{lnk}\",%'"
                    data_trg = await db_select(sql, (), BASE_ENT)
                    if not len(data_trg):
                        TRG_VID = TRG_RIGHTID = TRG_RIGHTTYPE = 0
                    else:
                        TRG_VID, TRG_RIGHTID, TRG_RIGHTTYPE = data_trg[0]

                    if TRG_VID and TRG_RIGHTID:
                        # out_line = ""
                        x_btn_crl = btn['children'][-1]['attrs']['x']
                        y_btn_crl = btn['children'][-1]['attrs']['y']
                        crl_vid = btn['children'][-1]['attrs']['id']
                        btn_i = btn['children'][-1]['attrs']['btn_i']
                        btn_value = btn['children'][-1]['attrs']['btn_value']
                        btn_link = btn['children'][-1]['attrs']['btn_link']
                        btn_kind = btn['children'][-1]['attrs']['btn_kind']
                        btn_sort = btn['children'][-1]['attrs']['btn_sort']

                        x_dest, y_dest = await out_line_x_y(TRG_RIGHTID, result)

                        if x_dest and y_dest:
                            line_vid = await get_time_time()

                            out_line = {"attrs": {"id": line_vid, "name": "line",
                                                  "points": [x_btn_crl, y_btn_crl + 4, x_btn_crl, y_dest, x_dest,
                                                             y_btn_crl, x_dest, y_dest], "bezier": True,
                                                  "stroke": "rgba(142, 152, 162, .99)", "strokeWidth": 1,
                                                  "hitStrokeWidth": 5}, "className": "Line"}
                            out_line = json.dumps(json.dumps(out_line, ensure_ascii=False), ensure_ascii=False)
                            item_children = {
                                "attrs": {"id": f"{crl_vid}", "name": "crl", "trg_vid": ent_vid, "out_line": out_line,
                                          "btn_i": btn_i, "btn_value": btn_value, "btn_link": btn_link,
                                          "btn_kind": btn_kind, "btn_sort": btn_sort, "x": x_btn_crl, "y": y_btn_crl,
                                          "radius": 4, "fill": "rgba(254, 254, 254, 1.0)",
                                          "stroke": "rgba(113, 129, 151, .99)", "strokeScaleEnabled": False,
                                          "strokeWidth": 1, "hitStrokeWidth": 20, "next_id": f"{TRG_RIGHTID}",
                                          "next_type": f"{TRG_RIGHTTYPE}", }, "className": "Circle"}

                            btn['children'][-1] = item_children  # btn['children'][-1]['attrs']['out_line'] = out_line

        result[ent_vid] = json.dumps(result_vid, ensure_ascii=False)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def x_y_iter_circle(x_rect, y_rect, msg_btn, msg_btns, msg_media):
    x_btn_crl = x_rect
    y_btn_crl = y_rect
    try:
        cell_row = []
        if msg_btn['i'] in [0, 1, 2]:
            cell_row = [0, 1, 2]
        elif msg_btn['i'] in [3, 4, 5]:
            cell_row = [3, 4, 5]
        elif msg_btn['i'] in [6, 7, 8]:
            cell_row = [6, 7, 8]

        row_cnt = await get_count_of_rows(msg_btns)

        if len(row_cnt) == 1:
            y_btn_crl = y_rect + 5 * 2
        elif len(row_cnt) == 2:
            first_key = list(row_cnt.keys())[0]
            if msg_btn in row_cnt[first_key]:
                y_btn_crl = y_rect + 5 * 2
            else:
                y_btn_crl = y_rect + 5 * 5
        elif len(row_cnt) == 3:
            first_key = list(row_cnt.keys())[0]
            second_key = list(row_cnt.keys())[1]

            if msg_btn in row_cnt[first_key]:
                y_btn_crl = y_rect
            elif msg_btn in row_cnt[second_key]:
                y_btn_crl = y_rect + 5 * 2
            else:
                y_btn_crl = y_rect + 5 * 5

        if msg_media:
            y_btn_crl = y_btn_crl + 30

        cell_ixs = [it for it in msg_btns if it['i'] in cell_row]

        if len(cell_ixs) == 1:
            x_btn_crl = x_rect + 5 * 9
        elif len(cell_ixs) == 2:
            if msg_btn['i'] == cell_ixs[0]['i']:
                x_btn_crl = x_rect - 5
            else:
                x_btn_crl = x_rect + 5 * 9
        elif len(cell_ixs) == 3:
            if msg_btn['i'] == cell_ixs[0]['i']:
                x_btn_crl = x_rect - 5 * 4
            elif msg_btn['i'] == cell_ixs[1]['i']:
                x_btn_crl = x_rect + 5 * 2 + 5 / 2
            else:
                x_btn_crl = x_rect + 5 * 9
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return x_btn_crl, y_btn_crl


async def get_x_y_for_trg(state_file, width, height, from_x=0, from_y=0, from_w=0, from_h=0, to_vid=0, to_w=0, to_h=0):
    to_x = from_x + width / 2 + from_w / 2 - 10
    to_y = kjs + 75
    try:
        try:
            with open(state_file) as f:
                vids = json.load(f)
        except:
            vids = {}
        if not len(vids) or not to_w: return

        if to_vid and to_vid in vids:
            to_vid = json.loads(vids[to_vid])
            to_x = to_vid['children'][0]['attrs']['x']
            to_y = to_vid['children'][0]['attrs']['y']
            return

        cell_i = 1
        # delta = 30

        while True:
            virtual_cells = [(from_x + (width / 2 + from_w / 2) * cell_i - 10, from_y), ]
            cell_i += 1

            for virt_cell in virtual_cells:
                virt_x, virt_y = virt_cell

                virt_x_min = virt_x - to_w / 2
                virt_x_max = virt_x + to_w / 2
                virt_y_min = virt_y - to_h / 2
                virt_y_max = virt_y + to_h / 2

                chk_cnt = 0
                cnt_vids = len(vids.items())
                for vid, vid_values in vids.items():
                    tmp_params = json.loads(vid_values)
                    tmp_w = tmp_params['attrs']['width']
                    tmp_h = tmp_params['children'][0]['attrs']['height']
                    tmp_x = tmp_params['children'][0]['attrs']['x']
                    tmp_y = tmp_params['children'][0]['attrs']['y']

                    tmp_x_min = tmp_x - tmp_w / 2
                    tmp_x_max = tmp_x + tmp_w / 2
                    tmp_y_min = tmp_y - tmp_h / 2
                    tmp_y_max = tmp_y + tmp_h / 2

                    x_intersect = not (virt_x_max < tmp_x_min or virt_x_min > tmp_x_max)
                    y_intersect = not (virt_y_max < tmp_y_min or virt_y_min > tmp_y_max)
                    if x_intersect and y_intersect: break
                    chk_cnt += 1

                if cnt_vids and cnt_vids == chk_cnt:
                    to_x = virt_x
                    to_y = virt_y
                    return
    except Exception as e:
        logger.info(log_ % str(e) + f"{height=}, {from_x=}, {from_h=}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return to_x, to_y


async def get_x_y_for_vid(state_file, width, height, from_x=0, from_y=0, from_w=0, from_h=0, to_vid=0, to_w=0, to_h=0):
    to_x = kjs + int(width / 2)
    to_y = kjs + 75
    try:
        try:
            with open(state_file) as f:
                vids = json.load(f)
        except:
            vids = {}
        if not len(vids) or not from_x:
            print(f"{to_x=}, {to_y=}, {kjs=}, {width=}")
            return

        if to_vid and to_vid in vids:
            to_vid = json.loads(vids[to_vid])
            to_x = to_vid['children'][0]['attrs']['x']
            to_y = to_vid['children'][0]['attrs']['y']
            return

        cell_i = 1
        delta = 30

        while True:
            virtual_cells = [(from_x, from_y + (from_h / 2 + to_h / 2 + delta) * cell_i), (
                from_x - (from_w / 2 + to_w / 2 + delta) * cell_i, from_y + (from_h / 2 + to_h / 2 + delta) * cell_i), (
                                 from_x + (from_w / 2 + to_w / 2 + delta) * cell_i,
                                 from_y + (from_h / 2 + to_h / 2 + delta) * cell_i), ]
            cell_i += 1

            for virt_cell in virtual_cells:
                virt_x, virt_y = virt_cell

                virt_x_min = virt_x - to_w / 2
                virt_x_max = virt_x + to_w / 2
                virt_y_min = virt_y - to_h / 2
                virt_y_max = virt_y + to_h / 2

                chk_cnt = 0
                cnt_vids = len(vids.items())
                for vid, vid_values in vids.items():
                    tmp_params = json.loads(vid_values)
                    tmp_w = tmp_params['attrs']['width']
                    tmp_h = tmp_params['children'][0]['attrs']['height']
                    tmp_x = tmp_params['children'][0]['attrs']['x']
                    tmp_y = tmp_params['children'][0]['attrs']['y']

                    tmp_x_min = tmp_x - tmp_w / 2
                    tmp_x_max = tmp_x + tmp_w / 2
                    tmp_y_min = tmp_y - tmp_h / 2
                    tmp_y_max = tmp_y + tmp_h / 2

                    x_intersect = not (virt_x_max < tmp_x_min or virt_x_min > tmp_x_max)
                    y_intersect = not (virt_y_max < tmp_y_min or virt_y_min > tmp_y_max)
                    if x_intersect and y_intersect: break
                    chk_cnt += 1

                if cnt_vids and cnt_vids == chk_cnt:
                    to_x = virt_x
                    to_y = virt_y
                    return
    except Exception as e:
        logger.info(log_ % str(e) + f"{height=}, {from_x=}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return to_x, to_y



async def get_x_y_for_btn(width, height, vids, from_vid, to_vid, to_w, to_h):
    to_x = int(width / 2) + kjs
    to_y = 10075
    try:
        if to_vid and to_vid in vids:
            to_vid = json.loads(vids[to_vid])
            to_x = to_vid['children'][0]['attrs']['x']
            to_y = to_vid['children'][0]['attrs']['y']
            return

        from_vid = json.loads(vids[from_vid])
        from_w = from_vid['attrs']['width']
        from_h = from_vid['children'][0]['attrs']['height']
        from_x = from_vid['children'][0]['attrs']['x']
        from_y = from_vid['children'][0]['attrs']['y']

        cell_i = 1  # влево [1 2 3], вправо [1 2 3], вниз [1 2 3], типа 9
        delta = 20

        while True:
            virtual_cells = [(from_x - (from_w / 2 + to_w / 2 + delta) * cell_i, from_y), (
                from_x - (from_w / 2 + to_w / 2 + delta) * cell_i, from_y - (from_h / 2 + to_h / 2 + delta) * cell_i), (
                                 from_x - (from_w / 2 + to_w / 2 + delta) * cell_i,
                                 from_y + (from_h / 2 + to_h / 2 + delta) * cell_i),

                             (from_x, from_y + (from_h / 2 + to_h / 2 + delta) * cell_i),

                             (from_x + (from_w / 2 + to_w / 2 + delta) * cell_i, from_y), (
                                 from_x + (from_w / 2 + to_w / 2 + delta) * cell_i,
                                 from_y - (from_h / 2 + to_h / 2 + delta) * cell_i), (
                                 from_x + (from_w / 2 + to_w / 2 + delta) * cell_i,
                                 from_y + (from_h / 2 + to_h / 2 + delta) * cell_i), ]
            cell_i += 1

            for virt_cell in virtual_cells:
                virt_x, virt_y = virt_cell

                virt_x_min = virt_x - to_w / 2
                virt_x_max = virt_x + to_w / 2
                virt_y_min = virt_y - to_h / 2
                virt_y_max = virt_y + to_h / 2

                chk_cnt = 0
                cnt_vids = len(vids.items())
                for vid, vid_values in vids.items():
                    # print(vid)
                    tmp_params = json.loads(vid_values)
                    tmp_w = tmp_params['attrs']['width']
                    tmp_h = tmp_params['children'][0]['attrs']['height']
                    tmp_x = tmp_params['children'][0]['attrs']['x']
                    tmp_y = tmp_params['children'][0]['attrs']['y']

                    tmp_x_min = tmp_x - tmp_w / 2
                    tmp_x_max = tmp_x + tmp_w / 2
                    tmp_y_min = tmp_y - tmp_h / 2
                    tmp_y_max = tmp_y + tmp_h / 2

                    x_intersect = not (virt_x_max < tmp_x_min or virt_x_min > tmp_x_max)
                    y_intersect = not (virt_y_max < tmp_y_min or virt_y_min > tmp_y_max)
                    if x_intersect and y_intersect: break
                    chk_cnt += 1  # print('не пересекаются')  # vid_values

                if cnt_vids and cnt_vids == chk_cnt:
                    to_x = virt_x
                    to_y = virt_y
                    return
    except Exception as e:
        logger.info(log_ % str(e) + f"{height=}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return to_x, to_y



async def get_txt_content(content, lz, mode, ent_type=None):
    result = ''
    try:
        if not content: return
        val_ = ''
        oper = ''

        if mode == 'trg':
            content = content if isinstance(content, list) else ast.literal_eval(content)

            for trg in content:
                if trg['name'] == 'cmd':
                    utm_ = trg['utm']
                    if utm_ == '1':
                        utm_ = '✅'
                    elif utm_ == '0':
                        utm_ = '☑️'

                    val_ = f"{trg['value']} {utm_}"
                elif trg['name'] == 'rct':
                    val_ = trg['value']
                elif trg['name'] == 'txt':
                    val_ = trg['value']
                elif trg['name'] == 'btn':
                    val_ = trg['link']
                elif trg['name'] == 'var':
                    if trg['value']['oper'] == 'eq':
                        oper = ' == '
                    elif trg['value']['oper'] == 'neq':
                        oper = ' != '
                    elif trg['value']['oper'] == 'lt':
                        oper = ' < '
                    elif trg['value']['oper'] == 'lte':
                        oper = ' ≤ '
                    elif trg['value']['oper'] == 'gt':
                        oper = ' > '
                    elif trg['value']['oper'] == 'gte':
                        oper = ' ≥ '
                    elif trg['value']['oper'] == 'in':
                        oper = ' in '
                    elif trg['value']['oper'] == 'nin':
                        oper = ' not in '

                    right = trg['value']['right']
                    # if ':' in right and '_T' in right: right = right.replace('_T', '')

                    val_ = f"{trg['value']['left']}{oper}{right}"
                elif trg['name'] == 'lst':
                    if trg['value']['oper'] == 'eq':
                        oper = ' == '
                    elif trg['value']['oper'] == 'include':
                        oper = ' include '
                    elif trg['value']['oper'] == 'notinclude':
                        oper = ' not include '

                    val_ = f"{trg['value']['left']}{oper}{trg['value']['right']}"
                break
        elif mode == 'act':
            content = content if isinstance(content, list) else ast.literal_eval(content)

            for trg in content:
                if trg['name'] == 'dly':
                    val_ = f"{trg['value']} {l_sec[lz]}"
                elif trg['name'] == 'wait':
                    val_ = l_act_wait_title[lz]
                elif trg['name'] == 'req':
                    val_ = trg['value']
                elif trg['name'] == 'unpin':
                    val_ = l_act_wait_title[lz]
                elif trg['name'] == 'var':
                    if trg['value']['oper'] == 'assign':
                        oper = ' = '
                    elif trg['value']['oper'] == 'plus':
                        oper = ' += '
                    elif trg['value']['oper'] == 'minus':
                        oper = ' -= '
                    elif trg['value']['oper'] == 'len':
                        oper = ' len of '
                    elif trg['value']['oper'] == 'random':
                        oper = ' random '

                    val_ = f"{trg['value']['left']}{oper}{trg['value']['right']}"
                elif trg['name'] == 'lst':
                    if trg['value']['oper'] == 'assign':
                        oper = ' = '
                    elif trg['value']['oper'] == 'add':
                        oper = ' add '
                    elif trg['value']['oper'] == 'remove':
                        oper = ' remove '

                    val_ = f"{trg['value']['left']}{oper}{trg['value']['right']}"
                break
        elif mode == 'msg':
            if ent_type == l_msg_quiz[lz]:
                val_ = content.strip().replace('\n', ' | ')
            else:
                val_ = content

        result = val_[:22].replace('\n', '').strip()
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result




async def out_line_x_y(next_id, result):
    x = y = None
    try:
        if not next_id: return

        for k, v in result.items():
            if k != next_id: continue

            try:
                ent_json = json.loads(v)
            except:
                ent_json = v

            x = ent_json['children'][0]['attrs']['x']
            y = ent_json['children'][0]['attrs']['y']
            break
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return x, y


async def in_lines_json(state_file, BASE_ENT):
    in_lines = []
    try:
        with open(state_file) as f:
            result = json.load(f)

        for k, v in result.items():
            try:
                result_vid = json.loads(v)
                in_lines = await in_lines_x_y(k, result, BASE_ENT)

                # print(f"{in_lines=}")
                result_vid['attrs']['in_lines'] = in_lines
                result[k] = json.dumps(result_vid, ensure_ascii=False)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return in_lines


async def in_lines_x_y(ent_vid, result, BASE_ENT):
    in_lines = []
    try:
        sql = "SELECT TRG_VID, TRG_CONTENT, TRG_RIGHTID FROM TRG WHERE TRG_RIGHTID=?"
        data_trg = await db_select(sql, (ent_vid,), BASE_ENT)
        for item_trg in data_trg:
            TRG_VID, TRG_CONTENT, TRG_RIGHTID = item_trg

            for k, v in result.items():
                if k != TRG_VID: continue
                ent_json = json.loads(v)
                in_lines.append(ent_json['attrs']['out_line'])

            for k, v in result.items():
                ent_json = json.loads(v)
                if not (ent_json['attrs']['sub_name'] == 'MSG' and ent_json['children'][-1][
                    'className'] == 'Group'): continue

                for item in ent_json['children'][-1]['children']:
                    if getattr(item, 'children', None) and len(item['children']) == 3 and item['children'][-1]['attrs'][
                        'trg_vid'] == TRG_VID:
                        in_lines.append(item['children'][-1]['attrs']['out_line'])

        sql = "SELECT TRG_VID FROM TRG WHERE TRG_LEFTID=?"
        data_trg = await db_select(sql, (ent_vid,), BASE_ENT)
        for item_trg in data_trg:
            TRG_VID = item_trg[0]

            for k, v in result.items():
                if k != TRG_VID: continue
                ent_json = json.loads(v)
                in_lines.append(ent_json['attrs']['out_false'])

        sql = "SELECT ACT_VID FROM ACT WHERE ACT_NEXTID=?"
        data_act = await db_select(sql, (ent_vid,), BASE_ENT)
        for item_act in data_act:
            ACT_VID = item_act[0]

            for k, v in result.items():
                if k != ACT_VID: continue
                ent_json = json.loads(v)
                in_lines.append(ent_json['attrs']['out_line'])

        sql = "SELECT MSG_VID FROM MSG WHERE MSG_NEXTID=?"
        data_msg = await db_select(sql, (ent_vid,), BASE_ENT)
        for item_msg in data_msg:
            MSG_VID = item_msg[0]

            for k, v in result.items():
                if k != MSG_VID: continue
                ent_json = json.loads(v)
                in_lines.append(ent_json['attrs']['out_line'])
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return in_lines


async def get_count_of_rows(msg_btns):
    result = {}
    try:
        for it in msg_btns:
            if it['i'] in [0, 1, 2]:
                if 0 in result:
                    result[0].append(it)
                else:
                    result[0] = [it]
            elif it['i'] in [3, 4, 5]:
                if 1 in result:
                    result[1].append(it)
                else:
                    result[1] = [it]
            elif it['i'] in [6, 7, 8]:
                if 2 in result:
                    result[2].append(it)
                else:
                    result[2] = [it]
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result
# endregion


# region neuro
async def get_openai_key(file_keys):
    result = None
    try:
        async with aiofiles.open(file_keys, 'r') as f:
            lines = await f.readlines()

        lines_new = []
        random.shuffle(lines)
        for key_ in lines:
            try:
                if key_.strip() == '': continue
                result = key_.strip()
                lines_new.append(key_.strip() + '\n')
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        async with aiofiles.open(file_keys, 'w') as f:
            await f.writelines(lines_new)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def del_openai_key(del_key, file_keys):
    try:
        async with aiofiles.open(file_keys, 'r') as f:
            lines = await f.readlines()

        lines_new = []
        random.shuffle(lines)
        for key_ in lines:
            try:
                if key_.strip() == del_key: continue
                lines_new.append(key_.strip() + '\n')
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        async with aiofiles.open(file_keys, 'w') as f:
            await f.writelines(lines_new)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def get_txt_wrapper(file_keys):
    result = None
    try:
        async with aiofiles.open(file_keys, 'r') as f:
            lines = await f.readlines()

        lines_new = []
        random.shuffle(lines)
        for key_ in lines:
            try:
                if key_.strip() == '': continue
                result = key_.strip()
                lines_new.append(key_.strip() + '\n')
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        async with aiofiles.open(file_keys, 'w') as f:
            await f.writelines(lines_new)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_time_time(is_lnk=False):
    result = None
    try:
        if is_lnk:
            result = str(int(time.time() * (1000 ** 1)) + random.randint(100, 999))
        else:
            result = str(int(time.time() * (1000 ** 2)) + random.randint(100, 999))
        await asyncio.sleep(0.05)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def train_ent_chatgpt(bot, ENT_TID, ENT_USERNAME, ENT_TYPE, BASE_ENT, lz, prompt='', BOT_TOKEN_=None):
    result_txt = [{'role': 'system', 'content': f'You are a helpful assistant for Telegram {ENT_TYPE}.'},
                  {'role': 'assistant', 'content': 'ok'}, ]
    result_img = ''
    try:
        # region init
        if ENT_TYPE == 'bot':
            extra_bot = Bot(token=BOT_TOKEN_)
            short = await extra_bot.get_my_short_description()
            short = short.short_description if short.short_description else ''
            desc = await extra_bot.get_my_description()
            desc = desc.description if desc.description else ''

            bot_info = f'Now I give you some details about this telegram bot: @username is `@{ENT_USERNAME}`, ' \
                       f'description is `{desc}`. ' \
                       f'And short description is `{short}`'
            result_txt.append({'role': 'user', 'content': bot_info}),
            result_img = f"{desc}, {short}"
            await extra_bot.session.close()
        elif ENT_TYPE in ['channel', 'group', 'supergroup']:
            get_chat_ = await bot.get_chat(int(ENT_TID))
            info_ = f'Now I give you some details about this telegram {ENT_TYPE}: link is `{ENT_USERNAME}`, ' \
                    f'description is `{get_chat_.description}`, title is `{get_chat_.title}`'
            result_txt.append({'role': 'user', 'content': info_}),
            result_img = f"{get_chat_.description}, {get_chat_.title}"
        # endregion

        if ENT_TYPE == 'bot':
            # region MSG
            sql = "SELECT MSG_TEXT, MSG_BUTTONS FROM MSG"
            data = await db_select(sql, (), BASE_ENT)

            for item in data[:5]:
                try:
                    MSG_TEXT, MSG_BUTTONS = item
                    MSG_BUTTONS = ast.literal_eval(MSG_BUTTONS) if MSG_BUTTONS else []
                    MSG_BUTTONS = ', '.join([it['lbl'] for it in MSG_BUTTONS if it and 'lbl' in it])

                    if MSG_TEXT:
                        result_txt.append({'role': 'user',
                                           'content': f'There is a message of this telegram {ENT_TYPE}: {MSG_TEXT[:128]}'})  # result_img = f"{result_img}{MSG_TEXT}\n"
                    if MSG_BUTTONS:
                        result_txt.append({'role': 'user',
                                           'content': f'There are some buttons of this telegram {ENT_TYPE}: {MSG_BUTTONS}'})  # result_img = f"{result_img}{MSG_BUTTONS}\n"
                except Exception as e:
                    logger.info(log_ % str(e))
                    await asyncio.sleep(round(random.uniform(0, 1), 2))  # endregion
        elif ENT_TYPE in ['channel', 'group']:
            sql = "SELECT CHANNEL_LASTMSG FROM CHANNEL WHERE ENT_TID=?"
            data_chn = await db_select(sql, (ENT_TID,), BASE_ENT)
            CHANNEL_LASTMSG = data_chn[0][0]

            if CHANNEL_LASTMSG:
                result_txt.append({'role': 'user',
                                   'content': f'There is a message of this telegram {ENT_TYPE}: {CHANNEL_LASTMSG}'})  # result_img = f"{result_img}. {CHANNEL_LASTMSG[:32]}\n"

        # region POST
        sql = "SELECT POST_TEXT, POST_BUTTON FROM POST"
        data = await db_select(sql, (), BASE_ENT)
        data = data[:5]

        for item in data:
            try:
                POST_TEXT, POST_BUTTON = item

                if POST_TEXT:
                    result_txt.append({'role': 'user',
                                       'content': f'There is a message of this telegram {ENT_TYPE}: {POST_TEXT[:64]}'})
                if POST_BUTTON:
                    result_txt.append({'role': 'user',
                                       'content': f'There are some buttons of this telegram {ENT_TYPE}: {POST_BUTTON}'})
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
        # endregion

        result_txt.append(
            {'role': 'user', 'content': f'So, this is all the information that exists about this {ENT_TYPE}. '
                                        'Your task is to generate new marketing text no more than 1024 symbols'})

        if prompt:
            result_txt.append({'role': 'user', 'content': prompt})
            prompt = f"Extra prompt: {prompt}"

        result_txt.append({'role': 'user', 'content': f'. Please give answer in ISO language code: `{lz}`'})
        result_img = f"{result_img}. {prompt}, {extra_prompt}"
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result_txt, result_img


async def pst_gen_ent(bot, chat_id, state, lc, lz, POST_TYPE, ENT_TID, ENT_TYPE, ENT_USERNAME, ENT_TITLE, MEDIA_D,
                      EXTRA_D, prompt='', ENT_TOKEN_=None):
    result = None
    try:
        if prompt in ['➡️️ Next', '/Next']: prompt = ''
        BASE_ENT = os.path.join(MEDIA_D, str(ENT_TID), f"{str(ENT_TID)}.db")
        prompt_txt, prompt_img = await train_ent_chatgpt(bot, ENT_TID, ENT_USERNAME, ENT_TYPE, BASE_ENT, lz, prompt,
                                                         ENT_TOKEN_)
        openai_keys = os.path.join(EXTRA_D, 'openai_keys.txt')
        templ = os.path.join(MEDIA_D, str(ENT_TID), datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f'))
        POST_FIDNOTE = None

        if POST_TYPE == 'text':
            # print(f"{prompt_txt=}")
            lst = await outsource_handle({'type': 'txt', 'prompt': prompt_txt}, openai_keys)
            if not len(lst): return
            res = lst[0]['answer']
            print(f"{res=}")
            await state.update_data(POST_TEXT=res.strip())
        elif POST_TYPE in ['photo', 'gif', 'sticker', 'video', 'telescope']:
            lst = await outsource_handle({'type': 'img', 'prompt': prompt_img}, openai_keys)
            if not len(lst): return

            dst = os.path.join(MEDIA_D, str(ENT_TID), f"{templ}.png")
            async with aiohttp.ClientSession() as session:
                async with session.get(lst[0]['answer']) as response:
                    res = await response.read()

                    async with aiofiles.open(dst, 'wb') as f:
                        await f.write(res)

            if POST_TYPE == 'gif':
                dst_gif = f"{templ}.gif"
                dst_gif = await convert_png_to_gif(dst, dst_gif)

                POST_LNK = await get_tgph_link(dst)
                res = await bot.send_animation(chat_id=chat_id, animation=types.FSInputFile(dst_gif))
                if os.path.exists(dst_gif): os.remove(dst_gif)

                POST_TYPE = 'animation'
                POST_FID = res.animation.file_id
                POST_FILENAME = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.gif')}"
            elif POST_TYPE == 'sticker':
                dst_webp = f"{templ}.webp"
                image = Image.open(dst)
                image.save(dst_webp, format="webp", quality=30)

                POST_LNK = await get_tgph_link(dst)
                res = await bot.send_sticker(chat_id=chat_id, sticker=types.FSInputFile(dst_webp))
                if os.path.exists(dst_webp): os.remove(dst_webp)

                POST_TYPE = 'sticker'
                POST_FID = res.sticker.file_id
                POST_FILENAME = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.webp')}"
            elif POST_TYPE == 'video':
                dst_mp4 = f"{templ}.mp4"
                dst_mp4 = await convert_png_to_mp4(ENT_TID, dst, dst_mp4, MEDIA_D)

                POST_LNK = await get_tgph_link(dst_mp4)
                res = await bot.send_video(chat_id=chat_id, video=types.FSInputFile(dst_mp4))
                if os.path.exists(dst_mp4): os.remove(dst_mp4)

                POST_TYPE = 'video'
                POST_FID = res.video.file_id
                POST_FILENAME = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')}"
            elif POST_TYPE == 'telescope':
                dst_new = os.path.join(MEDIA_D, str(ENT_TID),
                                       datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.png'))
                img = Image.open(dst)
                new_size = (640, 640)
                resized_img = img.resize(new_size)
                resized_img.save(dst_new)

                dst_mp4 = f"{templ}.mp4"
                dst_mp4 = await convert_png_to_mp4(ENT_TID, dst_new, dst_mp4, MEDIA_D)
                POST_LNK = await get_tgph_link(dst_mp4)

                res = await bot.send_video_note(chat_id=chat_id, video_note=types.FSInputFile(dst_mp4))
                res_note = await bot.send_video(chat_id=chat_id, video=types.FSInputFile(dst_mp4))
                await bot.delete_message(chat_id, res_note.message_id)
                if os.path.exists(dst_mp4): os.remove(dst_mp4)
                if os.path.exists(dst_new): os.remove(dst_new)

                POST_TYPE = 'video_note'
                POST_FID = res.video_note.file_id
                POST_FIDNOTE = res_note.video.file_id
                POST_FILENAME = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')}"
            else:
                POST_LNK = await get_tgph_link(dst)
                res = await bot.send_photo(chat_id=chat_id, photo=types.FSInputFile(dst))

                POST_TYPE = 'photo'
                POST_FID = res.photo[-1].file_id
                POST_FILENAME = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.png')}"

            await bot.delete_message(chat_id, res.message_id)
            if dst and os.path.exists(dst): os.remove(dst)

            await state.update_data(POST_TYPE=POST_TYPE, POST_LNK=POST_LNK, POST_FILENAME=POST_FILENAME,
                                    POST_FID=POST_FID, POST_FIDNOTE=POST_FIDNOTE)
        elif POST_TYPE in ['audio', 'voice']:
            lst = await outsource_handle({'type': 'txt', 'prompt': prompt_txt}, openai_keys)
            if not len(lst): return
            MSG_TEXT = lst[0]['answer']
            MSG_TEXT = await format_text(MSG_TEXT)
            print(f"{MSG_TEXT=}")
            lst = await outsource_handle(
                {'type': 'tts', 'prompt': MSG_TEXT, 'lc': lc, 'dir_name': os.path.join(MEDIA_D, str(ENT_TID))},
                openai_keys)
            if not len(lst): return

            dst = lst[0]['answer']
            if POST_TYPE == 'audio':
                res = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(dst),
                                           thumbnail=types.FSInputFile(os.path.join(EXTRA_D, 'img.jpg')),
                                           title=ENT_TITLE, performer=ENT_USERNAME, disable_notification=True)
                POST_FID = res.audio.file_id
            else:
                res = await bot.send_voice(chat_id=chat_id, voice=types.FSInputFile(dst), disable_notification=True)
                POST_FID = res.voice.file_id

                res_note = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(dst),
                                                thumbnail=types.FSInputFile(os.path.join(EXTRA_D, 'img.jpg')),
                                                title=ENT_TITLE, performer=ENT_USERNAME, disable_notification=True)
                await bot.delete_message(chat_id, res_note.message_id)

                if res_note.audio:
                    POST_FIDNOTE = res_note.audio.file_id
                else:
                    audio = AudioFileClip(dst)
                    video_clip = VideoClip(lambda t: np.zeros((480, 640, 3), dtype=np.uint8), duration=audio.duration)
                    video_clip = video_clip.set_audio(audio)
                    file_name_video = dst[:dst.rfind('.')] + '.mp4'
                    video_clip.write_videofile(file_name_video, codec="libx264", audio_codec="aac", fps=24)

                    res_note = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(dst),
                                                    thumbnail=types.FSInputFile(os.path.join(EXTRA_D, 'img.jpg')),
                                                    title=ENT_TITLE, performer=ENT_USERNAME, disable_notification=True)
                    await bot.delete_message(chat_id, res_note.message_id)
                    if os.path.exists(file_name_video): os.remove(file_name_video)
                    if res_note.audio: POST_FIDNOTE = res_note.audio.file_id
            await bot.delete_message(chat_id, res.message_id)

            POST_LNK = None
            try:
                audio = AudioFileClip(dst)
                video_clip = VideoClip(lambda t: np.zeros((480, 640, 3), dtype=np.uint8), duration=audio.duration)
                video_clip = video_clip.set_audio(audio)
                file_name_video = dst[:dst.rfind('.')] + '.mp4'
                video_clip.write_videofile(file_name_video, codec="libx264", audio_codec="aac", fps=24)
                POST_LNK = await get_tgph_link(file_name_video)
                if os.path.exists(file_name_video): os.remove(file_name_video)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
            finally:
                pass
            if os.path.exists(dst): os.remove(dst)

            print(f"{POST_LNK=}")
            await state.update_data(POST_TYPE=POST_TYPE, POST_LNK=POST_LNK, POST_FILENAME=os.path.basename(dst),
                                    POST_FID=POST_FID, POST_FIDNOTE=POST_FIDNOTE)
        else:
            lst = await outsource_handle({'type': 'txt', 'prompt': prompt_txt}, openai_keys)
            if not len(lst): return
            MSG_TEXT = lst[0]['answer']

            dst_txt = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.txt')
            async with aiofiles.open(dst_txt, 'w') as f:
                await f.write(str(MSG_TEXT))

            dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.zip')
            dst = os.path.join(MEDIA_D, str(ENT_TID), dt_)
            with zipfile.ZipFile(dst, 'w') as zipf:
                zipf.write(dst_txt, arcname=f'%d-%m-%Y_%H-%M-%S-%f.txt')
            if os.path.exists(dst_txt): os.remove(dst_txt)

            res = await bot.send_document(chat_id=chat_id, document=types.FSInputFile(dst),
                                          thumbnail=types.FSInputFile(os.path.join(EXTRA_D, 'parse.jpg')),
                                          disable_notification=True, disable_content_type_detection=True)
            await bot.delete_message(chat_id, res.message_id)
            POST_FID = res.document.file_id
            if os.path.exists(dst): os.remove(dst)

            await state.update_data(POST_TYPE=POST_TYPE, POST_FILENAME=os.path.basename(dst), POST_FID=POST_FID)

        result = True
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def recognize_speech(chat_id, lc, MEDIA_D, file_name, model='base'):
    result = text = file_wav = None
    try:
        # try:
        #     model = whisper.load_model(model)
        #     tmp = model.transcribe(file_name)
        #     text = tmp['text']
        # except Exception as e:
        #     logger.info(log_ % f"whisper error: {e}")

        if not text or text == '':
            ext = file_name.split('.')[-1]
            recognizer = sr.Recognizer()
            file_wav = os.path.join(MEDIA_D, f"{chat_id}.wav")

            try:
                if ext == 'mp3':
                    audio = AudioSegment.from_mp3(file_name)
                elif ext == 'ogg':
                    audio = AudioSegment.from_ogg(file_name)
                else:
                    audio = AudioSegment.from_file(file_name, format=ext)
                audio.export(file_wav, format="wav")
            except:
                video_clip = mp.VideoFileClip(file_name)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(file_wav, codec='pcm_s16le')
                audio_clip.close()
                video_clip.close()

            with sr.AudioFile(file_wav) as source:
                try:
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language=lc)
                except:
                    pass

        if not text or text == '': raise Exception
        result = text.strip()
        logger.info(log_ % f"recognition: {text[:32]}")
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        if file_name and os.path.exists(file_name): os.remove(file_name)
        if file_wav and os.path.exists(file_wav): os.remove(file_wav)
        return result


async def g4f_chat_completion(result_txt):
    result = None
    try:
        logger.info(log_ % f"g4f starting...\n{result_txt[-1]}")

        cnt = 1
        while cnt >= 0:
            try:
                result = await g4f.ChatCompletion.create_async(model=g4f.models.default, messages=result_txt, )
                # provider=g4f.Provider.Bing)
                if not result: raise Exception
                if 'bing' in result.lower() and ':' in result: result = result[result.find(':') + 1:]
                if '1024' in result.lower() and ':' in result: result = result[result.find(':') + 1:]
                if 'bing' in result.lower() and '.' in result: result = result[result.find('.') + 1:]
                if '\n' in result:
                    res = result.split('\n\n')[0]
                    if '[1]:' in res:
                        ix = result.find('\n\n')
                        result = result[ix:].strip()

                    if '[3]:' in result:
                        result = result.split('[3]:')[-1]

                    if '[4]:' in result:
                        result = result.split('[4]:')[-1]

                    result = result.replace('[^1^]', '').replace('[1]', '').replace('[^2^]', '').replace('[2]',
                                                                                                         '').replace(
                        '[^3^]', '').replace('[3]', '').replace('[^4^]', '').replace('[4]', '')
                    result = result.replace('https://bing.com/search?q=', '').replace('""', '').replace('dw.com',
                                                                                                        '').replace(
                        'Википедия', '')
                    result = result.replace(' , ', ', ').replace('\n: ', '').replace('\n\n: ', '').replace(' — ',
                                                                                                           ' - ').replace(
                        '/ru/', '')
                    result = result.replace('%D0%', '').replace('%D1%', '').replace('%87%', '').replace('%82%',
                                                                                                        '').replace(
                        '%BE%', '').replace('%B0%', '').replace('%B5%', '').replace('%B1%', '').replace('%8B%',
                                                                                                        '').replace(
                        '%BA%', '').replace('%80%', '').replace('%8E%', '').replace('()', '').replace('https://www.',
                                                                                                      '').replace(' .',
                                                                                                                  '.')
                    result = result.replace('Источник: ', '').replace('8782BE', '').replace('82B0BABEB5', '').replace(
                        'B1BE828B', '').replace('B8', '').replace('BAB0BA', '').replace('BEBDB8', '').replace(
                        '80B0B1BE82B08E82', '').replace('a-41716550', '').replace(' – DW – ', '')
                    result = result.strip()
                if 'bing' in result.lower() and '.' in result:
                    tmp = result.split('\n\n')
                    if len(tmp) > 1:
                        result = result.replace(tmp[0], '')
                if 'copilot' in result.lower():
                    result = result[result.find(':') + 1:]
                    if '---' in result: result = result[result.find('---') + 1:].strip()

                result = result.replace('[^4^][4]', '').replace('[^4^]', '').replace('«', '').replace('»', '')
                result = result.replace('Bing', '').strip()

                break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(3, 4), 2))
            finally:
                cnt -= 1

        result = result.replace('**', '').rstrip('.')
    except Exception as e:
        logger.info(log_ % f"{str(e)}")
    finally:
        return result


async def outsource_handle(lst, path):
    result = []
    try:
        data_ = []
        if isinstance(lst, dict): lst = [lst]

        for item in lst:
            try:
                if item['type'] == 'tgph':
                    file_path = item['prompt']

                    if not item['prompt'].startswith('https://'):
                        if os.path.getsize(file_path) > 5242880: continue
                        ext = str(file_path[file_path.rfind('.'):]).lower()
                        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.mp4']: continue

                        async with aiofiles.open(file_path, 'rb') as f:
                            file_content = await f.read()

                        file_content_hex = binascii.hexlify(file_content).decode('utf-8')
                        file_name = os.path.basename(file_path)
                        data_.append({'type': item['type'], 'prompt': file_content_hex, 'extra': 'file_path',
                                      'file_name': file_name})
                    else:
                        data_.append({'type': item['type'], 'prompt': item['prompt'], 'extra': 'link_path'})
                elif item['type'] == 'txt':
                    prompt = item['prompt']

                    if isinstance(prompt, str):
                        prompt = [{"role": "system", "content": 'You are a helpful assistant for Telegram'},
                                  {"role": "user", "content": prompt}]

                    data_.append({'type': item['type'], 'prompt': prompt})
                elif item['type'] == 'img':
                    if item['prompt'] == 'variation':
                        prompt = item['prompt']
                        ext = str(item['file_path'][item['file_path'].rfind('.'):]).lower()
                        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.mp4']: continue
                        if os.path.getsize(item['file_path']) > 5242880: continue

                        src = os.path.join(item['dir_name'], item['file_path'])
                        dst = datetime.datetime.utcnow().strftime(f"%f-{os.path.basename(item['file_path'])}")
                        dst = os.path.join(item['dir_name'], dst)
                        shutil.copyfile(src, dst)

                        jpg_path = Path(dst)
                        png_path = jpg_path.with_suffix(".png")
                        image = Image.open(str(jpg_path))
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                            image.save(dst, format="JPEG", quality=15)
                        else:
                            image.save(dst, format="JPEG", quality=55)
                        image = Image.open(str(jpg_path))
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                            image.save(str(png_path), format="PNG", quality=15)
                        else:
                            image.save(str(png_path), format="PNG", quality=50)
                        item['file_path'] = png_path

                        async with aiofiles.open(item['file_path'], 'rb') as f:
                            file_content = await f.read()
                        file_content = binascii.hexlify(file_content).decode('utf-8')
                        file_name = os.path.basename(item['file_path'])
                        if os.path.exists(dst): os.remove(dst)
                        if os.path.exists(png_path): os.remove(png_path)
                    else:
                        special_characters = ['\'', '\"', '`', '~', '*', '_', '|', '#', '$', '[', ']', '(', ')', '{',
                                              '}', ';', '<', '>', '@']
                        special_characters += emojis_
                        prompt = item['prompt'].replace('```py\n', '')
                        for char in special_characters: prompt = prompt.replace(char, '')
                        prompt = f"{prompt[:512]} {extra_prompt}"

                        file_content = ''
                        file_name = '' if 'file_name' not in item else item['file_name']

                    count = 1 if 'count' not in item else item['count']
                    data_.append({'type': item['type'], 'prompt': prompt, 'count': count, 'file_name': file_name,
                                  'file_content': file_content})
                elif item['type'] == 'tts':
                    prompt = item['prompt'][:4095]
                    lc = 'en' if 'lc' not in item else item['lc']
                    dir_name = '' if 'dir_name' not in item else item['dir_name']

                    data_.append({'type': item['type'], 'prompt': prompt, 'lc': lc, 'dir_name': dir_name})
                elif item['type'] == 'stt':
                    async with aiofiles.open(item['prompt'], 'rb') as f:
                        file_content = await f.read()
                    file_content_hex = binascii.hexlify(file_content).decode('utf-8')
                    lc = '' if 'lc' not in item else item['lc']

                    data_.append({'type': item['type'], 'prompt': file_content_hex, 'lc': lc})
                elif item['type'] == 'tl':
                    prompt = item['prompt']
                    lc = 'en' if 'lc' not in item['lc'] else item['lc']

                    if isinstance(prompt, str):
                        prompt = [{"role": "system", "content": 'You are a helpful translator'}, {"role": "user",
                                                                                                  "content": f"Translate the following text (to `{lc}`-ISO language code): {prompt}"}]

                    data_.append({'type': item['type'], 'prompt': prompt, 'lc': lc})
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        if str(path).startswith('http'):
            timeout = aiohttp.ClientTimeout(total=6 * 60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url=path, json={'lst': data_}) as response:
                    resp = await response.read()
                    result = json.loads(resp.decode('utf-8'))['lst']

                    for i in range(len(result)):
                        if result[i]['type'] == 'tts':
                            file_content_binary = binascii.unhexlify(result[i]['answer'])
                            dt_ = datetime.datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S-%f.mp3")
                            dst_mp3 = os.path.join(result['dir_name'], dt_)

                            async with aiofiles.open(dst_mp3, 'wb') as f:
                                await f.write(file_content_binary)
                            result[i] = {'type': result[i]['type'], 'answer': dst_mp3}
        else:
            for item in data_:
                try:
                    if item['type'] != 'stt': print(log_ % f"{str(item)}")

                    if item['type'] == 'tgph':
                        if item['extra'] == 'link_path':
                            async with aiohttp.ClientSession() as session:
                                async with session.get(item['prompt']) as response:
                                    resp = await response.read()
                                    file_path = datetime.datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S-%f.jpg")

                                    async with aiofiles.open(file_path, 'wb') as f:
                                        await f.write(resp)
                        else:
                            file_content_binary = binascii.unhexlify(item['prompt'])
                            file_path = f"{round(time.time())}-{item['file_name']}"

                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(file_content_binary)

                        try:
                            cnt = 2
                            while cnt >= 0:
                                try:
                                    res = await Telegraph().upload_file(file_path)
                                    result.append(
                                        {'type': item['type'], 'answer': f"https://telegra.ph{res[0]['src']}"})
                                    break
                                except Exception as e:
                                    logger.info(log_ % str(e))
                                    await asyncio.sleep(round(random.uniform(6, 11), 2))
                                finally:
                                    cnt -= 1
                        finally:
                            if os.path.exists(file_path): os.remove(file_path)
                    elif item['type'] == 'txt':
                        is_res = False
                        # prompt = item['prompt']

                        cnt = 2
                        while cnt >= 0:
                            api_key = await get_openai_key(path)

                            try:
                                if not api_key: break
                                client = AsyncOpenAI(api_key=api_key)
                                res = await client.chat.completions.create(model="gpt-3.5-turbo",
                                                                           messages=item['prompt'], max_tokens=1200,
                                                                           stream=False)
                                result.append({'type': item['type'], 'answer': res.choices[0].message.content})
                                is_res = True
                                break
                            except Exception as e:
                                logger.info(log_ % f"{api_key} " + str(e))
                                if 'billing_hard_limit_reached' in str(e).lower():
                                    await del_openai_key(api_key, path)
                                    if not api_key: break
                                elif 'context_length_exceeded' in str(e).lower():
                                    max_content_element = max(item['prompt'], key=lambda x: len(x["content"]))
                                    item['prompt'].remove(max_content_element)
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif str(e).lower().startswith('You exceeded your current quota'):
                                    await asyncio.sleep(round(random.uniform(5, 10), 2))
                                    break
                                elif 'try again in' in str(e).lower():
                                    part_ = str(e).lower().split('try again in')[-1]
                                    time_ = part_.split('.')[0]
                                    if 'm' in time_:
                                        await asyncio.sleep(round(random.uniform(41, 49), 2))
                                    else:
                                        await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'try again' in str(e).lower():
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'seconds' in str(e).lower() or 'too many' in str(e).lower():
                                    await asyncio.sleep(20)
                                elif 'is not supported' in str(e).lower():
                                    break
                                elif 'rate_limit_exceeded' in str(e).lower():
                                    break  # await asyncio.sleep(round(random.uniform(61, 62), 2))
                                else:
                                    await asyncio.sleep(round(random.uniform(3, 4), 2))
                            finally:
                                cnt -= 1

                        print(f"{isinstance(item['prompt'], list)}")
                        if not is_res:
                            res = await g4f_chat_completion(item['prompt'])
                            if res:
                                result.append({'type': item['type'], 'answer': res.strip()})
                                print(f"g4f: {res}")
                    elif item['type'] == 'img':
                        cnt = 1
                        model_num = 3
                        while cnt >= 0:
                            api_key = await get_openai_key(path)
                            try:
                                if not api_key: break
                                client = AsyncOpenAI(api_key=api_key)
                                if item['prompt'] == 'variation':
                                    file_path = f"{round(time.time())}-{item['file_name']}"
                                    file_content = binascii.unhexlify(item['file_content'])
                                    async with aiofiles.open(file_path, 'wb') as f:
                                        await f.write(file_content)

                                    try:
                                        res = await client.images.create_variation(image=open(file_path, "rb"), n=1,
                                                                                   response_format='url',
                                                                                   size="1024x1024")
                                    finally:
                                        if os.path.exists(file_path): os.remove(file_path)
                                else:
                                    res = await client.images.generate(prompt=item['prompt'],
                                                                       model=f"dall-e-{model_num}",
                                                                       n=int(item['count']), quality="standard",
                                                                       response_format='url', size="1024x1024")
                                for it in res.data: result.append({'type': item['type'], 'answer': it.url})
                                break
                            except Exception as e:
                                logger.info(log_ % f"{api_key} " + str(e))
                                if 'billing_hard_limit_reached' in str(e).lower():
                                    await del_openai_key(api_key, path)
                                    if not api_key: break
                                elif str(e).lower().startswith('You exceeded your current quota'):
                                    await asyncio.sleep(round(random.uniform(5, 10), 2))
                                    break
                                elif 'try again in' in str(e).lower():
                                    part_ = str(e).lower().split('try again in')[-1]
                                    time_ = part_.split('.')[0]
                                    if 'm' in time_:
                                        await asyncio.sleep(round(random.uniform(41, 49), 2))
                                    else:
                                        await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'try again' in str(e).lower():
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'seconds' in str(e).lower() or 'too many' in str(e).lower():
                                    await asyncio.sleep(20)
                                elif 'is not supported' in str(e).lower():
                                    break
                                elif 'rate_limit_exceeded' in str(e).lower():
                                    model_num = 2
                                    await asyncio.sleep(round(random.uniform(3, 4),
                                                              2))  # break  # await asyncio.sleep(round(random.uniform(61, 62), 2))
                                else:
                                    await asyncio.sleep(round(random.uniform(3, 4), 2))
                            finally:
                                cnt -= 1
                    elif item['type'] == 'tts':
                        is_res = False

                        dt_ = datetime.datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S-%f.mp3")
                        dst_mp3 = os.path.join(item['dir_name'], dt_)

                        cnt = 1
                        while cnt >= 0:
                            api_key = await get_openai_key(path)
                            try:
                                if not api_key: break
                                client = AsyncOpenAI(api_key=api_key)
                                # alloy - между мужчиной и женщиной
                                # echo - дурацкий русский
                                # fable - среднее между alloy и echo
                                # onyx - низкий голос (неплохой)
                                # nova - такая 32 летняя девушка
                                # shimmer - между мужчиной и женщиной
                                response = await client.audio.speech.create(model='tts-1',
                                                                            voice=random.choice(['alloy', 'shimmer']),
                                                                            input=item['prompt'].replace('```py\n', ''))
                                response.stream_to_file(dst_mp3)
                                is_res = True
                                break
                            except Exception as e:
                                logger.info(log_ % f"{api_key} " + str(e))
                                if 'billing_hard_limit_reached' in str(e).lower():
                                    await del_openai_key(api_key, path)
                                    if not api_key: break
                                elif str(e).lower().startswith('You exceeded your current quota'):
                                    await asyncio.sleep(round(random.uniform(5, 10), 2))
                                    break
                                elif 'try again in' in str(e).lower():
                                    part_ = str(e).lower().split('try again in')[-1]
                                    time_ = part_.split('.')[0]
                                    if 'm' in time_:
                                        await asyncio.sleep(round(random.uniform(41, 49), 2))
                                    else:
                                        await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'try again' in str(e).lower():
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'seconds' in str(e).lower() or 'too many' in str(e).lower():
                                    await asyncio.sleep(20)
                                elif 'is not supported' in str(e).lower():
                                    break
                                elif 'rate_limit_exceeded' in str(e).lower():
                                    break  # await asyncio.sleep(round(random.uniform(61, 62), 2))
                                else:
                                    await asyncio.sleep(round(random.uniform(3, 4), 2))
                            finally:
                                cnt -= 1

                        if not is_res:
                            special_characters = ['\'', '\"', '`', '~', '*', '_', '|', '#', '$', '[', ']', '(', ')',
                                                  '{', '}', ':', ';', '<', '>', '@', '-', '+', '=']
                            special_characters += emojis_
                            tmp_text = item['prompt'].replace('```py\n', '')
                            for char in special_characters: tmp_text = tmp_text.replace(char, '')
                            gTTS(text=tmp_text, lang=item['lc'], slow=False).save(dst_mp3)

                        result.append(
                            {'type': item['type'], 'answer': dst_mp3})  # if os.path.exists(dst_mp3): os.remove(dst_mp3)
                    elif item['type'] == 'stt':
                        is_res = False
                        text = ''
                        dt_ = datetime.datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S-%f.mp3")
                        src_mp3 = os.path.abspath(os.path.join(os.path.dirname(__file__), dt_))
                        dt_ = datetime.datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S-%f.wav")
                        file_wav = os.path.abspath(os.path.join(os.path.dirname(__file__), dt_))
                        file_content_binary = binascii.unhexlify(item['prompt'])

                        async with aiofiles.open(src_mp3, 'wb') as f:
                            await f.write(file_content_binary)

                        cnt = 1
                        while cnt >= 0:
                            api_key = await get_openai_key(path)
                            try:
                                if not api_key: break
                                client = AsyncOpenAI(api_key=api_key)
                                res = await client.audio.transcriptions.create(model="whisper-1",
                                                                               file=open(src_mp3, "rb"))
                                text = res.text
                                is_res = True
                                break
                            except Exception as e:
                                logger.info(log_ % f"{api_key} " + str(e))
                                if 'billing_hard_limit_reached' in str(e).lower():
                                    await del_openai_key(api_key, path)
                                    if not api_key: break
                                elif str(e).lower().startswith('You exceeded your current quota'):
                                    await asyncio.sleep(round(random.uniform(5, 10), 2))
                                    break
                                elif 'try again in' in str(e).lower():
                                    part_ = str(e).lower().split('try again in')[-1]
                                    time_ = part_.split('.')[0]
                                    if 'm' in time_:
                                        await asyncio.sleep(round(random.uniform(41, 49), 2))
                                    else:
                                        await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'try again' in str(e).lower():
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'seconds' in str(e).lower() or 'too many' in str(e).lower():
                                    await asyncio.sleep(20)
                                elif 'is not supported' in str(e).lower():
                                    break
                                elif 'rate_limit_exceeded' in str(e).lower():
                                    break  # await asyncio.sleep(round(random.uniform(61, 62), 2))
                                else:
                                    await asyncio.sleep(round(random.uniform(3, 4), 2))
                            finally:
                                cnt -= 1

                        if not is_res:
                            print('not is_res (stt)')
                            ext = src_mp3.split('.')[-1]
                            recognizer = sr.Recognizer()

                            try:
                                if ext == 'mp3':
                                    audio = AudioSegment.from_mp3(src_mp3)
                                elif ext == 'ogg':
                                    audio = AudioSegment.from_ogg(src_mp3)
                                else:
                                    audio = AudioSegment.from_file(src_mp3, format=ext)
                                audio.export(file_wav, format="wav")
                            except:
                                video_clip = mp.VideoFileClip(src_mp3)
                                audio_clip = video_clip.audio
                                audio_clip.write_audiofile(file_wav, codec='pcm_s16le')
                                audio_clip.close()
                                video_clip.close()

                            with sr.AudioFile(file_wav) as source:
                                try:
                                    print(f"sr.AudioFile(file_wav)")
                                    recognizer.adjust_for_ambient_noise(source)
                                    audio_data = recognizer.record(source)
                                    text = recognizer.recognize_google(audio_data, language=item['lc'])
                                    print(f"{text=}")
                                except Exception as e:
                                    logger.info(log_ % str(e))
                                    await asyncio.sleep(round(random.uniform(0, 1), 2))

                        result.append({'type': item['type'], 'answer': str(text).rstrip('.').strip()})
                        if os.path.exists(src_mp3): os.remove(src_mp3)
                        if os.path.exists(file_wav): os.remove(file_wav)
                    elif item['type'] == 'tl':
                        is_res = False

                        cnt = 2
                        while cnt >= 0:
                            api_key = await get_openai_key(path)
                            try:
                                if not api_key: break
                                client = AsyncOpenAI(api_key=api_key)
                                res = await client.chat.completions.create(model="gpt-3.5-turbo",
                                                                           messages=item['prompt'], max_tokens=1200,
                                                                           stream=False)
                                result.append({'type': item['type'], 'answer': res.choices[0].message.content})
                                is_res = True
                                break
                            except Exception as e:
                                logger.info(log_ % f"{api_key} " + str(e))
                                if 'billing_hard_limit_reached' in str(e).lower():
                                    await del_openai_key(api_key, path)
                                    if not api_key: break
                                elif str(e).lower().startswith('You exceeded your current quota'):
                                    await asyncio.sleep(round(random.uniform(5, 10), 2))
                                    break
                                elif 'try again in' in str(e).lower():
                                    part_ = str(e).lower().split('try again in')[-1]
                                    time_ = part_.split('.')[0]
                                    if 'm' in time_:
                                        await asyncio.sleep(round(random.uniform(41, 49), 2))
                                    else:
                                        await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'try again' in str(e).lower():
                                    await asyncio.sleep(round(random.uniform(21, 23), 2))
                                elif 'seconds' in str(e).lower() or 'too many' in str(e).lower():
                                    await asyncio.sleep(20)
                                elif 'is not supported' in str(e).lower():
                                    break
                                elif 'rate_limit_exceeded' in str(e).lower():
                                    break  # await asyncio.sleep(round(random.uniform(61, 62), 2))
                                else:
                                    await asyncio.sleep(round(random.uniform(3, 4), 2))
                            finally:
                                cnt -= 1

                        if not is_res:
                            res = await g4f_chat_completion(item['prompt'])
                            if res:
                                result.append({'type': item['type'], 'answer': res})
                except Exception as e:
                    logger.info(log_ % str(e))  # await asyncio.sleep(round(random.uniform(0, 1), 2))
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def generate_image(prompt, EXTRA_D):
    result = None
    try:
        answer = await outsource_handle({'type': 'img', 'prompt': prompt}, os.path.join(EXTRA_D, 'openai_keys.txt'))
        if len(answer):
            answer = await outsource_handle({'type': 'tgph', 'prompt': answer[0]['answer']},
                                            os.path.join(EXTRA_D, 'openai_keys.txt'))
            result = answer[0]['answer']
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_grant_balance(key_):
    result = False
    try:
        headers = {"Authorization": f"Bearer {key_}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://api.openai.com/dashboard/billing/credit_grants") as response:
                bdata = await response.json()

                if 'total_available' in bdata and bdata["total_available"] > 0.01:
                    result = True
                    print(f'{key_}: billing_data = {bdata["total_available"]}$')
                else:
                    print(f'{key_}: key is not valid')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result
# endregion


# region convert
async def return_file_id(BOT_TID, FILE_NAME, MSG_TYPE, IS_LINK, BASE_D, EXTRA_D, MEDIA_D):
    file_id = file_id_note = file_type = None
    try:
        cnt = 3
        while cnt > 0:
            try:
                sql = "SELECT OWNER_TID, BOT_STATUS, BOT_TOKEN FROM BOT WHERE BOT_TID=?"
                data = await db_select(sql, (BOT_TID,), BASE_D)
                if not len(data): return
                OWNER_TID, BOT_STATUS, BOT_TOKEN = data[0]

                extra_bot = Bot(token=BOT_TOKEN)
                if MSG_TYPE == 'web':
                    ext = FILE_NAME[FILE_NAME.rfind('.'):].lower()
                    # print(f"ext = {ext}")

                    if ext in ['.png', '.jpg', '.jpeg']:
                        MSG_TYPE = 'photo'
                    elif ext in ['.gif', '.giff']:
                        MSG_TYPE = 'gif'
                    elif ext in ['.mp4']:
                        MSG_TYPE = 'video'

                try:
                    MEDIA = FILE_NAME if IS_LINK else types.FSInputFile(FILE_NAME)
                    res = None
                    if MSG_TYPE == 'photo':
                        res = await extra_bot.send_photo(OWNER_TID, MEDIA, disable_notification=True)
                        file_id = res.photo[-1].file_id
                        file_type = 'photo'
                    elif MSG_TYPE == 'gif':
                        res = await extra_bot.send_animation(OWNER_TID, MEDIA, disable_notification=True)

                        if res.animation:
                            file_id = res.animation.file_id
                            file_type = 'gif'
                        elif res.video:
                            file_id = res.video.file_id
                            file_type = 'video'
                    elif MSG_TYPE == 'video':
                        width = height = None
                        if not IS_LINK:
                            try:
                                cap = cv2.VideoCapture(FILE_NAME)
                                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                print(f"{width=}, {height=}")
                            except Exception as e:
                                logger.info(log_ % str(e))
                                await asyncio.sleep(round(random.uniform(0, 1), 2))

                        res = await extra_bot.send_video(chat_id=OWNER_TID, video=MEDIA, width=width, height=height,
                                                         disable_notification=True)

                        if res.video:
                            file_id = res.video.file_id
                            file_type = 'video'
                        elif res.animation:
                            file_id = res.animation.file_id
                            file_type = 'gif'
                    elif MSG_TYPE == 'video_note':
                        FILE_NAME = await hand_video_note(FILE_NAME, IS_LINK, BOT_TID, MEDIA_D)
                        res = await extra_bot.send_video_note(OWNER_TID, types.FSInputFile(FILE_NAME),
                                                              disable_notification=True)

                        if res.video_note:
                            file_id = res.video_note.file_id
                            file_id_note = await send_video_my(extra_bot, OWNER_TID, MEDIA)
                            IS_LINK = 0
                            file_type = 'video_note'
                        elif res.animation:
                            file_id = res.animation.file_id
                            file_type = 'gif'
                        elif res.video:
                            file_id = res.video.file_id
                            file_type = 'video'
                    elif MSG_TYPE == 'audio':
                        F_NAME = FILE_NAME
                        if IS_LINK and FILE_NAME.lower().endswith('.mp4'):
                            MEDIA = types.FSInputFile(await download_file_my(MEDIA, BOT_TID, 'mp4', MEDIA_D))

                        file_id, file_name_video = await send_audio_my(extra_bot, BOT_TID, OWNER_TID, MEDIA, FILE_NAME,
                                                                       BASE_D, EXTRA_D)
                        if file_name_video:
                            if os.path.exists(FILE_NAME): os.remove(FILE_NAME)
                            print(f'del {FILE_NAME=}, остался {file_name_video=}')
                            FILE_NAME = file_name_video

                        file_type = 'audio'
                        if F_NAME != FILE_NAME and os.path.exists(F_NAME): os.remove(F_NAME)
                    elif MSG_TYPE == 'voice':
                        F_NAME = FILE_NAME
                        res = await extra_bot.send_voice(OWNER_TID, MEDIA, disable_notification=True)

                        if res.voice:
                            print('is +voice')
                            file_id = res.voice.file_id
                            file_type = 'voice'
                        elif res.audio:
                            print('is +audio')
                            file_id = res.audio.file_id
                            file_type = 'audio'

                        file_id_note, file_name_video = await send_audio_my(extra_bot, BOT_TID, OWNER_TID, MEDIA,
                                                                            FILE_NAME, BASE_D, EXTRA_D)
                        if file_name_video:
                            if os.path.exists(FILE_NAME): os.remove(FILE_NAME)
                            print(f'del {FILE_NAME=}, остался {file_name_video=}')
                            FILE_NAME = file_name_video

                        if F_NAME != FILE_NAME and os.path.exists(F_NAME): os.remove(F_NAME)
                    elif MSG_TYPE == 'document':
                        F_NAME = FILE_NAME
                        if IS_LINK:
                            F_NAME = await download_file_my(MEDIA, BOT_TID, FILE_NAME.split(".")[-1], MEDIA_D)
                            MEDIA = types.FSInputFile(F_NAME)

                        thumb = types.FSInputFile(os.path.join(EXTRA_D, 'parse.jpg'))
                        res = await extra_bot.send_document(OWNER_TID, MEDIA, disable_content_type_detection=True,
                                                            disable_notification=True, thumbnail=thumb)
                        file_id = res.document.file_id
                        file_type = 'document'
                        if F_NAME != FILE_NAME and os.path.exists(F_NAME): os.remove(F_NAME)
                    elif MSG_TYPE == 'sticker':
                        F_NAME = FILE_NAME
                        if IS_LINK:
                            F_NAME = await download_file_my(MEDIA, BOT_TID, FILE_NAME.split(".")[-1], MEDIA_D)

                        if not F_NAME.endswith('.webp'):
                            image = Image.open(F_NAME)
                            dt = datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.webp')
                            F_NAME = os.path.join(MEDIA_D, str(BOT_TID), dt)
                            await asyncio.sleep(0.05)
                            image.save(F_NAME, format="webp", quality=50)
                            if os.path.getsize(F_NAME) > 1048576: return
                            MEDIA = types.FSInputFile(F_NAME)
                        else:
                            MEDIA = types.FSInputFile(F_NAME)

                        res = await extra_bot.send_sticker(OWNER_TID, MEDIA)

                        if res.sticker:
                            file_id = res.sticker.file_id
                            file_type = 'sticker'
                        elif res.document:
                            file_id = res.document.file_id
                            file_type = 'document'

                        if F_NAME != FILE_NAME and os.path.exists(F_NAME): os.remove(F_NAME)

                    if res:
                        await extra_bot.delete_message(OWNER_TID, res.message_id)
                finally:
                    await extra_bot.session.close()
                return
            except Exception as e:
                logger.info(log_ % str(e) + " (repeat)")
                if 'Internal Server Error' not in str(e): break
                await asyncio.sleep(6)
            finally:
                cnt += 1
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return file_id, file_id_note, file_type, FILE_NAME, IS_LINK


async def return_tgph_link(FILE_NAME, MSG_TYPE, IS_LINK):
    if MSG_TYPE == 'photo':
        result = photo_jpg
    elif MSG_TYPE == 'gif':
        result = gif_jpg
    elif MSG_TYPE == 'video':
        result = video_jpg
    elif MSG_TYPE == 'video_note':
        result = video_note_jpg
    elif MSG_TYPE == 'audio':
        result = audio_jpg
    elif MSG_TYPE == 'voice':
        result = voice_jpg
    elif MSG_TYPE == 'sticker':
        result = sticker_jpg
    else:
        result = document_jpg

    try:
        print(f"here {FILE_NAME=}, ")
        if IS_LINK:
            result = FILE_NAME
            print(f'IS_LINK return_tgph_link: {result}')
        elif FILE_NAME.lower().endswith('.jpg') or FILE_NAME.lower().endswith('.jpeg') or FILE_NAME.lower().endswith(
                '.png') or FILE_NAME.lower().endswith('.mp4') or FILE_NAME.lower().endswith('.gif'):
            print('hare ai in FILE_NAME')
            res = await get_tgph_link(FILE_NAME)
            if res:
                result = res  # print(f'new return_tgph_link: {result}')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def jpg_video_preview(tgph_link, BOT_TID, MSG_TYPE, file_id, BASE_D, MEDIA_D):
    result = None
    destination = destination2 = destination3 = None
    try:
        if MSG_TYPE == 'photo':
            result = photo_jpg
        elif MSG_TYPE == 'gif':
            result = gif_jpg
        elif MSG_TYPE == 'video':
            result = video_jpg
        elif MSG_TYPE == 'video_note':
            result = video_note_jpg
        elif MSG_TYPE == 'audio':
            result = audio_jpg
        elif MSG_TYPE == 'voice':
            result = voice_jpg
        elif MSG_TYPE == 'sticker':
            result = sticker_jpg
        else:
            result = document_jpg

        # download
        sql = "SELECT OWNER_TID, BOT_STATUS, BOT_TOKEN FROM BOT WHERE BOT_TID=?"
        data = await db_select(sql, (BOT_TID,), BASE_D)
        if not len(data): return
        OWNER_TID, BOT_STATUS, BOT_TOKEN = data[0]

        dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')
        dt_2 = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f-2.jpg')
        dt_3 = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f-3.jpg')
        destination = os.path.join(MEDIA_D, str(BOT_TID), dt_)
        destination2 = os.path.join(MEDIA_D, str(BOT_TID), dt_2)
        destination3 = os.path.join(MEDIA_D, str(BOT_TID), dt_3)

        extra_bot = Bot(token=BOT_TOKEN)
        try:
            file = await extra_bot.get_file(file_id)
            await extra_bot.download_file(file.file_path, destination)
        finally:
            await extra_bot.session.close()

        # save frame to jpg
        clip = mp.VideoFileClip(destination)
        frame_at_second = int(clip.duration / 2)
        frame = clip.get_frame(frame_at_second)
        new_image = Image.fromarray(frame)
        new_image.save(destination2)

        # square jpg
        img = Image.open(destination2)
        width, height = img.size
        min_side = width if width < height else height
        half_square_side = int(min_side / 2)
        left_x = int(width / 2 - half_square_side)
        left_y = int(height / 2 - half_square_side)
        right_x = int(width / 2 + half_square_side)
        right_y = int(height / 2 + half_square_side)
        clip_convert = img.crop((left_x, left_y, right_x, right_y))
        clip_convert.save(destination3, quality=20)

        res = await get_tgph_link(destination3)
        if result:
            result = res
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        if destination and os.path.exists(destination): os.remove(destination)
        if destination2 and os.path.exists(destination2): os.remove(destination2)
        if destination3 and os.path.exists(destination3): os.remove(destination3)
        return result


async def jpg_photo_preview(tgph_link, BOT_TID, MEDIA_D):
    result = tgph_link
    try:
        dt = datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.jpg')
        dt_finish = datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f-2.jpg')
        file_name = os.path.join(MEDIA_D, str(BOT_TID), dt)
        file_finish = os.path.join(MEDIA_D, str(BOT_TID), dt_finish)

        async with aiohttp.ClientSession() as session:
            async with session.get(tgph_link) as response:
                resp = await response.read()
                with open(file_name, 'wb') as f:
                    f.write(resp)
        if not os.path.exists(file_name): return

        # square jpg
        img = Image.open(file_name)
        img = img.convert('RGB')
        width, height = img.size
        min_side = width if width < height else height
        half_square_side = int(min_side / 2)
        left_x = int(width / 2 - half_square_side)
        left_y = int(height / 2 - half_square_side)
        right_x = int(width / 2 + half_square_side)
        right_y = int(height / 2 + half_square_side)
        clip_convert = img.crop((left_x, left_y, right_x, right_y))
        clip_convert.save(file_finish, quality=20)

        result = await get_tgph_link(file_finish)
        result = '' if result is None else result
        if os.path.exists(file_name): os.remove(file_name)
        if os.path.exists(file_finish): os.remove(file_finish)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def resize_media(file_name, basewidth=1024):
    result = file_name
    try:
        if str(file_name).lower().endswith('.png'):
            im = Image.open(file_name)
            rgb_im = im.convert('RGB')
            tmp_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.jpg')
            rgb_im.save(tmp_name)
            if os.path.exists(file_name):
                os.remove(file_name)
            result = file_name = tmp_name

        img = Image.open(file_name)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.LANCZOS)
        img.save(file_name)
        result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def resize_video_note(file_name, basewidth):
    result = file_name
    try:
        if not str(file_name).lower().endswith('.mp4'):
            clip = mp.VideoFileClip(file_name)
            tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
            clip.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                 remove_temp=True)

            if os.path.exists(file_name):
                os.remove(file_name)
            file_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.mp4')
            if os.path.exists(tmp_name):
                os.rename(tmp_name, file_name)
            result = file_name
        if basewidth == 440:
            clip = mp.VideoFileClip(file_name)
            clip_resized = clip.resize((basewidth, basewidth))
            tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
            clip_resized.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                         remove_temp=True)
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists(tmp_name):
                os.rename(tmp_name, file_name)
            result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def hand_video_note(MEDIA, IS_LINK, BOT_TID, MEDIA_D):
    result = MEDIA
    try:
        file_name = MEDIA
        if IS_LINK:
            async with aiohttp.ClientSession() as session:
                async with session.get(MEDIA) as response:
                    resp = await response.read()

                    dt = datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.mp4')
                    file_name = os.path.join(MEDIA_D, str(BOT_TID), dt)
                    with open(file_name, 'wb') as f:
                        f.write(resp)

        if os.path.exists(file_name):
            clip = mp.VideoFileClip(file_name)
            width, height = clip.size
            min_side = width if width < height else height
            min_side = 640 if min_side > 640 else min_side
            half_square_side = int(min_side / 2)
            left_x = width / 2 - half_square_side
            left_y = height / 2 - half_square_side
            right_x = width / 2 + half_square_side
            right_y = height / 2 + half_square_side
            clip_convert = crop(clip, x1=left_x, y1=left_y, x2=right_x, y2=right_y)
            clip_convert = clip_convert.subclip(0, 59) if int(clip.duration) > 59 else clip_convert

            tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
            clip_convert.write_videofile(filename=tmp_name, codec='libx264', audio_codec='aac',
                                         temp_audiofile='temp-audio.m4a', remove_temp=True)
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists(tmp_name):
                os.rename(tmp_name, file_name)
            print(f'success: {file_name}')
            result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def send_audio_my(extra_bot, BOT_TID, OWNER_TID, MEDIA, FILE_NAME, BASE_D, EXTRA_D):
    result = file_name_video = None
    try:
        cnt = 3
        while cnt > 0:
            try:
                sql = "SELECT BOT_USERNAME, BOT_FIRSTNAME FROM BOT WHERE BOT_TID=?"
                data = await db_select(sql, (BOT_TID,), BASE_D)
                BOT_USERNAME, BOT_FIRSTNAME = data[0]
                performer = f'@{BOT_USERNAME}'
                title = BOT_FIRSTNAME
                thumb = types.FSInputFile(os.path.join(EXTRA_D, 'img.jpg'))

                res = await extra_bot.send_audio(chat_id=OWNER_TID, audio=MEDIA, thumbnail=thumb, title=title,
                                                 performer=performer, disable_notification=True)
                await extra_bot.delete_message(OWNER_TID, res.message_id)
                if res.audio: result = res.audio.file_id

                if not result or os.path.getsize(FILE_NAME) < 5242880:
                    print('inside')
                    audio = AudioFileClip(FILE_NAME)
                    video_clip = VideoClip(lambda t: np.zeros((480, 640, 3), dtype=np.uint8), duration=audio.duration)
                    video_clip = video_clip.set_audio(audio)
                    file_name_video = FILE_NAME[:FILE_NAME.rfind('.')] + '.mp4'
                    video_clip.write_videofile(file_name_video, codec="libx264", audio_codec="aac", fps=24)

                    res = await extra_bot.send_audio(chat_id=OWNER_TID, audio=types.FSInputFile(file_name_video),
                                                     thumbnail=thumb, title=title, performer=performer,
                                                     disable_notification=True)
                    await extra_bot.delete_message(OWNER_TID, res.message_id)
                    # if os.path.exists(file_name_video): os.remove(file_name_video)
                    if res.audio and not result: result = res.audio.file_id
                break
            except Exception as e:
                logger.info(log_ % str(e) + " (repeat)")
                if 'Internal Server Error' not in str(e): break
                await asyncio.sleep(6)
            finally:
                cnt += 1
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result, file_name_video


async def send_video_my(extra_bot, OWNER_TID, MEDIA):
    result = None
    try:
        res = await extra_bot.send_video(OWNER_TID, MEDIA, supports_streaming=True, disable_notification=True)
        result = res.video.file_id
        await extra_bot.delete_message(OWNER_TID, res.message_id)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def download_file_my(MEDIA, BOT_TID, ext, MEDIA_D):
    result = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(MEDIA) as response:
                resp = await response.read()

                dt = datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.{ext}')
                file_name = os.path.join(MEDIA_D, str(BOT_TID), dt)
                with open(file_name, 'wb') as f:
                    f.write(resp)
                result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def facade_get_fid(BOT_TID, dst, msg_type, IS_LINK, BASE_D, EXTRA_D, MEDIA_D):
    tmp_json = {}
    FILE_NAME = None
    try:
        file_id, file_id_note, file_type, FILE_NAME, IS_LINK = await return_file_id(BOT_TID, dst, msg_type, IS_LINK,
                                                                                    BASE_D, EXTRA_D, MEDIA_D)
        tgph_link = await return_tgph_link(FILE_NAME, msg_type, IS_LINK)

        if tgph_link.endswith('.mp4'):
            tgph_link2 = await jpg_video_preview(tgph_link, BOT_TID, msg_type, file_id, BASE_D, MEDIA_D)
        else:
            tgph_link2 = await jpg_photo_preview(tgph_link, BOT_TID, MEDIA_D)

        tmp_json = {'file_id': str(file_id), 'file_id_note': str(file_id_note), 'file_type': str(file_type),
                    'file_name': os.path.basename(FILE_NAME), 'tgph_link': tgph_link, 'tgph_link2': tgph_link2, }
        print(f"{tmp_json=}")
    except Exception as e:
        # logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        if FILE_NAME and os.path.exists(FILE_NAME): os.remove(FILE_NAME)
        return tmp_json


async def convert_png_to_gif(input_name, output_name):
    result = None
    try:
        image = Image.open(input_name)
        frames = [image.copy(), ImageOps.grayscale(image)]

        frames[0].save(output_name, save_all=True, append_images=frames[1:], duration=500, loop=0, optimize=True)
        result = output_name if os.path.exists(output_name) else None
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def convert_png_to_mp4(ENT_TID, input_name, output_name, MEDIA_D):
    result = None
    try:
        tmp_gif = os.path.join(MEDIA_D, str(ENT_TID), datetime.datetime.utcnow().strftime(f'%d-%m-%Y_%H-%M-%S-%f.gif'))
        tmp_gif = await convert_png_to_gif(input_name, tmp_gif)

        clip = mp.VideoFileClip(tmp_gif)
        clip = mp.concatenate_videoclips([clip] * 12, method="compose")
        clip.write_videofile(output_name, fps=24)
        if os.path.exists(tmp_gif): os.remove(tmp_gif)

        result = output_name if os.path.exists(output_name) else None
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def item_to_static_sticker(bot, chat_id, input_file, PACK_TYPE, PACK_KIND, is_upload=True, is_circle=False,
                                 is_rbg=False):
    result = result_upl = None
    file_jpg = input_file[:input_file.rfind('.')] + '_.jpg'
    file_png = input_file[:input_file.rfind('.')] + '_.png'
    try:
        size_kb = 512000
        if PACK_KIND == 'video':
            size_kb = 256000
        elif PACK_KIND == 'animated':
            size_kb = 64000
        pixels = (100, 100) if PACK_TYPE == 'emoji' else (512, 512)
        sticker_format = 'static'

        # region pre
        if input_file.lower().endswith('.webp') and os.path.getsize(input_file) <= size_kb:
            image = Image.open(input_file)
            width, height = image.size
            if PACK_TYPE == 'emoji' and width == 100 and height == 100:
                upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                    sticker_format=sticker_format)
                result_upl = upl.file_id
                return
            elif PACK_TYPE == 'sticker' and width <= 512 and height <= 512:
                upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                    sticker_format=sticker_format)
                result_upl = upl.file_id
                return
        elif input_file.lower().endswith('.tgs') and os.path.getsize(input_file) <= size_kb:
            upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                sticker_format=sticker_format)
            result_upl = upl.file_id
            return
        # endregion

        # region pixels
        image = Image.open(input_file)
        width, height = image.size
        left = (width - min(width, height)) // 2
        top = (height - min(width, height)) // 2
        right = (width + min(width, height)) // 2
        bottom = (height + min(width, height)) // 2
        image = image.crop((left, top, right, bottom))
        image = image.resize(pixels, resample=Image.LANCZOS)
        image = image.convert("RGB")
        image.save(file_jpg, format="JPEG")
        # endregion

        # region size
        quality = 90
        while quality > 0:
            img = Image.open(file_jpg)
            img.save(file_jpg, format="JPEG", quality=quality)

            if os.path.getsize(file_jpg) < size_kb: break
            quality = 1 if quality == 0 else quality - 10
        if os.path.getsize(file_jpg) > size_kb: return
        # endregion

        # region is_circle
        rad = 25
        fill_ = 255
        image = Image.open(file_jpg)
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)

        if is_circle:
            # draw.ellipse((0, 0, image.width, image.height), fill=255)
            left, top, right, bottom = (0, 0, image.width, image.height)
            draw.pieslice(((left, top), (right, bottom)), 0, 360, fill=fill_, outline=fill_)
        else:
            left, top, right, bottom = (0, 0, image.width, image.height)
            draw.pieslice(((left, top), (left + 2 * rad, top + 2 * rad)), 180, 270, fill=fill_, outline=fill_)
            draw.pieslice(((right - 2 * rad, top), (right, top + 2 * rad)), 270, 0, fill=fill_, outline=fill_)
            draw.pieslice(((left, bottom - 2 * rad), (left + 2 * rad, bottom)), 90, 180, fill=fill_, outline=fill_)
            draw.pieslice(((right - 2 * rad, bottom - 2 * rad), (right, bottom)), 0, 90, fill=fill_, outline=fill_)
            draw.rectangle((left + rad, top, right - rad, bottom), fill=fill_)
            draw.rectangle((left, top + rad, right, bottom - rad), fill=fill_)
        res = Image.new('RGBA', image.size, (0, 0, 0, 0))
        res.paste(image, mask=mask)
        res.save(file_png)
        res.close()
        # endregion

        # region rbg
        try:
            if is_rbg:
                img = Image.open(file_png)
                output_ = remove(img)
                output_.save(file_png)
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(0, 1), 2))
        # endregion

        if is_upload:
            upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(file_png),
                                                sticker_format=sticker_format)
            result_upl = upl.file_id
        else:
            result = await bot.send_sticker(chat_id, types.FSInputFile(file_png))
            result = result.sticker.file_id
        print(
            f"result_upl ok")  # res = await bot.send_sticker(chat_id, types.FSInputFile(file_png))  # await bot.delete_message(chat_id, res.message_id)  # result = res.sticker.file_id
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        try:
            if os.path.exists(file_jpg): os.remove(file_jpg)
            if os.path.exists(file_png): os.remove(file_png)
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(0, 1), 2))
        return result, result_upl


async def item_to_dynamic_sticker(bot, chat_id, input_file, bot_username, MEDIA_D, PACK_TYPE, PACK_KIND, is_upload=True,
                                  is_circle=False, is_rbg=False):
    result = result_upl = None
    file_jpg = input_file[:input_file.rfind('.')] + '_.jpg'
    file_mp4 = input_file[:input_file.rfind('.')] + '_.mp4'
    file_png = input_file[:input_file.rfind('.')] + '_.png'
    file_gray_png = input_file[:input_file.rfind('.')] + 'gray.png'
    file_webm = input_file[:input_file.rfind('.')] + '_.webm'
    spec_dir = os.path.join(MEDIA_D, str(chat_id), 'spec')
    try:
        # region data
        size_kb = 512000
        if PACK_KIND == 'video':
            size_kb = 256000
        elif PACK_KIND == 'animated':
            size_kb = 64000

        fps = 30
        bitrate = '60k'
        i_input_data = f'{spec_dir}/frame_%04d.png'
        rounded = 'null'

        pixels = (100, 100) if PACK_TYPE == 'emoji' else (512, 512)
        pixels_str = '100x100' if PACK_TYPE == 'emoji' else '512x512'
        side_sz = 100 if PACK_TYPE == 'emoji' else 512
        sticker_format = PACK_KIND
        os.makedirs(spec_dir, exist_ok=True, mode=0o777)
        # endregion

        # region pre
        if input_file.lower().endswith('.webm') and os.path.getsize(input_file) <= size_kb:
            # clip = mp.VideoFileClip(input_file).subclip(0, 2)
            # frame_at_second = int(clip.duration / 2)
            # frame = clip.get_frame(frame_at_second)
            # image = Image.fromarray(frame)
            # width, height = image.size

            if PACK_TYPE == 'emoji':  # and width == 100 and height == 100 and input_file.lower().endswith('.webm'):
                upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                    sticker_format=sticker_format)
                result_upl = upl.file_id
                return
            elif PACK_TYPE == 'sticker':  # and width <= 512 and height <= 512 and input_file.lower().endswith('.webm'):
                upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                    sticker_format=sticker_format)
                result_upl = upl.file_id
                return
        elif input_file.lower().endswith('.tgs') and os.path.getsize(input_file) <= size_kb:
            upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(input_file),
                                                sticker_format=sticker_format)
            result_upl = upl.file_id
            return
        # endregion

        if input_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            frames = 12
            rad = 25
            fill_ = 255
            bitrate = '100k'

            # region pixels
            image = Image.open(input_file)
            width, height = image.size
            left = (width - min(width, height)) // 2
            top = (height - min(width, height)) // 2
            right = (width + min(width, height)) // 2
            bottom = (height + min(width, height)) // 2
            image = image.crop((left, top, right, bottom))
            image = image.resize(pixels, resample=Image.LANCZOS)
            image = image.convert("RGB")
            image.save(file_jpg, format="JPEG")
            # endregion

            # region size
            quality = 90
            while quality > 0:
                img = Image.open(file_jpg)
                img.save(file_jpg, format="JPEG", quality=quality)

                if os.path.getsize(file_jpg) < size_kb: break
                quality = 1 if quality == 0 else quality - 10
            if os.path.getsize(file_jpg) > size_kb: return
            # endregion

            # region color
            img = Image.open(file_jpg)
            img = img.convert("RGBA")
            img.save(file_png)
            # endregion

            # region gray
            img = Image.open(file_jpg)
            img = ImageOps.grayscale(img)
            img = img.convert("RGBA")
            img.save(file_gray_png)
            # endregion

            for it_png in [file_png, file_gray_png]:
                try:
                    # region is_circle
                    image = Image.open(it_png)
                    mask = Image.new('L', image.size, 0)
                    draw = ImageDraw.Draw(mask)

                    if is_circle:
                        left, top, right, bottom = (0, 0, image.width, image.height)
                        draw.pieslice(((left, top), (right, bottom)), 0, 360, fill=fill_, outline=fill_)
                    else:
                        left, top, right, bottom = (0, 0, image.width, image.height)
                        draw.pieslice(((left, top), (left + 2 * rad, top + 2 * rad)), 180, 270, fill=fill_,
                                      outline=fill_)
                        draw.pieslice(((right - 2 * rad, top), (right, top + 2 * rad)), 270, 0, fill=fill_,
                                      outline=fill_)
                        draw.pieslice(((left, bottom - 2 * rad), (left + 2 * rad, bottom)), 90, 180, fill=fill_,
                                      outline=fill_)
                        draw.pieslice(((right - 2 * rad, bottom - 2 * rad), (right, bottom)), 0, 90, fill=fill_,
                                      outline=fill_)
                        draw.rectangle((left + rad, top, right - rad, bottom), fill=fill_)
                        draw.rectangle((left, top + rad, right, bottom - rad), fill=fill_)
                    res = Image.new('RGBA', image.size, (0, 0, 0, 0))
                    res.paste(image, mask=mask)
                    res.save(it_png)
                    res.close()
                    # endregion

                    # region rbg
                    if is_rbg:
                        img = Image.open(it_png)
                        output_ = remove(img)
                        output_.save(it_png)  # endregion
                except Exception as e:
                    logger.info(log_ % str(e))
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            for i in range(0, frames * 2):
                it_png = file_png if i < frames else file_gray_png
                shutil.copy(it_png, f"{spec_dir}/frame_{i:04d}.png")
        else:
            # clip = mp.VideoFileClip(input_file).subclip(0, 3)
            # clip.close()
            # for i, frame in enumerate(clip.iter_frames(fps=clip.fps, dtype='uint8')):
            #     if i> clip.fps * 3 - 10: break
            #     it_png = f"{spec_dir}/frame_{i:04d}.png"
            #     clip.save_frame(it_png, t=i / clip.fps, withmask=True)

            try:
                if not is_circle and PACK_TYPE == 'sticker':
                    clip = mp.VideoFileClip(input_file)
                    width, height = clip.size

                    if width != height and (width > side_sz or height > side_sz):
                        if width > height:
                            pixels_str = f"{side_sz}x{int(side_sz * (height / width))}"
                        else:
                            pixels_str = f"{int(side_sz * (width / height))}x{side_sz}"
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            try:
                ffmpeg_command = ['ffmpeg', '-i', input_file, '-filter_complex_threads', '2', '-r', str(fps), '-b:v',
                    '40k', '-crf', '30', '-s', pixels_str, '-t', '3', '-an', '-y', file_mp4]
                p = await asyncio.create_subprocess_exec(*ffmpeg_command)
                await p.communicate()

                if os.path.exists(input_file): os.remove(input_file)
                input_file = file_mp4
                i_input_data = input_file
                print('end', pixels_str)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            if is_circle:
                rounded = '[0:v]crop=ih:ih[video square];[video square]split=3[black canvas][white canvas][video square];[black canvas]setsar=1:1,drawbox=color=black@1:t=fill[black background];[white canvas]scale=w=iw*2:h=iw*2,format=yuva444p,geq=lum=\'p(X,Y)\':a=\'st(1,pow(min(W/2,H/2),2))+st(3,pow(X-(W/2),2)+pow(Y-(H/2),2));if(lte(ld(3),ld(1)),255,0)\',drawbox=color=white@1:t=fill[scaled up white circle];[scaled up white circle]scale=w=iw/2:h=iw/2[white circle];[black background][white circle]overlay[alpha mask];[video square][alpha mask]alphamerge,format=yuva420p'
            else:
                # rounded = f'split[s0][s1];[s0]pad=width={side_sz}:height={side_sz}:color=black[s2];[s1]scale={side_sz}:{side_sz}:force_original_aspect_ratio=decrease[s3];[s2][s3]overlay=W-w-1:H-h-1,setsar=1'
                # rounded = 'split[s0][s1];[s0]pad=width=512:height=512:color=black[s2];[s1]scale=512:512:force_original_aspect_ratio=decrease[s3];[s2][s3]overlay=W-w-1:H-h-1,drawbox=0:0:iw:ih:color=black@0.0[rounded]'
                print('here 2', i_input_data, os.path.exists(input_file))

        ffmpeg_command = ['ffmpeg', '-i', i_input_data, '-filter_complex', rounded,

            '-filter_complex_threads', '2', '-c:v', 'libvpx-vp9', '-r', str(fps), '-b:v', bitrate, '-crf', '30', '-s',
            pixels_str, '-pix_fmt', 'yuva420p', '-t', '3', '-an', '-y', file_webm]

        print(f"{ffmpeg_command=}")
        p = await asyncio.create_subprocess_exec(*ffmpeg_command)
        await p.communicate()

        # region webm
        # images = []
        # for it_png in sorted(os.listdir(spec_dir)):
        #     images.append(np.array(Image.open(os.path.join(spec_dir, it_png))))
        # with imageio.get_writer(file_webm, mode='I', fps=fps, codec='libvpx-vp9', pixelformat='yuva420p') as writer:
        #     for image in images:
        #         try:
        #             writer.append_data(image)
        #             for _ in range(frames): writer.append_data(image)
        #         except Exception as e:
        #             logger.info(log_ % str(e))
        #             await asyncio.sleep(round(random.uniform(0, 1), 2))
        # endregion

        if is_upload:
            upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(file_webm),
                                                sticker_format=sticker_format)
            result_upl = upl.file_id
        else:
            upl = await bot.upload_sticker_file(user_id=chat_id, sticker=types.FSInputFile(file_webm),
                                                sticker_format=sticker_format)
            result_upl = upl.file_id

            tmp_name = f"by_{chat_id}_{str(time.time()).split('.')[-1]}_by_{bot_username}"
            sticker = types.InputSticker(sticker=result_upl, emoji_list=['👩🏽‍💻'])
            await bot.create_new_sticker_set(user_id=chat_id, name=tmp_name, title=str_empty, stickers=[sticker],
                                             sticker_format=sticker_format)
            get_sticker_set_ = await bot.get_sticker_set(name=tmp_name)
            result = await bot.send_sticker(chat_id, get_sticker_set_.stickers[0].file_id)
            await bot.delete_sticker_set(tmp_name)
            result = result.sticker.file_id
        print(f"result_upl ok")

        # sticker = types.InputSticker(sticker=result, emoji_list=['👩🏽‍💻'])  # await bot.add_sticker_to_set(user_id=chat_id, name=name, sticker=sticker)  # get_sticker_set2_ = await bot.get_sticker_set(name=name)  # res2 = get_sticker_set2_.stickers[-1].file_id  # await bot.send_sticker(chat_id, res2)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        try:
            if os.path.exists(spec_dir):
                shutil.rmtree(spec_dir)
            if os.path.exists(file_jpg): os.remove(file_jpg)
            if os.path.exists(file_png): os.remove(file_png)
            if os.path.exists(file_webm): os.remove(file_webm)
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(0, 1), 2))
        return result, result_upl


async def squared_video_ffmpeg(file_name, MEDIA_D):
    result = None
    try:
        clip = mp.VideoFileClip(file_name)
        width, height = clip.size
        min_side = width if width < height else height
        min_side = 640 if min_side > 640 else min_side
        file_name_part2 = f"{datetime.datetime.utcnow().strftime('r_%d-%m-%Y_%H-%M-%S-%f.mp4')}"
        file_video_note = os.path.join(MEDIA_D, file_name_part2)
        center_x = int(width / 2) - int(min_side / 2)
        center_y = int(height / 2) - int(min_side / 2)

        ffmpeg_command = ['ffmpeg', '-i', file_name, '-filter_complex_threads', '2', '-vf',
            f'scale={min_side}:{min_side},setsar=1:1', '-r', '30', '-s', f'{min_side}x{min_side}', '-vf',
            f'crop={min_side}:{min_side}:{center_x}:{center_y}', '-t', '59', '-y', file_video_note]
        p = await asyncio.create_subprocess_exec(*ffmpeg_command)
        await p.communicate()
        result = file_video_note
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def handle_ver(emj, emj_data, entities_list):
    entities_list.append(
        {'match_start': emj_data.get('match_start'), 'match_end': emj_data.get('match_end'), 'emoji': emj})
    return str(None)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html.strip())
    return cleantext


async def format_text_md(txt, is_web=False):
    result = txt
    try:
        if format_text == '': return
        result = result[0].upper() + result[1:]
        tmp_arr = re.split(r'\s+', result)
        entities = []
        emoji.demojize(string=tmp_arr[0], language='en', version=-1,
                       handle_version=lambda emj, emj_data: handle_ver(emj, emj_data, entities))
        distinct_list = list({e['emoji'] for e in entities})
        is_first_emoji = True if len(distinct_list) else False
        # is_first_emoji = any(unicodedata.category(c).startswith('So') for c in result)
        sym_lst = ('<', '>', '#', '$', '=', '*', '_', '|', '[', '~', '{', '`')

        if not is_first_emoji and len(tmp_arr) > 0:
            if not tmp_arr[0].startswith(sym_lst):
                result = result.replace(tmp_arr[0], f"*{tmp_arr[0]}*", 1)

        if not is_first_emoji:
            item = random.choice(emojis_)
            result = f"{item} {result}"

        tmp_arr = re.split(r'\s+', result)
        if len(tmp_arr) > 2 and not tmp_arr[1].startswith(sym_lst):
            result = result.replace(tmp_arr[1], f"*{tmp_arr[1]}*", 1)

        # italic
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'italic: {word}')
                # result = result.replace(word, f"_{word}_")
                word_pattern = re.escape(word)  # Экранируем специальные символы в слове
                result = re.sub(rf'\b{word_pattern}\b', f"_{word}_", result)
                break

        # spoiler
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'spoiler: {word}')
                # result = result.replace(word, f"||{word}||")
                word_pattern = re.escape(word)  # Экранируем специальные символы в слове
                result = re.sub(rf'\b{word_pattern}\b', f"||{word}||", result)
                break

        # under
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'under: {word}')
                # result = result.replace(word, f"__{word}__")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"__{word}__", result)
                break

        # bold
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'bold: {word}')
                # result = result.replace(word, f"*{word}*")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"*{word}*", result)
                break

        # mono
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'mono: {word}')
                # result = result.replace(word, f"`{word}`")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"`{word}`", result)
                break

        if not is_web:
            # quote
            tmp_arr = re.split(r'\s+', result)
            i = min(len(tmp_arr), 15)
            while i > 0:
                i -= 1
                r_i = random.randint(0, len(tmp_arr) - 1)
                word = tmp_arr[r_i]
                if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                        map(lambda c: c.isascii() and not c.isalnum(), word))):
                    word_pattern = re.escape(word)
                    result = re.sub(rf'\b{word_pattern}\b', f">{word}", result)
                    break

            # pre
            tmp_arr = re.split(r'\s+', result)
            i = min(len(tmp_arr), 15)
            while i > 0:
                i -= 1
                r_i = random.randint(0, len(tmp_arr) - 1)
                word = tmp_arr[r_i]
                if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                        map(lambda c: c.isascii() and not c.isalnum(), word))):
                    # print(f'quote: {word}')
                    # result = result.replace(word, f"```\n{word}```")
                    word_pattern = re.escape(word)
                    result = re.sub(rf'\b{word_pattern}\b', f"```{word}```", result)
                    break

            # py  # tmp_arr = re.split(r'\s+', result)  # i = min(len(tmp_arr), 15)  # while i > 0:  #     i -= 1  #     r_i = random.randint(0, len(tmp_arr) - 1)  #     word = tmp_arr[r_i]  #     if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(  #             sym_lst) and not any(  #         map(lambda c: c.isascii() and not c.isalnum(), word))):  #         # print(f'python: {word}')  #         # result = result.replace(word, f"```py\n{word}```")  #         word_pattern = re.escape(word)  #         result = re.sub(rf'\b{word_pattern}\b', f"```py\n{word}```", result)  #         break

        # hashtag
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'hashtag: {word}')
                # result = result.replace(word, f"#{word}")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"#{word}", result)
                break

        # tmp_arr = re.split(r'\s+', result)
        # i = min(len(tmp_arr), 15)
        # while i > 0:
        #     i -= 1
        #     r_i = random.randint(0, len(tmp_arr) - 1)
        #     word = tmp_arr[r_i]
        #     if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(
        #         sym_lst) and not any(
        #         map(lambda c: c.isascii() and not c.isalnum(), word))):
        #         print(f'cashtag: {word}')
        #         result = result.replace(word, f"${word}")
        #         break

        result = result.replace('( ', '(')
        result = result.replace(' )', ')')
        result = result.replace(' ,', ',')
    except Exception as e:
        logger.info(log_ % e)
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def format_link_md(txt):
    result = txt
    try:
        if format_text == '': return
        tmp_arr = re.split(r'\s+', result)
        arr_links = []
        arr_tlg_links = []

        for item in tmp_arr:
            if item.lower().startswith('https://t.me/') and item not in arr_tlg_links:
                arr_tlg_links.append(item)
            elif item.lower().startswith('https://') and item not in arr_links:
                arr_links.append(item)

        for tlg_link in arr_tlg_links:
            tmp1 = tlg_link.lower().split("https://t.me/")
            if len(tmp1) < 2: continue
            tmp2 = tmp1[1].split('/')
            link_name = tmp2[0].replace(',', '')
            arr_tlg_links_item = tlg_link.replace(',', '')
            result = result.replace(arr_tlg_links_item,
                                    f"[{link_name}]({arr_tlg_links_item.strip()})")  # [inline URL](http://www.example.com/)

        for link in arr_links:
            tmp1 = link.lower().split("https://")
            if len(tmp1) < 2: continue
            tmp2 = tmp1[1].split('/')
            link_name = tmp2[0]
            result = result.replace(link, f"[{link_name}]({link.strip()})")

        # if result == txt and 'https://' in txt and 'href="' in txt:  #     ix1 = str(result).find('href="')  #     ix2 = str(result).find('">', ix1)  #     tmp1 = result[ix1 + len('href="'):ix2]  #     tmp2 = tmp1.split("https://")[1].split('/')[0]  #     result = result.replace(f'>{tmp1}</a>', f'>{tmp2}</a>')
    except Exception as e:
        logger.info(log_ % e)
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def format_text(txt, is_web=False):
    result = txt
    try:
        if format_text == '': return
        result = result[0].upper() + result[1:]
        tmp_arr = re.split(r'\s+', result)
        entities = []
        emoji.demojize(string=tmp_arr[0], language='en', version=-1,
                       handle_version=lambda emj, emj_data: handle_ver(emj, emj_data, entities))
        distinct_list = list({e['emoji'] for e in entities})
        is_first_emoji = True if len(distinct_list) else False
        # is_first_emoji = any(unicodedata.category(c).startswith('So') for c in result)
        sym_lst = ('<', '>', '#', '$', '=', 'href')

        if not is_first_emoji and len(tmp_arr) > 0:
            if not tmp_arr[0].startswith(('<', '#', '$', '=', 'href')):
                result = result.replace(tmp_arr[0], f"<b>{tmp_arr[0]}</b>", 1)

        if not is_first_emoji:
            item = random.choice(emojis_)
            result = f"{item} {result}"

        tmp_arr = re.split(r'\s+', result)
        if len(tmp_arr) > 2 and not tmp_arr[1].startswith(sym_lst):
            result = result.replace(tmp_arr[1], f"<b>{tmp_arr[1]}</b>", 1)

        # italic
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'italic: {word}')
                # result = result.replace(word, f"<i>{word}</i>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"<i>{word}</i>", result)
                break

        # spoiler
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'spoiler: {word}')
                # result = result.replace(word, f"<tg-spoiler>{word}</tg-spoiler>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"<tg-spoiler>{word}</tg-spoiler>", result)
                break

        # under
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'under: {word}')
                # result = result.replace(word, f"<u>{word}</u>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"<u>{word}</u>", result)
                break

        # bold
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'bold: {word}')
                # result = result.replace(word, f"<b>{word}</b>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"<b>{word}</b>", result)
                break

        # code
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'mono: {word}')
                # result = result.replace(word, f"<code>{word}</code>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"<code>{word}</code>", result)
                break

        if not is_web:
            # quote
            tmp_arr = re.split(r'\s+', result)
            i = min(len(tmp_arr), 15)
            while i > 0:
                i -= 1
                r_i = random.randint(0, len(tmp_arr) - 1)
                word = tmp_arr[r_i]
                if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                        map(lambda c: c.isascii() and not c.isalnum(), word))):
                    # print(f'quote: {word}')
                    # result = result.replace(word, f"<blockquote>{word}</blockquote>")
                    word_pattern = re.escape(word)
                    result = re.sub(rf'\b{word_pattern}\b', f"<blockquote>{word}</blockquote>", result)
                    break

            # pre
            tmp_arr = re.split(r'\s+', result)
            i = min(len(tmp_arr), 15)
            while i > 0:
                i -= 1
                r_i = random.randint(0, len(tmp_arr) - 1)
                word = tmp_arr[r_i]
                if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                        map(lambda c: c.isascii() and not c.isalnum(), word))):
                    # print(f'python: {word}')
                    # result = result.replace(word, f"<pre>py\n{word}</pre>")
                    word_pattern = re.escape(word)
                    result = re.sub(rf'\b{word_pattern}\b', f"<pre>{word}</pre>", result)
                    break

        # hashtag
        tmp_arr = re.split(r'\s+', result)
        i = min(len(tmp_arr), 15)
        while i > 0:
            i -= 1
            r_i = random.randint(0, len(tmp_arr) - 1)
            word = tmp_arr[r_i]
            if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(sym_lst) and not any(
                    map(lambda c: c.isascii() and not c.isalnum(), word))):
                # print(f'hashtag: {word}')
                # result = result.replace(word, f"<span>#{word}</span>")
                word_pattern = re.escape(word)
                result = re.sub(rf'\b{word_pattern}\b', f"#{word}", result)
                break

        # tmp_arr = re.split(r'\s+', result)
        # i = min(len(tmp_arr), 15)
        # while i > 0:
        #     i -= 1
        #     r_i = random.randint(0, len(tmp_arr) - 1)
        #     word = tmp_arr[r_i]
        #     if (0 < r_i < len(tmp_arr) - 1 and len(word) >= 4 and not word.startswith(
        #         sym_lst) and not any(map(lambda c: c.isascii() and not c.isalnum(), word))):
        #         print(f'cashtag: {word}')
        #         result = result.replace(word, f"<span>${word}</span>")
        #         break

        result = result.replace('( ', '(')
        result = result.replace(' )', ')')
        result = result.replace(' ,', ',')
    except Exception as e:
        logger.info(log_ % e)
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def format_link(txt):
    result = txt
    try:
        if format_text == '': return
        tmp_arr = re.split(r'\s+', result)
        arr_links = []
        arr_tlg_links = []

        for item in tmp_arr:
            if item.lower().startswith('https://t.me/') and item not in arr_tlg_links:
                arr_tlg_links.append(item)
            elif item.lower().startswith('https://') and item not in arr_links:
                arr_links.append(item)

        for tlg_link in arr_tlg_links:
            tmp1 = tlg_link.lower().split("https://t.me/")
            if len(tmp1) < 2: continue
            tmp2 = tmp1[1].split('/')
            link_name = tmp2[0].replace(',', '')
            arr_tlg_links_item = tlg_link.replace(',', '')
            result = result.replace(arr_tlg_links_item, f"<a href='{arr_tlg_links_item.strip()}'>{link_name}</a>")

        for link in arr_links:
            tmp1 = link.lower().split("https://")
            if len(tmp1) < 2: continue
            tmp2 = tmp1[1].split('/')
            link_name = tmp2[0]
            result = result.replace(link, f"<a href='{link.strip()}'>{link_name}</a>")

        if result == txt and 'https://' in txt and 'href="' in txt:
            ix1 = str(result).find('href="')
            ix2 = str(result).find('">', ix1)
            tmp1 = result[ix1 + len('href="'):ix2]
            tmp2 = tmp1.split("https://")[1].split('/')[0]
            result = result.replace(f'>{tmp1}</a>', f'>{tmp2}</a>')
    except Exception as e:
        logger.info(log_ % e)
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def upper_register(txt):
    result = str(txt).replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3', '³').replace('4', '⁴').replace(
        '5', '⁵').replace('6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹')
    try:
        if len(result) == 4:
            result = f"{result[0]}˙{result[1]}ᵏ"
        elif len(result) == 5:
            result = f"{result[0]}{result[1]}˙{result[2]}ᵏ"
        elif len(result) == 6:
            result = f"{result[0]}{result[1]}{result[2]}˙{result[3]}ᵏ"
        elif len(result) >= 7:
            result = f"{result[0]}˙{result[2]}ᴹ"
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def convert_tgmd_to_html(markdown_text):
    result = markdown_text
    try:
        # markdown_text = "👩🏽‍💻 Lorem _начало_, ыусщте  df d d\n_Это_ *пример* [link](https://t.me) текста с *жирным* и _курсивом_\n\n[Ссылка на Google](https://www.google.com)\n\n#Хэштег #markdown #HTML\n\n$Кэштег $python $coding\n\n~Этот текст будет перечеркнут~\n\n__Этот текст будет подчеркнут__\n\n`Это кодовый фрагмент`\n\n```Это тоже кодовый фрагмент```"
        markdown_text = markdown_text.replace('\n', '<br>')

        # Заменяем * на <b> (жирный) только если он окружен пробелами или не имеет соседей с символами букв и цифр
        html_text = re.sub(r'(?<![\w*])\*(?!\*)\s*(.*?)\s*\*(?!\*)(?![\w*])', r'<b>\1</b>', markdown_text)
        html_text = re.sub(r'__(.*?)__', r'<u>\1</u>', html_text)
        html_text = re.sub(r'\|\|(.*?)\|\|', r'<code>\1</code>', html_text)
        html_text = re.sub(r'_(.*?)_', r'<i>\1</i>', html_text)
        html_text = re.sub(r'~(.*?)~', r'<s>\1</s>', html_text)
        html_text = re.sub(r'```(.*?)```', r'<code>\1</code>', html_text)
        html_text = re.sub(r'`(.*?)`', r'<code>\1</code>', html_text)

        html_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_text)
        html_text = re.sub(r'#(\w+)', r'<span>#\1</span>', html_text)
        html_text = re.sub(r'\$(\w+)', r'<span>$\1</span>', html_text)

        # async with aiofiles.open("index.html", "w", encoding="utf-8") as f:
        #     await f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<title>Markdown to HTML</title>\n<style>\nspan {{\n    color: #007bff;\n}}\na {{\n  text-decoration: none;\n}}\n</style>\n</head>\n<body>\n{html_text}\n</body>\n</html>")
        result = html_text
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


def escape_md(*content, sep=" ") -> str:
    """
    Escape Markdown text

    E.g. for usernames

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.quote(_join(*content, sep=sep))


async def random_text(text):
    result = text
    try:
        space_arr = []
        start_pos = 0
        for item in text:
            try:
                if item == ' ':
                    start_pos = (text.find(' ', start_pos)) + 1
                    space_arr.append(start_pos)
            except Exception:
                pass
        if len(space_arr) != 0:
            random_pos = random.choice(space_arr)
            result = f"{text[:random_pos]} {text[random_pos:]}"

        dic_char = {'В': 'B', 'М': '𐌑', 'С': 'Ϲ', 'а': 'a', 'в': 'ʙ', 'р': 'ρ', 'с': 'ϲ', 'п': 'n', 'ш': 'ɯ', 'э': '϶',
                    'к': 'κ'}  # 'и': 'ᥙ',
        arr = ['В', 'М', 'С', 'а', 'в', 'р', 'с', 'п', 'ш', 'э', 'к']  # 'и',
        random_chr = random.choice(arr)
        random_pos = arr.index(random_chr)
        for ix in range(0, random_pos):
            try:
                result = result.replace(arr[ix], dic_char[arr[ix]])
                result = f"{result}​"
            except Exception as e:
                logger.info(log_ % str(e))  # await asyncio.sleep(round(random.uniform(1, 2), 2))

        result = result[0:1023]  # result = result.replace('р', 'р')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def fun_stegano(f_name):
    result = f_name
    try:
        if not os.path.exists(f_name):
            logger.info(log_ % f"SteganoFun: no file {f_name}")
            return
        b_name = os.path.basename(f_name)
        d_name = os.path.dirname(f_name)
        random_name = os.path.join(d_name, f"{random.choice(string.ascii_letters + string.digits)}_{b_name}")
        random_len = random.randrange(5, 15)
        random_txt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random_len))

        if f_name.lower().endswith('png'):
            tmp = lsb.hide(f_name, random_txt)
            tmp.save(random_name)

            if os.path.exists(f_name):
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('jpeg') or f_name.lower().endswith('jpg'):
            exifHeader.hide(f_name, random_name, random_txt)

            if os.path.exists(f_name):
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('pdf'):
            keys = ['Title', 'Author', 'Producer', 'Creator', 'Language', 'PDFVersion', 'CreatorTool', 'DocumentID',
                    'InstanceID', 'FileModifyDate']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        et.set_tags([f_name], tags={key: random_txt}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}");  logger.debug("")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            try:
                with ExifToolHelper() as et:
                    et.set_tags([f_name], tags={'FilePermissions': 777777}, params=["-P", "-overwrite_original"])
            except Exception:
                # logger.info(log_ % f"for file {f_name}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('mov') or f_name.lower().endswith('mp4'):
            keys = ['Copyright', 'FileModifyDate', 'CreateDate', 'ModifyDate', 'TrackCreateDate', 'TrackModifyDate',
                    'MediaCreateDate', 'MediaModifyDate', 'MinorVersion']  # PageCount
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_date = (datetime.datetime.utcnow() - datetime.timedelta(
                            hours=random.randrange(1, 23))).strftime('%Y:%m:%d %H:%M:%S+03:00')
                        et.set_tags([f_name], tags={key: random_date}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            keys = ['XResolution', 'YResolution', 'Duration']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_num = random.randrange(1, 180)
                        et.set_tags([f_name], tags={key: random_num}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        else:
            keys = ['FileModifyDate']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_date = (datetime.datetime.utcnow() - datetime.timedelta(
                            hours=random.randrange(1, 23))).strftime('%Y:%m:%d %H:%M:%S+03:00')
                        et.set_tags([f_name], tags={key: random_date}, params=["-P", "-overwrite_original"])
                except Exception as e:
                    logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            try:
                with ExifToolHelper() as et:
                    et.set_tags([f_name], tags={'FilePermissions': 777777}, params=["-P", "-overwrite_original"])
            except Exception as e:
                logger.info(log_ % f"for file {f_name}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        logger.info(log_ % f"stagano ok")
    except Exception as e:
        logger.info(log_ % f"stageno error: {str(e)}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def correct_tag(txt, orig_txt=''):
    result = txt
    try:
        cnt_open = cnt_close = 0
        last_ix_open = last_ix_close = 0
        for i in range(0, len(txt)):
            try:
                if txt[i] == '<' and i + 1 < len(txt) - 1 and txt[i + 1] != '/':
                    cnt_open += 1
                    last_ix_open = i
                elif txt[i] == '<' and i + 1 < len(txt) - 1 and txt[i + 1] == '/':
                    cnt_close += 1
                    last_ix_close = i
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        if cnt_open and cnt_close:
            flag = False
            tmp = last_ix_close
            while tmp < len(txt) - 1:
                tmp += 1
                if txt[tmp] == '>':
                    flag = True
                    break
            if not flag:
                result = f"{txt[0:last_ix_open]} {{..}}"
            elif len(txt) < len(orig_txt):
                result = f"{result} {{..}}"
        elif cnt_open and cnt_close and cnt_open != cnt_close:
            result = f"{txt[0:last_ix_open]} {{..}}"
        elif len(txt) < len(orig_txt):
            result = f"{result} {{..}}"
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


# async def photo_to_video_sticker(bot, user_id, input_file, bot_username):
#     result = None
#     file_jpg = input_file[:input_file.rfind('.')] + '_.jpg'
#     file_gif = input_file[:input_file.rfind('.')] + '.gif'
#     file_mp4 = input_file[:input_file.rfind('.')] + '.mp4'
#     file_webm = input_file[:input_file.rfind('.')] + '.webm'
#     try:
#         image = Image.open(input_file)
#         width, height = image.size
#         left = (width - min(width, height)) // 2
#         top = (height - min(width, height)) // 2
#         right = (width + min(width, height)) // 2
#         bottom = (height + min(width, height)) // 2
#         image = image.crop((left, top, right, bottom))
#         image = image.resize((512, 512), resample=Image.LANCZOS)
#         image.save(file_jpg, format="JPEG")
#
#         quality = 90
#         while quality > 0:
#             img = Image.open(file_jpg)
#             img.save(file_jpg, format="JPEG", quality=quality)
#
#             if os.path.getsize(file_jpg) < 40000: break
#             quality = 1 if quality == 0 else quality - 10
#         if os.path.getsize(file_jpg) > 40000: return
#
#         image = Image.open(file_jpg)
#         frames = [image.copy(), ImageOps.grayscale(image)]
#         frames[0].save(file_gif, save_all=True, append_images=frames[1:], duration=500, loop=0, optimize=True)
#         clip = mp.VideoFileClip(file_gif)
#         clip = mp.concatenate_videoclips([clip] * 4, method="compose")
#         clip.write_videofile(file_mp4, fps=30, audio_codec='none', preset='ultrafast', bitrate="500k", threads=1)
#
#         command = ['ffmpeg', '-i', file_mp4, '-c:v', 'libvpx-vp9', '-b:v', '500k', '-an', '-y', file_webm]
#         subprocess.run(command)
#
#         sticker = types.InputSticker(sticker=types.FSInputFile(file_webm), emoji_list=['❤️'])
#         name = f"by_{user_id}_{str(time.time()).split('.')[-1]}_by_{bot_username}"
#         print(f"{name=}, {len(name)}")
#         await bot.create_new_sticker_set(user_id=user_id, name=name, title=f"{user_id}", stickers=[sticker],
#                                          sticker_format='video')
#         get_sticker_set_ = await bot.get_sticker_set(name=name)
#         result = get_sticker_set_.stickers[0].file_id
#     except TelegramRetryAfter as e:
#         logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
#         await asyncio.sleep(e.retry_after + 1)
#     except Exception as e:
#         logger.info(log_ % str(e))
#         await asyncio.sleep(round(random.uniform(0, 1), 2))
#     finally:
#         if os.path.exists(file_jpg): os.remove(file_jpg)
#         if os.path.exists(file_gif): os.remove(file_gif)
#         if os.path.exists(file_mp4): os.remove(file_mp4)
#         if os.path.exists(file_webm): os.remove(file_webm)
#         return result
#
#
# async def video_to_video_sticker(bot, user_id, input_file, bot_username):
#     result = None
#     file_mp4 = input_file[:input_file.rfind('.')] + '_.mp4'
#     file_webm = input_file[:input_file.rfind('.')] + '.webm'
#     try:
#         target_size = 512
#         clip = mp.VideoFileClip(input_file)
#         top = (clip.size[1] - target_size) // 2
#         bottom = top + target_size
#         left = (clip.size[0] - target_size) // 2
#         right = left + target_size
#         cropped_clip = clip.crop(x1=left, y1=top, x2=right, y2=bottom)
#         resized_clip = cropped_clip.resize(width=target_size, height=target_size)
#         resized_clip.write_videofile(file_mp4, audio=False)
#         clip.close()
#         cropped_clip.close()
#         resized_clip.close()
#
#         command = ['ffmpeg', '-i', file_mp4, '-c:v', 'libvpx-vp9', '-b:v', '50k', '-crf', '30', '-s', '512x512', '-t',
#             '3', '-an', '-y', file_webm]
#         subprocess.run(command)
#
#         sticker = types.InputSticker(sticker=types.FSInputFile(file_webm), emoji_list=['❤️'])
#         name = f"by_{user_id}_{str(time.time()).split('.')[-1]}_by_{bot_username}"
#         print(f"{name=}, {len(name)}")
#         await bot.create_new_sticker_set(user_id=user_id, name=name, title=f"{user_id}", stickers=[sticker],
#                                          sticker_format='video')
#         get_sticker_set_ = await bot.get_sticker_set(name=name)
#         result = get_sticker_set_.stickers[0].file_id
#     except TelegramRetryAfter as e:
#         logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
#         await asyncio.sleep(e.retry_after + 1)
#     except Exception as e:
#         logger.info(log_ % str(e))
#         await asyncio.sleep(round(random.uniform(0, 1), 2))
#     finally:
#         if os.path.exists(file_mp4): os.remove(file_mp4)
#         if os.path.exists(file_webm): os.remove(file_webm)
#         return result


async def correct_link(link):
    result = link
    try:
        link = str(link)
        if len(str(link).strip()) < 4:
            result = None
            return
        link = link.strip()
        res = link.split()
        try:
            float(res[0])
            link = str(link.split()[1]).strip('@\'!')
        except:
            link = str(link.split()[0]).strip('@\'!')
        link = link.lstrip(':').rstrip('.')
        link = link.replace('@https://', 'https://').replace('@:t.me/', 'https://t.me/')

        if link.startswith('t.me/') and not ('+' in link or 'join_my_chat' in link):
            link = link.replace('t.me/', '')
        elif link.startswith('t.me/') and ('+' in link or 'join_my_chat' in link):
            link = f"https://{link}"
        elif link.endswith('.t.me'):
            link = link.replace('.t.me', '')
        else:
            if 'http://' in link:
                link = link.replace('http://', 'https://')
            link = link[len(const_url):len(link)] if const_url in link and not (
                    't.me/+' in link or 't.me/join_my_chat/' in link) else link

        if 'https://telesco.pe/' in link:
            link = link.replace('https://telesco.pe/', '')

        try:
            link = str(int(link))
        except Exception:
            link = link if 't.me/+' in str(link) or 't.me/join_my_chat/' in str(link) else f"@{link}"

        try:
            if link.split('/')[-1].isdigit():
                link = f"{link[:link.rindex('/')]}"
        except Exception:
            pass

        try:
            if '+' in link:
                link = str(int(link.split('+')[-1]))
        except Exception:
            pass

        try:
            if link.startswith('join_my_chat/'):
                link = f"t.me/{link}"
            elif link.startswith('@join_my_chat/'):
                link = link.replace('@', 't.me/')
        except Exception:
            pass

        link = link.lstrip(':-.')

        try:
            link = link.replace('@://', '')
            link = link.replace('@//', '')
            link = link.replace('@/', '')
            link = link.replace('@.me/', '')
            link = link.replace('@.', '')
            link = link.replace('@@', '')
            for el in link:
                if el not in string.ascii_letters + string.digits + "@_https://t.me/+ ":
                    link = link.replace(el, '')
        except Exception:
            pass

        result = str(result).rstrip('/').rstrip('.').rstrip(':')
        result = None if '@None' == link else link
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result
# endregion


# region telegraph
async def tgph_select(access_token, url):
    result = telegraph_ = None
    try:
        telegraph_ = Telegraph(access_token=access_token)
        pages_ = (await telegraph_.get_page_list())['pages']

        for page_ in pages_:
            if page_['url'] == url:
                result = await telegraph_.get_page(path=page_['path'], return_content=True, return_html=False)
                return
    except Exception as e:
        if 'Flood control exceeded' in str(e):
            try:
                secs = int(str(e).split(' seconds')[0].split()[-1])
                if secs < 10: await asyncio.sleep(secs + 1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        elif 'All connection attempts failed' in str(e):
            await asyncio.sleep(20)
        else:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return telegraph_, result


async def tgph_change(access_token, url, json_):
    retry = 2
    while retry > 0:
        try:
            await asyncio.sleep(round(random.uniform(1, 2), 2))
            telegraph_ = Telegraph(access_token=access_token)
            pages_ = await telegraph_.get_page_list()

            for page_ in pages_['pages']:
                if page_['url'] != url: continue

                get_page_ = await telegraph_.get_page(path=page_['path'], return_content=True, return_html=False)
                try:
                    content_json = json.loads(str(get_page_['content'][0]))
                    if len(content_json) > 20: raise Exception
                except:
                    await telegraph_.edit_page(path=page_['path'], title=page_['title'], html_content='{}')
                    content_json = {}

                timestamp_ = str(utils.datetime_to_timestamp(datetime.datetime.utcnow()))
                content_json[timestamp_] = json_
                post_dumps = json.dumps(content_json, ensure_ascii=False)
                await telegraph_.edit_page(path=page_['path'], title=page_['title'], html_content=post_dumps)
                return 1
        except Exception as e:
            if 'Flood control exceeded' in str(e):
                try:
                    secs = int(str(e).split(' seconds')[0].split()[-1])
                    if secs < 10: await asyncio.sleep(secs + 1)
                except Exception as e:
                    logger.info(log_ % str(e))
                    await asyncio.sleep(round(random.uniform(1, 2), 2))
            elif 'All connection attempts failed' in str(e):
                await asyncio.sleep(20)
            else:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        finally:
            retry -= 1
    return 0


async def tgph_clear(access_token, url):
    retry = 2
    while retry > 0:
        try:
            await asyncio.sleep(round(random.uniform(0, 1), 2))
            telegraph_ = Telegraph(access_token=access_token)
            pages_ = await telegraph_.get_page_list()

            for page_ in pages_['pages']:
                if page_['url'] == url:
                    await telegraph_.edit_page(path=page_['path'], title=page_['title'], html_content='{}')
                return 1
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))
        finally:
            retry -= 1
    return 0


async def get_tgph_link(file_name):
    result = None
    try:
        ext = str(file_name[file_name.rfind('.'):]).lower()
        if file_name and os.path.exists(file_name) and os.path.getsize(file_name) < 5242880 and ext in ['.jpg', '.jpeg',
                                                                                                        '.png', '.gif',
                                                                                                        '.mp4']:
            cnt = 2
            while cnt >= 0:
                try:
                    telegraph_ = Telegraph()
                    res = await telegraph_.upload_file(file_name)
                    result = f"https://telegra.ph{res[0]['src']}"
                    return
                except Exception as e:
                    logger.info(log_ % f"Telegraph (cnt={cnt}): {str(e)}")
                    await asyncio.sleep(round(random.uniform(6, 10), 2))
                    cnt -= 1
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def is_ban_menu(chat_id):
    result = False
    try:
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()

                    if str(chat_id) in ban_ids:
                        result = True
                    return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        # telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)  # html_ = {'one': '1', 'two': '2'}  # html_ = json.dumps(html_, ensure_ascii=False)  # page_ = telegraph_.create_page(title='broadcasting', html_content=html_, author_name='bot_username', author_url='https://t.me/bot_username', return_content=True)  # page_url = page_['url']
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def ban_handler_menu(bot, chat_id, args):
    try:
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        if not args:
            for item in pages['pages']:
                try:
                    if item['path'] == 'ban-04-11-7':
                        page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                        ban_ids = str(page['content'])
                        ban_ids = ban_ids[:4096]
                        ban_ids = ' '.join([f"<code>{it}</code>" for it in ban_ids.split()])

                        await bot.send_message(chat_id, ban_ids)
                        return
                except Exception as e:
                    logger.info(log_ % str(e))
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

        prepare_ids = args.split()
        prepare_ids = [prepare_id for prepare_id in prepare_ids if prepare_id.isdigit()]
        if not len(prepare_ids): return

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()
                    length1 = len(ban_ids)
                    ban_ids = f"{page['content']} {' '.join(prepare_ids)}"
                    ban_ids = ban_ids.split()
                    ban_ids = list(set(ban_ids))
                    length2 = len(ban_ids)
                    modul = abs(length1 - length2)
                    await telegraph_.edit_page(path=item['path'], title="ban", html_content=' '.join(ban_ids))

                    if length1 != length2:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th added to /ban (len: {length2})")
                    else:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th already in /ban (len: {length2})")
                    break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def unban_handler_menu(bot, chat_id, args):
    try:
        if not args:
            return
        else:
            prepare_ids = args.split()

        prepare_ids = [prepare_id for prepare_id in prepare_ids if prepare_id.isdigit()]
        if not len(prepare_ids): return
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()
                    length1 = len(ban_ids)

                    ban_ids = [ban_id for ban_id in ban_ids if ban_id not in prepare_ids]
                    length2 = len(ban_ids)
                    ban_ids = list(set(ban_ids))
                    modul = abs(length1 - length2)
                    html_content = ' '.join(ban_ids)
                    html_content = '0' if html_content == '' else html_content
                    await telegraph_.edit_page(path=item['path'], title="ban", html_content=html_content)

                    if length1 != length2:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th removed from /ban (len: {length2})")
                    else:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th already deleted from /ban (len: {length2})")
                    break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def check_tgph_posts(bot_username, BASE_D):
    try:
        arr = [k for k, v in TGPH_TOKENS.items() if bot_username in k]
        access_key = arr[0] if len(arr) else None
        if not access_key: return

        access_token = TGPH_TOKENS[access_key]
        telegraph_ = Telegraph(access_token=access_token)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['url'] != access_key: continue
                page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=False)
                try:
                    content_json = json.loads(str(page['content'][0]))
                except:
                    content_json = {}

                for OFFER_USERTID, v in content_json.items():
                    OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT, OFFER_TZ = v

                    sql = "INSERT OR IGNORE INTO OFFER (OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, " \
                          "OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, " \
                          "OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT, " \
                          "OFFER_TZ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    await db_change(sql, (
                        int(OFFER_USERTID), v[OFFER_TEXT], v[OFFER_MEDIATYPE], v[OFFER_FILEID], v[OFFER_BUTTON],
                        v[OFFER_ISBUTTON], v[OFFER_TGPHLINK], v[OFFER_ISTGPH], v[OFFER_ISSPOILER], v[OFFER_ISPIN],
                        v[OFFER_ISSILENCE], v[OFFER_ISGALLERY], v[OFFER_DT], v[OFFER_TZ],), BASE_D)

                    del content_json[str(OFFER_USERTID)]
                    post_dumps = json.dumps(content_json, ensure_ascii=False)
                    await telegraph_.edit_page(path=item['path'], title=access_key, html_content=post_dumps)
                    return
            except Exception as e:
                if 'Flood control exceeded' in str(e):
                    await run_shell(f'/usr/bin/pm2 restart {bot_username}')
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def in_ban_list(tid, username=None):
    result = False
    try:
        b_ids = [68728482,  # @yagupov
                 201960795,  # @korsdp
                 ]

        if username and username.startswith('kwprod'):
            result = True
        elif tid in b_ids:
            result = True
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def create_tgph_json_and_token(title_hash):
    ENT_TOKENTGPH = ENT_PAGETGPH = ENT_JSONTGPH = None
    try:
        telegraph_ = Telegraph()
        account_ = await telegraph_.create_account(short_name='me', author_name='blog', author_url="https://t.me")

        page_1 = await telegraph_.create_page(title=f"TGPH-JSON-USERS-blog",
                                              html_content="<a href='https://t.me'>@blog</a>", author_name='blog',
                                              author_url="https://t.me")
        page_2 = await telegraph_.create_page(title=f"TGPH-JSON-USERS-{title_hash}", html_content='{}')

        ENT_TOKENTGPH = account_['access_token']
        ENT_PAGETGPH = page_1['url']
        ENT_JSONTGPH = page_2['url']
        print(f"access_token = {ENT_TOKENTGPH}, ENT_PAGETGPH = {ENT_PAGETGPH}, ENT_JSONTGPH = {ENT_JSONTGPH}")
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH


async def generate_tgph_page(bot, title_hash, USER_ID, ENT_TID, ENT_USERNAME, ENT_FN, MEDIA_D, BASE_D,
                             entity_type='bot'):
    ENT_TOKENTGPH = ENT_PAGETGPH = ENT_JSONTGPH = tgph_ph = None
    try:
        if entity_type == 'bot':
            sql = "SELECT BOT_TOKENTGPH, BOT_PAGETGPH, BOT_JSONTGPH FROM BOT WHERE BOT_TID=?"
            data = await db_select(sql, (ENT_TID,), BASE_D)
        else:
            sql = "SELECT UB_TOKENTGPH, UB_PAGETGPH, UB_JSONTGPH FROM UB WHERE UB_TID=?"
            data = await db_select(sql, (ENT_TID,), BASE_D)

        if len(data):
            ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH = data[0]
            if ENT_TOKENTGPH and ENT_PAGETGPH and ENT_JSONTGPH: return

        # file_name = os.path.join(MEDIA_D, datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpeg'))
        # try:
        #     profile_photos_ = await bot.get_user_profile_photos(user_id=USER_ID, limit=1)
        #
        #     if len(profile_photos_.photos):
        #         photo_id = profile_photos_.photos[-1][-1].file_id
        #         file = await bot.get_file(photo_id)
        #         await bot.download_file(file.file_path, file_name)
        #         tgph_ph = await get_tgph_link(file_name)
        # except Exception as e:
        #     logger.info(log_ % str(e))
        #     await asyncio.sleep(round(random.uniform(0, 1), 2))
        # finally:
        #     if file_name and os.path.exists(file_name): os.remove(file_name)
        # tgph_ph = tgph_ph if tgph_ph else bot_logo_jpeg

        tgph_ph = logo_photo
        ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH = await create_tgph_page(tgph_ph, title_hash, ENT_TID, ENT_USERNAME,
                                                                           ENT_FN, BASE_D, entity_type)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH


async def create_tgph_page(tgph_ph, title_hash, ENT_TID, ENT_USERNAME, ENT_FN, BASE_D, entity_type='bot'):
    ENT_TOKENTGPH = ENT_PAGETGPH = ENT_JSONTGPH = None
    try:
        cnt = 2
        while cnt >= 0:
            try:
                telegraph_ = Telegraph()
                title = "📰 Telegraph blog"
                author_url = f"https://t.me/{ENT_USERNAME}"
                tgph_ph = str(tgph_ph).replace('https://telegra.ph', '')
                bio = "💙 verified"

                account_ = await telegraph_.create_account(short_name=short_name, author_name=ENT_USERNAME,
                                                           author_url=author_url)
                n = f"<a href='https://t.me/{ENT_USERNAME}'>@{ENT_USERNAME}</a> <br>{ENT_FN}" if ENT_USERNAME else f"<b>{ENT_FN}</b>"
                los = "<figure><img src='{0}'/><figcaption>Photo: @{1}</figcaption></figure><blockquote>Landing <i>Telegram</i> Bot</blockquote>👩🏽‍💻 <b>Account:</b> {2}<br>[<b>id</b>=<code>{3}</code>]<br><b>Info:</b> {4}<br><aside>By</aside><aside><a href='https://t.me/{5}'>Link</a></aside>"
                html_ = los.format(tgph_ph, ENT_USERNAME, n, ENT_TID, bio, ENT_USERNAME)
                page_1 = await telegraph_.create_page(title=title, html_content=html_, author_name=ENT_USERNAME,
                                                      author_url=author_url)
                page_2 = await telegraph_.create_page(title=title_hash, html_content='{}')

                ENT_TOKENTGPH = account_['access_token']
                ENT_PAGETGPH = page_1['url']
                ENT_JSONTGPH = page_2['url']

                if entity_type == 'bot':
                    sql = "UPDATE BOT SET BOT_TOKENTGPH=?, BOT_PAGETGPH=?, BOT_JSONTGPH=? WHERE BOT_TID=?"
                    await db_change(sql, (ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH, ENT_TID,), BASE_D)
                else:
                    sql = "UPDATE UB SET UB_TOKENTGPH=?, UB_PAGETGPH=?, UB_JSONTGPH=? WHERE UB_TID=?"
                    await db_change(sql, (ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH, ENT_TID,), BASE_D)
                return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
                cnt -= 1
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return ENT_TOKENTGPH, ENT_PAGETGPH, ENT_JSONTGPH


# endregion


# region admin
async def pre_upload(bot, chat_id, media_name, media_type, EXTRA_D, BASE_D):
    result = None
    try:
        sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME=?"
        data = await db_select(sql, (media_name,), BASE_D)

        if not len(data):
            media = types.FSInputFile(os.path.join(EXTRA_D, media_name))
            res = None

            if media_type == 'photo':
                res = await bot.send_photo(chat_id=chat_id, photo=media)
                result = res.photo[-1].file_id
            elif media_type == 'video':
                res = await bot.send_video(chat_id=chat_id, video=media)
                result = res.video.file_id
            elif media_type == 'animation':
                res = await bot.send_animation(chat_id=chat_id, animation=media)
                result = res.animation.file_id
            elif media_type == 'audio':
                res = await bot.send_audio(chat_id=chat_id, audio=media)
                result = res.audio.file_id
            elif media_type == 'voice':
                res = await bot.send_voice(chat_id=chat_id, voice=media)
                result = res.voice.file_id
            elif media_type == 'video_note':
                res = await bot.send_video_note(chat_id=chat_id, video_note=media)
                result = res.video_note.file_id
            elif media_type == 'document':
                res = await bot.send_document(chat_id=chat_id, document=media, disable_content_type_detection=True)
                result = res.document.file_id
            elif media_type == 'sticker':
                res = await bot.send_sticker(chat_id=chat_id, sticker=media)
                result = res.sticker.file_id

            if res:
                await bot.delete_message(chat_id, res.message_id)
            sql = "INSERT OR IGNORE INTO FILE(FILE_FILEID, FILE_FILENAME) VALUES (?, ?)"
            await db_change(sql, (result, media_name,), BASE_D)
            logger.info(log_ % str(f'FILE_FILEID: {result}'))
        else:
            result = data[0][0]

        if media_type == 'photo':
            await bot.send_chat_action(chat_id=chat_id, action='upload_photo')
        elif media_type == 'video':
            await bot.send_chat_action(chat_id=chat_id, action='record_video')
        elif media_type == 'video_note':
            await bot.send_chat_action(chat_id=chat_id, action='record_video_note')
        elif media_type == 'animation':
            await bot.send_chat_action(chat_id=chat_id, action='record_video')
        elif media_type == 'audio':
            await bot.send_chat_action(chat_id=chat_id, action='upload_audio')
        elif media_type == 'voice':
            await bot.send_chat_action(chat_id=chat_id, action='record_voice')
        elif media_type == 'document':
            await bot.send_chat_action(chat_id=chat_id, action='upload_document')
        elif media_type == 'sticker':
            await bot.send_chat_action(chat_id=chat_id, action='choose_sticker')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id=1, call=None):
    try:
        sql = "SELECT OFFER_ID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, " \
              "OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT FROM OFFER"
        data_offers = await db_select(sql, (), BASE_D)
        if not data_offers:
            if call: await call.message.delete()
            await bot.send_message(chat_id, l_post_text[lz], reply_markup=markupAdmin)
            await state.set_state(FsmOffer.text)
            return

        # region config
        post_id = 1 if post_id < 1 else post_id
        item = data_offers[post_id - 1]
        OFFER_ID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT = item
        show_offers_datetime = l_post_datetime[lz]
        show_offers_button = l_post_buttons[lz]
        show_offers_off = l_off[lz]

        extra = f"\n\n{show_offers_datetime}: {OFFER_DT if OFFER_DT else show_offers_off}\n" \
                f"{show_offers_button}: {OFFER_BUTTON if OFFER_BUTTON else show_offers_off}\n"
        OFFER_TEXT = OFFER_TEXT or ''
        OFFER_TEXT = '' if OFFER_MEDIATYPE == 'video_note' or OFFER_MEDIATYPE == 'sticker' else OFFER_TEXT
        moment = 1020 - len(OFFER_TEXT) - len(extra)
        OFFER_TEXT = await correct_tag(f"{l_post_text[0:(len(OFFER_TEXT) + moment)]}") if moment <= 0 else OFFER_TEXT

        # endregion
        # region reply_markup
        reply_markup = get_keyboard_admin(data_offers, 'offers', post_id)

        buttons = [types.InlineKeyboardButton(text=f"✅ {l_btn[lz]}" if OFFER_ISBUTTON else f"☑️ {l_btn[lz]}",
                                              callback_data=f'ofr_isbtn_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=f"✅ {l_pin[lz]}" if OFFER_ISPIN else f"☑️ {l_pin[lz]}",
                                              callback_data=f'ofr_ispin_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=f"✅ {l_silence[lz]}" if OFFER_ISSILENCE else f"☑️ {l_silence[lz]}",
                                              callback_data=f'ofr_issilence_{OFFER_ID}_{post_id}'), ]
        reply_markup.row(*buttons)

        buttons = [types.InlineKeyboardButton(text=f"✅ {l_gallery[lz]}" if OFFER_ISGALLERY else f"☑️ {l_gallery[lz]}",
                                              callback_data=f'ofr_isgallery_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=f"✅ {l_preview[lz]}" if OFFER_ISTGPH else f"☑️ {l_preview[lz]}",
                                              callback_data=f'ofr_ispreview_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=f"✅ {l_spoiler[lz]}" if OFFER_ISSPOILER else f"☑️ {l_spoiler[lz]}",
                                              callback_data=f'ofr_isspoiler_{OFFER_ID}_{post_id}'), ]
        reply_markup.row(*buttons)

        buttons = [types.InlineKeyboardButton(text=l_post_new[lz], callback_data=f'ofr_new_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=l_post_delete[lz], callback_data=f'ofr_del_{OFFER_ID}_{post_id}'),
                   types.InlineKeyboardButton(text=l_post_change[lz], callback_data=f'ofr_edit_{OFFER_ID}_{post_id}'), ]
        reply_markup.row(*buttons)

        reply_markup.row(
            types.InlineKeyboardButton(text=l_post_publish[lz], callback_data=f'ofr_publication_{OFFER_ID}_{post_id}'))

        # endregion
        # region show
        if OFFER_FILEID and '[' not in OFFER_FILEID:
            OFFER_TEXT = OFFER_TEXT + extra
            if not call:
                if OFFER_MEDIATYPE == 'photo' or OFFER_MEDIATYPE == 'text':
                    await bot.send_photo(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'animation':
                    await bot.send_animation(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'video':
                    await bot.send_video(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'audio':
                    await bot.send_audio(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'document':
                    await bot.send_document(chat_id=chat_id, document=OFFER_FILEID, caption=OFFER_TEXT,
                                            disable_content_type_detection=True, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'sticker':
                    await bot.send_sticker(chat_id=chat_id, sticker=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'voice':
                    if has_restricted:
                        text = l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                        await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                               disable_web_page_preview=True)
                    else:
                        await bot.send_voice(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'video_note':
                    if has_restricted:
                        text = l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                    else:
                        await bot.send_video_note(chat_id=chat_id, video_note=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
            else:
                if OFFER_MEDIATYPE == 'photo' or OFFER_MEDIATYPE == 'text':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_photo(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaPhoto(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                      has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'animation':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_animation(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                                 reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaAnimation(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                          has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'video':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_video(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaVideo(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                      has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'audio':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_audio(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
                    else:
                        media = types.InputMediaAudio(media=OFFER_FILEID, caption=OFFER_TEXT)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'document':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_document(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                                disable_content_type_detection=True,
                                                reply_markup=reply_markup.as_markup())
                    else:
                        media = types.InputMediaDocument(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                         disable_content_type_detection=True)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'sticker':
                    await bot.send_sticker(chat_id, OFFER_FILEID)
                    await bot.send_message(chat_id=chat_id, text=OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'video_note':
                    if has_restricted:
                        text = l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                    else:
                        await bot.send_video_note(chat_id=chat_id, video_note=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'voice':
                    if has_restricted:
                        text = l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                        await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                               disable_web_page_preview=True)
                    else:
                        await bot.send_voice(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
        else:
            if call and str(post_id) == await get_current_page_number(call):
                await call.message.edit_reply_markup(reply_markup=reply_markup.as_markup())
            elif OFFER_FILEID:
                OFFER_FILEID = ast.literal_eval(OFFER_FILEID) if OFFER_FILEID and '[' in OFFER_FILEID else OFFER_FILEID
                OFFER_MEDIATYPE = ast.literal_eval(
                    OFFER_MEDIATYPE) if OFFER_MEDIATYPE and '[' in OFFER_MEDIATYPE else OFFER_MEDIATYPE

                media = []
                for i in range(0, len(OFFER_FILEID)):
                    caption = OFFER_TEXT if i == 0 else None

                    if OFFER_MEDIATYPE[i] == 'photo':
                        media.append(
                            types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                    elif OFFER_MEDIATYPE[i] == 'video':
                        media.append(
                            types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                    elif OFFER_MEDIATYPE[i] == 'audio':
                        media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                    elif OFFER_MEDIATYPE[i] == 'document':
                        media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                              disable_content_type_detection=True))

                await bot.send_media_group(chat_id, media)
                await bot.send_message(chat_id=chat_id, text=extra, reply_markup=reply_markup.as_markup())  # endregion
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def get_current_page_number(call):
    result = '_'
    try:
        lst = call.message.reply_markup.inline_keyboard
        for items in lst:
            for it in items:
                if it.text.startswith('·'):
                    result = it.text.strip('·')
                    result = result.strip()
                    break
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, ids):
    try:
        if ids == 'me':
            user_ids = [chat_id]
        elif not ids or ids == 'all':
            sql = "SELECT USER_TID FROM USER"
            data = await db_select(sql, (), BASE_D)
            user_ids = [item[0] for item in data]
        else:
            sql = "SELECT USER_TID FROM USER"
            data = await db_select(sql, (), BASE_D)
            user_ids = [item[0] for item in data]
            user_ids = [item for item in user_ids if str(item) in ids]

        duration = 0 if len(user_ids) < 50 else int(len(user_ids) / 50)
        if str(chat_id) in my_tids:
            text = l_broadcast_start[lz].format(duration)
            await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        all_len = len(user_ids)
        max_size = 20  # 1
        # max_size = 1  # 1
        fact_len = 0

        sql = "SELECT OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, " \
              "OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, " \
              "OFFER_DT FROM OFFER WHERE OFFER_ID=?"
        data = await db_select(sql, (offer_id,), BASE_D)
        if not len(data): return

        while True:
            try:
                random.shuffle(user_ids)
                await asyncio.sleep(0.05)
                tmp_user_ids = [user_ids.pop() for _ in range(0, max_size) if len(user_ids)]
                coroutines = [send_user(bot, tmp_user_id, offer_id, data[0]) for tmp_user_id in tmp_user_ids]
                results = await asyncio.gather(*coroutines)

                for result in results:
                    if result:
                        fact_len += 1

                if not len(user_ids): break
                per = int(float(len(user_ids)) / float(all_len) * 100.0)

                if str(chat_id) in my_tids:
                    text = l_broadcast_process[lz].format(100 - per)
                    await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.info(log_ % {str(e)})
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        if str(chat_id) not in my_tids:
            sql = "DELETE FROM OFFER WHERE OFFER_ID=?"
            await db_change(sql, (offer_id,), BASE_D)

        text = l_broadcast_finish[lz].format(fact_len)
        await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def send_user(bot, chat_id, offer_id, item, message_id=None, current=1):
    result = None
    try:
        OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT = item

        len_ = 1
        if OFFER_ISBUTTON:
            reply_markup = await create_replymarkup2(bot, offer_id, OFFER_BUTTON, 'ofr')
        else:
            reply_markup = InlineKeyboardBuilder()

        if '[' in OFFER_MEDIATYPE:
            OFFER_FILEID = ast.literal_eval(OFFER_FILEID)
            OFFER_MEDIATYPE = ast.literal_eval(OFFER_MEDIATYPE)
            OFFER_TGPHLINK = ast.literal_eval(OFFER_TGPHLINK)
            len_ = len(OFFER_FILEID)

            OFFER_FILEID = OFFER_FILEID[current - 1] if message_id else OFFER_FILEID[0]
            OFFER_MEDIATYPE = OFFER_MEDIATYPE[current - 1] if message_id else OFFER_MEDIATYPE[0]
            OFFER_TGPHLINK = OFFER_TGPHLINK[current - 1] if message_id else OFFER_TGPHLINK[0]

        if OFFER_ISTGPH and OFFER_TGPHLINK and '[' not in OFFER_TGPHLINK:
            OFFER_MEDIATYPE = 'text'
            OFFER_TEXT = OFFER_TEXT if OFFER_TEXT and OFFER_TEXT != '' else str_empty
            OFFER_TEXT = f"<a href='{OFFER_TGPHLINK}'>​</a>{OFFER_TEXT}"

            if OFFER_ISGALLERY:
                OFFER_TEXT = '' if OFFER_TEXT == str_empty and OFFER_MEDIATYPE != 'text' else OFFER_TEXT
                buttons = [
                    types.InlineKeyboardButton(text="←", callback_data=f'gallery_prev_{offer_id}_{current}_{len_}'),
                    types.InlineKeyboardButton(text=f"{current}/{len_}",
                                               switch_inline_query_current_chat=f"{offer_id} ~"),
                    types.InlineKeyboardButton(text="→", callback_data=f'gallery_next_{offer_id}_{current}_{len_}'), ]
                reply_markup.row(*buttons)

        if '[' in OFFER_MEDIATYPE and not message_id:
            media = []
            for i in range(0, len(OFFER_FILEID)):
                caption = OFFER_TEXT if i == 0 else None

                if OFFER_MEDIATYPE[i] == 'photo':
                    media.append(
                        types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'video':
                    media.append(
                        types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'audio':
                    media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                elif OFFER_MEDIATYPE[i] == 'document':
                    media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                          disable_content_type_detection=True))

            result = await bot.send_media_group(chat_id, media)
        if OFFER_MEDIATYPE == 'text':
            # await bot.send_message(chat_id=5491025132, text='OFFER_TEXT2')
            result = await bot.send_message(chat_id=chat_id, text=OFFER_TEXT, disable_web_page_preview=not OFFER_ISTGPH,
                                            disable_notification=OFFER_ISSILENCE, reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'animation':
            result = await bot.send_animation(chat_id=chat_id, animation=OFFER_FILEID, caption=OFFER_TEXT,
                                              has_spoiler=OFFER_ISSPOILER, disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'photo':
            result = await bot.send_photo(chat_id=chat_id, photo=OFFER_FILEID, caption=OFFER_TEXT,
                                          has_spoiler=OFFER_ISSPOILER, disable_notification=OFFER_ISSILENCE,
                                          reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'video':
            result = await bot.send_video(chat_id=chat_id, video=OFFER_FILEID, caption=OFFER_TEXT,
                                          has_spoiler=OFFER_ISSPOILER, disable_notification=OFFER_ISSILENCE,
                                          reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'audio':
            result = await bot.send_audio(chat_id=chat_id, audio=OFFER_FILEID, caption=OFFER_TEXT,
                                          disable_notification=OFFER_ISSILENCE, reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'voice':
            has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

            if has_restricted:
                result = await bot.send_voice(chat_id=chat_id, voice=OFFER_FILEID, caption=OFFER_TEXT,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
            else:
                result = await bot.send_audio(chat_id=chat_id, audio=OFFER_FILEID, caption=OFFER_TEXT,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'document':
            result = await bot.send_document(chat_id=chat_id, document=OFFER_FILEID, caption=OFFER_TEXT,
                                             disable_notification=OFFER_ISSILENCE, disable_content_type_detection=True,
                                             reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'video_note':
            has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

            if has_restricted:
                result = await bot.send_video(chat_id=chat_id, video=OFFER_FILEID, caption=OFFER_TEXT,
                                              has_spoiler=OFFER_ISSPOILER, disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
            else:
                result = await bot.send_video_note(chat_id=chat_id, video_note=OFFER_FILEID,
                                                   disable_notification=OFFER_ISSILENCE,
                                                   reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'sticker':
            result = await bot.send_sticker(chat_id=chat_id, sticker=OFFER_FILEID, disable_notification=OFFER_ISSILENCE,
                                            reply_markup=reply_markup.as_markup())

        if result and OFFER_ISPIN and not message_id and isinstance(result, list):
            await bot.pin_chat_message(chat_id=chat_id, message_id=result[0].message_id, disable_notification=False)
        elif result and OFFER_ISPIN and not message_id:
            await bot.pin_chat_message(chat_id=chat_id, message_id=result.message_id, disable_notification=False)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def generate_calendar_admin(bot, state, lz, chat_id, message_id=None, is_new=True):
    try:
        data = await state.get_data()
        shift_month = data.get('shift_month', 0)
        is_timer = data.get('is_timer', None)

        dt_ = datetime.datetime.utcnow() + datetime.timedelta(hours=0) + datetime.timedelta(days=32 * shift_month)
        if shift_month:
            dt_ = datetime.datetime(year=dt_.year, month=dt_.month, day=1)

        month_dic = {1: l_month_1[lz], 2: l_month_2[lz], 3: l_month_3[lz], 4: l_month_4[lz], 5: l_month_5[lz],
                     6: l_month_6[lz], 7: l_month_7[lz], 8: l_month_8[lz], 9: l_month_9[lz], 10: l_month_10[lz],
                     11: l_month_11[lz], 12: l_month_12[lz]}
        month = month_dic[dt_.month]

        reply_markup = InlineKeyboardBuilder()
        buttons = [types.InlineKeyboardButton(text="«", callback_data=f'calendar_left'),
                   types.InlineKeyboardButton(text=f"{month} {dt_.year}", callback_data='cb_99'),
                   types.InlineKeyboardButton(text="»", callback_data=f'calendar_right'), ]
        reply_markup.row(*buttons)

        buttons_ = [types.InlineKeyboardButton(text=l_weekday_1[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_2[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_3[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_4[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_5[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_6[lz], callback_data='cb_99'),
                    types.InlineKeyboardButton(text=l_weekday_7[lz], callback_data='cb_99'), ]
        reply_markup.row(*buttons_)

        week_first_day = datetime.datetime(year=dt_.year, month=dt_.month, day=1).weekday() + 1
        buttons_ = []
        for i in range(0, 6 * 7):
            buttons_.append(types.InlineKeyboardButton(text=" ", callback_data=f'cb_99'))

        month_days = monthrange(dt_.year, dt_.month)[1]
        for i in range(week_first_day + dt_.day - 1, month_days + week_first_day):
            cb_ = f'cb_{i - week_first_day + 1}..{dt_.month}..{dt_.year}'
            buttons_[i - 1] = types.InlineKeyboardButton(text=f"{i - week_first_day + 1}", callback_data=cb_)

        tmp = []
        for i in range(0, len(buttons_)):
            tmp.append(buttons_[i])
            if len(tmp) >= 7:
                reply_markup.row(*tmp)
                tmp = []
        text = l_post_timer[lz] if is_timer else l_post_date[lz]

        if is_new:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup.as_markup())
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                        reply_markup=reply_markup.as_markup())
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def callbacks_ofr_admin(bot, FsmOffer, call, state, BASE_D, bot_un):
    try:
        chat_id = call.from_user.id
        cmd = str(call.data.split("_")[1])
        post_id = int(call.data.split("_")[-1])
        offer_id = int(call.data.split("_")[-2])
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        if cmd == 'new':
            await state.clear()

            await state.set_state(FsmOffer.text)

            await bot.send_message(call.from_user.id, l_post_text[lz], reply_markup=markupAdmin)
        elif cmd == 'del':
            await state.clear()

            sql = "DELETE FROM OFFER WHERE OFFER_ID=?"
            await db_change(sql, (offer_id,), BASE_D)

            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id - 1,
                                    call)
        elif cmd == 'edit':
            await state.clear()

            await state.set_state(FsmOffer.text)
            await state.update_data(offer_id=offer_id)

            await bot.send_message(call.from_user.id, l_post_text[lz], reply_markup=markupAdmin)
        elif cmd == 'isbtn':
            sql = "SELECT OFFER_BUTTON, OFFER_ISBUTTON FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_BUTTON, OFFER_ISBUTTON = data[0]

            if OFFER_BUTTON:
                OFFER_ISBUTTON = 0 if OFFER_ISBUTTON else 1
                sql = "UPDATE OFFER SET OFFER_ISBUTTON=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISBUTTON, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = l_buttons_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'ispin':
            sql = "SELECT OFFER_ISPIN FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISPIN = 0 if data[0][0] else 1
            sql = "UPDATE OFFER SET OFFER_ISPIN=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISPIN, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'issilence':
            sql = "SELECT OFFER_ISSILENCE FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISSILENCE = 0 if data[0][0] else 1
            sql = "UPDATE OFFER SET OFFER_ISSILENCE=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISSILENCE, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'isgallery':
            sql = "SELECT OFFER_ISGALLERY, OFFER_FILEID FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISGALLERY, OFFER_FILEID = data[0]

            if OFFER_FILEID and '[' in OFFER_FILEID:
                OFFER_ISGALLERY = 0 if data[0][0] else 1
                sql = "UPDATE OFFER SET OFFER_ISGALLERY=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISGALLERY, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = l_gallery_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'ispreview':
            sql = "SELECT OFFER_ISTGPH, OFFER_TGPHLINK FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISTGPH, OFFER_TGPHLINK = data[0]

            if not OFFER_TGPHLINK:
                text = l_preview_text[lz]
                await call.answer(text=text, show_alert=True)

            OFFER_ISTGPH = 0 if OFFER_ISTGPH else 1
            sql = "UPDATE OFFER SET OFFER_ISTGPH=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISTGPH, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'isspoiler':
            sql = "SELECT OFFER_ISSPOILER, OFFER_MEDIATYPE FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISSPOILER, OFFER_MEDIATYPE = data[0]

            if OFFER_MEDIATYPE and OFFER_MEDIATYPE in ['photo', 'animation', 'video'] or '[' in OFFER_MEDIATYPE:
                OFFER_ISSPOILER = 0 if data[0][0] else 1
                sql = "UPDATE OFFER SET OFFER_ISSPOILER=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISSPOILER, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = l_spoiler_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'publication':
            await state.clear()
            await call.answer()

            reply_markup = InlineKeyboardBuilder()
            buttons = [types.InlineKeyboardButton(text=l_me[lz], callback_data=f"publication_me_{offer_id}"),
                       types.InlineKeyboardButton(text=l_all[lz], callback_data=f"publication_all_{offer_id}"),
                       types.InlineKeyboardButton(text=l_ids[lz], callback_data=f"publication_ids_{offer_id}"), ]
            reply_markup.add(*buttons).adjust(1)

            text = l_recipient[lz]
            await bot.send_message(chat_id, text, reply_markup=reply_markup.as_markup())
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def callbacks_publication_admin(bot, FsmIds, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        data, option, offer_id = call.data.split('_')

        if option == 'me':
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, 'me'))
        elif option == 'all':
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, 'all'))
        elif option == 'ids':
            await state.set_state(FsmIds.start)
            await state.update_data(offer_id=offer_id)

            text = l_enter[lz]
            await bot.send_message(chat_id, text)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_ids_start_admin(bot, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        arr = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./?]', message.text)
        ids = [it for it in arr if it != '']
        data = await state.get_data()
        offer_id = data.get('offer_id')

        loop = asyncio.get_event_loop()
        loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, ids))
        await state.clear()
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_text_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            await bot.send_message(chat_id, l_post_media[lz])
            await state.set_state(FsmOffer.media)
        else:
            if len(message.html_text) >= 1024:
                text = l_post_text_limit[lz].format(len(message.html_text))
                await bot.send_message(chat_id, text)
                return

            await state.update_data(offer_text=message.html_text)
            await bot.send_message(chat_id=chat_id, text=l_post_media[lz])
            await state.set_state(FsmOffer.media)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_album_admin(bot, FsmOffer, message, album, state, MEDIA_D, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        offer_text = None
        offer_file_id = None
        offer_file_type = None
        offer_tgph_link = None
        file_name_part = None

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            if not offer_text:
                await state.update_data(offer_text=str_empty)

            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        else:
            await bot.send_message(chat_id, l_post_media_wait[lz].format('album', 1))

            for obj in album:
                if obj.photo:
                    media_id = obj.photo[-1].file_id
                    media_type = 'photo'
                    dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpg')
                    file_name_part_new = f"{dt_}"
                elif obj.video:
                    media_id = obj.video.file_id
                    media_type = 'video'
                    file_name_part_new = obj.video.file_name
                elif obj.audio:
                    media_id = obj.audio.file_id
                    media_type = 'video_note'
                    file_name_part_new = obj.video.file_name
                else:
                    media_id = obj.document.file_id
                    media_type = 'document'
                    file_name_part_new = obj.video.file_name

                file_name = os.path.join(MEDIA_D, file_name_part_new)
                file = await bot.get_file(media_id)
                await bot.download_file(file.file_path, file_name)

                tgph_link = await get_tgph_link(file_name)
                tgph_link = '' if tgph_link is None else tgph_link
                if file_name and os.path.exists(file_name): os.remove(file_name)

                offer_tgph_link = (ast.literal_eval(str(offer_tgph_link)) + [tgph_link]) if offer_tgph_link else [
                    tgph_link]
                file_name_part = (ast.literal_eval(str(file_name_part)) + [file_name_part_new]) if file_name_part else [
                    file_name_part_new]
                offer_file_id = (ast.literal_eval(str(offer_file_id)) + [media_id]) if offer_file_id else [media_id]
                offer_file_type = (ast.literal_eval(str(offer_file_type)) + [media_type]) if offer_file_type else [
                    media_type]

                await state.update_data(offer_file_id=str(offer_file_id), offer_file_type=str(offer_file_type),
                                        offer_tgph_link=str(offer_tgph_link), file_name_part=str(file_name_part))
                await asyncio.sleep(0.05)

            if len(ast.literal_eval(str(offer_file_id))) < 2:
                await bot.send_message(chat_id=chat_id, text=l_post_media[lz])
                await state.set_state(FsmOffer.media)
                return

            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_media_admin(bot, FsmOffer, message, state, MEDIA_D, BASE_D, EXTRA_D):
    chat_id = message.from_user.id
    lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

    try:
        data = await state.get_data()
        offer_text = data.get('offer_text', None)

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            if not offer_text:
                await state.update_data(offer_text=str_empty)

            text = l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                l_post_button[lz].replace('XXXXX', '')
            await bot.send_message(chat_id, text)
            await state.set_state(FsmOffer.button)
        else:
            file_name = file_name_part = file_id = file_id_note = file_type = None
            if message.text:
                await bot.send_message(chat_id=chat_id, text=l_post_media[lz])
                return
            elif message.photo:
                file_id = message.photo[-1].file_id
                file_name_part = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpg')}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'photo'
            elif message.animation:
                await bot.send_message(chat_id, l_post_media_wait[lz].format('giff', 1))
                file_id = message.animation.file_id
                file_name_part = f"{message.animation.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'animation'

                if not (file_name.lower().endswith('.mp4') or file_name.lower().endswith(
                        '.gif') or file_name.lower().endswith('.giff')):
                    clip = mp.VideoFileClip(file_name)
                    tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
                    clip.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                         remove_temp=True)

                    if os.path.exists(file_name): os.remove(file_name)
                    file_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.mp4')
                    file_name_part = os.path.basename(file_name)
                    if os.path.exists(tmp_name): os.rename(tmp_name, file_name)
            elif message.sticker:
                if message.sticker.is_animated or message.sticker.is_video:
                    await bot.send_message(chat_id=chat_id, text=l_post_media[lz])
                    await state.set_state(FsmOffer.media)
                    return

                file_id = message.sticker.file_id
                dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.webp')
                file_name_part = f"{dt_}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'sticker'
            elif message.video:
                await bot.send_message(chat_id, l_post_media_wait[lz].format('video', 1))
                file_id = message.video.file_id
                file_name_part = f"{message.video.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)

                clip = mp.VideoFileClip(file_name)
                if int(clip.duration) < 60 and clip.size and clip.size[0] == clip.size[1] and clip.size[0] <= 640:
                    res = await bot.send_video_note(chat_id, types.FSInputFile(file_name))
                    file_id = res.video_note.file_id
                    file_type = 'video_note'
                else:
                    file_type = 'video'
            elif message.audio:  # m4a
                file_id = message.audio.file_id
                file_name_part = f"{message.audio.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'audio'

                performer = message.from_user.username if message.from_user.username else '@performer'
                title = html.quote(message.from_user.first_name)
                thumbnail = types.InputFile(os.path.join(EXTRA_D, 'img.jpg'))
                res = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(file_name), thumbnail=thumbnail,
                                           title=title, performer=performer)
                file_id = res.audio.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.voice:
                await bot.send_message(chat_id, l_post_media_wait[lz].format('voice', 1))
                file_id = message.voice.file_id
                dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.ogg')
                file_name_part = f"{dt_}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'voice'

                ogg_version = AudioSegment.from_ogg(file_name)
                ogg_version.export(file_name[:file_name.rfind('.')] + '.mp3', format="mp3")

                performer = message.from_user.username if message.from_user.username else '@performer'
                title = html.quote(message.from_user.first_name)
                thumbnail = types.InputFile(os.path.join(EXTRA_D, 'img.jpg'))
                res = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(file_name), thumbnail=thumbnail,
                                           title=title, performer=performer)
                file_id_note = res.audio.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.video_note:
                file_id = message.video_note.file_id
                file_name_part = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'video_note'

                res = await bot.send_video(chat_id=chat_id, video=types.FSInputFile(file_name))
                file_id_note = res.video.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.document:
                file_id = message.document.file_id
                file_name_part = f"{message.document.file_name}"
                file_type = 'document'

            offer_tgph_link = await get_tgph_link(file_name)
            offer_tgph_link = '' if offer_tgph_link is None else offer_tgph_link
            if file_name and os.path.exists(file_name): os.remove(file_name)

            await state.update_data(offer_file_id=file_id, offer_file_id_note=file_id_note, offer_file_type=file_type,
                                    offer_tgph_link=offer_tgph_link, file_name_part=file_name_part)

            text = l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                l_post_button[lz].replace('XXXXX', '')
            await bot.send_message(chat_id, text)
            await state.set_state(FsmOffer.button)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    # except FileIsTooBig as e:
    #     logger.info(log_ % str(e))
    #     await asyncio.sleep(round(random.uniform(0, 1), 2))
    #     await bot.send_message(chat_id, l_post_media_toobig[lz])
    except Exception as e:
        if 'too big' in str(e):
            await bot.send_message(chat_id, l_post_media_toobig[lz])
        else:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_button_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            await bot.send_message(message.from_user.id, l_post_media[lz])
            await state.set_state(FsmOffer.media)
        elif message.text in ['➡️️ Next', '/Next']:
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        else:
            res_ = await check_buttons(bot, chat_id, message.text.strip())
            if len(res_) == 0:
                text = l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                    l_post_button[lz].replace('XXXXX', '')
                await bot.send_message(chat_id, text)
                await state.set_state(FsmOffer.button)
                return

            await state.update_data(offer_button=message.text.strip())
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_date_cb_admin(bot, FsmOffer, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        offer_date = call.data.split('_')[-1]
        if offer_date == '99': return
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)

        day_, month_, year_ = offer_date.split('..')
        dt_user = datetime.datetime(year=int(year_), month=int(month_), day=int(day_))
        dt_user = dt_user.strftime("%d-%m-%Y")
        await state.update_data(offer_date=offer_date)

        sql = "SELECT USER_TZ FROM USER WHERE USER_TID=?"
        data = await db_select(sql, (chat_id,), BASE_D)
        USER_TZ = data[0][0] if data[0][0] else "+00:00"
        offer_tz = USER_TZ
        await state.update_data(offer_tz=offer_tz)
        sign_ = USER_TZ[0]
        h_, m_ = USER_TZ.strip(sign_).split(':')
        dt_now = datetime.datetime.utcnow()
        if sign_ == "+":
            dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
        else:
            dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))

        datetime_plus = (dt_cur + datetime.timedelta(hours=1)).strftime("%H:%M")
        datetime_current = dt_cur.strftime("%H:%M")

        text = l_generate_calendar_time[lz].format(dt_user, datetime_plus, datetime_current, USER_TZ)
        await bot.send_message(chat_id, text)
        await state.set_state(FsmOffer.time_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def calendar_handler_admin(bot, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        message_id = call.message.message_id
        shift = call.data.split('_')[-1]

        data = await state.get_data()
        shift_month = data.get('shift_month', 0)

        if shift == 'left':
            shift_month = 0 if shift_month == 0 else shift_month - 1
        elif shift == 'right':
            shift_month = shift_month + 1

        await state.update_data(shift_month=shift_month)
        await generate_calendar_admin(bot, state, lz, chat_id, message_id, False)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_date_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            text = l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                l_post_button[lz].replace('XXXXX', '')
            await bot.send_message(chat_id, text)
            await state.set_state(FsmOffer.button)
        else:
            await bot.send_message(chat_id, l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_time_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        text = message.text.strip()

        data = await state.get_data()
        offer_date = data.get('offer_date')
        day_, month_, year_ = offer_date.split('..')
        dt_user = datetime.datetime(year=int(year_), month=int(month_), day=int(day_))

        if message.text == '⬅️ Prev':
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        elif message.text in ['➡️️ Next', '/Next']:
            await bot.send_message(chat_id, l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
        else:
            sql = "SELECT USER_TZ FROM USER WHERE USER_TID=?"
            data = await db_select(sql, (chat_id,), BASE_D)
            USER_TZ = data[0][0] if data[0][0] else "+00:00"
            offer_tz = USER_TZ
            await state.update_data(offer_tz=offer_tz)
            sign_ = USER_TZ[0]
            h_, m_ = USER_TZ.strip(sign_).split(':')
            dt_now = datetime.datetime.utcnow()
            if sign_ == "+":
                dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
            else:
                dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))
            datetime_plus = (dt_cur + datetime.timedelta(hours=1)).strftime("%H:%M")
            datetime_current = dt_cur.strftime("%H:%M")

            try:
                arr = text.strip().split(':')
                dt_user_new = datetime.datetime(year=int(year_), month=int(month_), day=int(day_), hour=int(arr[0]),
                                                minute=int(arr[1]))
                if dt_user_new < dt_cur:
                    await message.answer(text=l_post_time_future[lz])
                    return
            except Exception as e:
                logger.info(log_ % str(e))
                text = l_generate_calendar_time[lz].format(dt_user.strftime("%d-%m-%Y"), datetime_plus,
                                                           datetime_current, USER_TZ)
                await bot.send_message(chat_id, text)
                return

            offer_dt = dt_user_new.strftime('%d-%m-%Y %H:%M')
            await state.update_data(offer_dt=offer_dt)

            await bot.send_message(chat_id, l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_finish_admin(bot, FsmOffer, message, state, EXTRA_D, BASE_D, bot_un):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        if message.text == '⬅️ Prev':
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        elif message.text in ['➡️️ Next', '/Next']:
            data = await state.get_data()
            offer_id = data.get('offer_id', None)
            offer_text = data.get('offer_text', None)
            offer_file_type = data.get('offer_file_type', 'text')
            default_photo = await pre_upload(bot, chat_id, 'text.jpg', 'photo', EXTRA_D, BASE_D)
            file_name_part = data.get('file_name_part', None)
            offer_file_id = data.get('offer_file_id', default_photo)
            offer_file_id_note = data.get('offer_file_id_note')

            offer_button = data.get('offer_button', None)
            offer_isbutton = 1 if offer_button else 0
            offer_tgph_link = data.get('offer_tgph_link', None)
            if offer_tgph_link and '[' in offer_tgph_link:
                offer_istgph = 1 if len([it for it in ast.literal_eval(str(offer_tgph_link)) if it != '']) else 0
            else:
                offer_istgph = 1 if offer_tgph_link else 0

            offer_tz = data.get('offer_tz', "+00:00")
            offer_dt = data.get('offer_dt', None)

            if offer_id:
                sql = "UPDATE OFFER SET OFFER_USERTID=?, OFFER_TEXT=?, OFFER_MEDIATYPE=?, OFFER_FILENAME=?, " \
                      "OFFER_FILEID=?, OFFER_FILEIDNOTE=?, OFFER_BUTTON=?, OFFER_ISBUTTON=?, OFFER_TGPHLINK=?, " \
                      "OFFER_ISTGPH=?, OFFER_DT=?, OFFER_TZ=?, OFFER_STATUS=? WHERE OFFER_ID=?"
                await db_change(sql, (
                    chat_id, offer_text, offer_file_type, file_name_part, offer_file_id, offer_file_id_note,
                    offer_button, offer_isbutton, offer_tgph_link, offer_istgph, offer_dt, offer_tz, 1, offer_id,),
                                BASE_D)
            else:
                sql = "INSERT OR IGNORE INTO OFFER (OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILENAME, " \
                      "OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, " \
                      "OFFER_DT, OFFER_TZ, OFFER_STATUS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                await db_change(sql, (
                    chat_id, offer_text, offer_file_type, file_name_part, offer_file_id, offer_file_id_note,
                    offer_button, offer_isbutton, offer_tgph_link, offer_istgph, offer_dt, offer_tz, 1,), BASE_D)

            sql = "SELECT * FROM OFFER"
            data = await db_select(sql, (), BASE_D)
            items = [item[0] for item in data]
            view_post_id = items.index(offer_id) + 1 if offer_id else len(data)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, view_post_id)
            await state.clear()
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


def get_keyboard_admin(data, src, post_id=1):
    row_width = len(data) if len(data) < 5 else 5
    reply_markup = InlineKeyboardBuilder()
    btns = get_numbers_with_mark(data, post_id, row_width)
    buttons = []

    for i in range(1, row_width + 1):
        arr = re.split(r'\s|[«‹·›»]', btns[i - 1])  # ('\s|(?<!\d)[,.](?!\d)', s)
        page_i = list(filter(None, arr))[0]
        page_name = f'offers_{src}_{str(int(page_i))}'
        buttons.append(types.InlineKeyboardButton(text=btns[i - 1], callback_data=page_name))
    reply_markup.add(*buttons).adjust(row_width)

    return reply_markup


async def callbacks_offers_admin(bot, FsmOffer, call, state, BASE_D, bot_un):
    try:
        chat_id = call.from_user.id
        post_id = int(call.data.split("_")[-1])
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def gallery_handler_admin(bot, call, state, BASE_D):
    try:
        await state.clear()
        chat_id = call.from_user.id
        message_id = call.message.message_id
        data, option, offer_id, current, len_ = call.data.split("_")
        offer_id = int(offer_id)
        current = int(current)
        len_ = int(len_)

        if option == 'prev':
            sql = "SELECT OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, " \
                  "OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, " \
                  "OFFER_DT FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            if not len(data): return

            current = len_ if current == 1 and option == 'prev' else current - 1
            await send_user(bot, chat_id, offer_id, data[0], message_id, current)
        elif option == 'next':
            sql = "SELECT OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, " \
                  "OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, " \
                  "OFFER_DT FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            if not len(data): return

            current = 1 if current == len_ and option == 'next' else current + 1
            await send_user(bot, chat_id, offer_id, data[0], message_id, current)
        elif data[1] == 'current':
            pass
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def edit_simple(bot, chat_id, post_id, message_id, current, BASE_D):
    result = None
    try:
        sql = "SELECT POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, " \
              "POST_TGPHLINK, POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER FROM POST WHERE POST_ID=?"
        data_posts = await db_select(sql, (post_id,), BASE_D)
        if not len(data_posts): return
        item = data_posts[0]
        POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, POST_TGPHLINK, POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER = item

        len_ = 0
        POST_TEXT = POST_TEXT if POST_TEXT else str_empty
        reply_markup = await create_replymarkup2(bot, post_id,
                                                 POST_BUTTON) if POST_ISBUTTON else InlineKeyboardBuilder()

        if '[' in POST_MEDIATYPE and POST_ISGALLERY:
            POST_FILEID = ast.literal_eval(POST_FILEID)
            POST_MEDIATYPE = ast.literal_eval(POST_MEDIATYPE)
            POST_TGPHLINK = ast.literal_eval(POST_TGPHLINK)

            len_ = len(POST_FILEID)
            POST_FILEID = POST_FILEID[current - 1]
            POST_MEDIATYPE = POST_MEDIATYPE[current - 1]
            POST_TGPHLINK = POST_TGPHLINK[current - 1]

        if POST_ISTGPH and POST_TGPHLINK:
            POST_MEDIATYPE = 'text'
            POST_TEXT = POST_TEXT if POST_TEXT and POST_TEXT != '' else str_empty
            POST_TEXT = f"<a href='{POST_TGPHLINK}'>​</a>{POST_TEXT}"

        if POST_ISGALLERY:
            POST_TEXT = '' if POST_TEXT == str_empty and POST_MEDIATYPE != 'text' else POST_TEXT
            buttons = [types.InlineKeyboardButton(text="←", callback_data=f'gal_prev_{post_id}_{current}_{len_}'),
                       types.InlineKeyboardButton(text=f"{current}/{len_}",
                                                  switch_inline_query_current_chat=f"{post_id} ~"),
                       types.InlineKeyboardButton(text="→", callback_data=f'gal_next_{post_id}_{current}_{len_}'), ]
            reply_markup.row(*buttons)

        if POST_MEDIATYPE == 'text':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=POST_TEXT,
                                        reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'photo':
            media = types.InputMediaPhoto(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,

                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'animation':
            media = types.InputMediaAnimation(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video':
            media = types.InputMediaVideo(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video_note':
            media = types.InputMediaVideo(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'audio':
            media = types.InputMediaAudio(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'voice':
            media = types.InputMediaAudio(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'document':
            media = types.InputMediaDocument(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        else:
            OFFER_FILEID = ast.literal_eval(POST_FILEID) if POST_FILEID and '[' in POST_FILEID else POST_FILEID
            OFFER_MEDIATYPE = ast.literal_eval(
                POST_MEDIATYPE) if POST_MEDIATYPE and '[' in POST_MEDIATYPE else POST_MEDIATYPE

            media = []
            POST_TEXT = None if POST_TEXT == str_empty else POST_TEXT
            for i in range(0, len(OFFER_FILEID)):
                caption = POST_TEXT if i == 0 else None

                if OFFER_MEDIATYPE[i] == 'photo':
                    media.append(
                        types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'video':
                    media.append(
                        types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'audio':
                    media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                elif OFFER_MEDIATYPE[i] == 'document':
                    media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                          disable_content_type_detection=True))

            await bot.send_media_group(chat_id, media)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def edit_simple2(bot, chat_id, user_id, entity_id, post_id, message_id, current, BASE_CHN):
    result = None
    try:
        sql = "SELECT POST_ID, POST_TYPE, POST_TEXT, POST_FID, POST_FIDNOTE, POST_LNK, POST_BUTTON, " \
              "POST_ISBUTTON, POST_ISSOUND, POST_ISSILENCE, POST_ISPIN, POST_ISPREVIEW, POST_ISSPOILER, " \
              "POST_ISGALLERY, POST_TZ, POST_DT, POST_TARGET, POST_BLOG, POST_WEB FROM POST WHERE POST_ID=?"
        data_posts = await db_select(sql, (post_id,), BASE_CHN)
        if not len(data_posts): return
        item = data_posts[0]
        POST_ID, POST_TYPE, POST_TEXT, POST_FID, POST_FIDNOTE, POST_LNK, POST_BUTTON, POST_ISBUTTON, POST_ISSOUND, POST_ISSILENCE, POST_ISPIN, POST_ISPREVIEW, POST_ISSPOILER, POST_ISGALLERY, POST_TZ, POST_DT, POST_TARGET, POST_BLOG, POST_WEB = item

        len_ = 0
        POST_TEXT = POST_TEXT if POST_TEXT else str_empty
        reply_markup = await create_replymarkup3(entity_id, post_id,
                                                 POST_BUTTON) if POST_ISBUTTON else InlineKeyboardBuilder()

        if '[' in POST_TYPE and POST_ISGALLERY:
            POST_FID = ast.literal_eval(POST_FID)
            POST_TYPE = ast.literal_eval(POST_TYPE)
            POST_LNK = ast.literal_eval(POST_LNK)

            len_ = len(POST_FID)
            POST_FID = POST_FID[current - 1]
            POST_TYPE = POST_TYPE[current - 1]
            POST_LNK = POST_LNK[current - 1]

        if POST_ISPREVIEW and POST_LNK:
            POST_TYPE = 'text'
            POST_TEXT = POST_TEXT if POST_TEXT and POST_TEXT != '' else str_empty
            POST_TEXT = f"<a href='{POST_LNK}'>​</a>{POST_TEXT}"

        if POST_ISGALLERY:
            button_id = 1
            sql = "SELECT CHAT_TID FROM PUSH WHERE POST_ID=? AND BUTTON_ID=?"
            data_in = await db_select(sql, (post_id, button_id,), BASE_CHN)
            if chat_id in [it[0] for it in data_in]:
                sql = "DELETE FROM PUSH WHERE CHAT_TID=? AND POST_ID=? AND BUTTON_ID=?"
                await db_change(sql, (chat_id, post_id, button_id,), BASE_CHN)
            else:
                sql = "INSERT OR IGNORE INTO PUSH (CHAT_TID, CHAT_FULLNAME, CHAT_USERNAME, CHAT_ISPREMIUM, POST_ID, BUTTON_ID) VALUES (?, ?, ?, ?, ?, ?)"
                await db_change(sql, (chat_id, 'full_name', 'username', 'is_premium', post_id, button_id,), BASE_CHN)
            sql = "SELECT BUTTON_ID FROM PUSH WHERE POST_ID=?"
            data = await db_select(sql, (post_id,), BASE_CHN)
            counters = {it[0]: sum(1 for x in data if x[0] == it[0]) for it in data}

            reply_markup = await create_replymarkup3(entity_id, post_id, POST_BUTTON,
                                                     counters) if POST_ISBUTTON else InlineKeyboardBuilder()

            POST_TEXT = '' if POST_TEXT == str_empty and POST_TYPE != 'text' else POST_TEXT
            if chat_id == user_id:
                middle = types.InlineKeyboardButton(text=f"{current}/{len_}",
                                                    switch_inline_query_current_chat=f"{entity_id} {post_id} ~")
            else:
                middle = types.InlineKeyboardButton(text=f"{current}/{len_}",
                                                    callback_data=f'gal_current_{entity_id}_{post_id}_{current}_{len_}')

            buttons = [
                types.InlineKeyboardButton(text="←", callback_data=f'gal_prev_{entity_id}_{post_id}_{current}_{len_}'),
                middle, types.InlineKeyboardButton(text="→",
                                                   callback_data=f'gal_next_{entity_id}_{post_id}_{current}_{len_}'), ]
            reply_markup.row(*buttons)

        if POST_TYPE == 'text':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=POST_TEXT,
                                        reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'photo':
            media = types.InputMediaPhoto(media=POST_FID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,

                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'animation':
            media = types.InputMediaAnimation(media=POST_FID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'video':
            media = types.InputMediaVideo(media=POST_FID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'video_note':
            media = types.InputMediaVideo(media=POST_FIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'audio':
            media = types.InputMediaAudio(media=POST_FID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'voice':
            media = types.InputMediaAudio(media=POST_FIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_TYPE == 'document':
            media = types.InputMediaDocument(media=POST_FID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        else:
            POST_FID = ast.literal_eval(POST_FID) if POST_FID and '[' in POST_FID else POST_FID
            POST_TYPE = ast.literal_eval(POST_TYPE) if POST_TYPE and '[' in POST_TYPE else POST_TYPE

            media = []
            POST_TEXT = None if POST_TEXT == str_empty else POST_TEXT
            for i in range(0, len(POST_FID)):
                caption = POST_TEXT if i == 0 else None

                if POST_TYPE[i] == 'photo':
                    media.append(types.InputMediaPhoto(media=POST_FID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif POST_TYPE[i] == 'video':
                    media.append(types.InputMediaVideo(media=POST_FID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif POST_TYPE[i] == 'audio':
                    media.append(types.InputMediaAudio(media=POST_FID[i], caption=caption))
                elif POST_TYPE[i] == 'document':
                    media.append(types.InputMediaDocument(media=POST_FID[i], caption=caption,
                                                          disable_content_type_detection=True))

            await bot.send_media_group(chat_id, media)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


# endregion


# region pyrogram
async def get_session(SESSION_TID, SESSION_D, BASE_S, EXTRA_D, CONF_P, is_proxy=False):
    res = proxy = None
    try:
        sql = "SELECT SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_PHONE FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not len(data): return
        SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_PHONE = data[0]

        if is_proxy:
            proxy = await get_proxy(SESSION_TID, EXTRA_D, CONF_P)

        res = Client(name=os.path.join(SESSION_D, SESSION_NAME), api_id=SESSION_APIID, api_hash=SESSION_APIHASH,
                     phone_number=SESSION_PHONE, proxy=proxy)
    finally:
        return res


async def is_my_chat(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E, is_history=False):
    result = r = None
    get_chat_history_count = 0
    try:
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*' LIMIT 10"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: return

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'isChat', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P, False) as app:
                    try:
                        r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)
                        if r is None:
                            logger.info(log_ % f"{link} is None")
                            return
                        txt_ = f"👩🏽‍💻 Администратор закрытой группы не принял заявки на вступление"
                        if r == -1:
                            await bot.send_message(chat_id, txt_)
                            return
                        result = await app.get_chat(r.id)

                        if is_history:
                            try:
                                get_chat_history_count = await app.get_chat_history_count(r.id)
                            except Exception as e:
                                logger.info(log_ % str(e))
                                await asyncio.sleep(round(random.uniform(0, 1), 2))
                    finally:
                        await leave_my_chat(app, result, link)
                break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired, SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result, get_chat_history_count


async def is_invite_chat(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E):
    result = r = None
    try:
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: continue

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'isChat', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P) as app:
                    try:
                        r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)

                        # get_chat https://t.me/+KO7_fV4aGKZkYTUy
                        if r == -1 or r is None: return
                        r = await app.get_chat(r.id)
                        logger.info(log_ % f"{SESSION_TID} get_chat {r.id}")

                        if not (r.type.value in ['group', 'supergroup']):
                            text = "🚶 Вставь ссылку на группу, а не канал"
                            await bot.send_message(chat_id, text)
                        elif hasattr(r.permissions, 'can_invite_users') and not r.permissions.can_invite_users:
                            text = "🚶 Зайди в «Разрешения» группы и включи <i>участникам группы</i> возможность: " \
                                   "«Добавление участников»"
                            await bot.send_message(chat_id, text)
                        else:
                            text = "🚶 Начинаем проверку группы..\n#длительность 2мин"
                            await bot.send_message(chat_id, text)
                            # await asyncio.sleep(r_conf('AWAIT_JOIN'))

                            try:
                                get_chat_member = await app.get_chat_member(chat_id=r.id, user_id=int(SESSION_TID))
                                result = True if get_chat_member and get_chat_member.status.value == 'member' else False
                            except Exception as e:
                                logger.info(log_ % str(e))
                                await asyncio.sleep(round(random.uniform(1, 2), 2))

                    finally:
                        await leave_my_chat(app, r, link)
                break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired, SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S):
    result = None
    try:
        if 't.me/c/' in str(link):
            try:
                tmp = link.strip('https://t.me/c/').split('/')[0]
                peer_channel = await app.resolve_peer(int(f"-100{tmp}"))
                result = await app.invoke(functions.channels.JoinChannel(channel=peer_channel))
            except Exception as e:
                logger.info(log_ % str(e))
        else:
            result = await app.join_chat(link)
        await asyncio.sleep(1)
    except (FloodWait, SlowmodeWait) as e:
        text = log_ % f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
        logger.info(text)
        await asyncio.sleep(round(random.uniform(5, 10), 2))

        till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime("%d-%m-%Y_%H-%M")
        sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
        SESSION_STATUS = f'Wait {till_time}'
        await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except UserAlreadyParticipant as e:
        logger.info(log_ % f"UserAlreadyParticipant {link}: {str(e)}")
        try:
            result = await app.get_chat(link)
        except Exception:
            pass
    except (InviteHashExpired, InviteHashInvalid) as e:
        logger.info(log_ % str(e))
        try:
            result = await app.join_chat(link)
        except Exception:
            await bot.send_message(chat_id, f"️👩🏽‍💻 Link {link} is invalid or try later")
    except (UsernameInvalid, UsernameNotOccupied, ChannelBanned) as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
        await bot.send_message(chat_id, f"️👩🏽‍💻 Link {link} is invalid or try later")
    except BadRequest as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(2, 3), 2))

        try:
            result = await app.join_chat(link)
        except Exception:
            result = -1
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def leave_my_chat(app, r, link):
    try:
        if not r: return
        chat_id = r.id if r and ('t.me/+' in str(link) or 'join_my_chat/' in str(link)) else link
        # like_names_res = is_names(r.title)
        if r.username and f'ferey' in r.username: return

        await app.leave_chat(chat_id, True)  # logger.info(log_ % f"\t{link} leave chat")
    except (FloodWait, SlowmodeWait) as e:
        wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
        logger.info(log_ % wait_)
        await asyncio.sleep(e.value + 1)
    except Exception:
        # logger.info(log_ % f"leave_my_chat_error: {link} {str(e)}")
        await asyncio.sleep(round(random.uniform(5, 10), 2))


async def get_chat_members(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E):
    result = []
    r = None
    try:
        text = f"🚶 Проверяем участников группы..\n#длительность 1мин"
        await bot.send_message(chat_id, text)
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            tmp_members = []
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: continue

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'getChatMembers', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P) as app:
                    try:
                        r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)

                        # get members
                        sql = "SELECT SESSION_TID FROM SESSION"
                        data_ = await db_select(sql, (), BASE_S)
                        data_ = [str(item[0]) for item in data_]
                        try:
                            async for member in app.get_chat_members(r.id, filter=enums.ChatMembersFilter.SEARCH):
                                if member.user.username and not member.user.is_bot and not member.user.is_deleted and not member.user.is_scam and not member.user.is_fake and not member.user.is_support and str(
                                        member.user.id) not in data_:
                                    tmp_members.append(member.user.username)
                        except ChatAdminRequired as e:
                            logger.info(log_ % str(e))
                            await bot.send_message(chat_id, f"🔺 Требуются права админа")
                            return
                        except Exception as e:
                            logger.info(log_ % str(e))
                    finally:
                        await leave_my_chat(app, r, link)

                    result = tmp_members
                    break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired, SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S):
    try:
        sql = "SELECT SESSION_NAME FROM SESSION WHERE SESSION_TID=?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data:
            await bot.send_message(my_tid, f"✅ Account {SESSION_TID} doesnt exist")
            return
        SESSION_NAME = os.path.join(SESSIONS_D, f'{data[0][0]}.session')

        sql = "DELETE FROM SESSION WHERE SESSION_TID = ?"
        await db_change(sql, (SESSION_TID,), BASE_S)

        sql = "DELETE FROM COMPANY WHERE COMPANY_FROMUSERTID = ?"
        await db_change(sql, (SESSION_TID,), BASE_S)

        if os.path.exists(SESSION_NAME):
            os.remove(SESSION_NAME)
        await bot.send_message(my_tid, f"✅ deleteAccount {SESSION_TID} ok")
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        await log(e, CONF_P)
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def delete_invalid_chat(chat, BASE_E):
    sql = "DELETE FROM CHANNEL WHERE CHANNEL_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM CHAT WHERE CHAT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM USER WHERE USER_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM BOT WHERE BOT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    chat = chat.strip('@')

    sql = "DELETE FROM CHANNEL WHERE CHANNEL_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM CHAT WHERE CHAT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM USER WHERE USER_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM BOT WHERE BOT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    # chat = chat if 'https://' in chat else f"@{chat}"  # await send_to_admins(f"deleteInvalidChat {chat}")


async def check_session_flood(SESSION_TID, BASE_S):
    result = SESSION_TID
    try:
        sql = "SELECT SESSION_STATUS FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data: return

        t_t = str(data[0][0]).split()
        if len(t_t) == 2:
            date_ = t_t[1].split('_')[0]
            time_ = t_t[1].split('_')[1]

            day = int(date_.split('-')[0])
            month = int(date_.split('-')[1])
            year = int(date_.split('-')[2])
            hour = int(time_.split('-')[0])
            minute = int(time_.split('-')[1])

            diff = datetime.datetime.now() - datetime.datetime(year=year, month=month, day=day, hour=hour,
                                                               minute=minute)

            if diff.days >= 0:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (None, SESSION_TID,), BASE_S)
                result = SESSION_TID
            else:
                result = None
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def check_session_limit(SESSION_TID, LIMIT_NAME, LIMIT, BASE_S):
    result = SESSION_TID
    try:
        sql = f"SELECT {LIMIT_NAME} FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data: return

        t_t = str(data[0][0]).split()
        if len(t_t) == 2:
            msg_by_day = int(t_t[0])
            date_ = t_t[1].split('-')

            day = int(date_[0])
            month = int(date_[1])
            year = int(date_[2])

            diff = datetime.datetime.now() - datetime.datetime(year=year, month=month, day=day)

            if diff.days > 0:
                result = f"0 {datetime.datetime.now().strftime('%d-%m-%Y')}"
                sql = f"UPDATE SESSION SET {LIMIT_NAME} = ? WHERE SESSION_TID = ?"
                await db_change(sql, (result, SESSION_TID,), BASE_S)
            elif msg_by_day < LIMIT:
                result = SESSION_TID
            else:
                result = None
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def check_inviteday(CONF_P, BASE_S, threshold=0):
    result = 0
    try:
        sql = "SELECT SESSION_TID,SESSION_INVITEDAY FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        for item in data:
            try:
                SESSION_TID, SESSION_INVITEDAY = item
                INVITEDAY_LIMIT_ = r_conf('INVITEDAY_LIMIT', CONF_P)
                checkSessionLimit_ = await check_session_limit(SESSION_TID, 'SESSION_INVITEDAY', INVITEDAY_LIMIT_,
                                                               BASE_S)
                if SESSION_INVITEDAY == '' or SESSION_INVITEDAY is None:
                    result += INVITEDAY_LIMIT_
                elif await check_session_flood(SESSION_TID, BASE_S) and checkSessionLimit_:
                    result += r_conf('INVITEDAY_LIMIT', CONF_P) - int(SESSION_INVITEDAY.split()[0])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        result = int(result * 0.6)
        if threshold:
            result = result if result < threshold else threshold
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def set_privacy(app):
    try:
        keys = [InputPrivacyKeyAddedByPhone(), InputPrivacyKeyChatInvite(), InputPrivacyKeyForwards(),
                InputPrivacyKeyPhoneCall(), InputPrivacyKeyPhoneNumber(), InputPrivacyKeyProfilePhoto(),
                InputPrivacyKeyStatusTimestamp(), InputPrivacyKeyVoiceMessages()]
        for key in keys:
            try:
                if key.QUALNAME == InputPrivacyKeyPhoneNumber().QUALNAME:
                    await app.invoke(SetPrivacy(key=key, rules=[InputPrivacyValueDisallowAll()]))
                elif key.QUALNAME == InputPrivacyKeyVoiceMessages().QUALNAME:
                    await app.invoke(SetPrivacy(key=key, rules=[InputPrivacyValueAllowAll()]))
                elif key.QUALNAME == InputPrivacyKeyProfilePhoto().QUALNAME:
                    await app.invoke(SetPrivacy(key=key, rules=[InputPrivacyValueAllowAll()]))
                else:
                    await app.invoke(SetPrivacy(key=key, rules=[InputPrivacyValueAllowContacts()]))
            except Exception as e:
                logger.info(log_ % f"{str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        try:
            await app.invoke(SetAccountTTL(ttl=AccountDaysTTL(days=365)))
            await app.invoke(SetAuthorizationTTL(authorization_ttl_days=365))
        except Exception as e:
            logger.info(log_ % f"{str(e)}")
            await asyncio.sleep(round(random.uniform(0, 1), 2))
    except (SlowmodeWait, FloodWait) as e:
        # await set_karma(e)
        await asyncio.sleep(e.value + 1)
    except Exception as e:
        logger.info(log_ % f"{str(e)}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))


# endregion


# region apiGoogle
async def api_sync_all(value_many, spreadsheet_id, CONF_P, EXTRA_D, range_many='A2', sheet_id='Sheet1',
                       value_input_option='USER_ENTERED', major_dimension="ROWS"):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    http_auth = credentials.authorize(httplib2.Http())
    sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)

    convert_value = []
    for item in value_many:
        convert_value.append(list(item))

    await api_write_cells(sheets_service, convert_value, range_many, spreadsheet_id, sheet_id, value_input_option,
                          major_dimension)


async def api_sync_update(value_many, spreadsheet_id, range_many, CONF_P, EXTRA_D, sheet_id='Sheet1',
                          value_input_option='USER_ENTERED', major_dimension="ROWS"):
    try:
        if range_many is None:
            logger.info(log_ % 'range_many is None')
            return
        scopes = r_conf('scopes', CONF_P)
        credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
        httpAuth = credentials.authorize(httplib2.Http())
        sheets_service = build('sheets', 'v4', http=httpAuth, cache_discovery=False)

        convert_value = []
        for item in value_many:
            convert_value.append(list(item))

        await api_write_cells(sheets_service, convert_value, range_many, spreadsheet_id, sheet_id, value_input_option,
                              major_dimension)
    except Exception as e:
        logger.info(log_ % str(e))


async def api_find_row_by_tid(USER_TID, CONF_P, EXTRA_D, sheet_id='Sheet1'):
    result = None
    try:
        scopes_ = r_conf('scopes', CONF_P)
        credential_file_ = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials_ = ServiceAccountCredentials.from_json_keyfile_name(credential_file_, scopes_)
        http_auth = credentials_.authorize(httplib2.Http())
        sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)
        spreadsheet_id = (r_conf('db_file_id', CONF_P))[0]

        values_list = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_id,
                                                                 fields='values').execute().get('values', [])

        row = 0
        for ix, item in enumerate(values_list):
            if str(USER_TID) in item:
                row = ix + 1
                break
        result = 'A' + str(row)
    finally:
        return result


async def api_write_cells(sheets_service, value_many, range_many, spreadsheet_id, sheet_id, valueInputOption,
                          majorDimension="ROWS"):
    result = False
    try:
        result = sheets_service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body={"valueInputOption": valueInputOption,
                                                                          "data": [{"range": f"{sheet_id}!{range_many}",
                                                                                    "majorDimension": majorDimension,
                                                                                    "values": value_many, }]}).execute()
        logger.info(log_ % 'write to db ok')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def api_append_cells(sheets_service, value_many, spreadsheet_id, valueInputOption):
    result = True
    try:
        sheets_service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range='A1',
                                                      valueInputOption=valueInputOption,
                                                      body={"values": value_many}).execute()

        logger.info(log_ % 'write to db ok')
    except Exception as e:
        logger.info(log_ % str(e))
        result = False
    return result


async def api_read_cells(sheets_service, range_many, spreadsheet_id, sheet_id='Sheet1'):
    result = None
    try:
        r = sheets_service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                            ranges=f"{sheet_id}!{range_many}").execute()

        result = r.get('valueRanges', [])[0]['values'] if len(r.get('valueRanges', [])) > 0 else None
        logger.info(log_ % 'read from db ok')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


def get_random_color():
    """
    Создаю случайный цвет с альфа каном
    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#Color
    :return:
    """
    return {"red": randrange(0, 255) / 255, "green": randrange(0, 255) / 255, "blue": randrange(0, 255) / 255,
            "alpha": randrange(0, 10) / 10  # 0.0 - прозрачный
            }


def api_create_file_or_folder(drive_service, mime_type, name, parent_id):
    creation_id = None
    try:
        body = {'name': name, 'mimeType': mime_type, 'parents': [parent_id],
                'properties': {'title': 'titleSpreadSheet', 'locale': 'ru_RU'}, 'locale': 'ru_RU'}
        result_folder = drive_service.files().create(body=body, fields='id').execute()
        creation_id = result_folder['id']
    finally:
        return creation_id


async def table_init(TABLE_API_JSON, CELL_NAMES, EXTRA_D, CONF_P, INI_D):
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(EXTRA_D, TABLE_API_JSON),
                                                                       r_conf('scopes', CONF_P))
        httpAuth = credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
        file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

        files = []
        db_file_name = 'db'
        files = await is_need_for_create(file_list_dic, files, 'application/vnd.google-apps.spreadsheet', db_file_name,
                                         CONF_P, INI_D)
        for i in range(0, len(files)):
            creation_id = api_create_file_or_folder(drive_service, 'application/vnd.google-apps.spreadsheet',
                                                    db_file_name, (r_conf('share_folder_id', CONF_P))[0])
            w_conf(get_new_key_config(files[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)
            await api_sync_all([CELL_NAMES], (r_conf('db_file_id', CONF_P))[0], CONF_P, EXTRA_D, 'A1')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def send_my_copy(bot, cnt, USER_TID, USER_USERNAME, result):
    try:
        # USER_TID = 5150111687
        await bot.copy_message(chat_id=int(USER_TID), from_chat_id=result.chat.id, message_id=result.message_id,
                               reply_markup=result.reply_markup)
        cnt += 1
        logger.info(log_ % f"\t{cnt}. send to user {USER_TID}-{USER_USERNAME} ok")
        await asyncio.sleep(0.05)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        logger.info(log_ % f"\tsend to user {USER_TID}-{USER_USERNAME} error")
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return cnt


async def api_get_file_list(drive_service, folder_id, tmp_dic=None, parent_name='', is_file=False):
    if tmp_dic is None:
        tmp_dic = {} or None
    if is_file:
        file = drive_service.files().get(fileId=folder_id, fields="id, name, size, modifiedTime, mimeType").execute()
        tmp_dic[file['id']] = [file['name'], file['mimeType'], parent_name, file['modifiedTime']]
        return tmp_dic
    q = "\'" + folder_id + "\'" + " in parents"
    fields = "nextPageToken, files(id, name, size, modifiedTime, mimeType)"
    results = drive_service.files().list(pageSize=1000, q=q, fields=fields).execute()
    items = results.get('files', [])
    for item in items:
        try:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                tmp_dic[item['id']] = [item['name'], item['mimeType'], parent_name, item['modifiedTime']]
                await api_get_file_list(drive_service, item['id'], tmp_dic, item['name'])
            else:
                tmp_dic[item['id']] = [item['name'], item['mimeType'], parent_name, item['modifiedTime']]
        except Exception as e:
            logger.info(log_ % str(e))

    tmp_dic_2 = {}
    for k, v in reversed(tmp_dic.items()):
        tmp_dic_2[k] = v

    return tmp_dic_2


async def upload_file(drive_service, name, post_media_name, folder_id):
    result = None
    try:
        if name == 'нет' or name is None: return

        request_ = drive_service.files().create(media_body=MediaFileUpload(filename=post_media_name, resumable=True),
                                                body={'name': name, 'parents': [folder_id]})
        response = None
        while response is None:
            status, response = request_.next_chunk()
            if status: logger.info(log_ % "Uploaded %d%%." % int(status.progress() * 100))
        logger.info(log_ % "Upload Complete!")
        # if os.path.exists(post_media_name):
        #     os.remove(post_media_name)
        result = True
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def api_dl_file(drive_service, id_, name, gdrive_mime_type, MEDIA_D):
    save_mime_type = None
    file_name = add = ''

    if gdrive_mime_type.endswith('document') and not (name.endswith('doc') or name.endswith('docx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif gdrive_mime_type.endswith('sheet') and not (name.endswith('xls') or name.endswith('xlsx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif gdrive_mime_type.endswith('presentation') and not (name.endswith('ppt') or name.endswith('pptx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif gdrive_mime_type == 'application/vnd.google-apps.folder':
        return ''

    if save_mime_type:
        request_ = drive_service.files().export_media(fileId=id_, mimeType=save_mime_type)
    else:
        request_ = drive_service.files().get_media(fileId=id_)

    if request_:
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(log_ % "Download %d%%." % int(status.progress() * 100))

        if gdrive_mime_type.endswith('.spreadsheet'):
            add = '.xlsx'
        elif gdrive_mime_type.endswith('.document'):
            add = '.docx'
        elif gdrive_mime_type.endswith('.presentation'):
            add = '.pptx'
        file_name = return_cutted_filename(name, add, MEDIA_D)
        with io.open(file_name, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        await asyncio.sleep(1)
    return file_name


def return_cutted_filename(name, add, MEDIA_D):
    file_name = f'{MEDIA_D}/{name}{add}'
    l_ = len(file_name)
    diff = 255 - l_
    if diff <= 0:
        ext = get_ext(name)
        name = name[0:len(name) - 1 - abs(diff) - len(ext)] + ext
        file_name = f'{MEDIA_D}/{name}{add}'
    return file_name


def get_name_without_ext(file_name):
    name = file_name
    try:
        ext = get_ext(name)
        if ext != '':
            index_ext = str(name).rindex(ext)
            index_slash = str(name).rindex('/') + 1 if '/' in name else 0
            name = name[index_slash:index_ext]
    finally:
        return name


def get_ext(name):
    ext = ''
    try:
        index = str(name).rindex('.')
        ext = name[index:len(name)]
        if len(ext) > 5:
            ext = ''
    finally:
        return ext


async def is_need_for_create(file_list_dic, unit, mime_type, name, CONF_P, INI_D):
    flag = False
    for k, v in file_list_dic.items():
        if v[0] == name and v[1] == mime_type:
            flag = True
            w_conf(get_new_key_config(name, CONF_P, INI_D), [k], CONF_P, INI_D)
            break
    if not flag: unit.append(name)
    return unit


def is_exists_google_id(file_list_dic, mime_type, name, parent_name):
    result = None
    for k, v in file_list_dic.items():
        if v[0] == name and v[1] == mime_type and v[2] == parent_name:
            return k
    return result


def get_new_key_config(value, CONF_P, INI_D):
    new_key = ""
    try:
        CONF_P.read(INI_D)
        for k, v in CONF_P.items('CONFIG'):
            if value == ast.literal_eval(v)[0]:
                arr = str(k).split('_')
                new_key = f'{arr[0]}_{arr[1]}_id'
                break
    finally:
        return new_key


async def api_init(CONF_P, INI_D, EXTRA_D, fields_0):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
    file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

    subflders = []
    mimeType_folder = 'application/vnd.google-apps.folder'
    static_folder_name = (r_conf('static_folder_name', CONF_P))[0]
    dynamic_folder_name = (r_conf('dynamic_folder_name', CONF_P))[0]
    subflders = await is_need_for_create(file_list_dic, subflders, mimeType_folder, static_folder_name, CONF_P, INI_D)
    subflders = await is_need_for_create(file_list_dic, subflders, mimeType_folder, dynamic_folder_name, CONF_P, INI_D)
    for i in range(0, len(subflders)):
        share_folder_id = (r_conf('share_folder_id', CONF_P))[0]
        creation_id = api_create_file_or_folder(drive_service, mimeType_folder, subflders[i], share_folder_id)
        w_conf(get_new_key_config(subflders[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)

    files = []
    mimeType_sheet = 'application/vnd.google-apps.spreadsheet'
    db_file_name = (r_conf('db_file_name', CONF_P))[0]
    files = await is_need_for_create(file_list_dic, files, mimeType_sheet, db_file_name, CONF_P, INI_D)
    for i in range(0, len(files)):
        db_file_name = (r_conf('db_file_name', CONF_P))[0]
        mimeType_sheet = 'application/vnd.google-apps.spreadsheet'
        share_folder_id = (r_conf('share_folder_id', CONF_P))[0]
        creation_id = api_create_file_or_folder(drive_service, mimeType_sheet, db_file_name, share_folder_id)
        w_conf(get_new_key_config(files[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)
        value_many = [fields_0]
        spreadsheetId = (r_conf('db_file_id', CONF_P))[0]
        await api_sync_all(value_many, spreadsheetId, CONF_P, EXTRA_D, 'A1')
    logger.info(log_ % 'api init ok')


async def get_cell_dialog(range_many, CONF_P, EXTRA_D):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    http_auth = credentials.authorize(httplib2.Http())
    sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)
    spreadsheet_id = '1sQWH3NpJAh8t4QDmP-8vvc7XaCTx4Uflc6LADA9zvN8'
    sheet_id = 'Лист1'

    result = None
    try:
        ranges = f"{sheet_id}!{range_many}"
        r = sheets_service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=ranges).execute()
        if ':' in range_many:
            result = r.get('valueRanges', [])[0]['values'] if len(r.get('valueRanges', [])) > 0 else None
            result = [item[0] for item in result]
        else:
            result = r.get('valueRanges', [])[0]['values'][0][0] if len(r.get('valueRanges', [])) > 0 else None
        logger.info(log_ % 'read from db ok')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_list_of_send_folder(CONF_P, EXTRA_D):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)

    tmp = []
    file_list_dic = await api_get_file_list(drive_service, (r_conf('dynamic_folder_id', CONF_P))[0], {})
    for k, v in file_list_dic.items():
        try:
            parent_folder = v[2]
            name_folder = v[0]
            datetime_ = datetime.datetime.now()
            if parent_folder == '' and datetime_ < datetime.datetime.strptime(name_folder, "%d-%m-%Y %H:%M"):
                tmp.append([name_folder, k])
        except Exception as e:
            logger.info(log_ % str(e))

    return tmp


async def save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name, post_media_type,
                                    post_pin, post_time, post_media_options, post_users='*'):
    try:
        scopes = r_conf('scopes', CONF_P)
        credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
        httpAuth = credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
        file_list_dic = await api_get_file_list(drive_service, (r_conf('dynamic_folder_id', CONF_P))[0], {})

        mime_type_folder = 'application/vnd.google-apps.folder'
        id_time_folder = is_exists_google_id(file_list_dic, mime_type_folder, post_time.strftime("%d-%m-%Y %H:%M"), '')
        if id_time_folder is None:
            id_time_folder = api_create_file_or_folder(drive_service, 'application/vnd.google-apps.folder',
                                                       post_time.strftime("%d-%m-%Y %H:%M"),
                                                       (r_conf('dynamic_folder_id', CONF_P))[0])

        mime_type_sheet = 'application/vnd.google-apps.spreadsheet'
        id_InfoXlsx = is_exists_google_id(file_list_dic, mime_type_sheet, 'info', post_time.strftime("%d-%m-%Y %H:%M"))
        if id_InfoXlsx is None:
            mime_type_sheet = 'application/vnd.google-apps.spreadsheet'
            id_InfoXlsx = api_create_file_or_folder(drive_service, mime_type_sheet, 'info', id_time_folder)
            v_m = [["текст", "кнопка(имя)", "кнопка(ссылка)", "медиа", "медиа тип", "закрепить(pin)", "пользователи"]]
            spreadsheet_id = id_InfoXlsx
            await api_sync_all(value_many=v_m, spreadsheet_id=spreadsheet_id, CONF_P=CONF_P, EXTRA_D=EXTRA_D,
                               range_many='A1', major_dimension="COLUMNS")

        name = os.path.basename(post_media_name) if post_media_name else 'нет'
        if post_media_type == 'poll':
            post_txt = post_media_name
            name = str(post_media_options)
        else:
            await upload_file(drive_service, name, post_media_name, id_time_folder)

        v_m = [[post_txt, post_btn if post_btn else 'no', post_url if post_url else 'no', name,
                post_media_type if post_media_type else 'no', 'yes' if post_pin else 'no', post_users]]
        spreadsheet_id = id_InfoXlsx
        await api_sync_all(value_many=v_m, spreadsheet_id=spreadsheet_id, CONF_P=CONF_P, EXTRA_D=EXTRA_D,
                           range_many='B1', major_dimension="COLUMNS")
        logger.info(log_ % 'save to google ok')
    except Exception as e:
        logger.info(log_ % str(e))


# endregion


# region payment
async def update_subscribe(bot, BASE_D, BOT_TOKEN_E18B):
    result = []
    try:
        dt_ = datetime.datetime.utcnow()
        if not (dt_.hour % 2 == 0 and dt_.minute % 2 == 0 and dt_.second % 2 == 0): return
        sql = "SELECT USER_TID, USER_LZ, USER_DTPAID, USER_ISPAID FROM USER"
        data = await db_select(sql, (), BASE_D)

        for item in data:
            try:
                USER_TID, USER_LZ, USER_DTPAID, USER_ISPAID = item

                if USER_ISPAID == 1 and USER_DTPAID and (
                        dt_ - datetime.datetime.strptime(USER_DTPAID, '%d-%m-%Y_%H-%M-%S')).days > 31:
                    await asyncio.sleep(round(random.uniform(0, 1), 2))
                    get_ = await bot.get_chat(chat_id=USER_TID)
                    chan_private_donate = channel_library_ru if USER_LZ == 'ru' else channel_library_en
                    extra_bot = Bot(token=BOT_TOKEN_E18B)
                    get_chat_member_ = await extra_bot.get_chat_member(chat_id=chan_private_donate, user_id=USER_TID)
                    await extra_bot.session.close()

                    if get_chat_member_.status in ['member', 'administrator', 'creator']:
                        USER_DTPAID = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S')
                        sql = "UPDATE USER SET USER_ISPAID=1, USER_USERNAME=?, USER_FULLNAME=?, USER_DTPAID=? " \
                              "WHERE USER_TID=?"
                        await db_change(sql, (get_.username, get_.full_name, USER_DTPAID, USER_TID,), BASE_D)
                    else:
                        sql = "UPDATE USER SET USER_ISPAID=0, USER_USERNAME=?, USER_FULLNAME=? WHERE USER_TID=?"
                        await db_change(sql, (get_.username, get_.full_name, USER_TID,), BASE_D)
                elif USER_ISPAID == -1 and USER_DTPAID and (
                        dt_ - datetime.datetime.strptime(USER_DTPAID, '%d-%m-%Y_%H-%M-%S')).days > 31:
                    result.append(
                        item)  # else:  #     sql = "UPDATE USER SET USER_USERNAME=?, USER_FULLNAME=? WHERE USER_TID=?"  #     await db_change(sql, (get_.username, get_.full_name, USER_TID,), BASE_D)
            except TelegramRetryAfter as e:
                logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
                await asyncio.sleep(e.retry_after + 1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def convert_domain_to_currency(domain):
    result = 'EUR'
    try:
        if domain == 'ae':
            result = 'AED'
        elif domain == 'af':
            result = 'AFN'
        elif domain == 'al':
            result = 'AFN'
        elif domain == 'am':
            result = 'AMD'
        elif domain == 'ar':
            result = 'ARS'
        elif domain == 'au':
            result = 'AUD'
        elif domain == 'az':
            result = 'AZN'
        elif domain == 'ba':
            result = 'BAM'
        elif domain == 'bd':
            result = 'BDT'
        elif domain == 'bg':
            result = 'BGN'
        elif domain == 'bn':
            result = 'BND'
        elif domain == 'bo':
            result = 'BOB'
        elif domain == 'br':
            result = 'BRL'
        elif domain == 'by':
            result = 'BYN'
        elif domain == 'ca':
            result = 'CAD'
        elif domain == 'ch':
            result = 'CHF'
        elif domain == 'cl':
            result = 'CLP'
        elif domain == 'cn':
            result = 'CNY'
        elif domain == 'co':
            result = 'COP'
        elif domain == 'cr':
            result = 'CRC'
        elif domain == 'cz':
            result = 'CZK'
        elif domain == 'dk':
            result = 'DKK'
        elif domain == 'do':
            result = 'DOP'
        elif domain == 'dz':
            result = 'DZD'
        elif domain == 'eg':
            result = 'EGP'
        elif domain == 'et':
            result = 'ETB'
        elif domain == 'uk':
            result = 'GBP'
        elif domain == 'ge':
            result = 'GEL'
        elif domain == 'gt':
            result = 'GTQ'
        elif domain == 'hk':
            result = 'HKD'
        elif domain == 'hh':
            result = 'HNL'
        elif domain == 'hr':
            result = 'HRK'
        elif domain == 'hu':
            result = 'HUF'
        elif domain == 'id':
            result = 'IDR'
        elif domain == 'il':
            result = 'ILS'
        elif domain == 'in':
            result = 'INR'
        elif domain == 'is':
            result = 'ISK'
        elif domain == 'jm':
            result = 'JMD'
        elif domain == 'ke':
            result = 'KES'
        elif domain == 'kg':
            result = 'KGS'
        elif domain == 'kr':
            result = 'KRW'
        elif domain == 'kz':
            result = 'KZT'
        elif domain == 'lb':
            result = 'LBP'
        elif domain == 'lk':
            result = 'LKR'
        elif domain == 'ma':
            result = 'MAD'
        elif domain == 'md':
            result = 'MDL'
        elif domain == 'mn':
            result = 'MNT'
        elif domain == 'mu':
            result = 'MUR'
        elif domain == 'mv':
            result = 'MVR'
        elif domain == 'mx':
            result = 'MXN'
        elif domain == 'my':
            result = 'MYR'
        elif domain == 'mz':
            result = 'MZN'
        elif domain == 'ng':
            result = 'NGN'
        elif domain == 'ni':
            result = 'NIO'
        elif domain == 'no':
            result = 'NOK'
        elif domain == 'np':
            result = 'NPR'
        elif domain == 'nz':
            result = 'NZD'
        elif domain == 'pa':
            result = 'PAB'
        elif domain == 'pe':
            result = 'PEN'
        elif domain == 'ph':
            result = 'PHP'
        elif domain == 'pk':
            result = 'PKR'
        elif domain == 'pl':
            result = 'PLN'
        elif domain == 'py':
            result = 'PYG'
        elif domain == 'qa':
            result = 'QAR'
        elif domain == 'ro':
            result = 'RON'
        elif domain == 'rs':
            result = 'RSD'
        elif domain == 'ru':
            result = 'RUB'
        elif domain == 'sa':
            result = 'SAR'
        elif domain == 'se':
            result = 'SEK'
        elif domain == 'sg':
            result = 'SGD'
        elif domain == 'th':
            result = 'THB'
        elif domain == 'tj':
            result = 'TJS'
        elif domain == 'tr':
            result = 'TRY'
        elif domain == 'tt':
            result = 'TTD'
        elif domain == 'tw':
            result = 'TWD'
        elif domain == 'tz':
            result = 'TZS'
        elif domain == 'ua':
            result = 'UAH'
        elif domain == 'ug':
            result = 'UGX'
        elif domain == 'us':
            result = 'USD'
        elif domain == 'uy':
            result = 'UYU'
        elif domain == 'uz':
            result = 'UZS'
        elif domain == 'vn':
            result = 'VND'
        elif domain == 'ye':
            result = 'YER'
        elif domain == 'za':
            result = 'ZAR'
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def create_invoice_link(BOT_TID, BOT_LC, msg_text, msg_btns, BASE_D):
    result = None
    try:
        sql = "SELECT BOT_TOKEN, BOT_TOKENPAY FROM BOT WHERE BOT_TID=?"
        data = await db_select(sql, (BOT_TID,), BASE_D)
        if not len(data): return
        BOT_TOKEN, BOT_TOKENPAY = data[0]

        btn_name = msg_btns[0]['lbl'].encode('utf-16', 'surrogatepass').decode('utf-16')
        # msg_text = await replace_user_vars(chat_id, msg_text)
        msg_text = msg_text if msg_text and msg_text != '' else btn_name
        soup = BeautifulSoup(msg_text, 'html.parser')
        msg_text = soup.get_text()

        currency = await convert_domain_to_currency(BOT_LC)
        price = msg_btns[0]['lnk']
        amount = int(price.replace('.', '').replace(',', '')) if '.' in price or ',' in price else int(
            f"{msg_btns[0]['lnk']}00")
        prices = [types.LabeledPrice(label=btn_name, amount=amount)]

        msg_media = {'title': btn_name, 'description': msg_text, 'payload': f"{BOT_TID}_{amount}",
                     'provider_token': BOT_TOKENPAY, 'currency': currency, 'prices': prices, 'max_tip_amount': amount,
                     'suggested_tip_amounts': [amount], }
        print(f'msg_media = {msg_media}')

        extra_bot = Bot(token=BOT_TOKEN)
        result = await extra_bot.create_invoice_link(title=msg_media['title'], description=msg_media['description'],
                                                     payload=msg_media['payload'],
                                                     provider_token=msg_media['provider_token'],
                                                     currency=msg_media['currency'], prices=msg_media['prices'],
                                                     max_tip_amount=msg_media['max_tip_amount'],
                                                     suggested_tip_amounts=msg_media['suggested_tip_amounts'], )
        await extra_bot.session.close()
        print(f'invoice_link = {result}')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


# endregion


# region web
async def region_web(bot, username, ENT_TID, ENT_LC, POST_ID, POST_TYPE, POST_TEXT, POST_LNK, POST_BUTTON, ENT_TYPE,
                     MEDIA_D, BASE_D, bot_username, PROJECT_TYPE='bot'):
    result = None
    try:
        POST_TEXT = POST_TEXT if POST_TEXT else ''
        POST_TEXT = POST_TEXT.replace('<tg-spoiler>', '').replace('</tg-spoiler>', '')
        POST_TEXT = POST_TEXT.replace('```py\n', '```')
        BASE_ENT = os.path.join(MEDIA_D, str(ENT_TID), f"{str(ENT_TID)}.db")

        if PROJECT_TYPE == 'bot':
            sql = "SELECT BOT_USERNAME, BOT_FIRSTNAME FROM BOT WHERE BOT_TID=?"
            data_bot = await db_select(sql, (ENT_TID,), BASE_D)
            ENT_USERNAME, ENT_FIRSTNAME = data_bot[0]
            ENT_LINK = f"https://t.me/{ENT_USERNAME}"
            ENT_USERNAME = f"@{ENT_USERNAME}"
        elif PROJECT_TYPE == 'ub':
            sql = "SELECT UB_USERNAME, UB_BOTUSERNAME, UB_CHANNELLINK FROM UB WHERE UB_TID=?"
            data_bot = await db_select(sql, (ENT_TID,), BASE_D)
            UB_USERNAME, UB_BOTUSERNAME, UB_CHANNELLINK = data_bot[0]

            if UB_USERNAME:
                ENT_USERNAME = UB_USERNAME
            elif UB_BOTUSERNAME:
                ENT_USERNAME = UB_BOTUSERNAME
            elif UB_CHANNELLINK:
                ENT_USERNAME = UB_CHANNELLINK
            else:
                ENT_USERNAME = ENT_TID

            ENT_LINK = f"https://t.me/{ENT_USERNAME}"
            ENT_USERNAME = f"@{ENT_USERNAME}"
        else:
            get_chat_ = await bot.get_chat(int(ENT_TID))
            ENT_LINK = f"https://t.me/{get_chat_.username}" if get_chat_.username else get_chat_.invite_link
            ENT_USERNAME = get_chat_.title

        WEB_D = os.path.join(MEDIA_D, str(ENT_TID), 'WEB')
        os.makedirs(WEB_D, exist_ok=True, mode=0o777)
        file_html = os.path.join(WEB_D, f"{POST_ID}.html")
        msg_text = POST_TEXT

        m_html = ''
        if POST_LNK:
            POST_LNKS = ast.literal_eval(POST_LNK) if '[' in POST_LNK else [POST_LNK]
            POST_TYPES = ast.literal_eval(POST_TYPE) if '[' in POST_TYPE else [POST_TYPE]
            TMP_TYPE = POST_TYPES[0]
            TMP_LNK = POST_LNKS[0]

            add_rounded = ' rounded-media' if TMP_TYPE == 'video_note' else ''
            add_number = '' if len(POST_LNKS) == 1 else f'<label id="media-number">1/{len(POST_LNKS)}</label>'
            add_prev = '' if len(POST_LNKS) == 1 else '<a id="media-prev">❮</a>'
            add_next = '' if len(POST_LNKS) == 1 else '<a id="media-next">❯</a>'
            add_dot = ''
            for j in range(len(POST_LNKS)):
                if j == 0:
                    add_dot = f'{add_dot}<span id="id-dot-{j}" class="dot active"></span>'
                else:
                    add_dot = f'{add_dot}<span id="id-dot-{j}" class="dot"></span>'
            add_dots = '' if len(POST_LNKS) == 1 else f'''<div id="media-dots">{add_dot}</div>'''
            add_media = ''

            print(f"{TMP_LNK=}")
            if TMP_TYPE in ['photo', 'gif']:
                add_media = f'<img class="media" src="{TMP_LNK}" alt="Media">'
            elif TMP_TYPE in ['video', 'video_note'] or TMP_TYPE in ['audio', 'voice'] and TMP_LNK:
                add_media = f'<video class="media{add_rounded}" src="{TMP_LNK}" controls loop autoplay playsinline></video>'

            m_html = f'''<div class="media-wrapper">{add_number}{add_media}{add_prev}{add_next}{add_dots}</div>'''
        print(m_html)

        txt_html = ''
        if msg_text and msg_text.strip() != '' and msg_text != str_empty:
            msg_text = msg_text.strip()
            if ENT_TYPE == 'MSG':
                msg_text = await convert_tgmd_to_html(msg_text)
            msg_arr = re.split(r'\s+', msg_text)

            for msg_item in msg_arr:
                if msg_item.startswith('#') or msg_item.startswith('$'):
                    msg_text = msg_text.replace(msg_item, f"<span>{msg_item}</span>")
            txt_html = f'<div class="text">{msg_text}</div>'

        btn_html = ''
        if POST_BUTTON:
            if ENT_TYPE == 'PST':
                extra_id = 0
                btns_html = ''
                row_html = '<div class="buttons-row">'
                dic_btns = await check_buttons2(POST_BUTTON, True)

                for k, v in dic_btns.items():
                    if not v[0] or (len(v) > 0 and v[-1] is None):
                        if len(row_html) > len('<div class="buttons-row">'):
                            btns_html = f"{btns_html}{row_html}</div>"
                            row_html = '<div class="buttons-row">'
                        continue

                    btn_ix = extra_id
                    btn_knd = 'like' if v[-1] == 'btn_' else 'link'
                    btn_lbl = str(v[0]).strip('⁰')
                    btn_lnk = v[-1]
                    if str(btn_lnk).startswith('tg://'):
                        btn_lnk = f"https://t.me/{username}" if username else "https://t.me"

                    hint_ = ''
                    if btn_knd == 'link':
                        hint_ = ' ᶺ'

                    row_html = f'{row_html}<a id="btn-{btn_knd}-{btn_ix}-0" class="button" data-url="{btn_lnk}">⁰ {btn_lbl}{hint_}</a>'
                    extra_id += 1

                if len(row_html) > len('<div class="buttons-row">'):
                    btns_html = f"{btns_html}{row_html}</div>"
                btn_html = f'<div class="buttons-wrapper">{btns_html}</div>'
            else:
                msg_btns = ast.literal_eval(POST_BUTTON)

                print(f"before {msg_btns=}")
                ix_other = i_pay = ix_pay = 0
                for i in range(len(msg_btns)):
                    if msg_btns[i]['knd'] == 'payment':
                        i_pay = i
                        ix_pay = msg_btns[i]['i']

                if i_pay:
                    msg_btns[i_pay], msg_btns[ix_other] = msg_btns[ix_other], msg_btns[i_pay]
                    msg_btns[ix_other]['i'] = 0
                    msg_btns[i_pay]['i'] = ix_pay
                print(f"after {msg_btns=}")

                btns_html = ''
                for i in range(1, 4):
                    b_html = await get_row_html(msg_text, msg_btns, i * 3 - 3, i * 3, POST_ID, ENT_TID, ENT_LC,
                                                BASE_ENT, BASE_D)
                    btns_html = f"{btns_html}{b_html}"
                btn_html = f'<div class="buttons-wrapper">{btns_html}</div>'

        sql = "SELECT VIEW_ID FROM VIEW WHERE ENT_VID=? AND ENT_TYPE=?"
        data_views = await db_select(sql, (POST_ID, ENT_TYPE,), BASE_ENT)
        msg_views = str(len(data_views))
        print(f"{btn_html=}, {msg_views=}")

        if POST_LNK:
            POST_LNKS = POST_LNK if '[' in POST_LNK else str([POST_LNK])
        else:
            POST_LNKS = '[]'

        html_web = html_template.format(m_html, txt_html, btn_html, msg_views, ENT_LINK, ENT_USERNAME, ENT_TID, POST_ID,
                                        POST_LNKS)
        if POST_ID:
            async with aiofiles.open(file_html, 'w', encoding='utf-8') as f:
                await f.write(html_web)
            result = f"https://t.me/{bot_username}/web?startapp={ENT_TID}_{POST_ID}"
            logger.info(f"{ENT_TID} ({POST_ID}): {result}")
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def region_blog(bot, ENT_TID, POST_TYPE, POST_TEXT, POST_LNK, BASE_D, PROJECT_TYPE='bot', is_format=False):
    result = None
    try:
        cnt = 1
        while cnt >= 0:
            try:
                POST_TEXT = POST_TEXT if POST_TEXT else str_empty
                POST_TEXT = POST_TEXT.replace('<tg-spoiler>', '').replace('</tg-spoiler>', '').replace('<span>',
                                                                                                       '').replace(
                    '</span>', '').replace('<pre>py\n', '').replace('<pre>', '').replace('</pre>', '')

                if PROJECT_TYPE == 'bot':
                    sql = "SELECT BOT_USERNAME, BOT_FIRSTNAME FROM BOT WHERE BOT_TID=?"
                    data_bot = await db_select(sql, (ENT_TID,), BASE_D)
                    ENT_USERNAME, ENT_FIRSTNAME = data_bot[0]
                    ENT_LINK = f"https://t.me/{ENT_USERNAME}"
                    ENT_USERNAME = f"@{ENT_USERNAME}"
                elif PROJECT_TYPE == 'ub':
                    sql = "SELECT UB_USERNAME, UB_BOTUSERNAME, UB_CHANNELLINK FROM UB WHERE UB_TID=?"
                    data_bot = await db_select(sql, (ENT_TID,), BASE_D)
                    UB_USERNAME, UB_BOTUSERNAME, UB_CHANNELLINK = data_bot[0]

                    if UB_USERNAME:
                        ENT_USERNAME = UB_USERNAME
                    elif UB_BOTUSERNAME:
                        ENT_USERNAME = UB_BOTUSERNAME
                    elif UB_CHANNELLINK:
                        ENT_USERNAME = UB_CHANNELLINK
                    else:
                        ENT_USERNAME = ENT_TID

                    ENT_LINK = f"https://t.me/{ENT_USERNAME}"
                    ENT_USERNAME = f"@{ENT_USERNAME}"
                else:
                    get_chat_ = await bot.get_chat(int(ENT_TID))
                    ENT_LINK = f"https://t.me/{get_chat_.username}" if get_chat_.username else get_chat_.invite_link
                    ENT_USERNAME = get_chat_.title

                figure_html = ''
                telegraph_ = Telegraph()
                await telegraph_.create_account(short_name=short_name, author_name=ENT_USERNAME, author_url=ENT_LINK)

                if POST_LNK:
                    POST_LNKS = ast.literal_eval(POST_LNK) if '[' in POST_LNK else [POST_LNK]
                    POST_TYPES = ast.literal_eval(POST_TYPE) if '[' in POST_TYPE else [POST_TYPE]

                    for i in range(len(POST_LNKS)):
                        tgph_ph = POST_LNKS[i].replace('https://telegra.ph', '')
                        if POST_TYPES[i] in ['video', 'video_note']:
                            figure_html = f'{figure_html}<figure><video src="{tgph_ph}" preload="auto" autoplay="autoplay" loop="loop" muted="muted"></video><figcaption>Video: {ENT_LINK}</figcaption></figure>'
                        else:
                            figure_html = f'{figure_html}<figure><img src="{tgph_ph}"/><figcaption>Photo: {ENT_LINK}</figcaption></figure>'

                p_html = ''
                if POST_TEXT and POST_TEXT != '':
                    POST_TEXT = POST_TEXT.strip()
                    if '\n' in POST_TEXT:
                        POST_TEXTS = POST_TEXT.split('\n')
                        for i in range(len(POST_TEXTS)):
                            if POST_TEXTS[i] == '': continue

                            if len(POST_TEXTS) > 2 and i == 1 and is_format:
                                p_html = f"{p_html}<p><blockquote>{POST_TEXTS[i]}</blockquote></p>"
                            elif len(POST_TEXTS) > 4 and i == 4 and is_format:
                                p_html = f"{p_html}<p><aside>{POST_TEXTS[i]}</aside></p>"
                            else:
                                p_html = f"{p_html}<p>{POST_TEXTS[i]}</p>"
                    else:
                        p_html = f"<p>{POST_TEXT}</p>"
                html_ = f"{figure_html}{p_html}"
                page_blog = await telegraph_.create_page(title=f"📰 {ENT_USERNAME}", html_content=html_,
                                                         author_name=str(ENT_USERNAME), author_url=ENT_LINK)
                result = page_blog['url']
                logger.info(f"{ENT_TID}: {result}")
                return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(3, 5), 2))
                cnt -= 1
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def check_webapp_hash(init_data, TOKEN_BOT, BOT_TOKEN_MAIN=None):
    result = None
    try:
        parsed_data = dict(parse_qsl(init_data))  # return k/v, but not dict!
        if "auth_date" not in parsed_data: return
        # auth_date = utils.timestamp_to_datetime(int(parsed_data['auth_date']))  # web_app opened seconds
        # print('seconds {(datetime.datetime.now() - auth_date).seconds}')
        # if (datetime.datetime.now() - auth_date).seconds > 36000 or "hash" not in parsed_data: return
        # какой смысл не делать с BOT_TOKEN_MAIN, если он используется в srv_bot_add и srv_app_upd

        hash_ = parsed_data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0)))

        secret_key = hmac.new(key=b"WebAppData", msg=BOT_TOKEN_MAIN.encode(), digestmod=hashlib.sha256)
        calculated_hash = hmac.new(key=secret_key.digest(), msg=data_check_string.encode(),
                                   digestmod=hashlib.sha256).hexdigest()

        if calculated_hash != hash_:
            secret_key = hmac.new(key=b"WebAppData", msg=TOKEN_BOT.encode(), digestmod=hashlib.sha256)
            calculated_hash = hmac.new(key=secret_key.digest(), msg=data_check_string.encode(),
                                       digestmod=hashlib.sha256).hexdigest()
            if calculated_hash != hash_: return

        res = {}
        for key, value in parse_qsl(init_data):
            if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
                value = json.loads(value)
            res[key] = value

        result = res
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


# endregion


# region notes
# sys.path.append('../hub')
# print("In module products sys.path[0], __package__ ==", sys.path[-1], __package__)
# from .. .hub import xtra
# dp.register_chosen_inline_handler(chosen_inline_handler_fun, lambda chosen_inline_result: True)
# dp.register_inline_handler(inline_handler_main, lambda inline_handler_main_: True)
# channel_post_handler
# edited_channel_post_handler
# poll_handler - а это получается реакция на размещение опроса
# poll_answer_handler - реакция на голосование
# chat_join_request_handler
# errors_handler
# current_state

# apt install redis -y
# nano /etc/redis/redis.conf
# systemctl restart redis.service
# systemctl status redis
# redis-cli
# netstat -lnp | grep redis

# apt update && apt upgrade -y
# curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
# apt install -y nodejs build-essential nginx yarn
# npm install -g npm pm2@latest -g
# ufw allow 'Nginx Full'
# curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
# echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
# node -v
# nginx -v
# yarn -v

# systemctl restart nginx
# systemctl reload nginx
# snap install core;  snap refresh core
# apt remove python3-certbot-nginx certbot -y
# rm -rf /etc/letsencrypt/renewal/
# rm -rf /etc/letsencrypt/archive/
# rm -rf /etc/letsencrypt/live/
# rm -rf /opt/letsencrypt
# rm -rf /etc/letsencrypt
# snap install --classic certbot
# ln -s /snap/bin/certbot /usr/bin/certbot
# endregion


# region functions
async def get_row_html(msg_text, msg_btns, start, finish, MSG_VID, BOT_TID, BOT_LC, BASE_BOT, BASE_D):
    result = ''
    try:
        row_html = '<div class="buttons-row">'

        for btn in msg_btns:
            try:
                if int(btn['i']) < start: continue

                if int(btn['i']) >= finish:
                    result = f"{row_html}</div>"
                    break

                sql = "SELECT PUSH_ID FROM PUSH WHERE POST_ID=? AND BUTTON_ID=?"
                data_push = await db_select(sql, (int(MSG_VID), int(btn["i"]),), BASE_BOT)
                btn_cnt_click = str(len(data_push)).replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3',
                                                                                                                  '³').replace(
                    '4', '⁴').replace('5', '⁵').replace('6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹')

                if btn['knd'] == 'payment':
                    invoice_link = await create_invoice_link(BOT_TID, BOT_LC, msg_text, msg_btns, BASE_D)
                    if not invoice_link: continue

                    btn_html = f'<a id="btn-{btn["knd"]}-{btn["i"]}-{str(len(data_push))}" class="button" data-url="{invoice_link}">{btn_cnt_click} {btn["lbl"]} ᶱ</a>'
                    row_html = f"{row_html}{btn_html}"
                elif btn['knd'] == 'phone':
                    btn_html = f'<a id="btn-{btn["knd"]}-{btn["i"]}-{str(len(data_push))}" class="button" data-url="{btn["lnk"]}">{btn_cnt_click} {btn["lbl"]} ⁿ</a>'
                    row_html = f"{row_html}{btn_html}"
                elif btn['knd'] in ['like', 'button_in']:
                    btn_html = f'<a id="btn-like-{btn["i"]}-{str(len(data_push))}" class="button" data-url="lnk">{btn_cnt_click} {btn["lbl"]}</a>'
                    row_html = f"{row_html}{btn_html}"
                elif btn['knd'] == 'link':
                    btn_html = f'<a id="btn-{btn["knd"]}-{btn["i"]}-{str(len(data_push))}" class="button" data-url="{btn["lnk"]}">{btn_cnt_click} {btn["lbl"]} ᶺ</a>'
                    row_html = f"{row_html}{btn_html}"
                    logger.info(log_ % f"{btn_html=}")
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        if len(row_html) > len('<div class="buttons-row">'):
            result = f"{row_html}</div>"
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def is_member_in_channel(bot, chat_id, lz):
    result = False
    try:
        # бот дб добавлен в канал предварительно
        channel_id = ferey_channel_en
        if lz == 'ru':
            channel_id = ferey_channel_europe
        elif lz == 'es':
            channel_id = ferey_channel_es
        elif lz == 'fr':
            channel_id = ferey_channel_fr
        elif lz == 'ar':
            channel_id = ferey_channel_ar
        elif lz == 'zh':
            channel_id = ferey_channel_zh

        get_chat_member_ = await bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
        if get_chat_member_.status in ['member', 'administrator', 'creator']:
            result = True
        else:
            text = l_subscribe_channel_for_post[lz].format(get_tg_channel(lz))
            await bot.send_message(chat_id, text)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_lz_by_entity_id(ENTITY_TID, BASE_D):
    result = 'en'
    try:
        sql = "SELECT OWNER_TID FROM CHANNEL WHERE CHANNEL_TID=?"
        data = await db_select(sql, (ENTITY_TID,), BASE_D)
        if not len(data): return
        OWNER_TID = data[0][0]

        sql = "SELECT USER_LZ FROM USER WHERE USER_TID=?"
        data = await db_select(sql, (OWNER_TID,), BASE_D)
        if not len(data): return
        result = data[0][0]
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def run_shell(cmd):
    result = None
    try:
        proc = await asyncio.create_subprocess_shell(cmd, stderr=asyncio.subprocess.PIPE,
                                                     stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        logger.info(log_ % f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            logger.info(log_ % f'{stdout.decode()}')
            result = f'[stdout]\n{stdout.decode()}'
        if stderr:
            logger.info(log_ % f'{stderr.decode()}')
            result = f'[stderr]\n{stderr.decode()}'
        else:
            result = str(proc.returncode)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


def _join(*content, sep=" "):
    return sep.join(map(str, content))


async def get_chat_channel(bot, link, SESSION_D, BASE_S):
    result = r = None
    try:
        sql = "SELECT SESSION_TID, SESSION_STATUS FROM SESSION"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)

        for _ in data:
            sql = "SELECT SESSION_TID, SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_STATUS FROM SESSION"
            data = await db_select(sql, (), BASE_S)
            random.shuffle(data)
            SESSION_TID, SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_STATUS = data[0]
            if SESSION_STATUS is not None: continue

            try:
                sql = "UPDATE SESSION SET SESSION_STATUS=? WHERE SESSION_TID=?"
                await db_change(sql, (f'get_chat_channel', SESSION_TID,), BASE_S)

                logger.info(log_ % f"{SESSION_TID} {SESSION_NAME}")
                name_ = os.path.join(SESSION_D, SESSION_NAME)
                async with Client(name=name_, api_id=SESSION_APIID, api_hash=SESSION_APIHASH) as app:
                    try:
                        r = await join_my_chat(bot, app, my_tid, link, SESSION_TID, BASE_S)
                        result = await bot.get_chat(r.id)
                    finally:
                        await leave_my_chat(app, r, link)
                        break
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired, SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS=? WHERE SESSION_TID=?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def auto_destroy_msg(bot, telegram_bot, chat_id, text, message_id, type_='text', sec=5):
    result = None
    try:
        if not random.choice([0, 1, 1]): return

        step = 1
        by = f"<a href='https://t.me/{ferey_telegram_demo_bot}'>by</a>"
        text = f"{text}\n\n{by} @{telegram_bot} <b>{sec}</b>sec"
        ix_sec = text.rfind('</b>sec')
        while text[ix_sec] != '>': ix_sec -= 1

        while sec > 0:
            try:
                text = text.replace(f"<b>{sec}</b>sec", f"<b>{sec - 1}</b>sec")
                sec -= step
                if type_ == 'text':
                    await bot.edit_message_text(text, chat_id, message_id, disable_web_page_preview=True)
                else:
                    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text)
                await asyncio.sleep(1)
            except TelegramRetryAfter as e:
                logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
                await asyncio.sleep(e.retry_after + 1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
                break
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        await bot.delete_message(chat_id, message_id)
        return result


async def log_old(txt, LOG_DEFAULT, colour=92):
    try:
        logging.info(f'\033[{colour}m%s\033[0m' % (str(txt)))
        async with aiofiles.open(LOG_DEFAULT, 'a') as f:
            await f.write(str(txt) + '\n')
    except Exception as e:
        logger.info(f'\033[{95}m%s\033[0m' % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def log(txt, color=21):
    try:
        '''DESC
21 - underscore     !
30 - black          !
90 - grey
91 - red            !
92 - green          !
93 - yellow         
94 - blue
95 - purple         !
96 - cyan           !
97 - white
---------------------
100 - grey bg
101 - red bg
102 - green bg
103 - yellow bg
104 - blue bg
105 - purple bg
106 - cyan bg
107 - white bg
'''

        logger.info(f'\033[{color}m%s\033[0m' % str(txt))
    except Exception:
        await asyncio.sleep(round(random.uniform(0, 1), 2))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fun_empty(txt):
    try:
        txt = str(txt)
        if '%' in txt:
            print(txt)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def lz_code(chat_id, lan, BASE_D):
    result = 'en'
    try:
        sql = "SELECT USER_LZ FROM USER WHERE USER_TID=?"
        data = await db_select(sql, (chat_id,), BASE_D)

        # first enter before DB
        if not len(data) or not data[0][0]:
            # chinese
            if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
                result = 'zh'
            # arabic    # ir, af
            elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
                result = 'ar'
            # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
            elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
                result = 'es'
            # french
            elif lan in ['fr', 'ch', 'be', 'ca']:
                result = 'fr'
            # europe
            elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
                result = 'ru'

            sql = "UPDATE USER SET USER_LZ=? WHERE USER_TID=?"
            await db_change(sql, (result, chat_id,), BASE_D)
        else:
            result = data[0][0]
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def no_war_text(txt):
    result = txt
    try:
        pass  # result = txt.replace('а', 'ä').replace('А', 'Ä').replace('в', 'ʙ').replace('В', 'B').replace('г', 'ґ')  # .replace('Г', 'Ґ').replace('е', 'é').replace('Е', 'É').replace('ж', 'җ').replace('Ж', 'Җ').replace('з', 'з́')  # .replace('З', 'З́').replace('й', 'ҋ').replace('Й', 'Ҋ').replace('к','қ').replace('К', 'Қ').replace('М', 'M')  # .replace('Н','H').replace('о', 'ô').replace('О', 'Ô').replace('р', 'p').replace('Р', 'P').replace('с', 'č')  # .replace('С', 'Č').replace('т', 'ҭ').replace('Т', 'Ҭ').replace('у', 'ў').replace('У', 'Ў').replace('х', 'x')  # .replace('Х', 'X').replace('э', 'є').replace('Э', 'Є')  # result = txt.replace('А', 'Ä').replace('в', 'ʙ').replace('В', 'B').replace('г', 'ґ').replace('Г', 'Ґ').  # replace('Е', 'É').replace('ж', 'җ').replace('Ж', 'Җ').replace('й', 'ҋ').replace('К', 'Қ').replace('М', 'M')  # .replace('Н', 'H').replace('о', 'ô').replace('О', 'Ô').replace('р', 'p').replace('Р', 'P').replace('С', 'Č')  # .replace('Т', 'Ҭ').replace('У', 'Ў').replace('х', 'x').replace('Х', 'X').replace('э', 'є')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_from_media(CONF_P, EXTRA_D, MEDIA_D, BASE_D, src, re_write=False, basewidth=1024):
    result = None
    try:
        is_link = await is_url(src)
        file_id = await get_fileid_from_src(src, is_link, BASE_D)
        if is_link and 'drive.google.com' not in src:
            result = src
        elif src is None:
            result = None
        elif file_id and re_write is False:
            result = file_id
        else:
            if os.path.basename(src) in os.listdir(MEDIA_D) and re_write is False:
                result = os.path.abspath(os.path.join(MEDIA_D, os.path.basename(src)))
            else:
                scopes = r_conf('scopes', CONF_P)
                credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
                credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
                http_auth = credentials.authorize(httplib2.Http())
                drive_service = build('drive', 'v3', http=http_auth, cache_discovery=False)

                if is_link:
                    docid = get_doc_id_from_link(src)
                    file_list_dic = await api_get_file_list(drive_service, docid, {}, is_file=True)
                else:
                    file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

                for k, v in file_list_dic.items():
                    if is_link:
                        result = await api_dl_file(drive_service, k, v[0], v[1], MEDIA_D)
                        break
                    elif str(v[0]).lower() == str(os.path.basename(src)).lower():
                        result = await api_dl_file(drive_service, k, v[0], v[1], MEDIA_D)
                        break

            if await is_image(result):
                result = await resize_media(result, basewidth)
            elif await is_video(result):
                result = await resize_video_note(result, basewidth)
            logger.info(log_ % 'dl media ok')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def is_url(url):
    status = False
    try:
        if url and '://' in url:  # and requests.get(url).status_code == 200:
            status = True
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return status


async def get_fileid_from_src(src, is_link, BASE_D):
    data = None
    try:
        if is_link:
            sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILELINK = ?"
        else:
            sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME = ?"
        data = await db_select(sql, (src,), BASE_D)
        if not data:
            return None
        data = data[0][0]
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return data


async def is_image(file_name):
    im = None
    try:
        if str(file_name).lower().endswith('.docx') or str(file_name).lower().endswith('.pdf') or str(
                file_name).lower().endswith('.mp4'):
            return False
        im = Image.open(file_name)
    except Exception as e:
        logger.info(log_ % 'isImage: ' + str(e))
    finally:
        return im


async def is_video(file_name):
    vi = None
    try:
        vi = True if str(mimetypes.guess_type(file_name)[0]).startswith('video') else False
    except Exception as e:
        logger.info(log_ % 'isVideo: ' + str(e))
    finally:
        return vi


async def get_thumb(MEDIA_D, file_name, sz_thumbnail=32):
    size = sz_thumbnail, sz_thumbnail
    result = ''
    try:
        name = get_name_without_ext(file_name)
        im = Image.open(file_name)
        im.thumbnail(size, Image.ANTIALIAS)
        result = f'{MEDIA_D}/"thumbnail_"{name}'
        im.save(result, "JPEG")
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def check_username(username):
    result = True
    try:
        if str(username).isdigit():
            result = False
        elif len(username) < 4 or len(username) > 31:
            result = False
        elif username.startswith('_') or username.endswith('_'):
            result = False
        elif '@' in username and not username.startswith('@'):
            result = False
        else:
            for it in username:
                if it not in string.ascii_letters + string.digits + "@_":
                    result = False
                    return
    except TelegramRetryAfter as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


def touch(path):
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path,
                     None)  # async with aiofiles.open(path, 'a'):  #     await asyncio.to_thread(os.utime, path, None)


def get_numbers_with_mark(data, id_, row_width=5):
    btns = []
    middle = int(row_width / 2 + 1)
    length = 5 if len(data) < 5 else len(data)

    if id_ == 1 or id_ == 2 or id_ == 3:
        btns.insert(0, f'1')
        btns.insert(1, f'2')
        btns.insert(2, f'3')
        btns.insert(3, f'4›')
        btns.insert(4, f'{length}»')

        btns[id_ - 1] = f'· {id_} ·'
    elif middle < id_ < length - middle + 1:  # 4
        btns.insert(0, f'«1')
        btns.insert(1, f'‹{id_ - 1}')
        btns.insert(2, f'· {id_} ·')
        btns.insert(3, f'{id_ + 1}›')
        btns.insert(4, f'{length}»')
    elif id_ == length or id_ == length - 1 or id_ == length - 2:
        btns.insert(0, f'«1')
        btns.insert(1, f'‹{length - 3}')
        btns.insert(2, f'{length - 2}')
        btns.insert(3, f'{length - 1}')
        btns.insert(4, f'{length}')

        btns[(row_width - (length - id_)) - 1] = f'· {id_} ·'

    if id_ == 4 and len(data) == 4:
        btns = ['«1', '‹2', '3', '· 4 ·', '5']

    return btns


def get_keyboard(data, src, post_id=1, chat_id=''):
    result = InlineKeyboardBuilder()

    row_width = len(data) if len(data) < 5 else 5
    btns = get_numbers_with_mark(data, post_id, row_width)
    buttons = []

    for i in range(1, row_width + 1):
        arr = re.split(r'\s|[«‹·›»]', btns[i - 1])  # ('\s|(?<!\d)[,.](?!\d)', s)
        page_i = list(filter(None, arr))[0]
        page_name = f'page_{src}_{chat_id}_{str(int(page_i))}'
        buttons.append(types.InlineKeyboardButton(text=btns[i - 1], callback_data=page_name))
    result.row(*buttons).adjust(row_width)
    return result


async def save_fileid(message, src, BASE_D):
    if message is None: return
    file_id = usr_id = ''
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.animation:  # giff
        file_id = message.animation.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:  # m4a
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.video_note:
        file_id = message.video_note.file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.poll:
        file_id = message.poll.id

    if await is_url(src):
        sql = f"INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILELINK) VALUES (?, ?);"
    else:
        sql = "INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILENAME) VALUES (?, ?);"
    if not await is_exists_filename_or_filelink(src, BASE_D):
        usr_id = await db_change(sql, (file_id, src,), BASE_D)
    return usr_id


async def is_exists_filename_or_filelink(src, BASE_D):
    sql = "SELECT * FROM FILE"
    data = await db_select(sql, (), BASE_D)
    for item in data:
        if src in item:
            return True
    return False


async def check_email(content):
    # Email-check regular expression
    result = None
    try:
        parts = content.split()
        for part in parts:
            USER_EMAIL = re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", part)
            if len(USER_EMAIL) != 0:
                result = USER_EMAIL[0]
                break
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def check_phone(content):
    result = None
    try:
        for phone in content.split():
            if phone and (str(phone).startswith('+') or str(phone).startswith('8') or str(phone).startswith('9') or str(
                    phone).startswith('7')) and len(str(phone)) >= 10:
                result = phone
                break
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_photo_file_id(bot, chat_id, file_id_text, BASE_D):
    result = None
    try:
        sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME='text.jpg'"
        data2 = await db_select(sql, (), BASE_D)
        if not len(data2):
            res = await bot.send_photo(chat_id, text_jpeg)
            result = res.photo[-1].file_id
            sql = "INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILENAME) VALUES (?, ?)"
            await db_change(sql, (file_id_text, 'text.jpg',), BASE_D)
        else:
            result = data2[0][0]
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


def is_yes_not(msg):
    result = False
    try:
        if msg and str(msg).lower().strip() in ['y', 'yes', 'да', 'д', 'lf', 'l', '1']:
            result = True
    finally:
        return result


def w_conf(key, val, CONF_P, INI_D):
    try:
        CONF_P.read(INI_D)
        CONF_P.set(SECTION, key, str(val))

        with open(INI_D, 'w') as configfile:
            CONF_P.write(configfile)
    except Exception as e:
        print(e, 95)


def r_conf(key, CONF_P):
    result = None
    try:
        s = CONF_P.get(SECTION, key)
        result = ast.literal_eval(s)
        if len(result) == 0:
            result = None
    finally:
        return result


def get_doc_id_from_link(link):
    try:
        begin = link[0:link.rindex('/')].rindex('/') + 1
        end = link.rindex('/')
        link = link[begin:end]
    finally:
        return link


def get_tg_channel(lan):
    result = 'ferey_channel_en'
    try:
        # chinese
        if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
            result = 'ferey_channel_zh'
        # arabic    # ir, af
        elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
            result = 'ferey_channel_ar'
        # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
        elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
            result = 'ferey_channel_es'
        # french
        elif lan in ['fr', 'ch', 'be', 'ca']:
            result = 'ferey_channel_fr'
        # europe
        elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
            result = 'ferey_channel_europe'
    except Exception as e:
        logger.info(e)
    finally:
        return result


def get_tg_group(lan):
    result = 'ferey_group_english'
    try:
        # chinese
        if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
            result = 'ferey_group_chinese'
        # arabic    # ir, af
        elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
            result = 'ferey_group_arabic'
        # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
        elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
            result = 'ferey_group_spanish'
        # french
        elif lan in ['fr', 'ch', 'be', 'ca']:
            result = 'ferey_group_french'
        # europe
        elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
            result = 'ferey_group_europe'
    except Exception as e:
        logger.info(e)
    finally:
        return result


async def send_to_admins(bot, CONF_P, txt):
    try:
        for admin_id in r_conf('admin_id', CONF_P):
            try:
                await bot.send_message(chat_id=int(admin_id), text=txt)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        logger.info(log_ % txt)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def template_sender(CONF_P, EXTRA_D, MEDIA_D):
    # post_media_id = None
    post_media_options = None

    # 1
    post_txt = f'''
🍃 Через 1 час в 20:00 я проведу прямой эфир!

Подключайся и смотри все самые интересные моменты!

🍂 Не пропусти возможность!
Переходи по моей ссылке, встроенной в кнопку.
'''
    post_btn = '🎥 Прямой эфир в instagram'
    post_url = 'https://www.instagram.com'
    post_media_type = 'photo'
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_pin = False
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=3)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name, post_media_type,
                                    post_pin, post_time, post_media_options)

    # 2
    post_txt = f'''
🔥 Как тебе прямой эфир? 
Расскажи об этом. 
Ниже я прикреплю Google-форму обратной связи

При заполнении, пришлю тебе Чек-лист по твоему запросу
'''
    post_btn = '⚠️ Google-форма обратной связи'
    post_url = 'https://docs.google.com/forms/d/e/1FAIpQLSehCkXuL9nCgRvPEdddgTnC99SMW-d_qTPzDjBzbASTAnX_lg/viewform'
    post_media_type = 'photo'
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_pin = True
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=4)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name, post_media_type,
                                    post_pin, post_time, post_media_options)

    # 3
    post_txt = post_btn = post_url = post_pin = None
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_media_type = 'video_note'
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=5)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name, post_media_type,
                                    post_pin, post_time, post_media_options)


async def api_update_send_folder(CONF_P, EXTRA_D, INI_D):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0]), r_conf('scopes', CONF_P))
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
    dynamic_folder_name = (r_conf('dynamic_folder_id', CONF_P))[0]
    file_list_dic = await api_get_file_list(drive_service, dynamic_folder_name, {})

    tmp = {}
    for k, v in file_list_dic.items():
        try:
            if v[1] == 'application/vnd.google-apps.folder':
                # google_folder.append(v[0])
                tmp[k] = v[0]  # google_key.append(v[2])
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))

    tmp = dict(sorted(tmp.items(), key=lambda para: para[-1], reverse=False))
    google_folder = []
    google_key = []
    for k, v in tmp.items():
        google_key.append(k)
        google_folder.append(v)

    # google_folder.sort()
    w_conf('google_folder', google_folder, CONF_P, INI_D)
    w_conf('google_key', google_key, CONF_P, INI_D)
    logger.info(log_ % google_folder)


async def scheduled_hour(part_of_hour, CONF_P, EXTRA_D, INI_D):
    logger.info(log_ % 'scheduled_hour ok')
    # await templateSender()
    await api_update_send_folder(CONF_P, EXTRA_D, INI_D)
    await asyncio.sleep(part_of_hour + 200)
    while True:
        logger.info(log_ % f'start sending...{str(datetime.datetime.now())}')
        await api_update_send_folder(CONF_P, EXTRA_D, INI_D)
        await asyncio.sleep(one_hour - (datetime.datetime.now()).minute * 60 + 200)


async def read_likes(BASE_D, POST_ID=1):
    cnt = '⁰'
    try:
        sql = "SELECT USER_ID FROM LIKE WHERE POST_ID = ?"
        data = await db_select(sql, (POST_ID,), BASE_D)
        cnt = str(0 + len(data))
        cnt = cnt.replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3', '³').replace('4', '⁴').replace('5',
                                                                                                                    '⁵').replace(
            '6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return cnt


async def db_has_like(user_id, post_id, BASE_D):
    data = True
    try:
        sql = "SELECT LIKE_ID FROM LIKE WHERE USER_ID=? AND POST_ID=?"
        data = await db_select(sql, (user_id, post_id,), BASE_D)
        data = True if data else False
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return data


def is_tid(item):
    result = False
    try:
        result = int(item)
    except Exception:
        # logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup(bot, owner_id, chat_id, offer_id, OFFER_BUTTON, BASE_D, COLUMN_OWNER="OFFER_CHATTID"):
    result = InlineKeyboardBuilder()
    try:
        if OFFER_BUTTON is None or OFFER_BUTTON == '': return
        tmp = []
        dic_btns = await check_buttons(bot, None, OFFER_BUTTON)
        buttons = []
        offer_id = int(offer_id)
        for k, v in dic_btns.items():
            try:
                if v[0]:
                    sql = f"SELECT * FROM OFFER WHERE {COLUMN_OWNER}=?"
                    data = await db_select(sql, (owner_id,), BASE_D)
                    items = [item[0] for item in data]
                    view_post_id = items.index(offer_id) + 1 if offer_id else len(data)

                    if len(tmp) > 0 and tmp[-1] is None:
                        result.add(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                        elif str(v[1]).startswith('btn_'):
                            buttons = [types.InlineKeyboardButton(text=str(v[0]),
                                                                  callback_data=f"{v[1]}_{chat_id}_{view_post_id}")]
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                        elif str(v[1]).startswith('btn_'):
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]),
                                                                      callback_data=f"{v[1]}_{chat_id}_{view_post_id}"))
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        if len(buttons) > 0:
            result.add(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result.as_markup()


async def create_replymarkup2(bot, offer_id, OFFER_BUTTON, type_='pst', is_counter=False):
    result = None
    try:
        if OFFER_BUTTON is None or OFFER_BUTTON == '': return
        tmp = []
        buttons = []
        offer_id = int(offer_id)
        dic_btns = await check_buttons(bot, None, OFFER_BUTTON, is_counter)
        result = InlineKeyboardBuilder()
        cnt_k = 0
        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.row(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                            cnt_k += 1
                        elif str(v[1]).startswith("btn_"):
                            buttons = [types.InlineKeyboardButton(text=str(v[0]),
                                                                  callback_data=f"btn_{type_}_{offer_id}_{cnt_k}")]
                            cnt_k += 1
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                            cnt_k += 1
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                            cnt_k += 1
                        elif str(v[1]).startswith("btn_"):
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]),
                                                                      callback_data=f"btn_{type_}_{offer_id}_{cnt_k}"))
                            cnt_k += 1
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                            cnt_k += 1
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.row(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup3(chat_id, post_id, POST_BUTTON, counters=None):
    if counters is None:
        counters = {}
    result = None
    try:
        if POST_BUTTON is None or POST_BUTTON == '': return
        tmp = []
        buttons = []
        post_id = int(post_id)
        dic_btns = await check_buttons2(POST_BUTTON, False)
        result = InlineKeyboardBuilder()
        cnt_k = 0
        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.row(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                            cnt_k += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if cnt_k not in counters else await upper_register(counters[cnt_k])
                            buttons = [types.InlineKeyboardButton(text=f"{counter} {str(v[0])}",
                                                                  callback_data=f"btn_{chat_id}_{post_id}_{cnt_k}")]
                            cnt_k += 1
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                            cnt_k += 1
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                            cnt_k += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if cnt_k not in counters else await upper_register(counters[cnt_k])
                            buttons.append(types.InlineKeyboardButton(text=f"{counter} {str(v[0])}",
                                                                      callback_data=f"btn_{chat_id}_{post_id}_{cnt_k}"))
                            cnt_k += 1
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                            cnt_k += 1
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.row(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup5(ent_id, post_id, POST_BUTTON, reply_markup, counters=None, is_spo=False):
    if counters is None:
        counters = {}
    result = reply_markup
    try:
        if POST_BUTTON is None or POST_BUTTON == '': return
        tmp = []
        btn_ix = 0
        buttons = []
        post_id = int(post_id)
        dic_btns = await check_buttons2(POST_BUTTON, False)

        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.row(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            cb_ = f"pst_{ent_id}_{post_id}_{btn_ix}"
                            if is_spo:
                                cb_ = f"pspoiler_{cb_}"
                                is_spo = not is_spo

                            buttons = [types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_)]
                            btn_ix += 1
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                            btn_ix += 1
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            cb_ = f"pst_{ent_id}_{post_id}_{btn_ix}"
                            if is_spo:
                                cb_ = f"pspoiler_{cb_}"
                                is_spo = not is_spo

                            buttons.append(types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_))
                            btn_ix += 1
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                            btn_ix += 1
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.row(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup_bot(ent_id, post_id, POST_BUTTON, reply_markup, cur_, len_, counters=None, is_spo=False):
    if counters is None:
        counters = {}
    result = reply_markup
    try:
        if POST_BUTTON is None or POST_BUTTON == '': return
        tmp = []
        btn_ix = 0
        buttons = []
        post_id = int(post_id)
        dic_btns = await check_buttons2(POST_BUTTON, False)

        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.row(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            cb_ = f"pst_{ent_id}_{post_id}_{btn_ix}_{cur_}_{len_}_like"
                            if is_spo:
                                cb_ = f"pspoiler_{cb_}"
                                is_spo = not is_spo

                            buttons = [types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_)]
                            btn_ix += 1
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                            btn_ix += 1
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            # cb_ = f"pst_{post_id}_{btn_ix}"
                            cb_ = f"pst_{ent_id}_{post_id}_{btn_ix}_{cur_}_{len_}_like"
                            if is_spo:
                                cb_ = f"pspoiler_{cb_}"
                                is_spo = not is_spo

                            buttons.append(types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_))
                            btn_ix += 1
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                            btn_ix += 1
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.row(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup4(ent_id, post_id, POST_BUTTON, reply_markup, counters=dict()):
    result = reply_markup
    try:
        if POST_BUTTON is None or POST_BUTTON == '': return
        tmp = []
        btn_ix = 0
        buttons = []
        post_id = int(post_id)
        dic_btns = await check_buttons2(POST_BUTTON, False)

        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.row(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            cb_ = f"btn_{ent_id}_{post_id}_{btn_ix}"

                            buttons = [types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_)]
                            btn_ix += 1
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                            btn_ix += 1
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                            btn_ix += 1
                        elif str(v[1]).startswith("btn_"):
                            counter = '⁰' if btn_ix not in counters else await upper_register(counters[btn_ix])
                            cb_ = f"btn_{ent_id}_{post_id}_{btn_ix}"

                            buttons.append(types.InlineKeyboardButton(text=f"{counter} {str(v[0])}", callback_data=cb_))
                            btn_ix += 1
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                            btn_ix += 1
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.row(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def check_buttons(bot, chat_id, txt, is_counter=False):
    result = {}
    txt = txt.strip()
    try:
        start_ = []
        finish_ = []
        for ix in range(0, len(txt)):
            try:
                if txt[ix] == '[':
                    start_.append([ix, '['])
                elif txt[ix] == ']':
                    finish_.append([ix, ']'])
                elif txt[ix] == '\n':
                    start_.append([ix, '\n'])
                    finish_.append([ix, '\n'])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        if len(start_) != len(finish_): return

        for ix in range(0, len(start_)):
            try:
                if start_[ix][-1] == '\n':
                    result[ix] = [None, None]
                else:
                    tmp = txt[start_[ix][0] + 1: finish_[ix][0]]
                    split_btn = tmp.strip().split('|')
                    if len(split_btn) > 1:
                        btn_name = split_btn[0].strip() if len(split_btn) > 1 else "🔗 Go"
                        btn_link = split_btn[-1].strip()
                        if not await is_url(btn_link):
                            await bot.send_message(chat_id, f"🔗 {btn_link}: invalid")
                            return
                    else:
                        btn_name = f"⁰{split_btn[0]}" if is_counter else split_btn[0]
                        # btn_link = cleanhtml(split_btn[0])[:20]
                        # btn_link = f"btn_{btn_link.encode('utf-8').hex()}"
                        btn_link = f"btn_"

                    result[ix] = [btn_name, btn_link]
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}", 95)
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def check_buttons2(txt, is_counter=False):
    result = {}
    try:
        if not txt: return
        txt = txt.strip()
        start_ = []
        finish_ = []
        for ix in range(0, len(txt)):
            try:
                if txt[ix] == '[':
                    start_.append([ix, '['])
                elif txt[ix] == ']':
                    finish_.append([ix, ']'])
                elif txt[ix] == '\n':
                    start_.append([ix, '\n'])
                    finish_.append([ix, '\n'])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        if len(start_) != len(finish_): return

        for ix in range(0, len(start_)):
            try:
                if start_[ix][-1] == '\n':
                    result[ix] = [None, None]
                else:
                    tmp = txt[start_[ix][0] + 1: finish_[ix][0]]
                    split_btn = tmp.strip().split('|')
                    if len(split_btn) > 1:
                        btn_name = split_btn[0].strip() if len(split_btn) > 1 else "🔗 Go"
                        btn_link = split_btn[-1].strip()
                        if not await is_url(btn_link):
                            return
                    else:
                        btn_name = f"⁰{split_btn[0]}" if is_counter else split_btn[0]
                        btn_link = f"btn_"

                    result[ix] = [btn_name, btn_link]
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}", 95)
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def get_post_of_dict(dicti_, pos=1):
    tmp = 1
    for k, v in dicti_.items():
        if tmp == pos:
            return k, v
        tmp += 1
    return None, None


async def del_extra_files(UNKNOWN_ERRORS_TXT, EXTRA_D):
    try:
        if os.path.exists(UNKNOWN_ERRORS_TXT): os.remove(UNKNOWN_ERRORS_TXT)

        max_dt = datetime.datetime(2020, 1, 1)
        arr = [it for it in os.listdir(EXTRA_D) if it.startswith('debug.') and it != 'debug.log']

        for item in arr:
            parts = item.split('.')
            if len(parts) <= 2: continue
            parts_dt = parts[1].split('_')
            cur_dt = datetime.datetime.strptime(f"{parts_dt[0]}_{parts_dt[1]}", '%Y-%m-%d_%H-%M-%S')

            if cur_dt > max_dt:
                max_dt = cur_dt

        for item in arr:
            file_item = os.path.join(EXTRA_D, item)
            parts = item.split('.')
            if len(parts) <= 2: continue
            parts_dt = parts[1].split('_')
            cur_dt = datetime.datetime.strptime(f"{parts_dt[0]}_{parts_dt[1]}", '%Y-%m-%d_%H-%M-%S')

            if cur_dt < max_dt and os.path.exists(file_item):
                os.remove(file_item)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def get_proxy(identifier, EXTRA_D, CONF_P, server=None):
    result = None
    try:
        if r_conf('proxy', CONF_P) == 0: return

        async with aiofiles.open(os.path.join(EXTRA_D, "proxy.txt"), "r") as f:
            lines = await f.readlines()
        random.shuffle(lines)

        for line in lines:
            try:
                hostname, port, username, password = line.strip().split('..')
                # logger.info(log_ % f"proxy ({identifier}): {hostname}")
                result = {"scheme": "socks5", "hostname": hostname, "port": int(port), "username": username,
                          "password": password}
                break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
    except Exception as e:
        logger.info(log_ % f"{str(e)}, {identifier}, {server}")
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def is_names(phrase):
    # (?s)\bhello\b.*?\b
    keywords = ['names', 'сотка', 'скорость', 'like', 'концентрат', 'aяз', 'чит-код', "сборная", 'ск-', 'капитан',
                'лагерь']
    for keyword in keywords:
        if keyword.lower() in phrase.lower():
            return True
    return False


async def haversine(lon1, lat1, lon2, lat2):
    result = None
    try:
        """
        Calculate the great circle distance in kilometers between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6372
        result = c * r * 1000.0
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


# endregion


def main():
    pass


if __name__ == "__main__":
    main()
