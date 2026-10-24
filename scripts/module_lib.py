#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D 型模組的共用建置器：原文由句索引按 id 取出，並斷言句屬於該篇。

各批次的內容（SPEC）放在 build_module_d*.py，呼叫 build(SPEC, '檔名.json')。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(SPEC, out_name):
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    ch = {p['序']: p for p in
          json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
    byid = {s['id']: s for s in ju}
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    laws = [(t['n'], t['名'], {q['id'] for q in t['引']}) for g in law['組'] for t in g['條']]

    out = {'模組': SPEC['模組'], '說明': SPEC['說明'], '出處': [], '篇': []}
    for item in SPEC['篇']:
        seq = item['篇序']
        p = ch[seq]
        key = p['篇名_規範']
        ids = {s['id'] for s in ju if s['pian'] == key}
        rows = []
        for layer in item['分層']:
            sid = layer['句']
            assert sid in byid, f'{seq} 句 id 不存在：{sid}'
            assert sid in ids, f'{seq}〈{p["篇名"]}〉不含句 {sid}'
            rows.append({'層': layer['層'], '原文': byid[sid]['text'], '句': sid, '解': layer['解']})
        points = []
        for sid in item['原文要點']:
            assert sid in ids, f'{seq} 原文要點不在本篇：{sid}'
            points.append({'句': sid, '文': byid[sid]['text']})
        related = [{'n': n, '名': nm} for n, nm, qs in laws if qs & ids]
        out['出處'].append({'篇序': seq, '篇名': p['篇名']})
        out['篇'].append({'篇序': seq, '篇名': p['篇名'], '一句': item['一句'],
                          '分層': rows, '原文要點': points, '誤讀': item['誤讀'],
                          '連通則': related})

    path = os.path.join(ROOT, 'data', out_name)
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {path}：{len(out["篇"])} 篇')
    for x in out['篇']:
        print(' ', x['篇序'], x['篇名'], '連通則', [r['n'] for r in x['連通則']])

