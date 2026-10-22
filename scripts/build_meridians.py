#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽出〈經脉〉十二經的六句結構，寫出 data/十二經病候.json。

〈經脉〉每一經都是同一個模板（六句）：
  1 起止（○X之脉，起于…）
  2 是動則病…
  3 是主…所生病者…
  4 氣盛有餘則…／氣虛則…
  5 為此諸病，盛則寫之…
  6 盛者寸口大三倍于人迎…
模板本身就是一種知識：靈樞把「經→路線→動病→所生病→虛實→治法→脉口人迎」寫成固定欄位。
本脚本只做抽取與命名，不改字；文句一律取自句索引。

用法：python3 scripts/build_meridians.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
SEQ = 10  # 〈經脉〉

ADJ = {'太陰': '太陰', '陽明': '陽明', '少陽': '少陽', '太陽': '太陽', '厥陰': '厥陰', '少陰': '少陰'}


def to_name(raw):
    """肺手太陰 → 手太陰肺經；大腸手陽明 → 手陽明大腸經"""
    m = re.match(r'^([\u4e00-\u9fff]{1,3})(手|足)(太陰|陽明|少陽|太陽|厥陰|少陰)$', raw)
    if not m:
        return raw + '經'
    zang, limb, yin = m.groups()
    return f'{limb}{yin}{zang}經'


def main():
    rows = [s for s in JU if s['seq'] == SEQ]
    blocks, cur = [], None
    for s in rows:
        t = s['text']
        m0 = re.match(r'^○?([\u4e00-\u9fff]{1,4})(?:手|足)(?:太陰|陽明|少陽|太陽|厥陰|少陰).{0,4}之脉', t)
        if m0:
            raw = t.lstrip('○').split('之脉')[0]
            cur = {'經': to_name(raw), '原名': raw, '句': []}
            blocks.append(cur)
        if cur is not None:
            cur['句'].append(s)
    def pick(q, kws):
        for s in q:
            if any(k in s['text'] for k in kws):
                return {'id': s['id'], '文': s['text']}
        return None

    out = []
    for b in blocks:
        q = b['句']
        if len(q) < 3:
            continue
        item = {'序': len(out) + 1, '經': b['經'], '原名': b['原名'],
                '起止': {'id': q[0]['id'], '文': q[0]['text']},
                '是動': pick(q, ['是動則病']),
                '所生病': pick(q, ['所生病']),
                '虛實': pick(q, ['氣盛有餘', '氣盛']),
                '治法': pick(q, ['盛則寫之', '虛則補之']),
                '脉口': pick(q, ['人迎'])}
        out.append(item)

    # 機器統計：每經「是動」「所生」各列幾項（以逗號斷）
    for x in out:
        if x['是動']:
            body = x['是動']['文'].split('是動則病', 1)[-1]
            x['動數'] = len([p for p in re.split(r'[，。；]', body) if p.strip()])
        if x['所生病']:
            body = re.split(r'所生病者?', x['所生病']['文'], maxsplit=1)[-1]
            x['生數'] = len([p for p in re.split(r'[，。；]', body) if p.strip()])
    data = {'說明': {'來源': '底本/靈樞經_句索引.json，篇 10〈經脉〉',
                     '模板': '起止／是動／所生病／虛實／治法／脉口人迎，六句一經',
                     '統計': '動數＝「是動則病」句內以逗號分隔的證候數；生數＝「所生病」句同法'},
            '經數': len(out), '經': out}
    p = os.path.join(ROOT, 'data', '十二經病候.json')
    json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('寫出 %s：%d 經；動候 %d、生病 %d' % (p, len(out),
          sum(x.get('動數', 0) for x in out), sum(x.get('生數', 0) for x in out)))


if __name__ == '__main__':
    main()
