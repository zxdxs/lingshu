#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽〈九鍼十二原〉的十二原，寫出 data/十二原.json。

結構：五藏之原各二（左右）＝10，加膏之原一、肓之原一，合為十二。
文句取自句索引；總數不等於 12 即失敗。

用法：python3 scripts/build_yuan.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = {s['id']: s for s in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}

ITEMS = [
 ('1-10-7', '肺', '陽中之少陰'),
 ('1-10-8', '心', '陽中之太陽'),
 ('1-10-9', '肝', '陰中之少陽'),
 ('1-10-10', '脾', '陰中之至陰'),
 ('1-10-11', '腎', '陰中之太陰'),
 ('1-10-12', '膏', '—'),
 ('1-10-13', '肓', '—'),
]
CN = {'一': 1, '二': 2}


def main():
    rows, total, missing = [], 0, []
    for sid, zang, yinyang in ITEMS:
        s = JU.get(sid)
        if not s:
            missing.append(sid); continue
        t = s['text']
        m = re.search(r'([\u4e00-\u9fff]{2,4})，(?:[\u4e00-\u9fff]{2,4})?([一二])。?$', t)
        # 穴名：取「出於X，X二」中的 X
        m2 = re.search(r'出於([\u4e00-\u9fff]{2,4})，([\u4e00-\u9fff]{2,4})([一二])', t)
        dong = m2.group(2) if m2 else (m.group(1) if m else '?')
        num = CN.get(m2.group(3), 0) if m2 else 0
        total += num
        rows.append({'藏': zang, '屬性': yinyang, '原': dong, '數': num, 'id': sid, '文': t})
    if missing:
        raise SystemExit(f'句ID 不存在：{missing}')
    if total != 12:
        raise SystemExit(f'十二原合計應 12，實得 {total}')
    out = {
        '說明': {'來源': '篇 1〈九鍼十二原〉',
                 '算法': '五藏之原各二（左右）＋膏之原一＋肓之原一＝十二',
                 '條數': len(rows), '合計': total},
        '原則': [{'id': i, '文': JU[i]['text']} for i in ('1-10-3', '1-10-4', '1-10-5', '1-10-14') if i in JU],
        '原': rows,
    }
    p = os.path.join(ROOT, 'data', '十二原.json')
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {p}：{len(rows)} 列、合計 {total} 原')


if __name__ == '__main__':
    main()
