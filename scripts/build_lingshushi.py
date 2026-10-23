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


MARK = re.compile(r'(马云|张云|志云|简案|甲乙|千金|外台|巢源|病源|杨上善|张本|志本|马本)')
LABEL = {'马云': '馬蒔（轉引）', '张云': '張介賓（轉引）', '志云': '張志聰（轉引）',
         '简案': '丹波元簡', '甲乙': '甲乙經', '千金': '千金方', '外台': '外台秘要',
         '巢源': '巢氏病源', '病源': '巢氏病源', '杨上善': '楊上善（轉引）',
         '张本': '版本校', '志本': '版本校', '马本': '版本校'}


def split_note(text):
    """把一條注按「马云／张云／志云／简案」等標記切段並署名。"""
    out = []
    pos = 0
    for m in MARK.finditer(text):
        if m.start() > pos:
            seg = text[pos:m.start()]
            out.append({'家': out[-1]['家'] if out and not out[-1]['文'] else '未署名', '文': seg})
        out.append({'家': LABEL[m.group(1)], '文': ''})
        pos = m.start()
    if pos < len(text):
        seg = text[pos:]
        if out and not out[-1]['文']:
            out[-1]['文'] = seg
        else:
            out.append({'家': '未署名', '文': seg})
    return [x for x in out if x['文']]


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
    loose = []       # 未繫上句的馬蒔轉引（只記篇）
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
                # 條目對不上底本句，仍可知道它在哪一篇：把引馬蒔處輯下來，句 id 留空
                if len(parts) >= 2:
                    rest0 = ' '.join(parts[1:])
                    for sg0 in split_note(rest0):
                        if sg0['家'] == '馬蒔（轉引）':
                            loose.append({'篇': name[seq], '句': '', '文': sg0['文'][:220]})
                continue
            got += 1
            sid = pos2id[p] if p < len(pos2id) else pos2id[-1]
            notes.setdefault((seq, p), {'句': sid, '注': rest[:400], '序': seq,
                                        'seg': split_note(rest[:400])})
        per_pian[seq] = {'條': len(items), '繫上': got}
        out['篇'].append({'序': seq, '篇': name[seq], '條': len(items), '繫上': got,
                          '家別': {}})

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
                note = '…'.join(d['注'] for _pos, d in cand[:2])[:240]
                hit.append({'id': q['id'], '文': q['文'], '注': note,
                            'seg': split_note(note)})
        if hit:
            out['通則'].append({'n': t['n'], '組': group, '名': t['名'], '引': hit})

    fam = {}
    ma = []
    fam_of = {x['序']: x for x in out['篇']}
    for (seq, pos), d in notes.items():
        for sg in d.get('seg', []):
            fam[sg['家']] = fam.get(sg['家'], 0) + 1
            if seq in fam_of:
                b = fam_of[seq]['家別']
                b[sg['家']] = b.get(sg['家'], 0) + 1
            if sg['家'] == '馬蒔（轉引）':
                ma.append({'篇': name[seq], '句': d['句'], '文': sg['文'][:220]})
    for t in out['通則']:
        for q in t['引']:
            for sg in q['seg']:
                if sg['家'] not in fam:
                    fam[sg['家']] = 1
    def _body(x):
        return re.sub(r'^(马云|张云|志云|简案|甲乙)[。、，\s]*', '', x)

    out['馬蒔'] = [x for x in ma + loose if len(_body(x['文'])) >= 6]
    out['統計'] = {'篇': sum(1 for x in out['篇'] if x['繫上']),
                   '家別': fam,
                   '條': sum(x['條'] for x in out['篇']),
                   '繫上': sum(x['繫上'] for x in out['篇']),
                   '通則條': len(out['通則']),
                   '通則引': sum(len(t['引']) for t in out['通則']),
                   '馬蒔總': len(out['馬蒔']), '馬蒔未繫上': len(loose)}
    with open(os.path.join(ROOT, 'data', '靈樞識.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ma_data = {'說明': '《靈樞識》所引馬蒔說輯存（轉引，非馬蒔原書）。馬蒔《靈樞注證發微》未入庫，'
                       '此處文字經丹波元簡轉手，可能節刪，引用時須標明轉引。',
               '來源': 'vendor/丹波元簡_靈樞識（殆知閣）',
               '數': len(out['馬蒔']), '條': out['馬蒔']}
    with open(os.path.join(ROOT, 'data', '馬蒔轉引.json'), 'w', encoding='utf-8') as f:
        json.dump(ma_data, f, ensure_ascii=False, indent=1)
    import csv
    os.makedirs(os.path.join(ROOT, 'export'), exist_ok=True)
    with open(os.path.join(ROOT, 'export', '馬蒔轉引_靈樞識.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['篇', '句ID', '馬蒔說（靈樞識轉引）'])
        for x in out['馬蒔']:
            w.writerow([x['篇'], x['句'], x['文']])
    print('馬蒔轉引', len(ma) + len(loose), '→ data/馬蒔轉引.json、export/馬蒔轉引_靈樞識.csv')
    print(out['統計'])
    for t in out['通則'][:5]:
        print(t['n'], t['名'], '|', t['引'][0]['注'][:90])


if __name__ == '__main__':
    main()
