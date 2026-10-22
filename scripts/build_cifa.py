#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽〈官鍼〉五刺與〈五邪〉，寫出 data/五刺.json、data/五邪.json。

五刺：半刺（肺）・豹文刺（心）・關刺（肝）・合谷刺（脾）・輸刺（腎）。
五邪：邪在肺／肝／脾胃／腎／心，各有病候與取法。

文句取自句索引；條數不足即失敗。

用法：python3 scripts/build_cifa.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = {s['id']: s for s in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}


def grab(ids):
    out = []
    for i in ids:
        if i not in JU:
            raise SystemExit(f'句ID 不存在：{i}')
        out.append({'id': i, '文': JU[i]['text']})
    return out


WUCI = [('半刺', '肺'), ('豹文刺', '心'), ('關刺', '肝'), ('合谷刺', '脾'), ('輸刺', '腎')]

WUXIE = [
 ('肺', ['20-1-1'], ['20-1-2'], ''),
 ('肝', ['20-2-1'], ['20-2-2'], ''),
 ('脾胃', ['20-3-1', '20-3-2'], ['20-3-3'],
  '底本此句作「邪左脾胃」，其餘四藏皆作「邪在」；照錄不改。'),
 ('腎', ['20-4-1', '20-4-2'], ['20-4-3'], ''),
 ('心', ['20-5-1'], ['20-5-2'], ''),
]


def main():
    rows = []
    for i, (name, zang) in enumerate(WUCI, 1):
        sid = f'7-6-{i + 1}'
        s = JU.get(sid)
        if not s:
            raise SystemExit(f'句ID 不存在：{sid}')
        rows.append({'序': i, '名': name, '應': zang, 'id': sid, '文': s['text']})
    if len(rows) != 5:
        raise SystemExit('五刺應 5')
    wuci = {'說明': {'來源': '篇 7〈官鍼〉', '條數': 5,
                     '重點': '五刺各應一藏：皮→肺、脉→心、筋→肝、肌→脾、骨→腎'},
            '原則': grab(['7-6-1']), '刺': rows}

    xie = []
    for i, (zang, bing, qu, note) in enumerate(WUXIE, 1):
        item = {'序': i, '藏': zang, '病': grab(bing), '取': grab(qu)}
        if note:
            item['註'] = note
        xie.append(item)
    wuxie = {'說明': {'來源': '篇 20〈五邪〉', '條數': 5,
                      '重點': '邪在五藏：先敘病候，再給取法'},
             '邪': xie}

    for name, data in (('五刺', wuci), ('五邪', wuxie)):
        p = os.path.join(ROOT, 'data', f'{name}.json')
        json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'寫出 {p}：{data["說明"]["條數"]} 條')


if __name__ == '__main__':
    main()
