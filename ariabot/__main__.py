#!/usr/bin/local/python
# -*- coding: utf-8 -*-
# Author: XuanPro

from ariabot import bot

from ariabot.bot import hello

if __name__ == "__main__":
    with bot:
        bot.loop.create_task(hello())
        bot.loop.run_forever()
