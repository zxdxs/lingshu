#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成離線閱讀器資料：reader/assets/data.js（window.LS）。

資料全部取自現有 JSON/CSV，不手寫內容。
用法：python3 scripts/build_reader.py
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'reader', 'assets')


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


def main():
    ch = load('底本/靈樞經_81篇.json')['篇']
    ju = {c['序']: c for c in load('底本/靈樞經_句讀層.json')['篇']}
    items = load('data/題庫_示例.json')
    idx = list(csv.DictReader(open(os.path.join(ROOT, 'export', '索引.csv'), encoding='utf-8-sig')))
    lim = list(csv.DictReader(open(os.path.join(ROOT, 'data', '能力邊界.csv'), encoding='utf-8-sig')))
    con = list(csv.DictReader(open(os.path.join(ROOT, 'data', '矛盾清單.csv'), encoding='utf-8-sig')))
    col = list(csv.DictReader(open(os.path.join(ROOT, 'data', '校勘點.csv'), encoding='utf-8-sig')))
    nd = list(csv.DictReader(open(os.path.join(ROOT, 'data', '表_九鍼.csv'), encoding='utf-8-sig')))
    yin = load('底本/音釋層.json')['音釋']
    cov = load('data/三源覆蓋率.json')['篇']
    sidx = load('底本/靈樞經_句索引.json')['句']
    byseq = {}
    for x in sidx:
        byseq.setdefault(x['seq'], []).append(x)
    themes = load('data/主題.json')['主題']
    for t in themes:
        for qq in t.get('句', []):
            n = __import__('check_quotes').norm(qq['文'])
            hit = ''
            for x in byseq.get(qq['篇'], []):
                if n and (n in x['norm'] or (len(x['norm']) >= 6 and x['norm'] in n)):
                    hit = x['id']; break
            qq['id'] = hit
        t['篇名'] = [next((p['篇名_規範'] for p in ch if p['序'] == s), '') for s in t.get('篇', [])]
        for st in t.get('路線', []):
            n = __import__('check_quotes').norm(st['證'])
            st['id'] = next((x['id'] for x in byseq.get(66, []) if n and (n in x['norm'] or (len(x['norm']) >= 6 and x['norm'] in n))), '')
    import glob as _g
    cpts = []
    for f in sorted(_g.glob(os.path.join(ROOT, 'data', '多層_*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        g = (d.get('組') or [{}])[0]
        cpts.append({'t': d.get('標題', ''), 's': d.get('副標', ''), 'w': g.get('字', ''),
                     'note': g.get('註', ''), 'layers': [{'ctx': L.get('語境', ''), 'txt': L.get('式', ''),
                                                          'src': L.get('出處', '')} for L in g.get('層', [])],
                     'png': '多層_' + g.get('字', '') + '.png'})

    juan = {}
    for p in ch:
        j = p.get('卷') or ''
        juan.setdefault(j, []).append(p)

    from collections import Counter as _C
    per = _C(i['source']['篇序'] for i in items['題'])
    pian = []
    for p in ch:
        seq = p['序']
        pian.append({
            'seq': seq, 'name': p['篇名_規範'], 'juan': p.get('卷', ''),
            'chars': len(p['經文']),
            'text': ju.get(seq, {}).get('句讀', p['經文']),
            'note': p.get('校記', ''),
            'items': per.get(seq, 0),
        })

    its = []
    for i in items['題']:
        its.append({
            'id': i['item_id'], 'seq': i['source']['篇序'], 'pian': i['source']['篇名'],
            'type': i['type'], 'bloom': i['bloom'], 'level': i.get('層級', ''),
            'stem': i['stem'], 'answer': i['answer'],
            'acc': i.get('可接受答案') or [],
            'note': i.get('note', ''), 'kind': i.get('答案類型', ''),
            'dis': i.get('distractors') or [],
            'case': '-CASE-' in i['item_id'], 'sid': i.get('句', ''),
        })

    rel = load('data/發布資訊.json')

    contact = load('data/聯絡.json')

    data = {
        'meta': {
            'title': rel['站名'],
            'release': rel,
            'bendi': '四部叢刊景明嘉靖趙府居敬堂本（Kanripo KR3e0002）',
            'stats': {'pian': len(ch), 'chars': sum(len(p['經文']) for p in ch),
                      'quote_seg': sum(len(__import__('re').findall(r'「([^」]{2,})」', i['stem'])) for i in items['題']),
                      'items': items['題數'], 'fill': items['題型分布'].get('fill_blank', 0),
                      'mcq': items['題型分布'].get('mcq', 0),
                      'err': items['題型分布'].get('error_identification', 0),
                      'index': len(idx), 'limits': len(lim), 'contradictions': len(con),
                      'ans_yuanwen': sum(1 for i in items['題'] if i.get('答案類型') == '原文'),
                      'ans_tuisuan': sum(1 for i in items['題'] if i.get('答案類型') == '推算'),
                      'ans_zhengli': sum(1 for i in items['題'] if i.get('答案類型') == '整理語')},
            'warn': rel['安全提醒短'],
            'safety': rel['安全提醒'],
            'safety_note': '原文與題目皆經逐字比對；校記與限制公開列出。臨床主張未經驗證。',
        },
        'juan': [{'no': k, 'label': ('卷' + str(k)) if k != '' else '卷首', 'n': len(v),
                  'chaps': [{'seq': p['序'], 'name': p['篇名_規範']} for p in v]}
                 for k, v in sorted(juan.items(), key=lambda x: (x[0] == '', str(x[0])))],
        'pian': pian,
        'items': its,
        'index': [{'c': r.get('類', ''), 'n': r.get('名', ''), 'seq': r.get('篇序', ''),
                   'pian': r.get('篇名', ''), 'pos': r.get('位置', '')} for r in idx],
        'limits': [{'id': r.get('編號', ''), 'cat': r.get('範疇', ''), 'issue': r.get('問題', ''),
                    'sev': r.get('嚴重度', ''), 'status': r.get('現狀', '')} for r in lim],
        'contradictions': [{'id': r.get('編號', ''), 'type': r.get('類型', ''), 'point': r.get('爭點', ''),
                            'verdict': r.get('判定', '')} for r in con],
        'collation': [{'id': r.get('編號', ''), 'seq': r.get('篇序', ''), 'pian': r.get('篇名', ''),
                       'anchor': r.get('錨點', ''), 'sid': r.get('句ID', ''),
                       'base': r.get('底本讀法', ''), 'taisu': r.get('太素', '') or '—',
                       'leijing': r.get('類經', '') or '—', 'verdict': r.get('判定', ''),
                       'basis': r.get('依據', ''), 'impact': r.get('影響', '')} for r in col],
        'themes': themes,
        'coverage': [{'seq': r.get('篇序', ''), 'pian': r.get('篇名', ''), 'chars': r.get('字數', 0),
                      't4': r.get('太素K4'), 't12': r.get('太素K12'),
                      'l4': r.get('類經K4'), 'l12': r.get('類經K12'),
                      'verdict': r.get('判讀', '')} for r in cov],
        'needles': [{'no': r.get('序', ''), 'name': r.get('鍼', ''), 'len': r.get('長', ''),
                     'use': r.get('功能', ''), 'src': r.get('原文', '')} for r in nd],
        'yinshi': [{'juan': r.get('卷', ''), 'text': r.get('音釋', '')[:220]} for r in yin],
        'concepts': cpts,
        'contact': contact,
    }
    os.makedirs(OUT, exist_ok=True)
    js = '/* 由 scripts/build_reader.py 生成，請勿手改。 */\nwindow.LS = ' + \
         json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8').write(js)
    print(f"寫出 reader/assets/data.js：{len(js)/1024:.0f} KB｜篇 {len(pian)}｜題 {len(its)}｜索引 {len(idx)}")


if __name__ == '__main__':
    main()
