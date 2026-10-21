#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把句級 ID 掛到校勘點（data/校勘點.csv 增『句ID』欄）。

以錨點文字比對該篇的句；找不到再用底本讀法前 12 字。
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm


def main():
    idx = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    by_seq = {}
    for s in idx:
        by_seq.setdefault(s['seq'], []).append(s)
    p = os.path.join(ROOT, 'data', '校勘點.csv')
    rows = list(csv.DictReader(open(p, encoding='utf-8-sig')))
    fields = list(rows[0].keys())
    if '句ID' not in fields:
        fields.append('句ID')
    hit = 0
    for r in rows:
        seq = int(r['篇序'])
        cands = [r.get('錨點', ''), (r.get('底本讀法', '') or '')[:12]]
        found = ''
        for c in cands:
            cn = norm(c)
            if len(cn) < 2:
                continue
            best = None
            for s in by_seq.get(seq, []):
                if cn and cn in s['norm']:
                    if best is None or len(s['norm']) > len(best['norm']):
                        best = s
            if best:
                found = best['id']; break
        r['句ID'] = found
        if found:
            hit += 1
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f'校勘點 {len(rows)} 條，掛上句 ID {hit} 條')
    return 0


if __name__ == '__main__':
    sys.exit(main())
