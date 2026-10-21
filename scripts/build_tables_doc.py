#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
產出 A 型表格化的學習文件 docs/13_A型表格化.md
資料來源：data/表_*.csv
"""
import json, os, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data')

def read(name):
    p = os.path.join(D, name)
    return list(csv.DictReader(open(p, encoding='utf-8-sig'))) if os.path.exists(p) else []

TABLES = [
    ('表_骨度.csv', '骨度第十四', ['起', '訖', '長'], ['部位（起）', '部位（訖）', '長度']),
    ('表_腸胃.csv', '腸胃第三十一', ['部位', '項目', '數值'], ['部位', '項目', '數值']),
    ('表_脈度.csv', '脈度第十七', ['經脉', '單側長'], ['經脉', '單側長']),
    ('表_五十營.csv', '五十營第十五', ['息數', '氣行', '水下刻'], ['息數', '氣行', '水下刻']),
    ('表_背腧.csv', '背腧第五十一', ['腧穴', '位置'], ['腧穴', '位置']),
    ('表_九鍼.csv', '九鍼（九鍼十二原／九鍼論）', ['序', '鍼', '長', '功能'], ['序', '鍼', '長', '功能']),
]

lines = ['# A 型表格化（定額型篇章）\n',
         '> 由底本自動抽取，每列皆可回溯原文。共 6 篇。\n',
         '> 這一型的特徵：數字密集、句式固定，是最划算的蒸餾對象——抽錯一眼可見，抽對即刻可用。\n']
total = 0
for fn, title, cols, heads in TABLES:
    rows = read(fn)
    total += len(rows)
    lines.append(f'\n## {title}\n')
    lines.append(f'抽取 **{len(rows)}** 列。\n')
    lines.append('| ' + ' | '.join(heads) + ' |')
    lines.append('|' + '---|' * len(heads))
    for r in rows:
        vals = [str(r.get(c, '')).replace('|', '／') for c in cols]
        lines.append('| ' + ' | '.join(vals) + ' |')
    lines.append('')

lines.append(f'\n---\n\n合計 **{total}** 列結構化知識。\n')
lines.append('## 使用建議\n\n')
lines.append('- **骨度**：先背「起訖→寸數」的骨架，再用自己的身體比對（分寸是比例，不是絕對長度）。\n')
lines.append('- **腸胃**：不必硬背，但要記住「胃大一尺五寸、容三斗五升」這類量級感。\n')
lines.append('- **脈度**：記住總數「十六丈二尺」，其餘按六陽／六陰分組記憶。\n')
lines.append('- **五十營**：重點是一晝夜五十周、一萬三千五百息，其餘是推算。\n')
lines.append('- **背腧**：記住「肺三、心五、膈七、肝九、脾十一、腎十四」這串奇數。\n')
lines.append('- **九鍼**：先記形制與長度，再記各針的用途。\n')

open(os.path.join(ROOT, 'docs', '13_A型表格化.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print(f"輸出 docs/13_A型表格化.md（{total} 列）")
