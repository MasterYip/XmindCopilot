from PIL import Image, ImageDraw, ImageFont
import textwrap
import imgkit
from markdown import markdown

# 使用示例
table_md = """
| 维度                | RNN       | LSTM             | GRU             |
|---------------------|-----------|------------------|-----------------|
| ​**门控数量**         | 0         | 3（遗忘/输入/输出） | 2（更新/重置）   |
| ​**参数数量**         | 最少       | 最多（比GRU多33%） | 中等            |
| ​**计算效率**         | 最高       | 最低             | 中等            |
| ​**长序列表现**       | 差         | 优秀             | 良好            |
| ​**典型应用场景**     | 短文本生成 | 机器翻译/语音识别 | 对话系统/股票预测|
"""

# markdown_table_to_image(table_md)


def md_table_to_image_via_html(table_md, output="table.png"):
    # 将Markdown转换为HTML
    html = markdown(table_md, extensions=['tables'])

    # 添加CSS样式
    styled_html = f"""
    <html>
      <head>
        <style>
          table {{ 
            border-collapse: collapse;
            width: 100%; 
            font-family: Arial;
          }}
          td, th {{
            border: 1px solid #ddd;
            padding: 8px;
          }}
          th {{
            background-color: #f2f2f2;
          }}
        </style>
      </head>
      <body>{html}</body>
    </html>
    """

    # 转换为图片
    options = {
        'format': 'png',
        'encoding': "UTF-8",
        'quiet': ''
    }
    imgkit.from_string(styled_html, output, options=options)


# 使用示例
md_table_to_image_via_html(table_md, "table_html.png")
