import matplotlib.pyplot as plt
import re
import unicodedata
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties


def markdown_table_to_png(md_table, output_path,
                          font_family='SimHei',
                          use_latex=False,
                          figsize=(10, 4),
                          dpi=300):
    """
    增强版表格生成函数

    参数：
    use_latex (bool): 是否启用LaTeX公式支持（需要系统安装LaTeX）
    """
    # 配置中文字体和LaTeX
    rcParams['font.sans-serif'] = [font_family, 'Microsoft YaHei', 'WenQuanYi Zen Hei']
    rcParams['axes.unicode_minus'] = False

    if use_latex:
        rcParams.update({
            "text.usetex": True,
            "font.family": "serif",
            "text.latex.preamble": r"\usepackage{ctex}"
        })

    # 字体度量计算
    font = FontProperties(family=font_family, size=12)
    fig = plt.figure(figsize=figsize)
    renderer = fig.canvas.get_renderer()

    # 表格解析和清洗
    def clean_content(text):
        """清洗不可见字符并保留LaTeX语法"""
        # 移除零宽空格等非常规字符
        cleaned = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
        # 保留可打印字符
        return ''.join(c for c in cleaned if unicodedata.category(c)[0] != 'C')

    def calculate_text_width(text, font_prop):
        """计算文本渲染宽度（近似值）"""
        # 中文字符宽度系数
        cn_width = 1.8 if use_latex else 1.5
        en_width = 1.0

        total = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                total += cn_width
            else:
                total += en_width
        return total * font_prop.get_size() / 10  # 尺寸系数调整

    # 解析表格数据
    rows = []
    for line in md_table.strip().split('\n'):
        line = re.sub(r'^\||\|$', '', line)  # 去除管道符
        cells = [clean_content(cell.strip()) for cell in line.split('|')]
        for i, cell in enumerate(cells):
            if not cell:
                cells.pop(i)

        # 跳过分隔行
        if not all(re.match(r'^[-:\s]+$', cell) for cell in cells):
            rows.append(cells)

    # 验证表格结构
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError("无效的Markdown表格格式")

    # 提取列标题和内容
    col_labels = rows[0]
    cell_text = rows[1:]
    col_count = len(col_labels)

    # 自动计算列宽
    max_widths = [0] * col_count
    for col in range(col_count):
        # 列标题宽度
        header_width = calculate_text_width(col_labels[col], font)
        max_widths[col] = header_width

        # 单元格内容宽度
        for row in cell_text:
            cell_width = calculate_text_width(row[col], font)
            if cell_width > max_widths[col]:
                max_widths[col] = cell_width

    # 归一化列宽
    total_width = sum(max_widths)
    col_widths = [w / total_width * 0.9 for w in max_widths]  # 保留10%边距

    # 创建图表
    ax = fig.add_subplot(111)
    ax.axis("off")

    # 创建表格
    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
        colWidths=col_widths,
        cellColours=None
    )

    # 样式优化
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # 表头样式
    for col in range(col_count):
        cell = table[0, col]
        cell.set_facecolor("#F5F5F5")
        cell.set_text_props(weight="bold", fontproperties=font)

    # 首列强调
    for row_idx in range(len(cell_text)):
        cell = table[row_idx+1, 0]
        cell.set_text_props(weight="bold", fontproperties=font)

    # 边框设置
    for key, cell in table.get_celld().items():
        cell.set_edgecolor("lightgray")

    # 自适应布局
    plt.tight_layout()

    # 保存输出
    try:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight',
                    pad_inches=0.05, metadata={'Creation Software': 'Markdown Table Renderer'})
    except Exception as e:
        if use_latex and "LaTeX" in str(e):
            raise RuntimeError("LaTeX渲染失败，请确认已安装LaTeX环境并包含ctex包")
        raise
    finally:
        plt.close(fig)


if __name__ == "__main__":
    # 使用示例（包含LaTeX）
    md_with_latex = """
    | 指标       | 公式                  | 说明             |
    |------------|-----------------------|------------------|
    | 欧拉公式   | $e^{i\pi} + 1 = 0$    | 最美数学公式     |
    | 质能方程   | $E = mc^2$            | 狭义相对论       |
    | 波函数     | $\Psi(x,t) = \psi(x)e^{-iEt/\hbar}$ | 量子力学描述    |
    """
    markdown_table_to_png(md_with_latex, "latex_table.png", use_latex=False)
