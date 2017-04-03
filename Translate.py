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



class Translate(ProcessInterface):
    recordMaxNum = 500
    lastmsg = '111'
    target = 'zh-CN'


    def __init__(self):
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        with open('key.md', 'r') as myfile:
            self.key = myfile.read().replace('\n', '')
        logging.info('Translate connected to MongoDB.')

    def process(self, msg, type):
        shallRunObj = self.isRun(msg, type)
        if shallRunObj['shallRun']:
            destination_chatroom_id = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg[
                'ToUserName']
            from google.cloud import translate
            translate_client = translate.Client()
            translation = translate_client.translate(
                self.lastmsg,
                target_language=self.target)
            # logging.info('Sending tag cloud file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send('人话 ➡️➡️ ' + translation['translatedText'], destination_chatroom_id)

    def isRun(self, msg, type):
        if type != TEXT or 'Content' not in msg:
            return {'shallRun': False}
        if msg['Content'] == '/fanyi':
            return {'shallRun': True}
        self.lastmsg = msg['Content']
        return {'shallRun': False}

    def translate_text(self, groupName, userName=None):
        link = '111'
        return link


if __name__ == '__main__':
    translate = Translate()
    translate.translate_text('602_635')
