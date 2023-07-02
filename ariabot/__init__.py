#!/usr/bin/local/python
# -*- coding: utf-8 -*-
# Author: XuanPro

import contextlib
import logging
import os
import signal
import sys

from telethon import connection, TelegramClient
from telethon.errors import AuthKeyDuplicatedError

from ariabot.aria2client import Aria2Client

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = int(os.getenv('USER_ID'))
RPC_URL = os.getenv('RPC_URL')
RPC_TOKEN = os.getenv('RPC_TOKEN')

Proxy_Type = os.getenv('Proxy_Type')
Proxy_Addr = os.getenv('Proxy_Addr')
Proxy_Port = os.getenv('Proxy_Port')
Proxy_User = os.getenv('Proxy_User')
Proxy_Passwd = os.getenv('Proxy_Passwd')
Proxy_Secret = os.getenv('Proxy_Secret')

# 日志
logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s=> [%(funcName)s] %(message)s ', level=logging.INFO)
logger = logging.getLogger(__name__)

# TG代理
connectionType = connection.ConnectionTcpMTProxyRandomizedIntermediate if Proxy_Type == "MTProxy" else connection.ConnectionTcpFull

# 获取代理
if Proxy_Type:
    if Proxy_User:
        proxy = {
            'proxy_type': Proxy_Type,
            'addr': Proxy_Addr,
            'port': Proxy_Port,
            'username': Proxy_User,
            'password': Proxy_Passwd
        }
    elif os.getenv('Proxy_Type') == "MTProxy":
        proxy = (Proxy_Addr, Proxy_Port, Proxy_Secret)
    else:
        proxy = (Proxy_Type, Proxy_Addr, Proxy_Port)
else:
    proxy = None


class TelegramClient(TelegramClient):
    async def reconnect(self):
        await self._disconnect()
        await self.connect()


try:
    bot = TelegramClient('bot', API_ID, API_HASH, connection=connectionType, proxy=proxy, connection_retries=None, request_retries=10).start(bot_token=BOT_TOKEN)
    Aria2 = Aria2Client(RPC_URL, RPC_TOKEN, bot, USER_ID)
except AuthKeyDuplicatedError:
    with contextlib.suppress(Exception):
        os.kill(os.getpid(), signal.SIGINT)
        os.remove('bot.session')
        python = sys.executable
        os.execv(python, ['python', '-m', 'ariabot'])
