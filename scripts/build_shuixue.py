#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽〈經水〉與〈本輸〉五輸，寫出 data/經水.json、data/五輸.json。

〈經水〉：十二經外合十二水，內屬藏府；後段給足六經的刺深與留呼，並立「法天之常」。
〈本輸〉：一經一句，句內以「；」分五段，各段先穴名再說明，末標「爲井／滎／腧／經／合」。

文句取自句索引；抽不到 12 條即失敗。

用法：python3 scripts/build_shuixue.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']


def rows(seq):
    return [s for s in JU if s['seq'] == seq]


def build_jingshui():
    rs = rows(12)
    # 十二經水對應：形如「X外合（于）Y水，內屬…」
    pairs = [s for s in rs if re.match(r'^[手足].{0,4}外合', s['text'])]
    if len(pairs) != 12:
        raise SystemExit(f'經水對應應 12，實得 {len(pairs)}')
    out = []
    for i, s in enumerate(pairs):
        m = re.match(r'^([手足].{0,4}?)外合(?:于)?(.+?水)(?:，|。)', s['text'])
        inner = s['text'].split('內屬', 1)[-1].strip('。').split('，')[0]
        out.append({'序': i + 1, '經': m.group(1), '水': m.group(2),
                    '內屬': inner.replace('于', ''), 'id': s['id'], '文': s['text']})

    # 刺深留呼：足六經一句一經（數字為漢字）
    CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    def cnum(t):
        if t == '十':
            return 10
        if '十' in t:
            a, b = t.split('十')
            return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)
        return CN.get(t, 0)
    depth = []
    for s in rs:
        t = s['text']
        m = re.match(r'^(足(?:太陰|少陰|厥陰|太陽|陽明|少陽)).*?深([一二三四五六七八九十]+)分?[，,、]?留([一二三四五六七八九十]+)呼', t)
        if m:
            depth.append({'經': m.group(1), '深': cnum(m.group(2)), '留': cnum(m.group(3)),
                          'id': s['id'], '文': t})
    hand = next((s for s in rs if '手之陰陽' in s['text'] and '無過二分' in s['text']), None)
    law = next((s for s in rs if '法天之常' in s['text']), None)
    warn = next((s for s in rs if '得惡火' in s['text']), None)
    return {'說明': {'來源': '篇 12〈經水〉', '條數': len(out),
                     '重點': '十二經外合十二水；足六經有具體刺深與留呼，手經一概不超過二分／一呼'},
            '水': out,
            '刺深': {'足': depth,
                     '手': {'id': hand['id'], '文': hand['text']} if hand else None,
                     '法天之常': {'id': law['id'], '文': law['text']} if law else None,
                     '過度之害': {'id': warn['id'], '文': warn['text']} if warn else None}}


def build_wushu():
    rs = rows(2)
    # 五輸句：含「爲井」且句內有「；」分段
    cand = [s for s in rs if '爲井' in s['text'] or '為井' in s['text']]
    out = []
    for s in cand:
        segs = re.split(r'[；;]', s['text'])
        got = {}
        for seg in segs:
            m = re.search(r'(?:出於|出于|溜于|溜於|注于|注於|行于|行於|入于|入於|過于|過於|过于)([^，；。]{2,12})[，,]', seg)
            k = re.search(r'[爲為](井|滎|腧|原|經|合)', seg)
            if m and k:
                xue = m.group(1)
                for sep in ('之前', '之後', '之間', '之外', '之內', '之端'):
                    if sep in xue:
                        xue = xue.split(sep)[-1]
                        break
                got[k.group(1)] = {'穴': xue[-4:], '文': seg}
        if len(got) >= 4:
            name = re.sub(r'^○', '', s['text']).split('出於')[0].split('出于')[0][:6]
            out.append({'序': len(out) + 1, '經': name, 'id': s['id'], '五輸': got})
    # 本輸的次序固定：五藏（肺心肝脾腎）→ 足三陽（膀胱膽胃）→ 三焦、小腸、大腸。
    # 只列十一經：全篇講「五五二十五腧、六六三十六腧」，心主（心包）的五輸不在本篇。
    NAMES = ['手太陰肺經', '手少陰心經', '足厥陰肝經', '足太陰脾經', '足少陰腎經',
             '足太陽膀胱經', '足少陽膽經', '足陽明胃經', '手少陽三焦經',
             '手太陽小腸經', '手陽明大腸經']
    if len(out) != len(NAMES):
        raise SystemExit(f'五輸應 {len(NAMES)} 經，實得 {len(out)}')
    for x, n in zip(out, NAMES):
        x['經'] = n
    return {'說明': {'來源': '篇 2〈本輸〉', '條數': len(out),
                     '重點': '一經一句，句內以「；」分井、滎、腧、經、合；陽經另有「原」穴（過于…爲原）。'
                             '本篇只列十一經（五藏五＋六府六），心主（心包）的五輸不在〈本輸〉。'},
            '輸': out}


def main():
    for name, fn in (('經水', build_jingshui), ('五輸', build_wushu)):
        data = fn()
        p = os.path.join(ROOT, 'data', f'{name}.json')
        json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'寫出 {p}：{data["說明"]["條數"]} 條')


if __name__ == '__main__':
    main()
