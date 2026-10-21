#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剩餘篇章彈性拆解（一）：癰疽(81) 名候表、邪客(71) 八虛與半夏湯

輸出：data/模組_R1.json、docs/28_癰疽與邪客.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t81, t71 = T(81), T(71)

# ---------- 癰疽名候 ----------
YONG = []
for m in re.finditer(r'發於([^，。]{1,8})[，]名曰([^，。]{1,4})[。]([^。]+)', t81):
    YONG.append({'部位': m.group(1), '名': m.group(2), '候': m.group(3)})

# ---------- 八虛 ----------
BA = []
for m in re.finditer(r'(肺|心|肝|脾|腎)有邪[，]其氣(留|流)[于於](兩肘|兩腋|兩髀|兩膕)', t71):
    BA.append({'藏': m.group(1), '留': '兩' + m.group(3)[1:], '位': m.group(3)})

# ---------- 不寐與半夏湯 ----------
BU = dict(
  機='衛氣獨衛其外，行於陽，不得入於陰；行於陽則陽氣盛，陽蹻陷，不得入於陰，陰虚，故目不瞑',
  治='補其不足，寫其有餘，調其虚實，以通其道而去其邪',
  方='流水千里以外者八升，揚之萬遍，取其清五升煮之，炊以葦薪，置秫米一升、治半夏五合，徐炊，令竭為一升半，去滓，飲汁一小杯，日三')

for y in YONG:
    assert sp(y['部位']) in sp(t81), y['部位']
for b in BA:
    assert sp(b['藏']) in sp(t71), b['藏']

mod = {'模組': '剩餘篇章（一）', '出處': [{'篇序': 81, '篇名': '癰疽'}, {'篇序': 71, '篇名': '邪客'}],
       '癰疽': YONG, '八虛': BA, '不寐': BU}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_R1.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '28_癰疽與邪客.md'), 'w', encoding='utf-8') as f:
    f.write('# 癰疽與邪客\n\n')
    f.write('> 出處：《靈樞》癰疽第八十一、邪客第七十一。\n\n---\n\n')
    f.write('## 一、癰疽名候（癰疽）\n\n')
    f.write(f'抽取 **{len(YONG)}** 條。\n\n| 部位 | 名 | 候 |\n|---|---|---|\n')
    for y in YONG: f.write(f"| {y['部位']} | {y['名']} | {y['候'][:36]} |\n")
    f.write('\n> 癰與疽之別：癰者「熱勝則肉腐，肉腐則為膿」，皮薄以澤；'
            '疽者「熱氣淳盛，下陷肌膚，筋髓枯」，皮堅如牛領。\n\n')
    f.write('## 二、八虛（邪客）\n\n| 藏 | 邪留 |\n|---|---|\n')
    for b in BA: f.write(f"| {b['藏']} | {b['位']} |\n")
    f.write('\n> 「凡此八虛者，皆機關之室，真氣之所過，血絡之所遊。邪氣惡血，固不得住留；'
            '住留則傷筋絡骨節，機關不得屈伸，故痀攣也。」\n\n')
    f.write('## 三、不寐與半夏秫米湯（邪客）\n\n')
    f.write(f"**病機**：{BU['機']}\n\n**治則**：{BU['治']}\n\n**方**：{BU['方']}\n\n")
    f.write('> 這是《靈樞》極少數的方劑記載，治「目不瞑」。'
            '注意：方中半夏有毒性，須炮製，不可自行服用。\n')

print('癰疽', len(YONG), '｜八虛', len(BA))
for y in YONG[:8]: print('  ', y['部位'], y['名'], '|', y['候'][:24])
for b in BA: print('  ', b['藏'], b['位'])
