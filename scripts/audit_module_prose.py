#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稽核模組的說明／譯文欄：① 「」引文是否逐字合底本 ② 有無未加引號的長段原文。

① 違規＝引號內文字在該篇找不到（內容或字形錯）
② 提示＝白話欄裡出現 ≥12 字的連續原文片段而沒加引號（可能漏標，也可能是刻意沿用）

用法：python3 scripts/audit_module_prose.py [--csv]
"""
import glob, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
BASE = {p['篇名_規範']: norm(p['正規化']) for p in CH}
NAMES = list(BASE)
FIELDS = ('說明', '譯文', '白話', '備註', 'note')


def locate(s):
    return [n for n in NAMES if s in BASE[n]]


def walk(node, hints, out):
    if isinstance(node, dict):
        h = node.get('篇名') if node.get('篇名') in BASE else hints
        for k, v in node.items():
            if k in FIELDS and isinstance(v, str):
                out.append((h, v))
            else:
                walk(v, h, out)
    elif isinstance(node, list):
        for x in node:
            walk(x, hints, out)


def longest_base_run(s):
    """回傳 s 中「在底本某篇可找到」的最長連續字串長度。"""
    best = 0
    for i in range(len(s)):
        lo, hi = i + best + 1, len(s)
        # 二分找最長前綴可命中
        while lo <= hi:
            mid = (lo + hi) // 2
            if any(s[i:i + mid] in b for b in BASE.values()):
                best = max(best, mid); lo = mid + 1
            else:
                hi = mid - 1
    return best


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', '模組_*.json'))):
        md = json.load(open(f, encoding='utf-8'))
        out = []
        walk(md, None, out)
        for hint, txt in out:
            for q in re.findall(r'「([^」]{4,})」', txt):
                n = norm(q)
                if hint and hint in BASE:
                    ok = n in BASE[hint]
                else:
                    ok = bool(locate(n))
                if not ok:
                    rows.append({'檔案': os.path.basename(f), '類': '引文不符', '篇': hint or '', '內容': txt[:60]})
            n = norm(txt)
            run = longest_base_run(n)
            if run >= 12:
                rows.append({'檔案': os.path.basename(f), '類': f'未加引號原文 {run} 字', '篇': hint or '', '內容': txt[:60]})
    c = Counter(r['類'].split(' ')[0] for r in rows)
    print('說明／譯文欄檢查：', dict(c) or '無問題')
    for r in rows[:10]:
        print(' ', r['類'], '|', r['檔案'], '|', r['內容'][:44])
    if '--csv' in sys.argv:
        import csv
        p = os.path.join(ROOT, 'data', '模組說明稽核.csv')
        with open(p, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['檔案', '類', '篇', '內容'])
            w.writeheader(); w.writerows(rows)
        print('寫出', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
