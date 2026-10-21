#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 型（體質型）蒸餾：把四篇體質文獻整理成「體質剖面」。

處理：通天(72) 五態人、衛氣失常(59) 膏脂肉、逆順肥瘦(38) 肥瘦壯嬰、天年(54) 生命週期
輸出：data/模組_體質.json、docs/14_體質剖面.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')

# ---------------- 五態人（自原文分段抽取） ----------------
t72 = T(72)
def _sec(a, b):
    i = t72.find(a)
    if i < 0:
        return ''
    j = t72.find(b, i + 1)
    if j < 0:
        j = len(t72)
    return t72[i:j]

sec_qing = _sec('少師曰：太陰之人', '黃帝曰：治人之五態奈何')
sec_zhi  = _sec('治人之五態奈何', '黃帝曰：夫五態之人者')
sec_xing = _sec('別五態之人奈何', '黃帝曰：')

NAMES = ['太陰之人', '少陰之人', '太陽之人', '少陽之人', '陰陽和平之人']

def pick(sec, name, prefix=''):
    i = sec.find(name + '，' + prefix) if prefix else sec.find(name + '，')
    if i < 0:
        i = sec.find(name)
    if i < 0:
        return ''
    j = sec.find('。', i)
    seg = sec[i:j]
    seg = re.sub(r'^' + re.escape(name) + '，?', '', seg)
    seg = re.sub(r'^其狀', '', seg)
    seg = re.sub(r'，?此' + re.escape(name) + r'也?$', '', seg)
    return seg.strip('，')

WU = []
for nm in NAMES:
    WU.append({'名': nm,
               '性情': pick(sec_qing, nm),
               '形態': pick(sec_xing, nm, '其狀'),
               '治則': pick(sec_zhi, nm)})

# ---------------- 膏脂肉（衛氣失常） ----------------
FEI = [
 dict(名='膏人', 判別='膕內不堅，皮緩', 形='縱腹垂腴，其肉淖',
      血氣='多氣，多氣者熱，熱者耐寒', 寒温='粗理者身寒，細理者身熱'),
 dict(名='脂人', 判別='膕內堅，皮滿', 附註='原文作「肥」，通「脂」', 形='其身收小，其肉堅',
      血氣='血清，氣滑少，故不能大', 寒温='細理者熱，粗理者寒'),
 dict(名='肉人', 判別='皮內不相離', 形='身體容大，上下容大',
      血氣='多血，則充形，充形則平', 寒温='—'),
]

# ---------------- 逆順肥瘦 ----------------
SHOU = [
 dict(名='肥人', 判別='皮薄，肩腋項肉薄，厚皮而黒色，脣臨臨然',
      血氣='其血黒以濁，其氣濇以遲', 刺法='深而留之，多益其數', 附='其為人也，貪於取與'),
 dict(名='瘦人', 判別='皮薄色少，肉亷亷然，薄脣輕言',
      血氣='其血清氣滑，易脱於氣，易損於血', 刺法='淺而疾之', 附='—'),
 dict(名='常人', 判別='端正敦厚', 血氣='血氣和調', 刺法='無失常數', 附='視其白黒，各為調之'),
 dict(名='壯士真骨', 判別='堅肉緩節，監監然，此人重',
      血氣='重則氣濇血濁；勁則氣滑血清', 刺法='重：深而留之，多益其數；勁：淺而疾之', 附='—'),
 dict(名='嬰兒', 判別='其肉脆', 血氣='血少氣弱', 刺法='以豪刺，淺刺而疾發鍼，日再可也', 附='—'),
]

PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t59, t38 = T(59), T(38)
for c in FEI:
    for k in ['形', '血氣']:
        assert sp(re.split(r'[，；]', c[k])[0]) in sp(t59), c['名']
for c in SHOU:
    for k in ['判別', '血氣']:
        if c[k] != '—':
            assert sp(re.split(r'[，；]', c[k])[0]) in sp(t38), (c['名'], k)

# ---------------- 天年 ----------------
stages = []
for m in re.finditer(r'(人生)?([一二三四五六七八九十百]+)(十)?歲，([^。]+)', T(54)):
    n = m.group(2) + (m.group(3) or '')
    stages.append({'齡': n + '歲', '描述': m.group(4)})

mod = {
    '模組': '體質剖面',
    '出處': [{'篇序': 72, '篇名': '通天'}, {'篇序': 59, '篇名': '衛氣失常'},
           {'篇序': 38, '篇名': '逆順肥瘦'}, {'篇序': 54, '篇名': '天年'}],
    '學習目標': ['依形態與性情辨出五態人', '分辨膏、脂、肉三型與其氣血特徵',
             '知道不同體質的刺法差異', '知道生命週期的十個階段'],
    '五態': WU, '膏脂肉': FEI, '肥瘦壯嬰': SHOU, '天年': stages,
}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_體質.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '14_體質剖面.md'), 'w', encoding='utf-8') as f:
    f.write('# 體質剖面（D 型）\n\n')
    f.write('> 出處：《靈樞》通天第七十二、衛氣失常第五十九、逆順肥瘦第三十八、天年第五十四。\n')
    f.write('> 用法：先看「形態」與「性情」，猜是哪一型；再對照治則。\n\n---\n\n')
    f.write('## 一、五態人（通天）\n\n')
    for c in WU:
        f.write(f"### {c['名']}\n\n")
        f.write(f"- **性情**：{c['性情']}\n")
        f.write(f"- **形態**：{c['形態']}\n")
        f.write(f"- **治則**：{c['治則']}\n\n")
    f.write('| 型 | 一句話特徵 |\n|---|---|\n')
    for c in WU:
        f.write(f"| {c['名']} | {c['性情'].split('，')[0]} |\n")
    f.write('\n> **注意**：五態講的是性情與形貌的**整體傾向**，不是道德評價。\n\n')
    f.write('## 二、膏、脂、肉（衛氣失常）\n\n')
    f.write('| 型 | 判別 | 形 | 氣血 | 寒温 |\n|---|---|---|---|---|\n')
    for c in FEI:
        f.write(f"| {c['名']} | {c['判別']} | {c['形']} | {c['血氣']} | {c['寒温']} |\n")
    f.write('\n> 原書作「人有肥、有膏、有內」，歷代多讀「內」為「肉」，「肥」通「脂」。\n\n')
    f.write('## 三、肥瘦壯嬰與刺法（逆順肥瘦）\n\n')
    f.write('| 型 | 判別 | 血氣 | 刺法 |\n|---|---|---|---|\n')
    for c in SHOU:
        f.write(f"| {c['名']} | {c['判別']} | {c['血氣']} | {c['刺法']} |\n")
    f.write('\n## 四、生命週期（天年）\n\n')
    f.write('| 齡 | 描述 |\n|---|---|\n')
    for s in stages:
        f.write(f"| {s['齡']} | {s['描述']} |\n")
    f.write('\n> 天年的重點不是「幾歲該怎樣」，而是**把衰老看成有階段的過程**：'
            '四十歲腠理始疏、五十歲肝氣始衰、六十歲心氣始衰……每階段有不同弱點。\n')

print('五態', len(WU), '｜膏脂肉', len(FEI), '｜肥瘦壯嬰', len(SHOU), '｜天年', len(stages))
for c in WU:
    print(f"  {c['名']}: 性[{c['性情'][:18]}] 形[{c['形態'][:18]}] 治[{c['治則'][:16]}]")
for s in stages: print('  ', s['齡'], s['描述'][:24])
