
# -*- coding: utf-8 -*-

# autopep8: off
import os
import sys
import glob
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import XmindCopilot
from XmindCopilot.fmt_cvt.md2xmind import MarkDown2Xmind
from XmindCopilot.search import topic_search
# autopep8: on

if __name__ == "__main__":
    xmind_path = "D:\\SFTR\\PlayerOS\\Player One.xmind8"
    workbook = XmindCopilot.load(xmind_path)
    rootTopic = workbook.getPrimarySheet().getRootTopic()
    filetreeTopic = topic_search(rootTopic, "头脑风暴", 2)

    md_file = "apps/temp.md"
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    md2xmind = MarkDown2Xmind(filetreeTopic)
    md2xmind.convert2xmind(md_content, cvtEquation=True, cvtWebImage=True, cvtHyperLink=True)
    XmindCopilot.save(workbook)
    pass
