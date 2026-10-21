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
    con = load('data/矛盾清單.csv'.replace('.csv', '.csv')) if False else list(
        csv.DictReader(open(os.path.join(ROOT, 'data', '矛盾清單.csv'), encoding='utf-8-sig')))

    juan = {}
    for p in ch:
        j = p.get('卷') or ''
        juan.setdefault(j, []).append(p)

    pian = []
    for p in ch:
        seq = p['序']
        pian.append({
            'seq': seq, 'name': p['篇名_規範'], 'juan': p.get('卷', ''),
            'chars': len(p['經文']),
            'text': ju.get(seq, {}).get('句讀', p['經文']),
            'note': p.get('校記', ''),
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
            'case': '-CASE-' in i['item_id'],
        })

    data = {
        'meta': {
            'title': '靈樞自學材料',
            'bendi': '四部叢刊景明嘉靖趙府居敬堂本（Kanripo KR3e0002）',
            'stats': {'pian': len(ch), 'chars': sum(len(p['經文']) for p in ch),
                      'items': items['題數'], 'fill': items['題型分布'].get('fill_blank', 0),
                      'mcq': items['題型分布'].get('mcq', 0),
                      'err': items['題型分布'].get('error_identification', 0),
                      'index': len(idx), 'limits': len(lim), 'contradictions': len(con)},
            'warn': '原文與題目皆經逐字比對；臨床主張未經驗證，不可據以施治。',
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
    }
    os.makedirs(OUT, exist_ok=True)
    js = '/* 由 scripts/build_reader.py 生成，請勿手改。 */\nwindow.LS = ' + \
         json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8').write(js)
    print(f"寫出 reader/assets/data.js：{len(js)/1024:.0f} KB｜篇 {len(pian)}｜題 {len(its)}｜索引 {len(idx)}")


if __name__ == '__main__':
    main()
