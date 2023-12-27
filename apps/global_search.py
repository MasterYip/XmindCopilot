'''
Author: MasterYip 2205929492@qq.com
Date: 2023-12-27 14:45:21
LastEditors: MasterYip
LastEditTime: 2023-12-27 15:05:52
FilePath: /XmindCopilot/apps/global_search.py
Description: file content
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# autopep8: off
import os
import sys
import glob
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from XmindCopilot.search import BatchSearch
# autopep8: on


def getXmindPath():
    path = []
    path += glob.glob('D:/SFTR/**/*.xmind', recursive=True)
    path += glob.glob('D:/SFTR/**/*.xmind8', recursive=True)
    path += glob.glob('E:/SFTRDatapool2/ProjectCompleted/**/*.xmind',
                      recursive=True)
    path += glob.glob('E:/SFTRDatapool2/ProjectCompleted/**/*.xmind8',
                      recursive=True)
    return path


def GlobalSearchLooper():
    while True:
        searchstr = input("Search:")
        BatchSearch(searchstr, getXmindPath(), True)


if __name__ == "__main__":
    GlobalSearchLooper()
