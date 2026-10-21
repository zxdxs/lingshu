#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 型收尾：五癃津液別(36)、五閱五使(37)、淫邪發夢(43)、五音五味(65)

輸出：data/模組_C2.json、docs/26_C型收尾.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

# ---------- 五液 ----------
YE = []
for m in re.finditer(r'(天寒衣薄|天熱衣厚|悲哀氣并|中熱胃緩|邪氣內逆)[，]?則為([^。；]+)', T(36)):
    YE.append({'因': m.group(1), '液': m.group(2)})

# ---------- 五官 ----------
GUAN = []
for m in re.finditer(r'(鼻|目|口脣|舌|耳)者[，](肺|肝|脾|心|腎)之官也', T(37)):
    GUAN.append({'官': m.group(1), '藏': m.group(2)})
HOU = []
for m in re.finditer(r'(肺|肝|脾|心|腎)病者[，]([^。；]+)', T(37)):
    HOU.append({'藏': m.group(1), '候': m.group(2)})

# ---------- 十二盛 ----------
SHENG = []
pat = r'(陰氣|陽氣|陰陽|上|下|甚饑|甚飽|肝氣|肺氣|心氣|脾氣|腎氣)(?:俱)?盛[，則]*(?:夢)?([^。；，]+)'
for m in re.finditer(pat, T(43)):
    SHENG.append({'氣': m.group(1), '夢': m.group(2)})

# ---------- 十五不足 ----------
BUZU = []
for m in re.finditer(r'客于([^，。；]+)[，]則夢([^。；]+)', T(43)):
    BUZU.append({'客於': m.group(1), '夢': m.group(2)})

for c in YE:
    assert sp(c['因']) in sp(T(36)), c['因']
for c in GUAN:
    assert sp(c['官']) in sp(T(37)), c['官']
for c in SHENG:
    assert sp(c['氣']) in sp(T(43)), c['氣']

mod = {'模組': 'C 型收尾', '出處': [{'篇序': 36, '篇名': '五癃津液別'},
                              {'篇序': 37, '篇名': '五閱五使'},
                              {'篇序': 43, '篇名': '淫邪發夢'}],
       '五液': YE, '五官': GUAN, '五病候': HOU, '十二盛': SHENG, '十五不足': BUZU}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_C2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '26_C型收尾.md'), 'w', encoding='utf-8') as f:
    f.write('# C 型收尾：津液、五官、夢象\n\n')
    f.write('> 出處：《靈樞》五癃津液別第三十六、五閱五使第三十七、淫邪發夢第四十三。\n\n---\n\n')
    f.write('## 一、津液五別（五癃津液別）\n\n| 因 | 所化 |\n|---|---|\n')
    for c in YE: f.write(f"| {c['因']} | {c['液']} |\n")
    f.write('\n> 津與液之別：三焦出氣，溫肌肉、充皮膚者為**津**；流而不行者為**液**。\n\n')
    f.write('## 二、五官與五病候（五閱五使）\n\n| 官 | 藏 |\n|---|---|\n')
    for c in GUAN: f.write(f"| {c['官']} | {c['藏']} |\n")
    f.write('\n| 藏病 | 候 |\n|---|---|\n')
    for c in HOU: f.write(f"| {c['藏']}病 | {c['候']} |\n")
    f.write('\n## 三、十二盛之夢（淫邪發夢）\n\n| 氣盛 | 夢 |\n|---|---|\n')
    for c in SHENG: f.write(f"| {c['氣']}盛 | {c['夢']} |\n")
    f.write('\n## 四、十五不足之夢（淫邪發夢）\n\n| 邪客 | 夢 |\n|---|---|\n')
    for c in BUZU: f.write(f"| 客於{c['客於']} | {c['夢']} |\n")
    f.write('\n---\n\n## 使用說明\n\n')
    f.write('1. 夢象這一組，當作**古人觀察身心關聯的方式**來讀，不要當成診斷依據。\n')
    f.write('2. 「十二盛者，至而寫之；十五不足者，至而補之」——原書的處理原則是瀉盛補虛。\n')
    f.write('3. 五官與五病候，是望診的經典對應，可與《五色》並讀。\n')

print('五液', len(YE), '｜五官', len(GUAN), '｜病候', len(HOU), '｜十二盛', len(SHENG), '｜十五不足', len(BUZU))
for c in SHENG: print('  ', c['氣'], '→', c['夢'][:22])
