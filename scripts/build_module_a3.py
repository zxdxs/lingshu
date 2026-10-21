#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A/E 最後一批：五禁(61)、經水(12)、衛氣標本(52)、營氣(16)、平人絕穀(32)、九宮八風(77)、歲露(79)

輸出：data/模組_A3.json、docs/24_A型第三批_與時間補遺.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t61, t12, t52, t16, t32, t77, t79 = map(T, (61, 12, 52, 16, 32, 77, 79))

# ---------- 五禁 ----------
WJ = []
for m in re.finditer(r'(甲乙|丙丁|戊[巳己]|庚辛|壬癸)日自[乗乘][^，。]*[，]無([^。]+)', t61):
    WJ.append({'日干': m.group(1), '禁': m.group(2).strip('。')})
WD = []
for m in re.finditer(r'([^，。；？！：]{2,14})[，]是([一二三四五])奪也', t61):
    WD.append({'序': m.group(2), '奪': m.group(1)})
WN = []
for m in re.finditer(r'([^。；？！：]{4,40})[，]是([一二三四五])逆也', t61):
    WN.append({'序': m.group(2), '逆': m.group(1)})

# ---------- 經水 ----------
JS = []
for m in re.finditer(r'(足太陽|足少陽|足陽明|足太陰|足少陰|足厥陰|手太陽|手少陽|手陽明|手太陰|手少陰|手心主)外合([^，。]+)[，]內屬([^，。]+)', t12):
    JS.append({'經': m.group(1), '經水': m.group(2), '屬': m.group(3)})

# ---------- 衛氣標本 ----------
BB = []
for m in re.finditer(r'(足太陽|足少陽|足少陰|足厥陰|足陽明|足太陰|手太陽|手少陽|手陽明|手太陰|手少陰|手心主)之本[，]在([^，。]+)[，]標在([^，。]+)', t52):
    BB.append({'經': m.group(1), '本': m.group(2), '標': m.group(3)})

# ---------- 營氣行次 ----------
YQ = []
for m in re.finditer(r'(注|合|循|出|入|上行|下行|従|從)(手太陰|手陽[明眀]|足陽[明眀]|足太陰|手少陰|手太陽|足太陽|足少陰|手厥陰|心主|手少陽|足少陽|足厥陰|督脉)', t16):
    YQ.append(m.group(2))
YQ = list(dict.fromkeys(YQ))

# ---------- 平人絕穀 ----------
PG = []
for m in re.finditer(r'(胃|小腸|迴腸|廣腸)大([^，。]+)[，]徑([^，。]+)[，]長([^，。]+)[，][^。]*?受[穀水]([^。]+)', t32):
    PG.append({'府': m.group(1), '大': m.group(2), '徑': m.group(3), '長': m.group(4), '受': m.group(5)[:30]})

# ---------- 八風 ----------
BF = []
for m in re.finditer(r'風從([^，。]{2,6})[來来][，]名曰([^，。]{2,4})[。]其傷人也[，]內[舎舍]於([^，。]+)[，]外在[於]?([^，。]+)[，](?:[，](?:其)?氣主([^。]+))?', t77):
    BF.append({'方位': m.group(1), '名': m.group(2), '內舍': m.group(3), '外在': m.group(4), '主氣': m.group(5)})

# ---------- 歲露：三虛 ----------
m = re.search(r'(三虛[^。]{0,120})', t79)
SANXU = m.group(1) if m else ''
if not SANXU:
    for cand in re.findall(r'[^。]{0,60}三虛[^。]{0,60}。', t79)[:2]:
        SANXU += cand

mod = {'模組': 'A/E 最後一批',
       '五禁': WJ, '五奪': WD, '五逆': WN, '經水': JS, '標本': BB,
       '營氣行次': YQ, '平人絕穀': PG, '八風': BF, '三虛': SANXU}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_A3.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '24_A型第三批_與時間補遺.md'), 'w', encoding='utf-8') as f:
    f.write('# A 型第三批與時間補遺\n\n')
    f.write('> 出處：《靈樞》五禁第六十一、經水第十二、衛氣第五十二、營氣第十六、平人絕穀第三十二、九宮八風第七十七、歲露論第七十九。\n\n---\n\n')
    f.write('## 一、五禁（五禁）\n\n| 日干 | 禁 |\n|---|---|\n')
    for r in WJ: f.write(f"| {r['日干']}日 | {r['禁']} |\n")
    f.write('\n## 二、五奪（五禁）\n\n')
    for r in WD: f.write(f"- {r['序']}奪：{r['奪']}\n")
    f.write('\n> 五奪皆不可寫（瀉）。\n\n')
    f.write('## 三、五逆（五禁）\n\n')
    for r in WN: f.write(f"- {r['序']}逆：{r['逆']}\n")
    f.write('\n## 四、十二經水（經水）\n\n| 經 | 外合經水 | 內屬 |\n|---|---|---|\n')
    for r in JS: f.write(f"| {r['經']} | {r['經水']} | {r['屬']} |\n")
    f.write('\n## 五、十二經標本（衛氣）\n\n| 經 | 本 | 標 |\n|---|---|---|\n')
    for r in BB: f.write(f"| {r['經']} | {r['本']} | {r['標']} |\n")
    f.write('\n## 六、營氣行次（營氣）\n\n')
    f.write(' → '.join(YQ) + '\n\n')
    f.write('## 七、平人絕穀（平人絕穀）\n\n| 府 | 大 | 徑 | 長 | 受 |\n|---|---|---|---|---|\n')
    for r in PG: f.write(f"| {r['府']} | {r['大']} | {r['徑']} | {r['長']} | {r['受']} |\n")
    f.write('\n## 八、八風（九宮八風）\n\n| 方位 | 名 | 內舍 | 外在 | 主氣 |\n|---|---|---|---|---|\n')
    for r in BF: f.write(f"| {r['方位']} | {r['名']} | {r['內舍']} | {r['外在']} | {r['主氣']} |\n")
    f.write('\n## 九、三虛（歲露論）\n\n')
    f.write(f'{SANXU}\n')

print('五禁', len(WJ), '｜五奪', len(WD), '｜五逆', len(WN), '｜經水', len(JS),
      '｜標本', len(BB), '｜營氣', len(YQ), '｜平人', len(PG), '｜八風', len(BF))
for r in WJ: print('  ', r)
for r in BF: print('  ', r['名'], r['方位'], r['內舍'])
