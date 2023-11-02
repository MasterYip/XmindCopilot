
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
// Support CLI pytest (Import error)
import XmindCopilot
from XmindCopilot.search import topic_search
from XmindCopilot.file_shrink import xmind_shrink
from XmindCopilot.fmt_cvt.md2xmind import MarkDown2Xmind
from XmindCopilot.fmt_cvt.latex_render import latex2img
from XmindCopilot.fmt_cvt.latex_render import latex2img_web
from XmindCopilot.topic_cluster import topic_cluster

TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
TEST_TEMPLATE_XMIND = os.path.join(
    os.path.dirname(__file__), "TestTemplate.xmind")
TEST_TEMPLATE_MD = os.path.join(os.path.dirname(__file__), "TestTemplate.md")
TEST_TEMPLATE_MDList = os.path.join(
    os.path.dirname(__file__), "TestIndentList.md")

if not os.path.isdir(TMP_DIR):
    os.mkdir(TMP_DIR)


class TestXmindCopilot(unittest.TestCase):
    def testXmindLoad(self):
        xmind_path = TEST_TEMPLATE_XMIND
        workbook = XmindCopilot.load(xmind_path)
        sheets = workbook.getSheets()
        first_sheet = sheets[0]
        root_topic = first_sheet.getRootTopic()
        print(root_topic.getTitle())
        subtopics = root_topic.getSubTopics()
        for topic in subtopics:
            print('  ', topic.getTitle())
        self.assertTrue(True)


class TestTopicCluster(unittest.TestCase):
    def testTopicCluster(self):
        xmind_path = TEST_TEMPLATE_XMIND
        workbook = XmindCopilot.load(xmind_path)
        rootTopic = workbook.getPrimarySheet().getRootTopic()
        topic_cluster(rootTopic)
        XmindCopilot.save(workbook, os.path.join(
            TMP_DIR, "TestTopicCluster.xmind"))
        self.assertTrue(True)


class TestSearch(unittest.TestCase):
    def testSearch(self):
        xmind_path = TEST_TEMPLATE_XMIND
        workbook = XmindCopilot.load(xmind_path)
        sheets = workbook.getSheets()
        first_sheet = sheets[0]
        root_topic = first_sheet.getRootTopic()
        search_topic = topic_search(root_topic, '常用标记')
        print("\n")
        print(search_topic.getTitle())
        for subtopic in search_topic.getSubTopics():
            print('  ', subtopic.getTitle())
        self.assertTrue(True)


class TestXmindShrink(unittest.TestCase):
    def testXmindShrink(self):
        xmind_path = TEST_TEMPLATE_XMIND
        xmind_shrink(xmind_path,
                     PNG_Quality=10, JPEG_Quality=20, use_pngquant=True,
                     replace=False,
                     output_path=os.path.join(TMP_DIR, "TestShrink.xmind"))
        self.assertTrue(True)


class TestXmindFmtConvert(unittest.TestCase):
    def testMarkdown2Xmind(self):
        file_path = TEST_TEMPLATE_MD
        xmind_path = os.path.join(TMP_DIR, "TestMd2Xmind.xmind")
        if os.path.isfile(xmind_path):
            os.remove(xmind_path)
        workbook = XmindCopilot.load(xmind_path)
        rootTopic = workbook.getPrimarySheet().getRootTopic()
        markdowntext = open(file_path, 'r', encoding='utf-8').read()
        # rootTopic.addSubTopicbyMarkDown(markdowntext)
        # rootTopic.convertTitle2WebImage(recursive=True)
        MarkDown2Xmind(rootTopic).convert2xmind(
            markdowntext, cvtWebImage=True, cvtHyperLink=True)
        MarkDown2Xmind(rootTopic).printSubSections(markdowntext)
        XmindCopilot.save(workbook)
        self.assertTrue(True)

    def testMarkdownList2Xmind(self):
        file_path = TEST_TEMPLATE_MDList
        xmind_path = os.path.join(TMP_DIR, "TestMdList2Xmind.xmind")
        if os.path.isfile(xmind_path):
            os.remove(xmind_path)
        workbook = XmindCopilot.load(xmind_path)
        rootTopic = workbook.getPrimarySheet().getRootTopic()
        markdowntext = open(file_path, 'r', encoding='utf-8').read()
        rootTopic.addSubTopicbyMarkDown(markdowntext)
        # MarkDown2Xmind(rootTopic).convert2xmind(markdowntext)
        XmindCopilot.save(workbook)
        self.assertTrue(True)

    def testLatexRenderer(self):
        text = r'$\sum_{i=0}^\infty x_i$'
        latex2img(text, size=48, color=(0.1, 0.8, 0.8),
                  out=os.path.join(TMP_DIR, "TestLatex.png"))

        text = r'$\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$'
        im = latex2img(text, size=48, color=(0.9, 0.1, 0.1))
        # im.show()

    def testLatexRendererWeb(self):
        # Example usage
        # latex_expression = r"a^2+b^2=c^2"
        latex_expression = r"""
                            $$
                            \dot{X} =
                            \begin{bmatrix}
                            0 & 1\\
                            -\frac{K}{m} & -D\\
                            \end{bmatrix}
                            X + 
                            \begin{bmatrix}
                            0 \\
                            -g
                            \end{bmatrix}
                            $$
                            """
        padding = 50
        image_format = 'png'
        try:
            path = latex2img_web(latex_expression, output_file=None,
                                 padding=padding, image_format=image_format)
            os.system("start %s" % path)
        except:
            print("Failed to render latex expression. please check network connection.")


## Legacy
# from XmindCopilot import xmind
# from XmindCopilot.search import topic_search
# from XmindCopilot.topic_cluster import topic_cluster, ClusterArgs, MarkerId
# from XmindCopilot.fileshrink import xmind_shrink
# import re
# from XmindCopilot.playerone_mgr import topic_info_transfer
# import os

def resource_cluster():
    args = ClusterArgs()
    args.sample_number = 5
    args.threshold = 0.0
    args.name_len = 4
    args.name_len_update = False

    workbook = xmind.load("E:/CodeTestFile/comprehensive-coding/XmindCopilot/test/XmlTest.xmind")
    sheets = workbook.getSheets()
    if not sheets[0].getTitle():
        print("Failed to open:"+workbook.get_path())

    root_topic = sheets[2].getRootTopic()
    topic = topic_search(root_topic, "Draft")
    topic.removeSubTopicbyMarkerId(MarkerId.flagRed, recursive=True)
    topic_cluster(topic, recursive=False, args=args)

    xmind.save(workbook)


def cluster_distribute():
    # TODO Cluster Distrubute
    pass


def player_info_transfer():
    workbook = xmind.load('D:/SFTR/PlayerOS/Player One.xmind')
    sheets = workbook.getSheets()
    if not sheets[0].getTitle():
        print("Failed to open:"+workbook.get_path())

    root_topic = sheets[0].getRootTopic()
    topic = topic_search(root_topic, "文件索引")
    topic_info_transfer(topic)
    xmind.save(workbook)
    

def batch_shrink():
    # Specify the <xmind file path> OR <folder path containing the xmind files>
    # folder_path = "D:\\CodeTestFiles\\HITSA-Courses-Xmind-Note"
    folder_path = "D:\\SFTR\\1 Course\\MITBlended_AI"

    # Specify the compression level
    use_pngquant = True
    # CV: 0-9(high-low) | pngquant: 1-100(low-high)
    PNG_Quality = 10
    # CV: 0-100(low-high)
    JPEG_Quality = 20
    
    '''
    ideal for xmind files: PNG_Quality=10, JPEG_Quality=20
    extreme compression: PNG_Quality=1, JPEG_Quality=0 (PNG will lose color(almost B&W?), JPEG will lose color details)
    '''
    xmind_shrink(folder_path, PNG_Quality, JPEG_Quality, replace=True, use_pngquant=use_pngquant)

if __name__ == '__main__':
    unittest.main()
