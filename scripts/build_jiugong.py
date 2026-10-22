#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理〈九宫八風〉的九宫、八風、三虛，寫出 data/九宫八風.json。

定位：這是**秦漢式法與曆法的背景知識**，不是待驗證的命題。作者與當時讀者共知，
所以原文只寫宫名與日數，不寫方位；方位依九宫通例補（標『注』，非原文）。
八風的「內舍／外在／氣主」全部照原文，可逐條回查。

用法：python3 scripts/build_jiugong.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = {s['id']: s for s in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句'] if s['seq'] == 77}

# 九宫：名、日數（原文）、方位（依式法通例補，標注）
GONG = [
 ('叶蟄', 46, '北（坎）'), ('天留', 46, '東北（艮）'), ('倉門', 46, '東（震）'),
 ('陰洛', 45, '東南（巽）'), ('天宫', 46, '南（離）'), ('玄委', 46, '西南（坤）'),
 ('倉果', 46, '西（兌）'), ('新洛', 45, '西北（乾）'),
]

# 八風：方位、風名、內舍、外在、氣主、句ID
FENG = [
 ('南', '大弱風', '心', '脉', '熱', '77-7-2'),
 ('西南', '謀風', '脾', '肌', '弱', '77-8-2'),
 ('西', '剛風', '肺', '皮膚', '燥', '77-9-2'),
 ('西北', '折風', '小腸', '手太陽脉（脉絕則溢，脉閉則結不通）', '善暴死', '77-10-2'),
 ('北', '大剛風', '腎', '骨與肩背之膂筋', '寒', '77-11-2'),
 ('東北', '凶風', '大腸', '兩脇腋骨下及肢節', '—', '77-12-2'),
 ('東', '嬰兒風', '肝', '筋紐', '身濕', '77-13-2'),
 ('東南', '弱風', '胃', '肌肉', '體重', '77-14-2'),
]


def main():
    nine = []
    for i, (name, days, dirn) in enumerate(GONG, 1):
        nine.append({'序': i, '宫': name, '日數': days, '方位': dirn})
    feng = []
    for i, (dirn, name, she, wai, qi, sid) in enumerate(FENG, 1):
        s = JU.get(sid)
        if not s:
            raise SystemExit(f'句ID 不存在：{sid}')
        feng.append({'序': i, '方位': dirn, '風': name, '內舍': she, '外在': wai,
                     '氣主': qi, 'id': sid, '文': s['text']})
    data = {
        '說明': {'定位': '秦漢式法與曆法的背景知識；作者與讀者共知，非待驗證命題',
                 '原文': '宫名與日數見 77-1-1；方位依九宫通例補，標『注』',
                 '八風': '內舍／外在／氣主全照原文，可逐條回查'},
        '九宫': nine,
        '八風': feng,
        '太一': {'id': '77-1-1', '文': JU['77-1-1']['text']},
        '移日': {'id': '77-3-1', '文': JU['77-3-1']['text']},
        '三虛': {'id': '77-15-2', '文': JU['77-15-2']['text']},
        '避風': {'id': '77-5-2', '文': JU['77-5-2']['text']},
    }
    p = os.path.join(ROOT, 'data', '九宫八風.json')
    json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {p}：九宫 {len(nine)}、八風 {len(feng)}')


if __name__ == '__main__':
    main()
