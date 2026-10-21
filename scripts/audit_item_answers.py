#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稽核填空題答案：是否為所標篇目的原文字串。

分類：
  原文   答案逐字見於該篇
  異寫   見於同篇的異寫（如太淵／大淵）——由 ALIAS 判定
  合成   由兩段原文併成（去掉逗號後仍見於該篇）
  非原文 其餘

用法：python3 scripts/audit_item_answers.py [--csv]
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
B = {p['序']: norm(p['正規化']) for p in CH}
NAME = {p['序']: p['篇名_規範'] for p in CH}
ALIAS = {'太淵': '大淵', '太衝': '大衝', '太谿': '大谿', '太': '大'}


def classify(seq, ans):
    a = norm(ans)
    if not a:
        return '空白', ''
    if a in B[seq]:
        return '原文', ''
    for k, v in ALIAS.items():
        if k in ans and norm(ans.replace(k, v)) in B[seq]:
            return '異寫', ans.replace(k, v)
    # 合成：答案每個字都在，且去掉連結詞後仍連續
    if a in B[seq].replace('，', ''):
        return '合成', ''
    return '非原文', ''


def main():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    rows = []
    for i in items:
        if i['type'] != 'fill_blank':
            continue
        k, fix = classify(i['source']['篇序'], i['answer'])
        if k != '原文':
            rows.append({'item_id': i['item_id'], '篇': i['source']['篇名'], '類': k,
                         '答案': i['answer'][:40], '建議': fix[:40], '題面': i['stem'][:60]})
    c = Counter(r['類'] for r in rows)
    kinds = Counter(i.get('答案類型') for i in items if i['type'] == 'fill_blank')
    print('填空題', sum(1 for i in items if i['type'] == 'fill_blank'),
          '｜答案類型', dict(kinds))
    print('逐字比對未命中', len(rows), dict(c))
    for r in rows[:12]:
        print(f"  {r['類']} | {r['篇']} | {r['答案']} | {r['題面'][:40]}")
    if '--csv' in sys.argv:
        import csv
        p = os.path.join(ROOT, 'data', '答案稽核.csv')
        with open(p, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['item_id', '篇', '類', '答案', '建議', '題面'])
            w.writeheader(); w.writerows(rows)
        print('寫出', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
