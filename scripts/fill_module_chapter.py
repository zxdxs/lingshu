#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""為模組中「原文」條目補上篇名（只補唯一命中者）。

用法：
  python3 scripts/fill_module_chapter.py          # 只報告
  python3 scripts/fill_module_chapter.py --write  # 寫回
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
BASE = {p['篇名_規範']: norm(p['正規化']) for p in CH}
NAMES = list(BASE)


def locate(s):
    return [n for n in NAMES if s in BASE[n]]


def walk(node, out):
    if isinstance(node, dict):
        raw = node.get('原文')
        if isinstance(raw, str) and len(norm(raw)) >= 6 and '篇名' not in node and '篇序' not in node:
            hits = locate(norm(raw))
            if len(hits) == 1:
                out.append((node, hits[0]))
        for v in node.values():
            walk(v, out)
    elif isinstance(node, list):
        for x in node:
            walk(x, out)


def main():
    write = '--write' in sys.argv
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', '模組_*.json'))):
        md = json.load(open(f, encoding='utf-8'))
        out = []
        walk(md, out)
        if not out:
            continue
        for node, name in out:
            node['篇名'] = name
            total += 1
        if write:
            json.dump(md, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f"{os.path.basename(f):28s} 補 {len(out):2d} 條")
    print(('已寫回' if write else '可補') + f' {total} 條')


if __name__ == '__main__':
    main()
