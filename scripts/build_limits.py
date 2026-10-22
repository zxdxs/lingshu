#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽《靈樞》自述的界限句，分成五級，寫出 data/界限分級.json。

分級（嚴格字面，不用推論）：
  A 死不治　——字面「死不治」或「死不可治」
  B 不治　　——字面「不治」或「不可治」，排除「死不治」與「迷惑而不治」這種非預後用法
  C 不可刺　——「不可刺」「勿刺」「無刺」「勿敢刺」，操作禁忌
  D 可令少愈，不可已 ——只此一條，最細的一級
  E 難已／易已／立已／必已 ——難易判斷（不是「不可」，是「難」）

每一級只照字面收，不代為引申；句ID 可回原文。

用法：python3 scripts/build_limits.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

GRADES = [
 ('A', '死不治', r'死不治|死不可治',
  '斷定死。靈樞最硬的一級。'),
 ('F', '帶時限的預後', r'[一二三四五六七八九十百半千]+(?:日|年|歲)[^。]{0,8}死|旦發夕死|夕發旦死|旦占夕死|夕占旦死',
  '不是「不治」，是「多久」。靈樞常把預後寫成一個時限。'),
 ('B', '不治', r'(?<!死)不可治|(?<!死)不治',
  '說「治不了」，但不說死。排除「迷惑而不治」這類非預後用法。'),
 ('D', '可令少愈，不可已', r'可令少愈|(?<!病)不可已',
  '最細的一級：能緩解，不能除。全書這類寫法極少。'),
 ('C', '不可刺', r'不可刺|勿刺|無刺|勿敢刺',
  '操作禁忌：不是病不可治，是此刻不可動手。'),
 ('E', '難已／易已', r'難已|易已',
  '不是「不可」，是「難／易」——靈樞對療效的第三種說法。'),
]

EXCLUDE = ['迷惑而不治', '未得其術', '非其説']
# 問句不算預後（「七日而死，何也？」是在問為什麼）
QUESTION = ['何也', '何如', '奈何', '何以']


def main():
    out, seen = [], {}
    units = {'日': 0, '年': 0, '歲': 0, '旦夕': 0}
    for code, name, pat, note in GRADES:
        rx = re.compile(pat)
        hits = []
        for s in JU:
            t = s['text']
            if any(x in t for x in EXCLUDE):
                continue
            if code == 'F' and any(x in t for x in QUESTION):
                continue
            if s['id'] in seen:      # 一句只歸一級（先到先得，A→E）
                continue
            if rx.search(t):
                hits.append({'id': s['id'], '篇': s['pian'], 'seq': s['seq'], '文': t})
                seen[s['id']] = code
                if code == 'F':
                    if '旦發夕死' in t or '夕發旦死' in t or '旦占夕死' in t or '夕占旦死' in t:
                        units['旦夕'] += 1
                    else:
                        for u in ('日', '年', '歲'):
                            if u in t:
                                units[u] += 1
                                break
        out.append({'級': code, '名': name, '數': len(hits), '說明': note,
                    '例': hits[:6], '全部': len(hits)})
    total = sum(g['數'] for g in out)
    data = {'說明': {'來源': '底本/靈樞經_句索引.json 全 81 篇',
                     '方法': '字面比對；一句只歸一級，順序 A→B→D→C→E（D 最細，先認）；排除「迷惑而不治」「未得其術」「非其説」',
                     '條數': total},
            '級': out, '時限單位': units}
    p = os.path.join(ROOT, 'data', '界限分級.json')
    json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {p}：' + '、'.join(f'{g["級"]} {g["數"]}' for g in out) + f'（合 {total}）')


if __name__ == '__main__':
    main()
