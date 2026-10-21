#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由 data/概念地圖.json 產生 mermaid 區塊，並寫回 docs/64。

用法：
  python3 scripts/make_concept_map.py            # 只印出，不寫檔
  python3 scripts/make_concept_map.py --write    # 寫回 docs/64_概念地圖.md
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', '概念地圖.json')
DOC = os.path.join(ROOT, 'docs', '64_概念地圖.md')


def mermaid(d):
    layers = d['層']
    out = ['```mermaid', 'flowchart TD']
    for i, name in enumerate(layers, 1):
        nodes = [n for n in d['節點'] if n['層'] == name]
        out.append(f'  subgraph L{i}["{name}"]')
        for n in nodes:
            out.append(f'    {n["id"]}["{n["名"]}"]')
        out.append('  end')
    for e in d['連線']:
        arrow = '-.->' if e['證據'] == '歸納' else '-->'
        out.append(f'  {e["a"]} {arrow}|{e["關係"]}| {e["b"]}')
    out.append('```')
    return '\n'.join(out)


def main():
    d = json.load(open(DATA, encoding='utf-8'))
    block = mermaid(d)
    if '--write' not in sys.argv:
        print(block)
        return 0
    text = open(DOC, encoding='utf-8').read()
    new, n = re.subn(r'```mermaid\n.*?\n```', block, text, count=1, flags=re.S)
    if not n:
        print('找不到 mermaid 區塊')
        return 1
    open(DOC, 'w', encoding='utf-8').write(new)
    print(f'已寫回 {DOC}：{len(d["節點"])} 節點、{len(d["連線"])} 連線')
    return 0


if __name__ == '__main__':
    sys.exit(main())
