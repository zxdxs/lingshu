#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句讀層複核：補上「標點轉移」未覆蓋的區段（標點本刪節所致）。

作法：對每個待補區段提供「已加標點版」，腳本剝除標點後必須與底本原字串
逐字相同，才套用。這保證只加標點、不改字。

輸入：data/補標點.json
輸出：底本/靈樞經_句讀層.json（更新，並標記 editorial 區段）
      底本/靈樞經_SBCK_底本_句讀.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '底本')
PUNC = '，。、；：？！「」（）〈〉《》—…·'

def strip_p(s):
    return ''.join(c for c in s if c not in PUNC and not c.isspace())

data = json.load(open(os.path.join(ROOT, 'data', '補標點.json'), encoding='utf-8'))
J = json.load(open(os.path.join(OUT, '靈樞經_句讀層.json'), encoding='utf-8'))

fail = []
applied = 0
for item in data['補標點']:
    n = item['篇序']
    ch = next(r for r in J['篇'] if r['序'] == n)
    src = strip_p(item['標點'])
    if src not in ch['句讀'].replace('\n', ''):
        fail.append((n, ch['篇名'], src[:40]))
        continue
    ch['句讀'] = ch['句讀'].replace('\n', '').replace(src, item['標點'], 1)
    ch.setdefault('編輯標點', []).append(
        {'字數': len(src), '說明': item.get('說明', '')})
    applied += 1

if fail:
    print("!! 未能套用（原字串不符）：")
    for f in fail:
        print("   ", f)
json.dump(J, open(os.path.join(OUT, '靈樞經_句讀層.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, '靈樞經_SBCK_底本_句讀.md'), 'w', encoding='utf-8') as f:
    f.write('# 黃帝素問靈樞經（四部叢刊本）· 句讀層\n\n')
    f.write('> **底本**：四部叢刊本《黃帝素問靈樞經》（SBCK / Kanripo KR3e0002）。\n')
    f.write('> **句讀**：現代標點。大部分自同系統標點本**轉移**；標點本刪節之區段（8 篇）由編者補標，標為 `editorial`。\n')
    f.write('> **性質**：標點屬詮釋層，**未經逐句人工複核**。原文層見 `靈樞經_SBCK_底本.md`。\n\n---\n\n')
    for r in J['篇']:
        f.write(f"## {r['序']}. {r['篇名']}\n\n{r['句讀']}\n\n")

print(f"套用 {applied} 段編輯標點")
