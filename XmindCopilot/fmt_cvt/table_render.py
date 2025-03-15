import matplotlib.pyplot as plt
import re
from matplotlib import rcParams
import unicodedata


def markdown_table_to_png(md_table, output_path, font_family='SimHei', figsize=(10, 4), dpi=300):
    """
    改进版Markdown表格转换函数，包含：
    - 不可见字符过滤
    - 中文兼容性增强
    - PNG保存优化
    """
    # 配置中文字体（增加备用字体列表）
    rcParams['font.sans-serif'] = [font_family, 'Microsoft YaHei', 'WenQuanYi Zen Hei'] + rcParams['font.sans-serif']
    rcParams['axes.unicode_minus'] = False

    # # 禁用PNG配置文件警告
    # rcParams['image.png.icc_profile'] = 'none'

    # 解析并清洗数据
    def clean_cell(content):
        """移除不可见字符并标准化Unicode"""
        # 去除零宽度空格（U+200B）和其他控制字符
        cleaned = re.sub(r'[\u200b-\u200d\ufeff]', '', content)
        # 移除其他不可打印字符
        return ''.join(c for c in cleaned if unicodedata.category(c)[0] != 'C')

    rows = []
    for line in md_table.strip().split('\n'):
        line = re.sub(r'^\||\|$', '', line)
        line = re.sub(r'\*{2}(.*?)\*{2}', r'\1', line)
        cells = [clean_cell(cell.strip()) for cell in line.split('|')]

        # 验证有效行（跳过纯分隔符行）
        if any(cell.replace('-', '') for cell in cells):
            rows.append(cells)

    # 验证表格结构
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError("无效的Markdown表格格式")

    # 提取数据
    col_labels = rows[0]
    cell_text = rows[1:]

    # 创建图表
    plt.figure(figsize=figsize)
    ax = plt.gca()
    ax.axis("off")

    # 自动计算列宽
    col_count = len(col_labels)
    col_widths = [0.9/col_count]*col_count  # 动态分配列宽

    # 创建表格
    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colWidths=col_widths
    )

    # 样式设置
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # 表头样式
    for col in range(col_count):
        cell = table[0, col]
        cell.set_facecolor("#F5F5F5")
        cell.set_text_props(weight="bold")

    # 第一列强调
    for row in range(len(cell_text)):
        cell = table[row+1, 0]
        cell.set_text_props(weight="bold")

    # 边框设置
    for key, cell in table.get_celld().items():
        cell.set_edgecolor("lightgray")

    # 保存优化
    plt.tight_layout()
    try:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    except Exception as e:
        raise RuntimeError(f"保存失败，请检查字体配置。错误详情：{str(e)}")
    finally:
        plt.close()


# 使用示例（包含零宽度空格测试）
md_str = """
| 维度\u200b                | RNN       | LSTM             | GRU\u200b             |
|---------------------|-----------|------------------|-----------------|
| ​**门控数量**         | 0         | 3（遗忘/输入/输出） | 2（更新/重置）   |
| ​**参数数量**         | 最少       | 最多（比GRU多33%） | 中等            |
"""

markdown_table_to_png(md_str, "rnn_comparison.png")
