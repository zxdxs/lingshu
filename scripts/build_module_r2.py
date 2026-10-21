#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剩餘篇章彈性拆解（二）：禁服(48) 人迎寸口、五味論(63) 五味所走

輸出：data/模組_R2.json、docs/29_禁服與五味論.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t48, t63 = T(48), T(63)

# ---------- 人迎寸口 ----------
MAI = []
for m in re.finditer(r'人迎大?([一二三四])倍(?:[于於]寸口)?[，]病在((?:足|手)[^；。]+)', t48):
    pre = t48[max(0, m.start() - 24):m.start()]
    if '脈口大' in pre or '寸口大' in pre:
        continue
    MAI.append({'倍': m.group(1), '足經病': m.group(2)})
MAI = list({(m['倍'], m.get('足經病')): m for m in MAI if m.get('足經病')}.values())
for m in re.finditer(r'([一二三四])倍而躁[，]在(手[^。；]+)', t48):
    MAI.append({'倍': m.group(1), '手經病': m.group(2)})

# ---------- 五味所走 ----------
WU = []
for m in re.finditer(r'([酸鹹辛苦甘])走(筋|血|氣|骨|肉)[，]多食之[，]令人([^；。]+)', t63):
    WU.append({'味': m.group(1), '走': m.group(2), '多食之害': m.group(3)})

seen=set(); uniq=[]
for w in WU:
    k=(w['味'],w['走'])
    if k in seen: continue
    seen.add(k); uniq.append(w)
WU=uniq
for w in WU:
    assert sp(w['味']) in sp(t63)

mod = {'模組': '剩餘篇章（二）', '出處': [{'篇序': 48, '篇名': '禁服'}, {'篇序': 63, '篇名': '五味論'}],
       '人迎寸口': MAI, '五味所走': WU}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_R2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '29_禁服與五味論.md'), 'w', encoding='utf-8') as f:
    f.write('# 禁服與五味論\n\n')
    f.write('> 出處：《靈樞》禁服第四十八、五味論第六十三。\n\n---\n\n')
    f.write('## 一、人迎寸口（禁服）\n\n')
    f.write('| 人迎倍數 | 病位 |\n|---|---|\n')
    for m in MAI:
        f.write(f"| {m['倍']}倍 | {m.get('足經病') or m.get('手經病')} |\n")
    f.write('\n> 平人：寸口主中，人迎主外，兩者相應，俱往俱來，若引繩大小齊等；'
            '春夏人迎微大，秋冬寸口微大。\n\n')
    f.write('## 二、五味所走（五味論）\n\n| 味 | 走 | 多食之害 |\n|---|---|---|\n')
    for w in WU:
        f.write(f"| {w['味']} | {w['走']} | {w['多食之害']} |\n")
    f.write('\n> 這一組講的是「五味偏嗜」的具體後果，不是「五味養生」。'
            '原文的語氣是「多食之，令人…」——重點在**過量**。\n')

print('人迎寸口', len(MAI), '｜五味', len(WU))
for m in MAI: print('  ', m)
for w in WU: print('  ', w)
