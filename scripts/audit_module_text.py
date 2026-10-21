#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稽核 data/模組_*.json 裡所有「原文」欄，是否逐字見於所標篇目。

判準（不依賴模組結構，避免猜錯）：
  1 若該條有明確篇名（自身或最近上層，或模組出處只有一篇）→ 必須見於該篇
  2 否則 → 必須至少見於 81 篇之一；並記錄實際落在哪篇
  3 不見於任何篇 → 標「不在底本」（多為誤收他書，例如歲露論那條出素問）

用法：python3 scripts/audit_module_text.py [--csv]
"""
import glob, json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
BASE = {p['篇名_規範']: norm(p['正規化']) for p in CH}
NAMES = [p['篇名_規範'] for p in CH]
KEYS = ('原文', '原文要點')


def locate(s):
    return [n for n in NAMES if s in BASE[n]]


def walk(node, hint, out, path):
    if isinstance(node, dict):
        h = node.get('篇名') if node.get('篇名') in BASE else None
        if h is None and node.get('篇序'):
            for p in CH:
                if p['序'] == node['篇序']:
                    h = p['篇名_規範']; break
        h = h or hint
        for k, v in node.items():
            if k in KEYS and isinstance(v, str):
                s = norm(v)
                if len(s) >= 6:
                    out.append({'path': '/'.join(path + [k]), 'hint': h, 'text': v[:50], 'norm': s})
            else:
                walk(v, h, out, path + [k])
    elif isinstance(node, list):
        for i, x in enumerate(node):
            walk(x, hint, out, path + [str(i)])


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', '模組_*.json'))):
        md = json.load(open(f, encoding='utf-8'))
        out = []
        src = md.get('出處')
        hint = src.get('篇名') if isinstance(src, dict) and src.get('篇名') in BASE else None
        if hint is None and isinstance(src, list) and len(src) == 1 and src[0].get('篇名') in BASE:
            hint = src[0]['篇名']
        walk({k: v for k, v in md.items() if k != '出處'}, hint, out, [])
        for r in out:
            hits = locate(r['norm'])
            if r['hint']:
                status = 'OK' if r['hint'] in hits else ('錯置' if hits else '不在底本')
            else:
                status = 'OK（篇未標）' if hits else '不在底本'
            rows.append({'檔案': os.path.basename(f), '路徑': r['path'], '標注篇': r['hint'] or '',
                         '實際見於': '、'.join(hits[:2]), '狀態': status, '原文': r['text']})
    c = Counter(r['狀態'] for r in rows)
    print('模組原文條目', len(rows), dict(c))
    for k in ('不在底本', '錯置'):
        for r in [x for x in rows if x['狀態'] == k][:8]:
            print(f"  {k}: {r['檔案']} | 標注 {r['標注篇']} | 實際 {r['實際見於']} | {r['原文'][:36]}")
    if '--csv' in sys.argv:
        import csv
        p = os.path.join(ROOT, 'data', '模組原文稽核.csv')
        with open(p, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['檔案', '路徑', '標注篇', '實際見於', '狀態', '原文'])
            w.writeheader(); w.writerows(rows)
        print('寫出', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
