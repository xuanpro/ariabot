#!/usr/bin/local/python
# -*- coding: utf-8 -*-
# Author: XuanPro

from aioaria2 import Aria2WebsocketClient
from aioaria2.exceptions import Aria2rpcException

from ariabot.util import getFileName


class Aria2Client:
    def __init__(self, rpc_url, rpc_token, bot, user):
        self.rpc_url = rpc_url
        self.rpc_token = rpc_token
        self.bot = bot
        self.user = user
        self.client = None

    async def init(self):
        try:
            self.client = await Aria2WebsocketClient.new(self.rpc_url, token=self.rpc_token)
            await self.client.getGlobalStat()
        except Aria2rpcException:
            await self.bot.send_message(self.user, 'Aria2连接出错, 请检查Url和Token')
            return

        # 注册回调事件
        self.client.onDownloadStart(self.on_download_start)
        self.client.onDownloadPause(self.on_download_pause)
        self.client.onDownloadComplete(self.on_download_complete)
        self.client.onDownloadError(self.on_download_error)

    async def on_download_start(self, _trigger, data):
        gid = data['params'][0]['gid']
        # 查询是否是绑定特征值的文件
        tellStatus = await self.client.tellStatus(gid)
        await self.bot.send_message(self.user, f'{getFileName(tellStatus)}\n\n 任务已经开始下载... \n 下载目录: `{tellStatus["dir"]}`')

    async def on_download_pause(self, _trigger, data):
        gid = data['params'][0]['gid']
        tellStatus = await self.client.tellStatus(gid)
        await self.bot.send_message(self.user, f'{getFileName(tellStatus)}\n\n 任务已经成功暂停')

    async def on_download_complete(self, _trigger, data):
        gid = data['params'][0]['gid']
        tellStatus = await self.client.tellStatus(gid)
        await self.bot.send_message(self.user, f'{getFileName(tellStatus)}\n\n 任务下载完成')

    async def on_download_error(self, _trigger, data):
        gid = data['params'][0]['gid']
        tellStatus = await self.client.tellStatus(gid)
        errorCode = tellStatus['errorCode']
        errorMessage = tellStatus['errorMessage']
        if errorCode == '12':
            await self.bot.send_message(self.user, f'{getFileName(tellStatus)}\n\n 任务正在下载,请删除后再尝试')
        else:
            await self.bot.send_message(self.user, errorMessage)
