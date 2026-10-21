#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""實測校準：把作答記錄變成難度與區辨度。

背景：`docs/33` 的「先驗難度」是設計指標，不是實測。真正的校準需要作答資料。
本腳本建立的是**管線**，不是結果——沒有資料時它不產出任何估計值。

用法：
    python3 scripts/calibrate_empirical.py --responses data/作答記錄.csv

記錄格式（UTF-8 CSV）：
    item_id,learner_id,correct,seconds
    Q-LS002-肺-輸,u001,1,12
    Q-LS002-肺-輸,u002,0,31

輸出：
    p 值（正確率）、高低分組區辨度、異常題標記。
"""
import csv, json, os, sys, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    rows = []
    with open(path, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                rows.append({'item_id': r['item_id'], 'learner': r['learner_id'],
                             'correct': int(r['correct']), 'sec': float(r.get('seconds') or 0)})
            except (KeyError, ValueError):
                continue
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--responses', required=False)
    ap.add_argument('--min-n', type=int, default=20, help='每題最少作答數才計參數')
    a = ap.parse_args()

    if not a.responses or not os.path.exists(a.responses):
        print('尚無作答資料。')
        print('請建立 data/作答記錄.csv，欄位：item_id,learner_id,correct,seconds')
        print('未達每題 --min-n 份作答前，不估計任何難度參數。')
        return

    rows = load(a.responses)
    if not rows:
        print('檔案存在但無有效記錄。')
        return

    by_item = defaultdict(list)
    by_learner = defaultdict(list)
    for r in rows:
        by_item[r['item_id']].append(r)
        by_learner[r['learner']].append(r)

    # 學員總分 → 高低分組（前 27% / 後 27%，經典做法）
    totals = sorted(((sum(x['correct'] for x in v), k) for k, v in by_learner.items()), reverse=True)
    n = len(totals)
    cut = max(1, int(n * 0.27))
    high = {k for _, k in totals[:cut]}
    low = {k for _, k in totals[-cut:]}

    out, thin = [], []
    for iid, rs in sorted(by_item.items()):
        if len(rs) < a.min_n:
            thin.append(iid)
            continue
        p = sum(r['correct'] for r in rs) / len(rs)
        hi = [r['correct'] for r in rs if r['learner'] in high]
        lo = [r['correct'] for r in rs if r['learner'] in low]
        d = (sum(hi) / len(hi) - sum(lo) / len(lo)) if hi and lo else ''
        sec = sorted(r['sec'] for r in rs)
        out.append({'item_id': iid, 'n': len(rs), 'p值': round(p, 3),
                    '區辨度D': round(d, 3) if d != '' else '',
                    '中位用時': round(sec[len(sec) // 2], 1) if sec else ''})

    with open(os.path.join(ROOT, 'data', '題目校準_實測.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['item_id', 'n', 'p值', '區辨度D', '中位用時'])
        w.writeheader()
        w.writerows(out)

    print(f'總作答 {len(rows)} 筆｜學員 {n} 人｜可估參數的題 {len(out)}｜作答不足 {len(thin)}')
    if out:
        hard = [r for r in out if r['p值'] < 0.2]
        easy = [r for r in out if r['p值'] > 0.9]
        bad = [r for r in out if r['區辨度D'] != '' and r['區辨度D'] < 0.1]
        print(f'  偏難(p<0.2): {len(hard)}｜偏易(p>0.9): {len(easy)}｜區辨度<0.1: {len(bad)}')
        print('  區辨度低的題目應優先檢視（可能提示過強、干擾項無效，或內容未教）')


if __name__ == '__main__':
    main()
