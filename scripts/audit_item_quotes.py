#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""題面引文稽核：題庫「」內的文字，是否逐字合該篇底本。

三類判定（依可靠度排序，皆可機器重現）：
  1 夾註     括號內容不是原文；去掉括號後若命中，判為夾註
  2 壓縮     該段是底本的「子序列」（字都在、順序對，只是不連續）→ 拼接／節引
  3 真錯     非子序列 → 逐字不符，需修

用法：python3 scripts/audit_item_quotes.py [--csv]
"""
import csv, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

PAREN = re.compile(r'（[^）]*）|\([^)]*\)')


def is_subseq(s, t):
    it = iter(t)
    return all(ch in it for ch in s)


def main():
    base = {p['篇名_規範']: norm(p['正規化'])
            for p in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']

    segs = bad = 0
    rows = []
    for it in items:
        m = re.match(r'《靈樞·([^》]+)》', it['stem'])
        if not m or m.group(1) not in base:
            continue
        name = m.group(1)
        for quote in re.findall(r'「([^」]{2,})」', it['stem']):
            for seg in [x for x in re.split(r'_+', quote) if len(norm(x)) >= 2]:
                segs += 1
                s = norm(seg)
                if s in base[name]:
                    continue
                bad += 1
                bare = norm(PAREN.sub('', seg))
                if bare and bare in base[name]:
                    kind = '夾註（括號非原文）'
                elif is_subseq(s, base[name]):
                    kind = '壓縮／拼接（子序列）'
                else:
                    kind = '真錯（非子序列）'
                rows.append({'item_id': it['item_id'], '篇序': it['source']['篇序'], '篇名': name,
                             '引文段': seg, '類型': kind})
    c = Counter(r['類型'] for r in rows)
    print(f'題數 {len(items)}｜含引文段 {segs}｜不符段 {bad}｜涉及題 {len({r["item_id"] for r in rows})}')
    for k, v in c.most_common():
        print(f'  {v:4d}  {k}')
    print('  真錯篇:', Counter(r['篇名'] for r in rows if r['類型'].startswith('真錯')).most_common())
    if '--csv' in sys.argv:
        out = os.path.join(ROOT, 'data', '題面引文稽核.csv')
        with open(out, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['item_id', '篇序', '篇名', '引文段', '類型'])
            w.writeheader(); w.writerows(rows)
        print('寫出', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
