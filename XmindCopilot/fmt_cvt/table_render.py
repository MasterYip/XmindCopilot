import matplotlib.pyplot as plt
import re
import unicodedata
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from ..utils import generate_id
import tempfile
import os

TEMP_DIR = tempfile.gettempdir()


def markdown_table_to_png(md_table, output_path=None,
                          font_family='SimHei',
                          font_size=12,
                          figsize=None,
                          row_height=0.3,
                          dpi=300):
    """
    增强版表格生成函数：
    - 支持**加粗**语法渲染
    - 支持自适应布局
    - 智能列宽计算
    """
    # 配置中文字体
    rcParams['font.sans-serif'] = [font_family, 'Microsoft YaHei', 'WenQuanYi Zen Hei']
    rcParams['axes.unicode_minus'] = False
    rcParams["mathtext.fontset"] = "cm"  # 使用Computer Modern字体

    if output_path is None:
        output_path = os.path.join(TEMP_DIR, generate_id() + ".png")

    # 解析表格数据
    rows = []
    bold_flags = []
    for line in md_table.strip().split('\n'):
        # Reserve empty cell
        line = re.sub(r'\|\|', '| - |', line)
        line = re.sub(r'^\||\|$', '', line)
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]

        # if not cells:
        #    continue

        # 处理加粗语法
        cleaned_cells = []
        bold_row = []
        for cell in cells:
            # 清洗不可见字符
            clean_cell = re.sub(r'[\u200b-\u200d\ufeff]', '', cell)
            clean_cell = ''.join(c for c in clean_cell if unicodedata.category(c)[0] != 'C')

            # 提取加粗标记
            is_bold = False
            if re.search(r'\*\*.*?\*\*', clean_cell):
                is_bold = True
                clean_cell = re.sub(r'\*\*', '', clean_cell)

            cleaned_cells.append(clean_cell)
            bold_row.append(is_bold)
        if any(cell.replace('-', '') for cell in cells):
            rows.append(cleaned_cells)
        bold_flags.append(bold_row)

    # 验证表格结构
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError("无效的Markdown表格格式")

    col_labels = rows[0]
    cell_text = rows[1:]
    col_count = len(col_labels)

    # 自动计算列宽
    font = FontProperties(family=font_family, size=font_size)
    col_widths = self_adaptive_col_width(rows, font)

    # 自适应布局计算
    if figsize is None:
        base_width = sum(col_widths) * 7.0  # 基础宽度系数
        figsize = (
            max(0.1, base_width),  # 最小宽度4英寸
            max(0.1, (len(cell_text)+1)*row_height)  # 最小高度2英寸
        )

    # 创建图表
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.axis("off")

    # 创建表格
    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colWidths=col_widths,
    )

    # 应用加粗样式
    apply_bold_style(table, bold_flags, font_size)

    # 优化样式
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    for key, cell in table.get_celld().items():
        cell.set_edgecolor("lightgray")
        cell.set_height(row_height)  # 设置固定行高（单位：英寸）

    # 紧凑布局
    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    return output_path


def self_adaptive_col_width(rows, font):
    """智能列宽计算算法"""
    # 临时绘图对象
    temp_fig = plt.figure()
    temp_ax = temp_fig.add_subplot(111)
    renderer = temp_fig.canvas.get_renderer()

    # 计算每列最大宽度
    col_count = len(rows[0])
    max_widths = [0] * col_count

    for col_idx in range(col_count):
        for row in rows:
            text_obj = temp_ax.text(0, 0, row[col_idx], fontproperties=font)
            text_obj.draw(renderer)
            bbox = text_obj.get_window_extent(renderer)
            max_widths[col_idx] = max(max_widths[col_idx], bbox.width)

        # 添加10%边距
        max_widths[col_idx] *= 1.2

    # 归一化处理
    total_width = sum(max_widths)
    return [w/total_width for w in max_widths]


def apply_bold_style(table, bold_flags, font_size):
    """应用加粗样式"""
    for (row, col), cell in table.get_celld().items():
        # 表头行加粗
        if row == 0:
            cell.set_facecolor("#F5F5F5")
            cell.set_text_props(weight='bold')
            continue

        # 内容行加粗
        if row-1 < len(bold_flags) and col < len(bold_flags[row-1]):
            if bold_flags[row-1][col]:
                cell.set_text_props(weight='bold')


if __name__ == "__main__":
    # 使用示例
    md_table = """
    | 维度                | RNN       | LSTM             | GRU             |
    |---------------------|-----------|------------------|-----------------|
    | ​**门控数量**         | 0         | 3（遗忘/输入/输出） | 2（更新/重置）   |
    | ​**参数数量**         | 最少       | 最多（比GRU多33%） | 中等            |
    | ​**计算效率**         | 最高       | 最低             | 中等            |
    | ​**长序列表现**       | 差         | 优秀             | 良好            |
    | ​**典型应用场景**     | 短文本生成 $y =a^b + \\frac{1}{2}$ | 机器翻译/语音识别 | 对话系统/股票预测|
    """
    md_table2 = """
    | 函数             | 公式                   | 特性             |
    |------------------|------------------------|------------------|
    | 正弦函数         | $\sin(x) \frac{1}{2}$  | 周期为$2\pi$     |
    | 欧拉公式         | $e^{i\pi} + 1 = 0$| 最美数学公式     |
    """
    
    md_table3 = """
    || 机制 | 作用原理 | 示例场景 |
    |---|-----|---------|---------|
    | 1 | 维度分解 | 每个头处理d_model/num_heads维子空间 | 512维向量用8个头时，每个头处理64维 |
    | 2  | 参数独立性 | 各头的Q/K/V矩阵独立初始化训练 | 即使两个头初始关注时态，训练后可能分化出过去/未来时态处理 |
    | 3 | 线性变换融合 | 最终拼接后的Wo矩阵筛选有效特征 | 重叠头的冗余信息在降维时被过滤 |
    """

    markdown_table_to_png(md_table3, "机制.png", figsize=None)
