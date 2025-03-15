import matplotlib.pyplot as plt
import re
import unicodedata
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

def markdown_table_to_png(md_table, output_path, 
                         font_family='SimHei',
                         font_size=12,
                         figsize=(6, 4), 
                         dpi=300):
    """
    修复渲染器问题的最终版本
    """
    # 配置字体和数学公式
    rcParams['font.sans-serif'] = [font_family, 'Microsoft YaHei', 'WenQuanYi Zen Hei']
    rcParams['axes.unicode_minus'] = False
    rcParams['mathtext.fontset'] = 'cm'

    # 初始化字体度量
    font = FontProperties(family=font_family, size=font_size)
    
    # 创建临时绘图对象用于计算
    temp_fig = plt.figure(figsize=figsize)
    temp_ax = temp_fig.add_subplot(111)
    renderer = temp_fig.canvas.get_renderer()

    # 文本预处理函数
    def preprocess_text(text):
        return re.sub(r'[\u200b-\u200d\ufeff]', '', 
                     ''.join(c for c in text if unicodedata.category(c)[0] != 'C'))

    # 列宽计算函数（修复版）
    def calculate_cell_width(text):
        """使用临时轴进行渲染计算"""
        text_obj = temp_ax.text(0, 0.5, text, 
                               fontproperties=font,
                               math_fontfamily='cm')
        text_obj.draw(renderer)
        bbox = text_obj.get_window_extent(renderer)
        temp_ax.cla()  # 清除临时轴内容
        return bbox.width

    # 解析表格数据
    rows = []
    for line in md_table.strip().split('\n'):
        line = re.sub(r'^\||\|$', '', line)
        cells = [preprocess_text(cell.strip()) for cell in line.split('|')]
        if any(cell.replace('-', '') for cell in cells):
            rows.append(cells)

    # 验证表格结构
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError("Invalid markdown table format")

    # 提取列标题和内容
    col_labels = rows[0]
    cell_text = rows[1:]
    col_count = len(col_labels)

    # 智能列宽计算
    max_widths = [0.0] * col_count
    for col in range(col_count):
        # 处理列标题
        header_width = calculate_cell_width(col_labels[col])
        max_widths[col] = header_width
        
        # 处理单元格内容
        for row in cell_text:
            cell_width = calculate_cell_width(row[col])
            if cell_width > max_widths[col]:
                max_widths[col] = cell_width

    # 创建最终图像
    final_fig = plt.figure(figsize=figsize)
    ax = final_fig.add_subplot(111)
    ax.axis("off")

    # 计算归一化列宽
    total_width = sum(max_widths)
    col_widths = [w / total_width * 0.95 for w in max_widths]

    # 创建表格
    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc='center',
        colWidths=col_widths,
    )

    # 样式设置
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    
    # 设置单元格样式
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#F5F5F5")
            cell.set_text_props(weight='bold')
        if col == 0 and row > 0:
            cell.set_text_props(weight='bold')

    # 保存输出
    try:
        final_fig.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    finally:
        plt.close(temp_fig)
        plt.close(final_fig)

# 测试用例
md_content = """
| 函数             | 公式                   | 特性             |
|------------------|------------------------|------------------|
| 正弦函数         | $\sin(x)$              | 周期为$2\pi$     |
| 欧拉公式         | $e^{i\pi} + 1 = 0$     | 最美数学公式     |
"""
# md_content = """
# | 维度                | RNN       | LSTM             | GRU             |
# |---------------------|-----------|------------------|-----------------|
# | **门控数量**         | 0         | 3（遗忘/输入/输出） | 2（更新/重置）   |
# | **参数数量**         | 最少       | 最多（比GRU多33%） | 中等            |
# | **计算效率**         | 最高       | 最低             | 中等            |
# | **长序列表现**       | 差         | 优秀             | 良好            |
# | **典型应用场景**     | 短文本生成 | 机器翻译/语音识别 | 对话系统/股票预测|
# """
markdown_table_to_png(md_content, "math_table.png")