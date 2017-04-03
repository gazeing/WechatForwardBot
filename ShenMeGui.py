# -*- coding: utf-8 -*-
from utilities import *
from itchat.content import *
from pymongo import MongoClient, DESCENDING
from ProcessInterface import ProcessInterface
import os
import itchat
import random
import time
import logging
import requests, re
from urllib import request


class ShenMeGui(ProcessInterface):
    recordMaxNum = 500
    imgDir = 'TagCloud'
    GOOGLE_SEARCH = 'https://www.googleapis.com/customsearch/v1?'
    key = ''
    lastmsg = '111'
    destination_chatroom_id = ''
    tempname = ''

    def __init__(self):
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        with open('key.md', 'r') as myfile:
            self.key = myfile.read().replace('\n', '')
        if not os.path.exists(self.imgDir):
            os.mkdir(self.imgDir)
        logging.info('ShenMeGui connected to MongoDB.')

    def process(self, msg, type):
        shallRunObj = self.isRun(msg, type)
        if shallRunObj['shallRun']:
            url = self.GOOGLE_SEARCH + self.key + self.lastmsg
            resp = self.query_api(url)
            if not resp:
                logging.info('no content')
            result = self.parse_google(resp)
            # logging.info('Generating tag cloud for {0}.'.format(shallRunObj['groupName']))
            # fn = self.generateTagCloudForGroup(shallRunObj['groupName'], shallRunObj['userName'])
            self.destination_chatroom_id = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg[
                'ToUserName']
            # logging.info('Sending tag cloud file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send(result['title'] + ' ➡️➡️ ' + result['link'], self.destination_chatroom_id)
            image = self.parse_image(resp)
            if image != 'error':
                # logging.info('downloading image from {0}.'.format(image))
                # self.tempname = self.generateTmpFileName()
                # request.urlretrieve(image, self.tempname, reporthook=self.upload_image)
                itchat.send('没图你说个jb ➡️ {0}'.format(image), self.destination_chatroom_id)

    def upload_image(self, count, blockSize, totalSize):
        if (count * blockSize) == totalSize:
            itchat.send('@img@{0}'.format(self.tempname), self.destination_chatroom_id)

    def query_api(self, google):
        data = ''
        r = requests.get(google)
        if r.status_code == 200:
            data = r.json()
        return data

    def parse_google(self, jsonstring):
        data = jsonstring
        link = data["items"][0]["link"]
        title = data["items"][0]["title"]
        return {'link': link, 'title': title}

    def parse_image(self, jsonstring):
        data = jsonstring
        try:
            image = data["items"][0]["pagemap"]["cse_image"][0]['src']
        except KeyError:  # includes simplejson.decoder.JSONDecodeError
            logging.info('Decoding JSON has failed')
            return 'error'
        return image

    def generateTmpFileName(self):
        return '{0}/{1}-{2}.png'.format(self.imgDir, int(time.time() * 1000), random.randint(0, 10000))

    # # 只能是unicode编码,不能在后面再转换为utf-8,否则无法正则匹配上.
    # html = unicode(html, 'gb2312')
    # # html = unicode(html, 'gb2312').encode('utf-8')
    # # print html
    # pattern = re.compile(PATTERN)
    # m = pattern.search(html)
    # if m:
    #     print
    #     m.group(1)
    # else:
    #     print
    #     'regex match failed'

    # Generate a tag cloud image from the latest self.recordMaxNum images. Return the file name.

    def generateSearchPage(self, groupName, userName=None):
        link = '111'
        return link

    # records = None
    # if userName is None:
    #     records = self.coll.find({'to': groupName}).sort([('timestamp', DESCENDING)]).limit(self.recordMaxNum)
    # else:
    #     records = self.coll.find({'from': userName, 'to': groupName}).sort([('timestamp', DESCENDING)]).limit(
    #         self.recordMaxNum)
    # texts = [r['content'] for r in records]
    # frequencies = Counter([w for text in texts for w in jieba.cut(text, cut_all=False) if len(w) > 1])
    # img = self.wordCloud.generate_from_frequencies(frequencies).to_image()
    # fn = self.generateTmpFileName()
    # img.save(fn)
    # return fn

    def isRun(self, msg, type):
        if type != TEXT or 'Content' not in msg:
            return {'shallRun': False}
        if msg['Content'] == '/shenmegui':
            return {'shallRun': True}
        self.lastmsg = msg['Content']
        return {'shallRun': False}


if __name__ == '__main__':
    shenmegui = ShenMeGui()
    shenmegui.generateSearchPage('602_635')
