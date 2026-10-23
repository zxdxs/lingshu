#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽《類經》張介賓注：類經把注放在括號內，括號外是經文。
把兩者分開後，注繫到它前面那段經文；再用通則引文去定位，
取引文範圍內（含句末少許）的注，作「類經注」節錄。

輸出：data/類經注.json
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm  # noqa: E402

# 只有書名、篇名、卷次的旁注不算張介賓解
CITE = re.compile(r'^(素問|靈樞|黃帝內經|靈樞經|素問經)')


def parse_juan(path):
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'#\+PROPERTY: JUAN (\d+)', raw)
    if not m:
        return None, '', [], ''
    juan = int(m.group(1))
    # 類名：卷首「類經卷X　明　張介賔　撰」之後那一行（如「藏象類」「運氣」）
    lei = ''
    clean_lines = []
    for ln in raw.split('\n'):
        t = ln.strip().replace('\u3000', '').replace('　', '').replace('¶', '')
        if not t or t.startswith('#') or t.startswith('<pb:'):
            continue
        clean_lines.append(t)
    for i, t in enumerate(clean_lines):
        if re.fullmatch(r'類經卷[一二三四五六七八九十]+.*撰', t) and i + 1 < len(clean_lines):
            lei = clean_lines[i + 1]
            break
    body = re.sub(r'^#.*$', '', raw, flags=re.M)
    body = re.sub(r'<pb:[^>]+>', '', body)
    body = body.replace('¶', '').replace('\u3000', '').replace('\n', '').replace('　', '')
    if lei and lei in body:
        body = body.replace(lei, '', 1)
    jing, notes, cur, start, idx = [], [], None, None, 0
    for ch in body:
        if ch in '(（':
            if cur is None:
                cur, start = [], idx
            else:
                cur.append(ch)
        elif ch in ')）':
            if cur is not None:
                notes.append((start, ''.join(cur)))
                cur = None
        else:
            if cur is not None:
                cur.append(ch)
            else:
                jing.append(ch)
                # 位置以「正規化後」計，才能與 norm(經文) 的 find 對齊
                if norm(ch):
                    idx += 1
    return juan, ''.join(jing), notes, lei


def main():
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    laws = [(g['組'], t) for g in law['組'] for t in g['條']]

    JU = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '*.txt'))):
        juan, jing, notes, lei = parse_juan(f)
        if juan is None:
            continue
        JU[juan] = {'經': norm(jing), '注': notes, 'raw': jing, '類': lei}

    out = {'說明': '明·張介賓《類經》注文節錄：括號內為注，括號外為經文；'
                   '注繫到其前一段經文，再用通則引文定位取注。',
           '來源': 'vendor/KR3e0085_類經（四庫全書本，Kanripo 錄文）',
           '統計': {}, '條': []}
    tot = 0
    for group, t in laws:
        got = []
        for q in t['引']:
            nq = norm(q['文'])
            if len(nq) < 6:
                continue
            for j, d in JU.items():
                p = d['經'].find(nq)
                if p < 0:
                    continue
                # 引文範圍內、或句末 30 字內的注
                # 注繫在它所注的那一句之後：只取引文末尾 ±（-8,+12）字內的注，
                # 寧可少收，也不把隔壁句的注拉過來。
                cand = [(s, x) for s, x in d['注']
                        if p + len(nq) - 8 <= s <= p + len(nq) + 12 and len(x) >= 12
                        and not CITE.match(x) and '○' not in x[:6]]
                if not cand:
                    continue
                txt = '…'.join(x for _s, x in cand[:2])[:240]
                got.append({'id': q['id'], '卷': j, '類': d['類'], '文': q['文'], '注': txt})
                break
        if got:
            tot += len(got)
            out['條'].append({'n': t['n'], '組': group, '名': t['名'], '引': got})
    out['統計'] = {'條': len(out['條']), '段': tot,
                   '卷數': len(JU), '注段總數': sum(len(d['注']) for d in JU.values())}
    with open(os.path.join(ROOT, 'data', '類經注.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(out['統計'])
    for x in out['條'][:6]:
        print(x['n'], x['名'], x['引'][0]['卷'], x['引'][0].get('類', ''), '|', x['引'][0]['注'][:80])


if __name__ == '__main__':
    main()
