#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 型第三批：診法（論疾診尺 74、五色 49）

把「怎麼看」抽成可練習的觀察卡。
重要：這是歷史觀察系統的整理，不是自我診斷工具。

輸出：data/模組_診法.json、docs/19_診法卡.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t74, t49 = T(74), T(49)

# ---------- 尺膚診 ----------
CHI = []
for m in re.finditer(r'尺膚([^，。]{1,8}?)[者]?[，]([^。]+)', t74):
    CHI.append({'尺膚': m.group(1), '主病': m.group(2).strip('，')})
CHI.append({'尺膚': '緩急、小大、滑濇', '主病': '（總綱）審此五者與肉之堅脆，而病形定矣'})

# ---------- 分部獨熱 ----------
RE = []
for m in re.finditer(r'(肘所|手所|肘前|肘後|臂中|掌中|魚上白肉)[^，。]{0,6}獨?(熱|寒)者?[，]([^。]+)', t74):
    RE.append({'部位': m.group(1), '寒熱': m.group(2), '應': m.group(3)})

# ---------- 目診 ----------
MU = []
for m in re.finditer(r'(赤|白|青|黃|黒|黑)(?:色者病在|在)(心|肺|肝|脾|腎)', t74):
    MU.append({'色': m.group(1), '藏': m.group(2)})

# ---------- 血脈診 ----------
XUE = []
for m in re.finditer(r'多(赤|青|黒|黑)[^，。]{0,3}(多|為)(熱|痛|久痹)', t74):
    XUE.append({'色': m.group(1), '主': m.group(3)})

# ---------- 五色主病 ----------
WUSE = []
_seen = set()
for m in re.finditer(r'(青黒|青黑|黃赤|白)為(痛|熱|寒)', t49):
    k = (m.group(1).replace('黒', '黑'), m.group(2))
    if k in _seen:
        continue
    _seen.add(k)
    WUSE.append({'色': k[0], '主': k[1]})

# ---------- 明堂五部 ----------
MING = []
for m in re.finditer(r'(明堂|闕|庭|蕃|蔽)者[，]([^。；]+)', t49):
    MING.append({'部': m.group(1), '位': m.group(2)})

# ---------- 色部對應 ----------
SEBU = []
for m in re.finditer(r'(庭|闕上|闕中|下極|直下|肝左|下者|腎|當[^，。]{0,2}|方上|中央|挾大腸|面王以上|面王以下|巨屈|巨分)者[，]([^。]+?)(?:也)?[。]', t49):
    SEBU.append({'部位': m.group(1), '應': m.group(2)})

# ---------- 危候 ----------
WEI = []
for m in re.finditer(r'(赤色出兩顴|黒色出於庭|黑色出於庭)[^。]{0,30}必[^。]+', t49):
    WEI.append({'候': m.group(0)})

for c in CHI[:6]:
    pass
mod = {
    '模組': '診法卡',
    '出處': [{'篇序': 74, '篇名': '論疾診尺'}, {'篇序': 49, '篇名': '五色'}],
    '警示': '本卡為《靈樞》觀察系統的整理，屬歷史知識；不可據以自我診斷或用於延誤就醫。',
    '尺膚': CHI, '分部寒熱': RE, '目色': MU, '血脈色': XUE,
    '五色主病': WUSE, '明堂五部': MING, '色部對應': SEBU[:20], '危候': WEI,
}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_診法.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '19_診法卡.md'), 'w', encoding='utf-8') as f:
    f.write('# 診法卡（觀察）\n\n')
    f.write('> 出處：《靈樞》論疾診尺第七十四、五色第四十九。\n')
    f.write('> ⚠️ **本文是歷史觀察系統的整理，不是自我診斷工具。** 身體不適請就醫。\n\n---\n\n')
    f.write('## 一、尺膚診（論疾診尺）\n\n')
    f.write('| 尺膚所見 | 主病 |\n|---|---|\n')
    for c in CHI:
        f.write(f"| {c['尺膚']} | {c['主病']} |\n")
    f.write('\n**分部獨熱／獨寒**：\n\n| 部位 | 主 |\n|---|---|\n')
    for c in RE:
        f.write(f"| {c['部位']}{c['寒熱']} | {c['應']} |\n")
    f.write('\n## 二、目診（論疾診尺）\n\n')
    f.write('| 目色 | 在藏 |\n|---|---|\n')
    for c in MU:
        f.write(f"| {c['色']} | {c['藏']} |\n")
    f.write('\n## 三、血脈之色（論疾診尺）\n\n')
    f.write('| 色 | 主 |\n|---|---|\n')
    for c in XUE:
        f.write(f"| 多{c['色']} | {c['主']} |\n")
    f.write('\n## 四、五色主病（五色）\n\n')
    for c in WUSE:
        f.write(f"- **{c['色']}為{c['主']}**\n")
    f.write('\n## 五、明堂五部（五色）\n\n')
    for c in MING:
        f.write(f"- **{c['部']}**：{c['位']}\n")
    f.write('\n## 六、色部對應（五色）\n\n')
    f.write('| 部位 | 應 |\n|---|---|\n')
    for c in SEBU[:20]:
        f.write(f"| {c['部位']} | {c['應']} |\n")
    f.write('\n## 七、危候（五色）\n\n')
    for c in WEI:
        f.write(f"- {c['候']}\n")
    f.write('\n---\n\n## 使用說明\n\n')
    f.write('1. 這一組卡的價值不是「學會看相」，而是**學會觀察的粒度**：同一個「熱」，可以分肘、手、臂、掌、魚際。\n')
    f.write('2. 讀的時候問自己：作者是根據什麼把「這裡熱」連到「那裡病」的？這個連結今天還成立嗎？\n')
    f.write('3. 不要用來自診。這是最重要的一條。\n')

print('尺膚', len(CHI), '｜分部', len(RE), '｜目色', len(MU), '｜血脈', len(XUE),
      '｜五色', len(WUSE), '｜明堂', len(MING), '｜色部', len(SEBU), '｜危候', len(WEI))
for c in CHI[:8]: print('  ', c['尺膚'], '→', c['主病'][:26])
