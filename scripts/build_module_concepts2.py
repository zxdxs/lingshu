#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 型第二批：營衛三焦（18）、五味（56）、病因傳變（66）

輸出：data/模組_概念2.json、docs/18_概念卡_營衛五味病因.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

# ---------- 營衛 ----------
t18 = T(18)
YINGWEI = [
 dict(術語='營', 定義='其清者為營……營在脉中', 原文='其清者為營，濁者為衛。營在脉中，衛在脉外'),
 dict(術語='衛', 定義='其濁者為衛……衛在脉外', 原文='其清者為營，濁者為衛。營在脉中，衛在脉外'),
 dict(術語='營衛大會', 定義='營周不休，五十而復大會，陰陽相貫，如環無端', 原文='營周不休，五十而復大會。陰陽相貫，如環無端。'),
 dict(術語='衛氣晝夜', 定義='衛氣行于陰二十五度，行于陽二十五度，分為晝夜', 原文='衛氣行于陰二十五度，行于陽二十五度，分為晝夜。'),
 dict(術語='老人不夜瞑', 定義='老者之氣血衰，其肌肉枯，氣道澀，營氣衰少而衛氣內伐，故晝不精，夜不瞑', 原文='老者之氣血衰，其肌肉枯，氣道澀，五藏之氣相摶，其營氣衰少而衛氣內伐，故晝不精，夜不瞑'),
 dict(術語='壯者晝精夜瞑', 定義='壯者之氣血盛，肌肉滑，氣道通，營衛之行不失其常', 原文='壯者之氣血盛，其肌肉滑，氣道通，營衛之行，不失其常，故晝精而夜瞑'),
 dict(術語='奪血者無汗', 定義='血之與氣異名同類；奪血者無汗，奪汗者無血', 原文='故奪血者無汗，奪汗者無血。故人生有兩死，而無兩生。'),
]
SANJIAO = [
 dict(焦='上焦', 文='上焦出于胃上口，並咽以上，貫膈而布胸中，走腋，循太陰之分而行，還至陽明，上至舌，下足陽明，常與營俱行于陽二十五度，行于陰亦二十五度，一周也。'),
 dict(焦='中焦', 文='中焦亦並胃中，出上焦之後。此所受氣者，泌糟粕，蒸津液，化其精微，上注于肺脉，乃化而爲血，以奉生身，莫貴于此，故獨得行于經隧，命曰營氣。'),
 dict(焦='下焦', 文='下焦者，別迴腸，注于膀胱而渗入焉。故水穀者，常并居于胃中，成糟粕而俱下于大腸，而成下焦，渗而俱下，濟泌別注，循下焦而渗入膀胱焉。'),
]
SANJIAO_SAY = dict(上焦='如霧', 中焦='如漚', 下焦='如瀆')

# ---------- 五味 ----------
t56 = T(56)
WUWEI = []
for m in re.finditer(r'穀味([酸苦甘辛鹹])先走(肝|心|脾|肺|腎)', t56):
    WUWEI.append({'味': m.group(1), '走': m.group(2)})
WUJIN = []
for m in re.finditer(r'(肝|心|脾|腎|肺)病禁([酸苦甘辛鹹])', t56):
    WUJIN.append({'藏': m.group(1), '禁': m.group(2)})
WUGU = []
for m in re.finditer(r'(秔米|麻|大豆|麥|黃黍)([酸苦甘辛鹹])', t56):
    WUGU.append({'物': m.group(1), '味': m.group(2)})

# ---------- 病因 ----------
t66 = T(66)
BINGYIN = [
 dict(部='喜怒不節', 傷='傷藏', 起='病起於陰', 文='喜怒不節則傷藏，藏傷則病起於陰也'),
 dict(部='清濕', 傷='襲虚', 起='病起於下', 文='清濕襲虚，則病起於下'),
 dict(部='風雨', 傷='襲虚', 起='病起於上', 文='風雨襲虚，則病起於上'),
]
LIANGXU = '風雨寒熱，不得虚，邪不能獨傷人。卒然逢疾風暴雨而不病者，盖無虚，故邪不能獨傷人。此必因虚邪之風，與其身形，兩虚相得，乃客其形。'
CHUAN = [{'舍': '皮膚', '候': '皮膚緩則腠理開，邪從毛髮入，毛髮立則淅然，故皮膚痛'}]
for m in re.finditer(r'留而不去，[則]?傳[舍舎]於([^，。]+)，在[^，。]+之時，([^。]+)。', t66):
    CHUAN.append({'舍': m.group(1), '候': m.group(2)})
CHUAN.append({'舍': '腸胃之外、募原之間', '候': '留著於脉，稽留而不去，息而成積'})

# 驗證
for c in YINGWEI:
    assert sp(c['原文']) in sp(t18), c['術語']
for c in SANJIAO:
    assert sp(c['文']) in sp(t18), c['焦']
for c in BINGYIN:
    assert sp(c['文']) in sp(t66), c['部']
assert sp(LIANGXU) in sp(t66)

mod = {
    '模組': '概念卡第二批',
    '出處': [{'篇序': 18, '篇名': '營衛生會'}, {'篇序': 56, '篇名': '五味'}, {'篇序': 66, '篇名': '百病始生'}],
    '營衛': YINGWEI, '三焦': SANJIAO, '三焦要訣': SANJIAO_SAY,
    '五味所走': WUWEI, '五藏所禁': WUJIN, '五穀五味': WUGU,
    '病因三部': BINGYIN, '兩虛相得': LIANGXU, '邪氣傳舍': CHUAN,
}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_概念2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '18_概念卡_營衛五味病因.md'), 'w', encoding='utf-8') as f:
    f.write('# 概念卡：營衛・五味・病因\n\n')
    f.write('> 出處：《靈樞》營衛生會第十八、五味第五十六、百病始生第六十六。\n\n---\n\n')
    f.write('## 一、營衛與睡眠（營衛生會）\n\n')
    for c in YINGWEI:
        f.write(f"- **{c['術語']}**：{c['定義']}\n")
    f.write('\n> 這一組對普通人的價值最高：**睡眠不是「睡不著」三個字，而是營衛運行的問題**。'
            '壯者氣血盛、氣道通，故晝精夜瞑；老者氣血衰、氣道澀，故晝不精夜不瞑。\n\n')
    f.write('## 二、三焦（營衛生會）\n\n')
    for c in SANJIAO:
        f.write(f"### {c['焦']}\n\n{c['文']}\n\n")
    f.write(f"> 要訣：**上焦{SANJIAO_SAY['上焦']}，中焦{SANJIAO_SAY['中焦']}，下焦{SANJIAO_SAY['下焦']}。**\n\n")
    f.write('## 三、五味（五味）\n\n')
    f.write('**五味所走**：\n\n| 味 | 先走 |\n|---|---|\n')
    for w in WUWEI:
        f.write(f"| {w['味']} | {w['走']} |\n")
    f.write('\n**五藏所禁**（重要：這是「忌口」的經典依據）：\n\n| 藏 | 禁 |\n|---|---|\n')
    for w in WUJIN:
        f.write(f"| {w['藏']}病 | 禁{w['禁']} |\n")
    f.write('\n**五穀五味**：\n\n')
    f.write('、'.join(f"{w['物']}{w['味']}" for w in WUGU) + '\n\n')
    f.write('> 注意：五禁是「病時之禁」，不是人人皆忌。沒有病的人不必按此忌口。\n\n')
    f.write('## 四、病因三部（百病始生）\n\n')
    f.write('| 病因 | 所傷 | 病起 |\n|---|---|---|\n')
    for b in BINGYIN:
        f.write(f"| {b['部']} | {b['傷']} | {b['起']} |\n")
    f.write(f"\n> **關鍵句**：{LIANGXU}\n\n")
    f.write('「兩虛相得，乃客其形」——邪氣本身不足以致病，必須**身形之虛**與**虛邪之風**相遇。\n\n')
    f.write('### 邪氣傳舍\n\n| 舍 | 候 |\n|---|---|\n')
    for c in CHUAN:
        f.write(f"| {c['舍']} | {c['候']} |\n")
    f.write('\n> 這是一條由淺入深的路徑：皮膚→絡脈→經→輸→伏衝之脈→腸胃→募原之間，最後成積。\n')

print('營衛', len(YINGWEI), '｜三焦', len(SANJIAO), '｜五味', len(WUWEI), '｜五禁', len(WUJIN),
      '｜五穀', len(WUGU), '｜病因', len(BINGYIN), '｜傳舍', len(CHUAN))
for c in CHUAN: print('  ', c['舍'], '→', c['候'][:24])
