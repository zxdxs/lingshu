#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E 型（曆法天人型）蒸餾：把時間結構抽成表與週期。

處理：順氣一日分為四時(44)、陰陽繫日月(41)、衛氣行(76)
輸出：data/模組_時間.json、docs/20_時間醫學.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'

# ---------- 日四時 ----------
t44 = T(44)
RI = []
BS = {'朝': ('旦慧', '人氣始生，病氣衰'), '日中': ('晝安', '人氣長，長則勝邪'),
      '日入': ('夕加', '人氣始衰，邪氣始生'), '夜半': ('夜甚', '人氣入藏，邪氣獨居於身')}
for m in re.finditer(r'(朝|日中|日入|夜半)(?:則)?[為](春|夏|秋|冬)', t44):
    bs, ji = BS.get(m.group(1), ('', ''))
    RI.append({'時段': m.group(1), '配': m.group(2), '病勢': bs, '機理': ji})
BINGSHI = ['旦慧', '晝安', '夕加', '夜甚']

# ---------- 五變五輸 ----------
WUBIAN = []
for m in re.finditer(r'(藏|色|時|音|味)主(冬|春|夏|長夏|秋)[，](長夏|冬|春|夏|秋)?刺(井|滎|榮|輸|經|合)', t44):
    WUBIAN.append({'所主': m.group(1), '時': m.group(2), '刺': m.group(4)})

# ---------- 十二月配足經 ----------
t41 = T(41)
YUE = []
for m in re.finditer(r'(寅|夘|卯|辰|巳|午|未|申|酉|戌|亥|子|丑)者[，]([^，。]+?)月[^，。]*?[，]?主(左|右)足之(少陽|太陽|陽明|少陰|太陰|厥陰)', t41):
    YUE.append({'地支': m.group(1), '月': m.group(2), '左右': m.group(3), '經': '足' + m.group(4)})

# ---------- 十日干配手經 ----------
RI10 = []
for m in re.finditer(r'(甲|乙|丙|丁|戊|己|巳|庚|辛|壬|癸)主(左|右)手之(少陽|太陽|陽明|少陰|太陰)', t41):
    RI10.append({'日干': '己' if m.group(1) == '巳' else m.group(1), '左右': m.group(2), '經': '手' + m.group(3)})

# ---------- 四時刺禁 ----------
CJ = []
for m in re.finditer(r'(正月、二月、三月|四月、五月、六月|七月、八月、九月|十月、十一月、十二月)[，][^，。]*在(左|右|足)?[^，。]*[，]無刺(左|右)足之(陽|陰)', t41):
    CJ.append({'月': m.group(1), '人氣在': m.group(2) or '—', '禁刺': m.group(3) + '足之' + m.group(4)})

# ---------- 衛氣行（舍→周→刻） ----------
t76 = T(76)
WEI = []
for m in re.finditer(r'日行([一二三四五六七八九十]+)舍[，]?人氣行[于]?身?([^，。]{1,20}?周)[^，。]*', t76):
    WEI.append({'日行舍': m.group(1), '氣行': m.group(2)})

mod = {
    '模組': '時間醫學',
    '出處': [{'篇序': 44, '篇名': '順氣一日分為四時'}, {'篇序': 41, '篇名': '陰陽繫日月'},
           {'篇序': 76, '篇名': '衛氣行'}],
    '日四時': RI, '病勢四段': BINGSHI, '五變五輸': WUBIAN,
    '十二月配足經': YUE, '十日干配手經': RI10, '四時刺禁': CJ, '衛氣行': WEI,
}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_時間.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '20_時間醫學.md'), 'w', encoding='utf-8') as f:
    f.write('# 時間醫學（E 型）\n\n')
    f.write('> 出處：《靈樞》順氣一日分為四時第四十四、陰陽繫日月第四十一、衛氣行第七十六。\n')
    f.write('> E 型的產物不是文字卡，是**週期圖與對應表**。\n\n---\n\n')
    f.write('## 一、一日四時（順氣一日分為四時）\n\n')
    f.write('| 時段 | 配四時 | 病勢 | 機理 |\n|---|---|---|---|\n')
    for r in RI:
        f.write(f"| {r['時段']} | {r['配']} | {r['病勢']} | {r['機理']} |\n")
    f.write('\n**病勢四段**：' + ' → '.join(BINGSHI) + '\n\n')
    f.write('> 機理：朝人氣始生、日中人氣長、夕人氣始衰、夜半人氣入藏。\n')
    f.write('> 這是全書最可自我驗證的一條——任何慢性不適，都可以記錄它一天中的起伏。\n\n')
    f.write('## 二、五變五輸（順氣一日分為四時）\n\n')
    f.write('| 所主 | 時 | 刺 |\n|---|---|---|\n')
    for w in WUBIAN:
        f.write(f"| {w['所主']} | {w['時']} | {w['刺']} |\n")
    f.write('\n## 三、十二月配足經（陰陽繫日月）\n\n')
    f.write('| 地支 | 月 | 左右 | 經 |\n|---|---|---|---|\n')
    for y in YUE:
        f.write(f"| {y['地支']} | {y['月']} | {y['左右']} | {y['經']} |\n")
    f.write('\n## 四、十日干配手經（陰陽繫日月）\n\n')
    f.write('| 日干 | 左右 | 經 |\n|---|---|---|\n')
    for r in RI10:
        f.write(f"| {r['日干']} | {r['左右']} | {r['經']} |\n")
    f.write('\n## 五、四時刺禁（陰陽繫日月）\n\n')
    f.write('| 月 | 人氣在 | 禁刺 |\n|---|---|---|\n')
    for c in CJ:
        f.write(f"| {c['月']} | {c['人氣在']} | {c['禁刺']} |\n")
    f.write('\n## 六、衛氣行（節錄）\n\n')
    f.write('| 日行舍 | 氣行 |\n|---|---|\n')
    for w in WEI[:12]:
        f.write(f"| {w['日行舍']} | {w['氣行']} |\n")
    f.write('\n> 衛氣一晝夜五十周於身，晝行陽二十五周、夜行陰二十五周。\n\n')
    f.write('---\n\n## 使用說明\n\n')
    f.write('1. 這一組要**畫圖**，不要背表。把「朝→日中→日入→夜半」畫成一條橫軸，標上病勢。\n')
    f.write('2. 十二月、十日干的對應屬漢代曆法思維，歷史意義大於實用價值，不必強記。\n')
    f.write('3. 四時刺禁是「何時不可刺何處」，屬操作層，僅供理解，不可自行操作。\n')

print('日四時', len(RI), '｜病勢', len(BINGSHI), '｜五變', len(WUBIAN),
      '｜月-經', len(YUE), '｜日干', len(RI10), '｜刺禁', len(CJ), '｜衛氣行', len(WEI))
for r in RI: print('  ', r)
for y in YUE: print('  ', y)
