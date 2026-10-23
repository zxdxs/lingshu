#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《靈樞識》（日·丹波元簡）條文索引。

此書體例：以經文短句為條目，條目下先引馬蒔（马云）、張介賓（张云）、張志聰（志云）等說，
再下自己的考證（簡案）。它不是逐句串講，而是「按句立條」的考證體。

做法：以「條目＝經文短句」對回底本句索引；條目之後的文字算作注（含轉引諸家）。
只取節錄，轉引他人之處照錄，並標明「轉引」。

輸出：data/靈樞識.json
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_zhangzhu import norm_map  # noqa: E402

CN = {c: i for i, c in enumerate('一二三四五六七八九', 1)}


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十')
        return CN[a] * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s)


def load_paras():
    raw = open(os.path.join(ROOT, 'vendor', '丹波元簡_靈樞識', 'raw.html'),
               encoding='utf-8', errors='replace').read()
    i = raw.find('markdown-content')
    ps = re.findall(r'<p>(.*?)</p>', raw[i:], re.S)
    out = []
    for p in ps:
        t = html.unescape(re.sub('<[^>]+>', '', p))
        t = re.sub(r'[\u3000\xa0\s]+', ' ', t).strip()
        if t and '本栏汇录' not in t:
            out.append(t)
    return out


def parse(paras):
    """切成 {序: [條目文字, …]}；每條以空白分開「經文短句」與「注」。"""
    secs, cur = {}, None
    for p in paras:
        if re.fullmatch(r'卷[一二三四五六七八九十]+', p):
            continue
        m = re.fullmatch(r'(.{2,12}?)(?:篇)?第([一二三四五六七八九十]+)', p)
        if m:
            cur = cn2int(m.group(2))
            secs.setdefault(cur, [])
            continue
        if cur:
            secs[cur].append(p)
    return secs


def main():
    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    name = {p['序']: p['篇名'] for p in ch}
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    byp = {}
    for s in ju:
        byp.setdefault(s['pian'], []).append(s)

    secs = parse(load_paras())
    out = {'說明': '日·丹波元簡《靈樞識》條文索引：以經文短句立條，條下為考證與轉引諸家。'
                   '只取節錄；「马云／张云／志云」為轉引，非本站直引原書。',
           '來源': '殆知閣·醫藏《靈樞識》（日·丹波元簡，2025-10-23 抓取）'
                   ' https://daizhige.org/醫藏/灵枢识.html',
           '統計': {}, '篇': [], '通則': []}

    notes = {}       # (序, 位置) -> 注
    per_pian = {}
    for seq in sorted(name):
        pl = sorted(byp.get(name[seq], []), key=lambda x: x['seq'])
        if not pl:
            continue
        B = []
        pos2id = []
        for s in pl:
            nb = norm_map(s['text'])[0]
            B.append(nb)
            pos2id.extend([s['id']] * len(nb))
        B = ''.join(B)
        items = secs.get(seq, [])
        got = 0
        for para in items:
            parts = para.split(' ')
            if len(parts) < 2:
                continue
            key = None
            p = -1
            # 條目可能由數截短句組成（「营气之道 内谷为宝」），由長到短試
            for k in range(min(3, len(parts) - 1), 0, -1):
                nk = norm_map(''.join(parts[:k]))[0]
                if len(nk) < 2:
                    continue
                q = B.find(nk)
                if q >= 0:
                    key = ' '.join(parts[:k])
                    rest = ' '.join(parts[k:])
                    p = q
                    break
            if p < 0:
                continue
            got += 1
            sid = pos2id[p] if p < len(pos2id) else pos2id[-1]
            notes.setdefault((seq, p), {'句': sid, '注': rest[:200]})
        per_pian[seq] = {'條': len(items), '繫上': got}
        out['篇'].append({'序': seq, '篇': name[seq], '條': len(items), '繫上': got})

    # 通則引文：取引文範圍內的條目注
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    laws = [(g['組'], t) for g in law['組'] for t in g['條']]
    for group, t in laws:
        hit = []
        for q in t['引']:
            seqs = [p['序'] for p in ch if p['篇名'] == q['篇']]
            if not seqs:
                continue
            seq = seqs[0]
            pl = sorted(byp.get(name[seq], []), key=lambda x: x['seq'])
            B = ''.join(norm_map(s['text'])[0] for s in pl)
            nq = norm_map(q['文'])[0]
            p = B.find(nq)
            if p < 0:
                continue
            cand = [(pos, d) for (s0, pos), d in notes.items()
                    if s0 == seq and p - 2 <= pos <= p + len(nq) + 4]
            if cand:
                hit.append({'id': q['id'], '文': q['文'],
                            '注': '…'.join(d['注'] for _pos, d in cand[:2])[:240]})
        if hit:
            out['通則'].append({'n': t['n'], '組': group, '名': t['名'], '引': hit})

    out['統計'] = {'篇': sum(1 for x in out['篇'] if x['繫上']),
                   '條': sum(x['條'] for x in out['篇']),
                   '繫上': sum(x['繫上'] for x in out['篇']),
                   '通則條': len(out['通則']),
                   '通則引': sum(len(t['引']) for t in out['通則'])}
    with open(os.path.join(ROOT, 'data', '靈樞識.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(out['統計'])
    for t in out['通則'][:5]:
        print(t['n'], t['名'], '|', t['引'][0]['注'][:90])


if __name__ == '__main__':
    main()
