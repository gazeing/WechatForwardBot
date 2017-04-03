# -*- coding: utf-8 -*-
import itchat, time, re
from itchat.content import *
from utilities import *
from sys import argv, exit
from GlobalTextHook import GlobalTextHook
from PaiDuiHook import PaiDuiHook
from HistoryRecorder import HistoryRecorder
from GroupTagCloud import GroupTagCloud
from ShenMeGui import ShenMeGui
from Translate import Translate
from GroupMessageForwarder import GroupMessageForwarder
from ProcessInterface import ProcessInterface
from ActivityInfo import ActivityInfo
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Some global switches for debugging use only
isDebug = not True

# Component initialization
itchat.auto_login(True)
plugins = [

    # GlobalTextHook({'李文耀': '刘佳欣', '正 王': '海潮'}),
    HistoryRecorder(),
    ShenMeGui(),
    Translate(),
    GroupTagCloud('~/Library/Fonts/wqy-microhei.ttc'),
    ActivityInfo('/users/steven.xu/Library/Fonts/wqy-microhei.ttc'),
    # GroupMessageForwarder(['Group1', 'Group2'], ['602_635', 'test1'])

]
for plugin in plugins:
    if not isinstance(plugin, ProcessInterface):
        logging.error('One of the plugins are not a subclass of ProcessInterface.')
        exit(-1)


# Core message loops
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def picture_reply(msg):
    logging.info(msg['ActualNickName']+':'+msg['Content'])
    for plugin in plugins:
        try:
            plugin.process(msg, PICTURE)
        except Exception as e:
            logging.error(e) # so that one plug's failure won't prevent others from being executed 


@itchat.msg_register([SHARING], isGroupChat=True)
def sharing_reply(msg):
    logging.info(msg['ActualNickName']+':'+msg['Content'])
    for plugin in plugins:
        try:
            plugin.process(msg, SHARING)
        except Exception as e:
            logging.error(e) # so that one plug's failure won't prevent others from being executed 


@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    logging.info(msg['ActualNickName']+':'+msg['Content'])
    for plugin in plugins:
        try:
            plugin.process(msg, TEXT)
        except Exception as e:
            logging.error(e) # so that one plug's failure won't prevent others from being executed 


if __name__ == '__main__':
    itchat.run()
