import sys
if "../" not in sys.path:
    sys.path.append("../")

import re
from urllib.parse import unquote
from XmindCopilot.search import topic_search
from XmindCopilot.topic_cluster import topic_cluster
from XmindCopilot.file_shrink import xmind_shrink
from XmindCopilot.playerone_mgr import topic_info_transfer, topic_info_clear
import XmindCopilot


def topic_traverse(topic):
    if topic.getHyperlink() and re.match("^file:(.*)\.xmind$", unquote(topic.getHyperlink())):
        print(unquote(str(topic.getHyperlink())))
        topic.setHyperlink(unquote(topic.getHyperlink())+"8")
    topics = topic.getSubTopics()
    for t in topics:
        topic_traverse(t)


# Topic info transfer (data transfer from player one to sub xmind)
xmind_path = "D:\\SFTR\\PlayerOS\\Player One.xmind8"
workbook = XmindCopilot.load(xmind_path)
rootTopic = workbook.getPrimarySheet().getRootTopic()
filetreeTopic = topic_search(rootTopic, "文件索引", 2)
# topic_info_transfer(filetreeTopic)
topic_info_clear(filetreeTopic)
XmindCopilot.save(workbook)

# Topic Cluster (cluster topics in draft)
# xmind_path = "D:\\SFTR\\PlayerOS\\Player One.xmind8"
# workbook = XmindCopilot.load(xmind_path)
# rootTopic = workbook.getPrimarySheet().getRootTopic()
# draftTopic = topic_search(rootTopic, "Draft", 2)
# topic_cluster(draftTopic)
# XmindCopilot.save(workbook)


# HyperLink rename (from .xmind to .xmind8)
# xmind_path = "D:\\SFTR\\PlayerOS\\Player One.xmind8"
# workbook = XmindCopilot.load(xmind_path)
# rootTopic = workbook.getPrimarySheet().getRootTopic()
# topic_traverse(rootTopic)
# XmindCopilot.save(workbook)

# Xmind Shrink
# xmind_path = "D:\\SFTR\\1 Course\\EE_Engineering\\5 电力电子技术"
# xmind_shrink(xmind_path)
