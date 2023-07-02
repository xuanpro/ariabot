#!/usr/bin/local/python
# -*- coding: utf-8 -*-
# Author: XuanPro

import asyncio
import os
import re
import sys
from asyncio.exceptions import TimeoutError
from base64 import b64encode
from contextlib import suppress
from datetime import datetime

from telethon import Button, events, functions
from telethon.errors import AlreadyInConversationError, MessageNotModifiedError

from ariabot import Aria2, bot, RPC_TOKEN, RPC_URL, USER_ID
from ariabot.util import byte2Readable, flatten_list, format_lists, format_name, getFileName, hum_convert, progress, split_list


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender.id != USER_ID:
        await event.respond('对不起，您无权使用Aria助手 😢')
        return
    await hello()


@bot.on(events.NewMessage(pattern='/menu', from_users=USER_ID))
async def menu(event):
    await event.respond('欢迎使用 **Aria2** 助手! 👏', buttons=get_menu())


@bot.on(events.NewMessage(pattern="/close", from_users=USER_ID))
async def close(event):
    await event.respond("键盘已关闭\n发送 /menu 开启键盘", buttons=Button.clear())


@bot.on(events.NewMessage(pattern="/recon", from_users=USER_ID))
async def recon(event):
    async def dc_info():
        nonlocal DCinfo
        start = datetime.now()
        await bot(functions.PingRequest(ping_id=0))
        end = datetime.now()
        ping_duration = (end - start).microseconds / 1000
        start = datetime.now()
        DCinfo += f"\n封包延迟: `PING | {ping_duration}`"
        await msg.edit(DCinfo)
        end = datetime.now()
        msg_duration = (end - start).microseconds / 1000
        DCinfo += f"\n消息延迟:   `MSG | {msg_duration}`"

    DCinfo = "**正在重连**"
    msg = await event.respond(DCinfo)
    await dc_info()
    await msg.edit(DCinfo)
    await bot.reconnect()
    DCinfo += "\n\n**重连完成**"
    await dc_info()
    await msg.edit(DCinfo)


@bot.on(events.NewMessage(pattern="/reboot", from_users=USER_ID))
async def restart(event):
    await event.respond("正在重启Bot", buttons=Button.clear())
    python = sys.executable
    os.execv(python, ['python', '-m', 'ariabot'])


@bot.on(events.NewMessage(pattern="/help", from_users=USER_ID))
async def helper(event):
    await event.respond(
        'start-开始程序\n'
        'menu-开启键盘\n'
        'close-关闭键盘\n'
        'recon-重连网络\n'
        'reboot-重启bot\n'
        'help-获取命令'
    )


@bot.on(events.NewMessage(from_users=USER_ID))
async def lisenter(event):
    text = event.raw_text
    if Aria2.client is None or Aria2.client.closed:
        await Aria2.init()
    if text == '🚀️ 查看状态':
        await getglobalstat(event)
        return
    elif text == '⬇ 正在下载':
        await downloading(event)
        return
    elif text == '⌛ 正在等待':
        await waiting(event)
        return
    elif text == '🆗 已完成/停止':
        await stoped(event)
        return
    elif text == '⏸ 暂停任务':
        await stopTask(event)
        return
    elif text == '▶️ 开始任务':
        await unstopTask(event)
        return
    elif text == '❌ 删除任务':
        await removeTask(event)
        return
    elif text == '🔁 修改下载':
        await editTaskFile(event)
        return
    elif text == '⏸ 全部暂停':
        await pauseAll(event)
        return
    elif text == '▶️ 全部开始':
        await unpauseAll(event)
        return
    elif text == '❌ 全部删除':
        await removeTaskAll(event)
        return
    elif text == '❌ 清空已结束':
        await removeAll(event)
        return
    elif text == '↩ 关闭键盘':
        await event.respond("键盘已关闭\n发送 /menu 开启键盘", buttons=Button.clear())
        return

    if 'http' in text or 'magnet' in text:

        pat1 = re.compile(r'magnet:\?xt=urn:btih:[0-9a-fA-F]{40,}.*')
        pat2 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

        res1 = pat1.findall(text)
        res2 = pat2.findall(text)

        for text in (res1 + res2):
            await Aria2.client.addUri([text])

    with suppress(Exception):
        if event.media and event.media.document:
            if event.media.document.mime_type == 'application/x-bittorrent':
                await event.respond('收到了一个BT种子')
                path = await bot.download_media(event.message)
                await Aria2.client.add_torrent(path)
                os.remove(path)


async def hello():
    addr = re.sub(r'://|:', '/', RPC_URL.strip('/'))
    token = b64encode(RPC_TOKEN.encode('utf-8')).decode('utf-8')
    url = f"http://ariang.eu.org/#!/settings/rpc/set/{addr}/{token}"
    giturl = 'https://github.com/xuanpro/ariabot'
    await bot.send_message(
        USER_ID,
        '欢迎使用 **Aria2** 助手! 👏\n\n'
        '发送 /start 开始程序\n'
        '发送 /menu  开启菜单\n'
        '发送 /close 关闭菜单\n'
        '发送 /recon 重连网络\n'
        '发送 /reboot 重启bot\n'
        '发送 /help 获取命令',
        buttons=[Button.url('🚀️AriaNg', url), Button.url('Github', giturl)])


# 文本按钮回调方法=============================


async def getglobalstat(event):
    res = await Aria2.client.getGlobalStat()
    downloadSpeed = hum_convert(int(res['downloadSpeed']))
    uploadSpeed = hum_convert(int(res['uploadSpeed']))
    numActive = res['numActive']
    numWaiting = res['numWaiting']
    numStopped = res['numStopped']
    info = f'欢迎使用 **Aria2** 助手! 👏\n\n'
    info += f'下载：`{downloadSpeed}`\n'
    info += f'上传：`{uploadSpeed}`\n'
    info += f'正在下载：`{numActive}`\n'
    info += f'正在等待：`{numWaiting}`\n'
    info += f'已完成/已停止：`{numStopped}`'
    await event.respond(info)


async def downloading(event):
    # 正在下载的任务
    tasks = await Aria2.client.tellActive()
    if not tasks:
        await event.respond('没有正在运行的任务')
        return
    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        if fileName == '':
            continue
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))
        send_str += f'任务名称: {fileName}\n进度: {prog}\n大小: {size}\n速度: {speed}\n\n'
    if send_str:
        for i in range(0, len(send_str), 4000):
            await event.respond(send_str[i:i + 4000])
    else:
        await event.respond('无法识别任务名称，请发送 /start 使用AriaNG查看')


async def waiting(event):
    # 正在等待的任务
    tasks = await Aria2.client.tellWaiting(0, 1000)
    if not tasks:
        await event.respond('任务列表为空')
        return
    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))
        send_str += f'任务名称: {fileName}\n进度: {prog}\n大小: {size}\n速度: {speed}\n\n'
    if send_str:
        for i in range(0, len(send_str), 4000):
            await event.respond(send_str[i:i + 4000])
    else:
        await event.respond('无法识别任务名称，请发送 /start 使用AriaNG查看')


async def stoped(event):
    # 已完成/停止的任务
    tasks = await Aria2.client.tellStopped(0, 1000)
    if not tasks:
        await event.respond('任务列表为空')
        return
    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))
        send_str += f'任务名称: {fileName}\n进度: {prog}\n大小: {size}\n速度: {speed}\n\n'
    if send_str:
        for i in range(0, len(send_str), 4000):
            await event.respond(send_str[i:i + 4000])
    else:
        await event.respond('无法识别任务名称，请发送 /start 使用AriaNG查看')


async def unstopTask(event):
    tasks = await Aria2.client.tellWaiting(0, 1000)
    if not tasks:
        await event.respond('任务列表为空')
        return
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        buttons.append(Button.inline(format_name(fileName), task['gid']))
    try:
        async with bot.conversation(event.sender.id, timeout=60) as conv:
            res, data, msg = await get_pagesplit('请选择要开始▶ 的任务', event, buttons, conv)
            if res:
                await msg.delete()
                await Aria2.client.unpause(data)
    except AlreadyInConversationError:
        wait = await bot.send_message(event.sender.id, "无法在同个聊天内启动多个对话")
        await asyncio.sleep(5)
        await wait.delete()
    except TimeoutError:
        await bot.edit_message(msg, "选择已超时")


async def stopTask(event):
    tasks = await Aria2.client.tellActive()
    if not tasks:
        await event.respond('任务列表为空')
        return
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append(Button.inline(format_name(fileName), gid))
    try:
        async with bot.conversation(event.sender.id, timeout=60) as conv:
            res, data, msg = await get_pagesplit('请选择要暂停⏸ 的任务', event, buttons, conv)
            if res:
                await msg.delete()
                await Aria2.client.pause(data)
    except AlreadyInConversationError:
        wait = await bot.send_message(event.sender.id, "无法在同个聊天内启动多个对话")
        await asyncio.sleep(5)
        await wait.delete()
    except TimeoutError:
        await bot.edit_message(msg, "选择已超时")


async def removeTask(event):
    tasks1 = await Aria2.client.tellActive()
    tasks2 = await Aria2.client.tellWaiting(0, 1000)
    tasks3 = await Aria2.client.tellStopped(0, 1000)
    tasks = tasks1 + tasks2
    if not (tasks + tasks3):
        await event.respond('任务列表为空')
        return
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append(Button.inline(format_name(fileName), 'del->' + gid))
    for task in tasks3:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append(Button.inline(format_name('结束·' + fileName), 'result->' + gid))
    try:
        async with bot.conversation(event.sender.id, timeout=60) as conv:
            res, data, msg = await get_pagesplit('请选择要删除❌ 的任务', event, buttons, conv)
            if res:
                mode, gid = data.split('->', 1)
                if mode == 'result':
                    await Aria2.client.removeDownloadResult(gid)
                else:
                    await Aria2.client.remove(gid)
                await bot.edit_message(msg, '任务删除成功')
    except AlreadyInConversationError:
        wait = await bot.send_message(event.sender.id, "无法在同个聊天内启动多个对话")
        await asyncio.sleep(5)
        await wait.delete()
    except TimeoutError:
        await bot.edit_message(msg, "选择已超时")


async def editTaskFile(event):
    tasks1 = await Aria2.client.tellActive()
    tasks2 = await Aria2.client.tellWaiting(0, 1000)
    tasks = tasks1 + tasks2
    if not tasks:
        await event.respond('任务列表为空')
        return
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append(Button.inline(format_name(fileName), gid))
    try:
        async with bot.conversation(event.sender.id, timeout=60) as conv:
            res, data, msg = await get_pagesplit('请选择要修改的任务', event, buttons, conv)
            if res:
                await editToTaskFile(res, conv, data)
    except AlreadyInConversationError:
        wait = await bot.send_message(event.sender.id, "无法在同个聊天内启动多个对话")
        await asyncio.sleep(5)
        await wait.delete()
    except TimeoutError:
        await bot.edit_message(msg, "选择已超时")


async def removeTaskAll(event):
    tasks1 = await Aria2.client.tellActive()
    tasks2 = await Aria2.client.tellWaiting(0, 1000)
    tasks = tasks1 + tasks2
    if not tasks:
        await event.respond('任务列表为空')
        return
    for task in tasks:
        await Aria2.client.remove(task['gid'])
    await event.respond('删除所有任务')


# 暂停所有
async def pauseAll(event):
    await Aria2.client.pauseAll()
    await event.respond('暂停所有任务')


# 开始所有
async def unpauseAll(event):
    await Aria2.client.unpauseAll()
    await event.respond('开始所有任务')


# 调用清除全部已完成/停止
async def removeAll(event):
    # 删除已完成或停止
    await Aria2.client.purgeDownloadResult()
    await event.respond('任务已清空')


# 编辑文件
async def editToTaskFile(event, conv, gid):
    msg = await event.edit('请稍后正在查询...')
    filesinfo = await Aria2.client.getFiles(gid)
    buttons = []
    for task in filesinfo:
        buttons.append(Button.inline(format_name(task['index'] + ':' + os.path.basename(task['path'].replace(' ', ''))), task['index']))
    size, line = 2, 10
    buttons = split_list(buttons, size)
    page = 0
    ids = []
    while True:
        btns = buttons
        if len(btns) > line:
            btns = split_list(btns, line)
            my_btns = [
                Button.inline('上一页', data='up'),
                Button.inline(f'{page + 1}/{len(btns)}', data='jump'),
                Button.inline('下一页', data='next')
            ]
            if page > len(btns) - 1:
                page = 0
            new_btns = btns[page]
            new_btns.append(my_btns)
        else:
            new_btns = btns
        new_btns.append([Button.inline('当页全选', 'checkall'), Button.inline('排除选择', 'exclude'), Button.inline('包含选择', 'over')])
        new_btns.append(get_cancel())
        with suppress(MessageNotModifiedError):
            msg = await msg.edit('请选择要下载的任务(可多选)' + (f"\n当前选择：{format_lists(ids)}" if ids else ''), buttons=new_btns)
        res_1 = await conv.wait_event(press_event(event))
        data_1 = res_1.data.decode()
        if data_1 == 'cancel':
            await bot.edit_message(msg, '取消选择')
            return
        elif data_1 == 'up':
            page -= 1
            if page < 0:
                page = len(btns) - 1
            continue
        elif data_1 == 'next':
            page += 1
            if page > len(btns) - 1:
                page = 0
            continue
        elif data_1 == 'jump':
            page_btns = [Button.inline(f'第 {i + 1} 页 {1 + i * line * size} - {(1 + i) * line * size}', data=str(i)) for i in range(len(btns))]
            page_btns = split_list(page_btns, 3)
            page_btns.append([Button.inline('返回', data='cancel')])
            await bot.edit_message(msg, '请选择跳转页面', buttons=page_btns)
            res_2 = await conv.wait_event(press_event(event))
            data_2 = res_2.data.decode()
            if data_2 == 'cancel':
                continue
            else:
                page = int(data_2)
                continue
        elif data_1 == 'over':
            break
        elif data_1 == 'exclude':
            numbers = [str(i) for i in range(1, len(filesinfo) + 1)]
            ids = [i for i in numbers if i not in ids]
            break
        elif data_1 in ids:
            ids.remove(data_1)
        elif data_1 == 'checkall':
            checkall = flatten_list(new_btns)
            pageids = [id for i in checkall if (id := i.to_dict()['data'].decode()).isdigit()]
            if set(pageids).issubset(set(ids)):
                ids = list(set(ids) - set(pageids))
            else:
                ids.extend(pageids)
        else:
            ids.append(data_1)
        ids = list(set(ids))
        ids.sort(key=lambda x: int(x))
        if len(ids) == len(filesinfo):
            break
    if ids:
        msg = await bot.edit_message(msg, f"当前选择：{format_lists(ids)}")
        args = {'select-file': ','.join(ids), 'bt-remove-unselected-file': 'true'}
        await Aria2.client.changeOption(gid, args)
        await msg.edit(msg.text + '\n修改完成')
    else:
        await bot.edit_message(msg, f"未修改")


def press_event(event):
    return events.CallbackQuery(func=lambda e: e.sender_id == event.sender.id)


def get_menu():
    return [
        [
            Button.text('🚀️ 查看状态'),
        ],
        [
            Button.text('⬇ 正在下载'),
            Button.text('⌛ 正在等待'),
            Button.text('🆗 已完成/停止')
        ],
        [
            Button.text('▶️ 开始任务'),
            Button.text('⏸ 暂停任务'),
            Button.text('❌ 删除任务'),
        ],
        [
            Button.text('▶️ 全部开始'),
            Button.text('⏸ 全部暂停'),
            Button.text('❌ 全部删除')
        ],
        [
            Button.text('🔁 修改下载'),
            Button.text('❌ 清空已结束'),
            Button.text('↩ 关闭键盘'),
        ],
    ]


def get_cancel():
    return [Button.inline('取消', 'cancel')]


async def get_pagesplit(text, event, buttons, conv):
    size, line = 2, 5
    buttons = split_list(buttons, size)
    page = 0
    msg = await conv.send_message(text)
    while True:
        btns = buttons
        if len(btns) > line:
            btns = split_list(btns, line)
            my_btns = [
                Button.inline('上一页', data='up'),
                Button.inline(f'{page + 1}/{len(btns)}', data='jump'),
                Button.inline('下一页', data='next')
            ]
            if page > len(btns) - 1:
                page = 0
            new_btns = btns[page]
            new_btns.append(my_btns)
        else:
            new_btns = btns
        new_btns.append(get_cancel())
        await msg.edit(text, buttons=new_btns)
        res = await conv.wait_event(press_event(event))
        data = res.data.decode()
        if data == 'cancel':
            await bot.edit_message(msg, '取消选择')
            return None, None, msg
        elif data == 'up':
            page -= 1
            if page < 0:
                page = len(btns) - 1
            continue
        elif data == 'next':
            page += 1
            if page > len(btns) - 1:
                page = 0
            continue
        elif data == 'jump':
            page_btns = [Button.inline(f'第 {i + 1} 页 {1 + i * line * size} - {(1 + i) * line * size}', data=str(i)) for i in range(len(btns))]
            page_btns = split_list(page_btns, 3)
            page_btns.append([Button.inline('返回', data='cancel')])
            await bot.edit_message(msg, '请选择跳转页面', buttons=page_btns)
            res_2 = await conv.wait_event(press_event(event))
            data_2 = res_2.data.decode()
            if data_2 == 'cancel':
                continue
            else:
                page = int(data_2)
                continue
        else:
            return res, data, msg
