#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""太素經注分離的可行性探針（只出統計，不產站上資料）。

問題：太素錄文沒有任何經／注標記，經文與楊上善注連排。
辦法：太素的經文來自素問、靈樞，所以「能在底本裡找到的字」＝經文候選；
      找不到的連續片段＝注候選。用 n-gram 覆蓋率切段，再用三道檢查驗它可不可信：

  1. 經文段在底本裡的 4-gram 密度（越高越像經文）
  2. 注候選段在底本裡的 4-gram 密度（越低越不像經文）
  3. 回頭用底本篇去對：抽出的經文能覆蓋該篇多少（recall）

用法：python3 scripts/probe_taisu.py [--json]
"""
import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_zhangzhu import norm_map  # noqa: E402

NG = 8          # 錨定用的 n-gram 長度
MIN_RUN = 8     # 連續覆蓋至少這麼長才算經文


def corpus():
    """回傳 {篇/卷名: 正規化字串} 與全部 8-gram 集合。"""
    parts = {}
    sq = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))
    for j in sq['卷']:
        parts['素問卷%d' % j['卷']] = norm_map(j['文本'])[0]
    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    for p in ch:
        parts['靈樞' + p['篇名']] = norm_map(p['正規化'])[0]
    grams = set()
    for t in parts.values():
        for i in range(len(t) - NG + 1):
            grams.add(t[i:i + NG])
    return parts, grams


def taisu_volumes():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3ea031_太素', '*.yaml'))):
        d = yaml.safe_load(open(f, encoding='utf-8'))
        if not d or 'seq' not in d:
            continue
        text = d['body']['text']
        if len(text) < 200:
            continue
        heads = [m.get('head_text') for m in d['body'].get('markers', []) if m.get('head_text')]
        out.append({'卷': d['seq'], 'text': text, 'heads': heads})
    return out


def mark(stream, grams):
    """逐字標記：從該位置起的 8-gram 是否見於底本。"""
    cov = bytearray(len(stream))
    for i in range(len(stream) - NG + 1):
        if stream[i:i + NG] in grams:
            for k in range(NG):
                cov[i + k] = 1
    return cov


def runs(cov):
    """切成 (開始, 結束, 是否覆蓋) 的片段。"""
    out = []
    start = 0
    cur = cov[0]
    for i in range(1, len(cov)):
        if cov[i] != cur:
            out.append((start, i, bool(cur)))
            start, cur = i, cov[i]
    out.append((start, len(cov), bool(cur)))
    return out


def density(s, grams4):
    if len(s) < 4:
        return 0.0
    g = [s[i:i + 4] for i in range(len(s) - 3)]
    return sum(1 for x in g if x in grams4) / len(g)


def validate(rows_and_streams, parts):
    """每一卷：抽出的經文能覆蓋哪幾篇（4-gram recall），對照注候選的覆蓋。

    若某篇 80% 以上的 4-gram 出現在該卷經文段，表示這一篇的經文被抽出來了；
    若同一篇在注候選裡也有大量出現，表示有經文被誤判成注（漏抽）。
    """
    out = []
    for vol, jing, zhu, raw in rows_and_streams:
        gj = {jing[i:i + 4] for i in range(len(jing) - 3)}
        gz = {zhu[i:i + 4] for i in range(len(zhu) - 3)}
        cand = []
        for name, t in parts.items():
            if len(t) < 200:
                continue
            gt = {t[i:i + 4] for i in range(len(t) - 3)}
            if not gt:
                continue
            rj = len(gt & gj) / len(gt)
            rz = len(gt & gz) / len(gt)
            if rj > 0.2:
                cand.append((rj, rz, name, len(gt)))
        cand.sort(reverse=True)
        out.append({'卷': vol, 'top': [{'篇': c[2], '經文recall': round(c[0], 2),
                                        '注recall': round(c[1], 2)} for c in cand[:3]]})
    return out


def main():
    parts, grams = corpus()
    grams4 = set()
    for t in parts.values():
        for i in range(len(t) - 3):
            grams4.add(t[i:i + 4])
    vols = taisu_volumes()
    rows = []
    for v in vols:
        raw = v['text']
        stream, idx = norm_map(raw)
        if not stream:
            continue
        cov = mark(stream, grams)
        segs = runs(cov)
        # 小洞（≤2 字）併回經文：異文造成
        merged = []
        for a, b, c in segs:
            if merged and c and merged[-1][2] and (a - merged[-1][1]) <= 2:
                merged[-1] = (merged[-1][0], b, True)
            else:
                merged.append((a, b, c))
        jing = ''.join(stream[a:b] for a, b, c in merged if c and b - a >= MIN_RUN)
        zhu = ''.join(stream[a:b] for a, b, c in merged if (not c) or b - a < MIN_RUN)
        # 平按：蕭延平校記，另計
        pingan = len(re.findall('平按', raw))
        rows.append({'卷': v['卷'], 'heads': v['heads'][:3],
                     '總字': len(stream), '經文': len(jing), '注候選': len(zhu),
                     '經文占比': round(100.0 * len(jing) / len(stream), 1),
                     '經文密度': round(density(jing, grams4), 2),
                     '注密度': round(density(zhu, grams4), 2),
                     '段數': sum(1 for a, b, c in merged if c and b - a >= MIN_RUN),
                     '平按': pingan})
    if '--json' in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    if '--write' in sys.argv:
        tot = sum(r['總字'] for r in rows)
        j = sum(r['經文'] for r in rows)
        z = tot - j
        summary = {'統計': {'卷': len(rows), '總字': tot, '經文': j, '注候選': z,
                          '經文占比': round(100.0 * j / tot, 1),
                          '經文密度': round(sum(r['經文密度'] * r['經文'] for r in rows) / max(1, j), 2),
                          '注密度': round(sum(r['注密度'] * r['注候選'] for r in rows) / max(1, z), 2),
                          '平按': sum(r['平按'] for r in rows)},
                   '說明': '太素經注分離探針：以底本 n-gram 覆蓋切段，只出統計，未產站上資料',
                   '參數': {'n-gram': NG, '最短經文段': MIN_RUN},
                   '卷': rows}
        out = os.path.join(ROOT, 'data', '太素探針.json')
        json.dump(summary, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('寫出', out, summary['統計'])
        return 0
    print(f"{'卷':>3} {'總字':>6} {'經文':>6} {'注':>6} {'經文%':>6} "
          f"{'經文密度':>7} {'注密度':>6} {'段':>4} {'平按':>4}  首類目")
    for r in rows:
        print(f"{r['卷']:>3} {r['總字']:>6} {r['經文']:>6} {r['注候選']:>6} {r['經文占比']:>6} "
              f"{r['經文密度']:>7} {r['注密度']:>6} {r['段數']:>4} {r['平按']:>4}  " +
              '、'.join(r['heads'] or [])[:24])
    if '--validate' in sys.argv:
        keep = []
        for v in vols:
            stream, _ = norm_map(v['text'])
            if not stream:
                continue
            cov = mark(stream, grams)
            segs = runs(cov)
            merged = []
            for a, b, c in segs:
                if merged and c and merged[-1][2] and (a - merged[-1][1]) <= 2:
                    merged[-1] = (merged[-1][0], b, True)
                else:
                    merged.append((a, b, c))
            jing = ''.join(stream[a:b] for a, b, c in merged if c and b - a >= MIN_RUN)
            zhu = ''.join(stream[a:b] for a, b, c in merged if (not c) or b - a < MIN_RUN)
            keep.append((v['卷'], jing, zhu, v['text']))
        for r in validate(keep, parts):
            print(r['卷'], '｜'.join(f"{t['篇']} 經{t['經文recall']}/注{t['注recall']}" for t in r['top']))
        return 0

    tot = sum(r['總字'] for r in rows)
    j = sum(r['經文'] for r in rows)
    print(f'合計 {tot} 字：經文 {j}（{100.0*j/tot:.1f}%）、注候選 {tot-j}')
    print('全卷平均 經文密度 %.2f、注密度 %.2f' % (
        sum(r['經文密度'] * r['經文'] for r in rows) / max(1, j),
        sum(r['注密度'] * r['注候選'] for r in rows) / max(1, sum(r['注候選'] for r in rows))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
