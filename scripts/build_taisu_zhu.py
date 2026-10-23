#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""太素經注分離：切平按、清書眉、密度過濾，再把通則引文後的楊注取出來。

方法見 docs/158。四道關：
  1. 8-gram 覆蓋切出經文段／注候選（見 probe_taisu.py）
  2. 注候選在「平按」處切開：平按＝蕭延平校記，不是楊上善注，丟掉
  3. 書眉／卷題／類目（markers 的 head_text）從流中移除
  4. 楊注段 4-gram 密度 >0.15 或長度 <12 者丟棄（太像經文就不要）

輸出：data/太素注.json（全書統計＋通則對讀）
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
from probe_taisu import corpus, mark, runs, MIN_RUN, NG  # noqa: E402

MAXD = 0.15      # 楊注段允許的經文味上限
MINLEN = 12      # 楊注段最短長度
# 經文印記：出現這些詞的段落幾乎不可能是楊注
JINGMARK = ('黃帝曰', '黄帝曰', '岐伯曰', '歧伯曰', '雷公曰', '問曰', '伯高曰', '少師曰', '少俞曰')
# 校記印記：蕭延平或版本校記的用語
JIAOMARK = ('平按', '補入', '原抄', '袁刻', '別本', '謹依', '顧本', '趙府本', '靈樞作', '素問作',
            '甲乙作', '經作', '當作', '疑是', '恐誤', '誤作', '脫', '衍')


def load_vols():
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


def split_pingan(s):
    """把一段注在「平按」處切開，只留平按之前的楊注。"""
    i = s.find('平按')
    return s[:i] if i >= 0 else s


def build(parts, grams, grams4):
    """回傳每卷的（經文流, 楊注清單, 篇界）。

    書眉／類目用 markers 的 offset 定位後「跳過」，不改原文，座標才不會亂。
    """
    vols = []
    for v in load_vols():
        raw = v['text']
        stream, idx = norm_map(raw)
        if not stream:
            continue
        # raw 位置 → norm 位置（供 markers 換算；idx 遞增）
        import bisect
        def r2n(r):
            return bisect.bisect_left(idx, r)
        # 書眉／類目：跳過
        skip = bytearray(len(stream))
        ranges = []
        for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3ea031_太素', '*.yaml'))):
            if not f.endswith(f'{v["卷"]:03d}.yaml'):
                continue
            d = yaml.safe_load(open(f, encoding='utf-8'))
            for m in d['body'].get('markers', []):
                if m.get('head_text'):
                    h = m['head_text']
                    off = m.get('offset', 0)
                    pos = raw.find(h, max(0, off - 5), off + len(h) + 5)
                    if pos < 0:
                        pos = raw.find(h)
                    if pos >= 0:
                        a, b = r2n(pos), r2n(pos + len(h))
                        for k in range(a, b):
                            skip[k] = 1
                if m['type'] == 'tls:div-start' and m.get('level') == 2:
                    ranges.append([r2n(m.get('offset', 0)), None])
                elif m['type'] == 'tls:div-end' and ranges and ranges[-1][1] is None:
                    ranges[-1][1] = r2n(m.get('offset', 0))
        for r in ranges:
            if r[1] is None:
                r[1] = len(stream)

        cov = mark(stream, grams)
        for k in range(len(stream)):
            if skip[k]:
                cov[k] = 0
        segs = runs(cov)
        merged = []
        for a, b, c in segs:
            if merged and c and merged[-1][2] and (a - merged[-1][1]) <= 2:
                merged[-1] = (merged[-1][0], b, True)
            else:
                merged.append((a, b, c))
        jing = [(a, b) for a, b, c in merged if c and b - a >= MIN_RUN]
        notes = []
        for a, b, c in merged:
            if c and b - a >= MIN_RUN:
                continue
            if any(skip[k] for k in range(a, b)):
                continue
            text = raw[idx[a]:idx[b - 1] + 1]
            text = split_pingan(text)
            text = re.sub(r'\s+', '', text)
            if len(text) < MINLEN:
                continue
            den = sum(1 for i in range(len(text) - 3) if text[i:i + 4] in grams4) / max(1, len(text) - 3)
            if den > MAXD:
                continue
            if any(k in text for k in JINGMARK) or any(k in text for k in JIAOMARK):
                continue
            if not any(ch in text for ch in '也者矣焉故即亦乃'):
                continue
            sect = 0
            for si, r in enumerate(ranges):
                if r[0] <= a < r[1]:
                    sect = si
                    break
            notes.append({'pos': a, '文': text[:400], '密度': round(den, 2), '篇': sect})
        vols.append({'卷': v['卷'], 'heads': v['heads'], 'stream': stream,
                     'jing': jing, 'notes': notes, 'ranges': ranges})
    return vols


def main():
    parts, grams = corpus()
    grams4 = set()
    for t in parts.values():
        for i in range(len(t) - 3):
            grams4.add(t[i:i + 4])

    vols = build(parts, grams, grams4)
    note_total = sum(len(v['notes']) for v in vols)
    note_chars = sum(len(n['文']) for v in vols for n in v['notes'])
    jing_chars = sum(b - a for v in vols for a, b in v['jing'])

    note_by_pos = {}
    for v in vols:
        for n in v['notes']:
            note_by_pos[(v['卷'], n['pos'])] = (n['文'], n['篇'])

    # 通則引文 → 太素經文位置 → 其後最近的楊注
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    laws = [(g['組'], t) for g in law['組'] for t in g['條']]
    hits = []
    for group, t in laws:
        rows = []
        for q in t['引']:
            nq = norm_map(q['文'])[0]
            if len(nq) < 6:
                continue
            found = None
            for v in vols:
                p = v['stream'].find(nq)
                if p < 0:
                    continue
                end = p + len(nq)
                # 引文所在的篇（div 範圍）
                sec = 0
                for si, r in enumerate(v['ranges']):
                    if r[0] <= p < r[1]:
                        sec = si
                        break
                pool = [(pos, t) for (j, pos), (t, sx) in note_by_pos.items()
                        if j == v['卷'] and sx == sec]
                near = sorted([x for x in pool if end - 8 <= x[0] <= end + 40])
                cand = near or sorted([x for x in pool if p <= x[0] <= end + 80])
                if cand:
                    found = {'id': q['id'], '卷': v['卷'], '文': q['文'],
                             '注': cand[0][1][:220], '距': cand[0][0] - end}
                    break
            rows.append(found)
        got = []
        seen = set()
        for r in rows:
            if not r or r['注'] in seen:
                continue
            seen.add(r['注'])
            got.append(r)
        if got:
            hits.append({'n': t['n'], '組': group, '名': t['名'], '引': got})

    # ── 逐段索引：每一段注繫到它前面的那句經文（模糊比對，容忍異文）──
    import difflib
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    sq = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))
    jnorm = [(x['id'], norm_map(x['text'])[0]) for x in ju]
    sqnorm = [(j['卷'], norm_map(j['文本'])[0]) for j in sq['卷']]
    name = {p['序']: p['篇名'] for p in
            json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}

    def gram_index(items):
        idx = {}
        for k, (_n, t) in enumerate(items):
            for i in range(len(t) - 3):
                idx.setdefault(t[i:i + 4], set()).add(k)
        return idx

    gj = gram_index(jnorm)
    # 素問用「位置索引」：卷太長，直接算整卷相似度會趨近 0
    sq_idx = {}
    for (juan, t) in sqnorm:
        for i in range(len(t) - 3):
            sq_idx.setdefault(t[i:i + 4], []).append((juan, i))

    def sq_best(tail, thr=0.7):
        pos = set()
        for i in range(len(tail) - 3):
            for c in sq_idx.get(tail[i:i + 4], []):
                pos.add(c)
                if len(pos) > 200:
                    break
            if len(pos) > 200:
                break
        best_r, best_j = 0.0, None
        for juan, i in list(pos)[:200]:
            t = dict(sqnorm)[juan]
            win = t[i:i + len(tail)]
            r = difflib.SequenceMatcher(None, tail, win).ratio()
            if r > best_r:
                best_r, best_j = r, juan
        return best_j, best_r

    def best(tail, items, gidx, thr=0.7):
        cand = set()
        for i in range(len(tail) - 3):
            cand |= gidx.get(tail[i:i + 4], set())
        best_r, best_k = 0.0, None
        for k in list(cand)[:200]:
            r = difflib.SequenceMatcher(None, tail, items[k][1]).ratio()
            if r > best_r:
                best_r, best_k = r, k
        return (items[best_k], best_r) if best_k is not None and best_r >= thr else (None, best_r)

    rows = []
    for v in vols:
        spans = v['jing']
        for n in v['notes']:
            prev = None
            for a, b in spans:
                if b <= n['pos']:
                    prev = (a, b)
                else:
                    break
            target, kind, ratio = '', '', 0.0
            if prev:
                tail = v['stream'][max(prev[0], prev[1] - 40):prev[1]]
                if len(tail) >= 8:
                    hit, r = best(tail, jnorm, gj)
                    if hit:
                        target, kind, ratio = hit[0], '靈樞', round(r, 2)
                    else:
                        j2, r2 = sq_best(tail)
                        if j2 is not None and r2 >= 0.7:
                            target, kind, ratio = '素問卷%d' % j2, '素問', round(r2, 2)
            rows.append({'卷': v['卷'], '類': (v['heads'][0] if v['heads'] else ''),
                         '句': target or '', '屬': kind, '比': ratio,
                         '距': (n['pos'] - prev[1]) if prev else -1,
                         '文': n['文'][:120]})
    idx_stat = {'段': len(rows), '靈樞': sum(1 for r in rows if r['屬'] == '靈樞'),
                '素問': sum(1 for r in rows if r['屬'] == '素問'),
                '未繫': sum(1 for r in rows if not r['屬'])}
    per_pian = {}
    for r in rows:
        if r['屬'] == '靈樞':
            k = r['句'].split('-')[0]
            per_pian[k] = per_pian.get(k, 0) + 1
    idx = {'說明': '太素注段索引：每段注繫到它前面的那句經文（靈樞句 id 或素問卷）。'
                   '比對用 4-gram 取候選＋difflib 相似度 ≥0.7，容忍異文；「距」＝注段起點與該句末的字數。',
           '來源': 'vendor/KR3ea031_太素；句 id 來自 底本/靈樞經_句索引.json',
           '統計': idx_stat,
           '篇': [{'序': int(k), '篇': name.get(int(k), ''), '段': v}
                  for k, v in sorted(per_pian.items()) if k.isdigit()],
           '條': rows}
    json.dump(idx, open(os.path.join(ROOT, 'data', '太素注索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('索引', idx_stat, '篇', len(idx['篇']))

    data = {'說明': '隋·楊上善《太素》注文節錄：以底本 n-gram 切經／注，切平按與書眉，'
                   '密度過濾後取引文後一段。機器分離、未校。',
            '來源': 'vendor/KR3ea031_太素（Kanripo 錄文，缺 5 卷）',
            '方法': '8-gram 覆蓋切段 → 平按切開 → 書眉移除 → 密度 ≤%.2f、長度 ≥%d' % (MAXD, MINLEN),
            '統計': {'卷': len(vols), '經文字': jing_chars, '注段': note_total,
                     '注字': note_chars, '通則條': len(hits),
                     '通則引': sum(len(t['引']) for t in hits)},
            '卷': [{'卷': v['卷'], 'heads': v['heads'][:4], '經文字': sum(b - a for a, b in v['jing']),
                    '注段': len(v['notes']),
                    '注字': sum(len(n['文']) for n in v['notes'])} for v in vols],
            '通則': hits}
    json.dump(data, open(os.path.join(ROOT, 'data', '太素注.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(data['統計'])
    for t in hits[:6]:
        print(t['n'], t['名'], '｜', t['引'][0]['注'][:80])


if __name__ == '__main__':
    main()
