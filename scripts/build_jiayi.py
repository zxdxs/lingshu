#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《針灸甲乙經》（晉·皇甫謐）與靈樞的篇次對照。

甲乙經把靈樞、素問的條文按病類重編，是現存最早的同類編本。
這一支腳只做兩件事：
1. 靈樞 81 篇的正文，落在甲乙經哪一卷哪一篇（以 4-gram 重合率判定）。
2. 通則引文在甲乙經的落點（供三源／四源對讀）。

不做經注分離（甲乙經本文含後人夾注，未分），也不逐字校勘。

輸出：data/甲乙經.json
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm  # noqa: E402
from build_zhangzhu import norm_map  # noqa: E402

def norm2(s):
    """繁簡＋異體併字：甲乙經是簡體排印，底本是繁體，必須先併再比。"""
    return norm_map(s)[0]

CN = {c: i for i, c in enumerate('一二三四五六七八九', 1)}
JUAN = re.compile(r'^卷([一二三四五六七八九十]+)$')
PIAN = re.compile(r'^(.{2,30})第([一二三四五六七八九十]+)(（[上下]）)?$')


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十')
        return CN[a] * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s)


def load():
    lines = [l.strip() for l in open(os.path.join(ROOT, 'vendor', '皇甫謐_甲乙經', 'text.txt'),
                                    encoding='utf-8') if l.strip()]
    juan = 0
    cur = None
    out = []
    # 只看正文：序與序例之後，第一個「卷N」
    start = 0
    for i, l in enumerate(lines):
        if JUAN.fullmatch(l):
            start = i
            break
    for l in lines[start:]:
        m = JUAN.fullmatch(l)
        if m:
            juan = cn2int(m.group(1))
            continue
        m = PIAN.fullmatch(l)
        if m and juan:
            cur = {'卷': juan, '篇': m.group(1) + '第' + m.group(2) + (m.group(3) or ''), '文': []}
            out.append(cur)
            continue
        if cur is not None:
            cur['文'].append(l)
    for x in out:
        x['text'] = ''.join(x['文'])
        x['norm'] = norm2(x['text'])
        del x['文']
    return out


def grams(s, n=4):
    return [s[i:i + n] for i in range(len(s) - n + 1)]


def main():
    pian = load()
    print('甲乙經 篇', len(pian), '卷', len({x['卷'] for x in pian}))
    # 4-gram 索引：gram → 篇 index set（只留出現在少數篇的，避免爆）
    idx = {}
    for k, x in enumerate(pian):
        for g in set(grams(x['norm'])):
            idx.setdefault(g, []).append(k)

    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    rows = []
    for p in ch:
        gs = set(grams(norm2(p['正規化'])))
        cnt = Counter()
        for g in gs:
            for k in idx.get(g, []):
                cnt[k] += 1
        if not cnt:
            rows.append({'序': p['序'], '篇': p['篇名'], '落點': [], '主': None, '重合': 0})
            continue
        top = cnt.most_common(3)
        locs = [{'卷': pian[k]['卷'], '篇': pian[k]['篇'],
                 '重合': round(100.0 * c / max(1, len(gs)), 1)} for k, c in top]
        rows.append({'序': p['序'], '篇': p['篇名'], '落點': locs, '主': locs[0], '重合': locs[0]['重合']})

    # 通則引文落點
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    laws = [(g['組'], t) for g in law['組'] for t in g['條']]
    out_law = []
    seg = [(k, x['norm']) for k, x in enumerate(pian)]
    for group, t in laws:
        got = []
        for q in t['引']:
            nq = norm2(q['文'])
            if len(nq) < 6:
                continue
            for k, s in seg:
                if nq in s:
                    got.append({'id': q['id'], '卷': pian[k]['卷'], '篇': pian[k]['篇']})
                    break
        if got:
            out_law.append({'n': t['n'], '組': group, '名': t['名'], '引': got})

    data = {'說明': '《針灸甲乙經》篇次對照：靈樞 81 篇落在甲乙經哪一卷哪一篇（4-gram 重合率），'
                   '以及通則引文在甲乙經的落點。',
            '來源': '殆知閣·醫藏《針灸甲乙經》（晉·皇甫謐，明刊本系統，2025-10-23 抓取）'
                    ' https://daizhige.org/醫藏/针灸甲乙经.html',
            '統計': {'靈樞篇': len(rows),
                     '有落點': sum(1 for r in rows if r['主']),
                     '重合≥30%': sum(1 for r in rows if r['重合'] >= 30),
                     '甲乙篇': len(pian), '甲乙卷': len({x['卷'] for x in pian}),
                     '通則條有落點': len(out_law),
                     '通則引有落點': sum(len(t['引']) for t in out_law)},
            '篇': rows, '通則': out_law}
    with open(os.path.join(ROOT, 'data', '甲乙經.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(data['統計'])
    for r in rows[:8]:
        print(r['序'], r['篇'], '→', r['主'], r['重合'])
    print('低重合篇', [(r['序'], r['篇'], r['重合']) for r in rows if r['重合'] < 10])


if __name__ == '__main__':
    main()
