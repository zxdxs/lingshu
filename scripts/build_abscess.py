#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽〈癰疽〉的部位、病名與死期，寫出 data/癰疽死期.json。

〈癰疽〉的寫法：發於某處，名曰某疽／某癰；接著給形狀、治法，最後（有時）給死期。
本脚本只抽三樣：部位、病名、死期（含出處句ID），不整理治法。

用法：python3 scripts/build_abscess.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = [s for s in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                encoding='utf-8'))['句'] if s['seq'] == 81]

DEATH = re.compile(r'([一二三四五六七八九十百半]+[餘]?日)[^。]{0,8}死|(死不可治)|(死不治)|([一二三四五六七八九十]+[歲嵗])死')
NAME = re.compile(r'發於([^，。]{1,8})[，]?名曰([^。，]{1,6})')


def main():
    rows, blocks = [], []
    for i, s in enumerate(JU):
        m = NAME.search(s['text'])
        if m:
            blocks.append({'部位': m.group(1), '名': m.group(2), '起': i, '句': [s]})
        elif blocks:
            blocks[-1]['句'].append(s)

    for b in blocks:
        death = None
        for s in b['句']:
            if '發於陽者' in s['text']:      # 通則句，不算某一名癰疽的死期
                continue
            m = DEATH.search(s['text'])
            if m:
                death = {'文': s['text'], 'id': s['id'],
                         '期': m.group(1) or m.group(4) or ('死不可治' if m.group(2) else '死不治')}
                break
        rows.append({'序': len(rows) + 1, '名': b['名'], '部位': b['部位'],
                     '死期': death['期'] if death else None,
                     '死期句': {'id': death['id'], '文': death['文']} if death else None,
                     '段': [{'id': x['id'], '文': x['text']} for x in b['句']]})

    rule = next((s for s in JU if '發於陽者' in s['text']), None)
    data = {'說明': {'來源': '篇 81〈癰疽〉',
                     '條數': len(rows),
                     '說明': '只抽部位、病名、死期；治法與形狀留在原文段裡'},
            '癰疽': rows,
            '通則': {'id': rule['id'], '文': rule['text']} if rule else None}
    p = os.path.join(ROOT, 'data', '癰疽死期.json')
    json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    have = sum(1 for r in rows if r['死期'])
    print(f'寫出 {p}：{len(rows)} 名，其中 {have} 名有明確死期')


if __name__ == '__main__':
    main()
