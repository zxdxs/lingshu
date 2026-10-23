#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《甲乙經》逐條對應：靈樞每一句，找甲乙經最相近的一條，並列出文字差異。

做法：
1. 甲乙經按句末標點切成「條」（5,000 餘條），每條記卷、篇。
2. 靈樞每一句（3,289 句）用 6-gram 倒排索引取候選條，再以 difflib 相似度取最佳。
3. 相似度 ≥0.85 才收；=1.0（併字後完全相同）記「同文」，其餘記「近似」。
4. 差異分兩類：字形／通假（ORTHO 表，編者判定）與其他（照實列出，不判是非）。

輸出：data/甲乙經條.json
"""
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_zhangzhu import norm_map  # noqa: E402

# 字形／通假類差異（編者判定，僅供分類，不代表誰對）
ORTHO = {('府', '腑'), ('腑', '府'), ('大', '太'), ('太', '大'), ('著', '着'), ('着', '著'),
         ('鬲', '膈'), ('膈', '鬲'), ('疏', '踈'), ('踈', '疏'), ('搏', '抟'), ('抟', '搏'),
         ('闷', '悗'), ('悗', '闷'), ('闭', '閇'), ('閇', '闭'), ('浓', '厚'), ('厚', '浓'),
         ('跷', '𫏋'), ('𫏋', '跷'), ('已', '以'), ('以', '已'), ('亦', '也'), ('也', '亦')}

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


def load_tiao():
    lines = [l.strip() for l in open(os.path.join(ROOT, 'vendor', '皇甫謐_甲乙經', 'text.txt'),
                                    encoding='utf-8') if l.strip()]
    start = next(i for i, l in enumerate(lines) if JUAN.fullmatch(l))
    juan, cur, secs = 0, None, []
    for l in lines[start:]:
        m = JUAN.fullmatch(l)
        if m:
            juan = cn2int(m.group(1))
            continue
        m = PIAN.fullmatch(l)
        if m and juan:
            cur = {'卷': juan, '篇': m.group(1) + '第' + m.group(2) + (m.group(3) or ''), '文': []}
            secs.append(cur)
            continue
        if cur is not None:
            cur['文'].append(l)
    tiao = []
    for s in secs:
        for p in re.split(r'(?<=[。！？])', ''.join(s['文'])):
            p = p.strip()
            n = norm_map(p)[0]
            if len(n) >= 8:
                tiao.append({'卷': s['卷'], '篇': s['篇'], '文': p, 'norm': n})
    return tiao


def diffs_of(a, b, cap=6):
    """回傳（用字差段數, 其他差異清單），只列片段，不判是非。"""
    sm = difflib.SequenceMatcher(None, a, b)
    ortho = 0
    other = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        x, y = a[i1:i2], b[j1:j2]
        if (x, y) in ORTHO or (len(x) == 1 and len(y) == 1 and (x, y) in ORTHO):
            ortho += 1
            continue
        if len(other) < cap:
            other.append({'甲': x[:16], '乙': y[:16]})
    return ortho, other


def main():
    data_note = '《甲乙經》逐條對應（引用句子集）：靈樞句 → 甲乙經條（相似度 ≥0.85）；差異照列，不判是非。'
    tiao = load_tiao()
    idx = {}
    for k, t in enumerate(tiao):
        n = t['norm']
        for i in range(len(n) - 5):
            idx.setdefault(n[i:i + 6], []).append(k)
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

    rows = []
    stat = {'句': len(ju), '可比': 0, '同文': 0, '近似': 0, '用字差段': 0}
    for s in ju:
        n = norm_map(s['text'])[0]
        if len(n) < 10:
            continue
        stat['可比'] += 1
        cands = set()
        for i in range(len(n) - 5):
            for k in idx.get(n[i:i + 6], []):
                cands.add(k)
                if len(cands) > 150:
                    break
            if len(cands) > 150:
                break
        best = (0.0, None)
        for k in list(cands)[:150]:
            r = difflib.SequenceMatcher(None, n, tiao[k]['norm']).ratio()
            if r > best[0]:
                best = (r, k)
        if best[1] is None or best[0] < 0.85:
            continue
        t = tiao[best[1]]
        ortho, other = diffs_of(n, t['norm'])
        same = t['norm'] == n
        rec = {'id': s['id'], '篇': s['pian'], '卷': t['卷'], '甲乙篇': t['篇'],
               '比': round(best[0], 3), '同文': same, '甲': s['text'], '乙': t['文'],
               '用字差': ortho, '異': other}
        rows.append(rec)
        stat['同文' if same else '近似'] += 1
        stat['用字差段'] += ortho

    # 引用句子集：通則、變體、病候、癰疽、界限、十二經病候 引到的句
    cited = set()

    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k in ('id', '句') and isinstance(v, str) and '-' in v:
                    cited.add(v)
                else:
                    walk(v)
        elif isinstance(n, list):
            for x in n:
                walk(x)

    for f in ('通則.json', '變體.json', '病候.json', '癰疽死期.json', '界限分級.json', '十二經病候.json'):
        path = os.path.join(ROOT, 'data', f)
        if os.path.exists(path):
            walk(json.load(open(path, encoding='utf-8')))
    sub = [r for r in rows if r['id'] in cited]
    slim = {'說明': data_note, '統計': {'引用句': len(cited), '有對應': len(sub),
                                     '總對上': len(rows), '同文': stat['同文'], '近似': stat['近似']},
            '條': sub}
    with open(os.path.join(ROOT, 'data', '甲乙經條_引用.json'), 'w', encoding='utf-8') as f2:
        json.dump(slim, f2, ensure_ascii=False, indent=1)
    print('引用句', len(cited), '有對應', len(sub))

    data = {'說明': '《甲乙經》逐條對應：靈樞句 → 甲乙經條（相似度 ≥0.85）；差異照列，不判是非。',
            '來源': 'vendor/皇甫謐_甲乙經（殆知閣，2025-10-23）；比對用繁簡＋異體併字',
            '方法': '6-gram 倒排取候選 → difflib 相似度取最佳；字形／通假差異另計（編者判定）',
            '統計': stat, '條': rows}
    with open(os.path.join(ROOT, 'data', '甲乙經條.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(stat)
    for r in rows[:5]:
        print(r['id'], r['比'], r['同文'], '|', r['異'][:2])
    print('近似最多差異:', sorted(rows, key=lambda r: -len(r['異']))[:3])


if __name__ == '__main__':
    main()
