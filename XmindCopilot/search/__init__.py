'''
Author: MasterYip 2205929492@qq.com
Date: 2023-08-20 18:06:15
LastEditors: MasterYip
LastEditTime: 2023-12-27 16:05:08
FilePath: /XmindCopilot/XmindCopilot/search/__init__.py
Description: file content
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing_extensions import deprecated
import re
import os
import XmindCopilot
from ..core import const


class Pointer(object):
    def __init__(self):
        # path - list of topic titles
        self.path = []
        # snapshot - record pathstr for CLI display
        self.snapshot = []

    def getpathstr(self, connectsym="->", rm_newline=True):
        """获取当前路径String"""
        str = ""
        for p in self.path:
            if rm_newline:
                p = p.replace("\r\n", "")
            str += p + connectsym
        return str

    def printer(self):
        """打印当前路径"""
        print(self.getpathstr())

    def treeprint(self):
        """DEPRECATED 结构化打印当前路径 仅保留最后一项"""
        if self.path:
            tab = ""
            for i in range(len(self.path)-1):
                tab += "\t|"
            print(tab+self.path[-1])

    def snap(self, simplify=False):
        """
        记录当前路径并添加至self.snapshot
        :param simplify: 是否简化路径(去除重复部分) DEPRECATED
        """
        if simplify:  # DEPRECATED
            result = ""
            path = self.getpathstr()
            if self.snapshot:
                priouspath = self.snapshot[-1]
                flag = 1
                for i in range(len(path)):
                    if i < len(priouspath):
                        if path[i] == priouspath[i] and flag:
                            # result += " "
                            pass
                        else:
                            flag = 0
                            result += path[i]
                    else:
                        result += path[i]
            print(result)
            self.snapshot.append(result)
        else:
            self.snapshot.append(self.getpathstr())


""" Title_search """


def topic_search(topic, str, depth: int = -1, re_match=False):
    # Search for title(return fisrt topic matched)
    title = topic.getTitle()
    # print(title,'\n')
    if title and (re_match and re.match(str, title) or str in title):
        return topic

    subtopiclist = topic.getSubTopics()
    if depth == -1 and subtopiclist:
        for t in subtopiclist:
            if topic_search(t, str):
                return topic_search(t, str)
    elif depth > 0 and subtopiclist:
        for t in subtopiclist:
            if topic_search(t, str, depth=depth-1):
                return topic_search(t, str, depth=depth-1)

    return None


def topic_search_snap(topic, ptr, str):
    title = topic.getTitle()
    if title:
        ptr.path.append(title)
        # 是否包含在标题中(正则表达式)
        if re.match(str, title):
            ptr.snap()
            # ptr.treeprint()
            # 并没有节省时间？
            # ptr.path.pop()
            # return
    else:
        ptr.path.append("[Title Empty]")

    subtopiclist = topic.getSubTopics()
    if subtopiclist:
        for t in subtopiclist:
            topic_search_snap(t, ptr, str)
    ptr.path.pop()
    return


@deprecated("Not used anymore")
def getTopicAddress(topic):
    """
    获取目标topic在workbook中的路径(停用)
    """
    connectsym = "->"
    route = ""
    parent = topic
    type = parent.getType()
    while type != const.TOPIC_ROOT:
        title = parent.getTitle()
        if title:
            route = title + connectsym + route
        else:
            route = "#FIG#" + connectsym + route
        parent = parent.getParentTopic()
        type = parent.getType()
    title = parent.getTitle()
    route = title + connectsym + route
    return route


""" Xmind File Search """


def workbooksearch(path, str):
    workbook = XmindCopilot.load(path, get_refs=False)
    sheets = workbook.getSheets()
    search_result = []
    if sheets[0].getTitle():
        for sheet in sheets:
            root_topic = sheet.getRootTopic()
            ptr = Pointer()
            # FIXME: 目前此函数只能从roottopic开始
            topic_search_snap(root_topic, ptr, str)
            search_result += ptr.snapshot
    else:
        if os.path.isfile(path):
            print("File doesn't exist:"+workbook.get_path())
        else:
            print("Failed to open:"+workbook.get_path())
    return search_result


""" Batch Search """


def BatchSearch(searchstr, paths, verbose=True):
    """
    Batch Search for xmind files
    :param searchstr: search string
    :param paths: xmind file path list
    :param verbose: whether to print the search result
    """
    tot_result = {}
    for path in paths:
        search_result = workbooksearch(path, searchstr)
        if search_result:
            tot_result[path] = search_result
            if verbose:
                print("\033[92m"+path+"\033[0m")
                for r in search_result:
                    # r = r.replace("\n", " ")
                    r = r.replace(
                        searchstr, "\033[1;91m"+searchstr+"\033[1;0m")
                    r = r.replace("->", "\033[1;96m->\033[1;0m")
                    print(r)
                print("\n")

    return tot_result
