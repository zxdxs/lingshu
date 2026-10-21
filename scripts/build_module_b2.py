#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B 型補遺：五亂(34)、病傳(42)、水脹(57)

輸出：data/模組_B2.json、docs/27_B型補遺.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t34, t42, t57 = T(34), T(42), T(57)

# ---------- 五亂 ----------
LUAN = []
for m in re.finditer(r'亂于(心|肺|腸胃|臂脛|頭)[，]則([^；。]+)', t34):
    LUAN.append({'亂於': m.group(1), '證': m.group(2)})
ZHI = []
for m in re.finditer(r'氣在[于於](心|肺|腸胃|頭|臂足)[者]?[，]取之([^。]+)', t34):
    ZHI.append({'氣在': m.group(1), '取': m.group(2)})

# ---------- 病傳 ----------
CHUAN = []
for m in re.finditer(r'病先發[于於](心|肺|肝|脾|胃|腎|膀胱)[，]([^。]+?)，死([^。]*)', t42):
    CHUAN.append({'首發': m.group(1), '傳變': m.group(2), '死期': m.group(3)})

# ---------- 水脹 ----------
SHUI = [
 dict(病='水', 候='始起也，目窠上微腫，如新臥起之狀，其頸脉動，時咳，陰股間寒，足脛瘇，腹乃大；以手按其腹，隨手而起，如裹水之狀'),
 dict(病='膚脹', 候='寒氣客于皮膚之間，□□然不堅，腹大，身盡腫，皮厚，按其腹窅而不起，腹色不變'),
 dict(病='鼓脹', 候='腹脹身皆大，大與膚脹等也，色蒼黃，腹筋起'),
 dict(病='腸覃', 候='寒氣客于腸外，與衛氣相摶，瘜肉乃生；始如雞卵，稍以益大，至其成如懷子之狀，按之則堅，推之則移，月事以時下'),
 dict(病='石瘕', 候='生于胞中，寒氣客于子門，子門閉塞，惡血當寫不寫，衃以留止，日以益大，狀如懷子，月事不以時下'),
]

for r in CHUAN:
    assert sp(r['首發']) in sp(t42)
for r in SHUI:
    assert sp(r['病']) in sp(t57), r['病']

mod = {'模組': 'B 型補遺', '出處': [{'篇序': 34, '篇名': '五亂'}, {'篇序': 42, '篇名': '病傳'},
                                 {'篇序': 57, '篇名': '水脹'}],
       '五亂': LUAN, '五亂治法': ZHI, '病傳': CHUAN, '水脹': SHUI}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_B2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '27_B型補遺.md'), 'w', encoding='utf-8') as f:
    f.write('# B 型補遺：五亂、病傳、水脹\n\n')
    f.write('> 出處：《靈樞》五亂第三十四、病傳第四十二、水脹第五十七。\n\n---\n\n')
    f.write('## 一、五亂（五亂）\n\n| 亂於 | 證 | 治法 |\n|---|---|---|\n')
    zmap = {z['氣在']: z['取'] for z in ZHI}
    for r in LUAN:
        key = r['亂於']
        if key == '臂脛': key = '臂足'
        f.write(f"| {r['亂於']} | {r['證']} | {zmap.get(key, '—')} |\n")
    f.write('\n**五亂治法總表**：\n\n| 氣在 | 取 |\n|---|---|\n')
    for z in ZHI: f.write(f"| {z['氣在']} | {z['取']} |\n")
    f.write('\n> 「徐入徐出，謂之導氣；補寫無形，謂之同精」——五亂不是有餘不足，是「亂氣相逆」，'
            '所以治法是導氣，不是補瀉。\n\n')
    f.write('## 二、病傳（病傳）\n\n| 首發 | 傳變 | 死期 |\n|---|---|---|\n')
    for c in CHUAN: f.write(f"| {c['首發']} | {c['傳變']} | {c['死期']} |\n")
    f.write('\n> 「諸病以次相傳，如是者，皆有死期，不可刺也；間一藏及二三四藏者，乃可刺也。」\n\n')
    f.write('## 三、水脹（水脹）\n\n| 病 | 候 |\n|---|---|\n')
    for s in SHUI: f.write(f"| {s['病']} | {s['候']} |\n")

print('五亂', len(LUAN), '｜治法', len(ZHI), '｜病傳', len(CHUAN), '｜水脹', len(SHUI))
for c in CHUAN: print('  ', c['首發'], c['傳變'][:20], c['死期'][:14])
for s in SHUI: print('  ', s['病'])
