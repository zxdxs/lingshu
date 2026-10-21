#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剩餘篇章彈性拆解（三）：邪氣藏府病形(4) 五藏脈變、五變(46) 體質易病

輸出：data/模組_R3.json、docs/30_五藏脈變與五變.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t4, t46 = T(4), T(46)

# ---------- 五藏脈變 ----------
PULSE = []
organs = [(m.group(1), m.start()) for m in re.finditer(r'(肺|肝|脾|腎|心)脉(?:急甚)', t4)]
for i, (org, pos) in enumerate(organs):
    end = organs[i + 1][1] if i + 1 < len(organs) else len(t4)
    seg = t4[pos:end]
    for m in re.finditer(r'(急甚|微急|緩甚|微緩|大甚|微大|小甚|微小|滑甚|微滑|濇甚|微濇)[者]?[為爲]([^；。]+)', seg):
        PULSE.append({'藏': org, '脈': m.group(1), '病': m.group(2)})

# ---------- 五變（體質易病） ----------
BIAN = []
for m in re.finditer(r'([^，。]{2,20}?)者[，]?[^，。]{0,10}?[，]?常為([^；。]+)', t46):
    pass
# 手工：五種體質與易病
BIAN = [
 dict(體質='肉不堅，腠理踈', 易病='風厥'),
 dict(體質='五藏皆柔弱', 易病='消癉'),
 dict(體質='小骨弱肉', 易病='寒熱'),
 dict(體質='粗理而肉不堅', 易病='痹'),
 dict(體質='皮膚薄而不澤，肉不堅而淖澤', 易病='腸中積聚'),
]
for b in BIAN:
    assert sp(b['體質']) in sp(t46), b['體質']

mod = {'模組': '剩餘篇章（三）', '出處': [{'篇序': 4, '篇名': '邪氣藏府病形'}, {'篇序': 46, '篇名': '五變'}],
       '五藏脈變': PULSE, '五變': BIAN}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_R3.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '30_五藏脈變與五變.md'), 'w', encoding='utf-8') as f:
    f.write('# 五藏脈變與五變\n\n')
    f.write('> 出處：《靈樞》邪氣藏府病形第四、五變第四十六。\n\n---\n\n')
    f.write('## 一、五藏脈變（邪氣藏府病形）\n\n')
    f.write('每一藏有十二種脈象變化：急甚／微急、緩甚／微緩、大甚／微大、小甚／微小、滑甚／微滑、濇甚／微濇。\n\n')
    f.write('| 藏 | 脈 | 病 |\n|---|---|---|\n')
    for p in PULSE: f.write(f"| {p['藏']} | {p['脈']} | {p['病'][:40]} |\n")
    f.write('\n> 這一組的教學價值：同一個「急」，甚與微對應的病完全不同。'
            '「甚」是極端、結構性；「微」是偏向、功能性。\n\n')
    f.write('## 二、五變（五變）\n\n| 體質 | 易病 |\n|---|---|\n')
    for b in BIAN: f.write(f"| {b['體質']} | {b['易病']} |\n")
    f.write('\n> 原文以木之堅脆比喻：同一陣風，吹在不同的木上，折的枝不同。'
            '「人之有常病也，亦因其骨節皮膚腠理之不堅固者，邪之所舍也。」\n')

print('五藏脈變', len(PULSE), '｜五變', len(BIAN))
for p in PULSE[:6]: print('  ', p['藏'], p['脈'], '→', p['病'][:26])
