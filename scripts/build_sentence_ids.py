#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立句級 ID：篇序-段-句（例 40-6-1）。

段＝句讀層的一行；句＝行內以 。！？ 切分（；不斷句）。
輸出：底本/靈樞經_句索引.json、export/句索引.csv
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

SPLIT = re.compile(r'(?<=[。！？])')


def main():
    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    ju = {c['序']: c for c in
          json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
    rows = []
    for p in ch:
        seq = p['序']
        txt = ju.get(seq, {}).get('句讀') or p['經文']
        duan = [d.strip() for d in re.split(r'\n+', txt) if d.strip()]
        for dn, d in enumerate(duan, 1):
            parts = [x.strip() for x in SPLIT.split(d) if x.strip()]
            for jn, s in enumerate(parts, 1):
                rows.append({'id': f'{seq}-{dn}-{jn}', 'seq': seq, 'pian': p['篇名_規範'],
                             'duan': dn, 'ju': jn, 'text': s, 'norm': norm(s)})
    out = {'說明': '句級 ID：篇序-段-句。段為句讀層一行，句以。！？切分（；不斷句）。',
           '數': len(rows), '句': rows}
    json.dump(out, open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'export', '句索引.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['句ID', '篇序', '篇名', '段', '句', '原文'])
        for r in rows:
            w.writerow([r['id'], r['seq'], r['pian'], r['duan'], r['ju'], r['text']])
    print(f'句索引 {len(rows)} 句（{len(ch)} 篇）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
