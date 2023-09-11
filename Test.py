import sys
if "../" not in sys.path:
    sys.path.append("../")

from XmindCopilot.search import topic_search
from XmindCopilot.topic_cluster import topic_cluster
from XmindCopilot.file_shrink import xmind_shrink
import XmindCopilot

# xmind_path = "D:\\SFTR\\PlayerOS\\Player One.xmind"
# workbook = XmindCopilot.load(xmind_path)
# rootTopic = workbook.getPrimarySheet().getRootTopic()
# draftTopic = topic_search(rootTopic, "Draft", 2)
# topic_cluster(draftTopic)
# XmindCopilot.save(workbook)

xmind_path = "D:\\SFTR\\1 Course\\EE_Engineering\\5 电力电子技术"
xmind_shrink(xmind_path)
