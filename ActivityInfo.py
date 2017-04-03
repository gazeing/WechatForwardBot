# -*- coding: utf-8 -*-
from utilities import *
from itchat.content import *
from ProcessInterface import ProcessInterface
from pymongo import MongoClient, DESCENDING
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as pp
from matplotlib.font_manager import FontProperties
from matplotlib.dates import HourLocator, DateFormatter
import numpy as np
from time import time
from collections import Counter
from datetime import datetime
import itchat
import random
import re
import os
import logging


class ActivityInfo(ProcessInterface):
    timestampSubtract = 3600 * 24  # 1 day
    imgDir = 'activityInfo'

    def __init__(self, fontPath):
        if not os.path.exists(self.imgDir):
            os.mkdir(self.imgDir)
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        self.prop = FontProperties(fname=fontPath)
        logging.info('ActivityInfo initialized.')

    def process(self, msg, type):
        if type != TEXT:
            return
        if msg['Content'] == '/activity':
            logging.info('Generating activity info for {0}.'.format(msg['User']['NickName']))
            fn = self.generateActivityInfoForGroup(msg['User']['NickName'])
            destinationChatroomId = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg['ToUserName']
            logging.info('Sending activity file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send('@img@{0}'.format(fn), destinationChatroomId)

    def generateActivityInfoForGroup(self, groupName):
        timestampNow = int(time())
        timestampYesterday = timestampNow - self.timestampSubtract
        records = list(self.coll.find({'to': groupName, 'timestamp': {'$gt': timestampYesterday}}).sort(
            [('timestamp', DESCENDING)]))
        fn = self.generateTmpFileName()
        # Get histogram for activity
        hist, bins = np.histogram([x['timestamp'] for x in records], bins=24)
        center = (bins[:-1] + bins[1:]) / 2
        datex = [datetime.fromtimestamp(x) for x in center]
        pp.figure(figsize=(6, 14))
        ax = pp.subplot(2, 1, 1)
        pp.plot_date(datex, hist, '.-')
        pp.gcf().autofmt_xdate()
        pp.xlabel('凸凹悉尼时间', fontproperties=self.prop)
        pp.ylabel('每小时消息数', fontproperties=self.prop)
        ax.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
        # Get pie chart for active users
        pieDat = Counter([x['from'] for x in records])
        others = 0
        allCount = len(records)
        pieDat2 = {}
        for name in pieDat:
            if pieDat[name] / allCount < 0.02:
                others += pieDat[name]
            else:
                pieDat2[name] = pieDat[name]
        pieDat2['其他'] = others
        pp.subplot(2, 1, 2)
        pp.pie(list(pieDat2.values()), labels=list(pieDat2.keys()), shadow=True,
               textprops={'fontproperties': self.prop})
        pp.savefig(fn)
        return fn

    def generateTmpFileName(self):
        return '{0}/{1}-{2}.png'.format(self.imgDir, int(time() * 1000), random.randint(0, 10000))


if __name__ == '__main__':
    ai = ActivityInfo('~/Library/Fonts/wqy-microhei.ttc')
    ai.generateActivityInfoForGroup('602_635')
