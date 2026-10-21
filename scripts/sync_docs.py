#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由資料重算 README 的數字，並產生 docs/00_索引.md（全部文件標題）。"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def count_modules():
    mods = set()
    for f in glob.glob(os.path.join(ROOT, 'data', '模組_*.json')):
        d = json.load(open(f, encoding='utf-8'))
        src = d.get('出處')
        if isinstance(src, dict):
            mods.add(src.get('篇序'))
        elif isinstance(src, list):
            mods |= {x.get('篇序') for x in src}
    return len(mods)

def main():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))
    n = items['題數']
    dist = items['題型分布']
    import csv
    nb = len(list(csv.DictReader(open(os.path.join(ROOT, 'data', '能力邊界.csv'), encoding='utf-8-sig'))))
    nm = count_modules()
    docs = sorted(glob.glob(os.path.join(ROOT, 'docs', '*.md')))

    p = os.path.join(ROOT, 'README.md')
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'\| 題目 \| \*\*\d+ 題\*\*（填空 \d+、選擇 \d+、辨誤 \d+） \|',
               f'| 題目 | **{n} 題**（填空 {dist.get("fill_blank",0)}、選擇 {dist.get("mcq",0)}、辨誤 {dist.get("error_identification",0)}） |', s)
    s = re.sub(r'\| 模組 \| \d+ 篇有專屬模組 \|', f'| 模組 | {nm} 篇有專屬模組 |', s)
    s = s.replace('`docs/42_能力邊界與問題標注.md`** — 29 條', f'`docs/42_能力邊界與問題標注.md`** — {nb} 條')
    s = re.sub(r'docs/       \d+ 份說明文件', f'docs/       {len(docs)} 份說明文件', s)
    open(p, 'w', encoding='utf-8').write(s)

    lines = ['# 文件索引', '', f'共 {len(docs)} 份，依編號排列。本檔由 `scripts/sync_docs.py` 產生，勿手改。', '',
             '| # | 標題 |', '|---|---|']
    for f in docs:
        if os.path.basename(f).startswith('00_'):
            continue
        head = ''
        for ln in open(f, encoding='utf-8'):
            if ln.startswith('# '):
                head = ln[2:].strip(); break
        lines.append(f'| {os.path.basename(f).split("_")[0]} | [{head}]({os.path.basename(f)}) |')
    open(os.path.join(ROOT, 'docs', '00_索引.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'README 同步：題數 {n}、模組 {nm} 篇、能力邊界 {nb} 條、文件 {len(docs)} 份')
    return 0

if __name__ == '__main__':
    sys.exit(main())
