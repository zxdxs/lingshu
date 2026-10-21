#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 型（概念定義型）蒸餾：術語卡。

處理：本神(8) 十義、決氣(30) 六氣與六脫、海論(33) 四海
每張卡含：術語、篇內義（原文）、白話、出處。
輸出：data/模組_術語.json、docs/17_術語卡.md
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')

# ---------------- 本神：十義 ----------------
t8 = T(8)
terms = []
for m in re.finditer(r'([^，。]{2,14})謂之([^，。]{1,3})', t8):
    terms.append({'術語': m.group(2), '定義': m.group(1), '篇': '本神', '篇序': 8})

# ---------------- 決氣：六氣 + 六脫 ----------------
t30 = T(30)
SIX = ['精', '氣', '津', '液', '血', '脉']
six = []
for s in SIX:
    m = re.search(r'([^。]{2,40})，是謂' + s + r'。', t30)
    if m:
        six.append({'術語': s, '定義': m.group(1), '篇': '決氣', '篇序': 30})
tuo = []
for m in re.finditer(r'([精氣津液血脉])[脫脱]者，([^。；]+)', t30):
    tuo.append({'術語': m.group(1) + '脫', '候': m.group(2), '篇': '決氣', '篇序': 30})

# ---------------- 海論：四海 ----------------
t33 = T(33)
hai = []
for m in re.finditer(r'(胃|衝脉|膻中|腦)(?:者)?[，]?[為爲]?([^，。]{2,8})之海', t33):
    name = m.group(2)
    name = name.replace('為', '').replace('爲', '')
    hai.append({'海': name, '主體': m.group(1).replace('者', ''), '篇序': 33})
# 輸
shu = {}
for m in re.finditer(r'(水穀|十二經|氣|髓)之海[^。]*?其輸上在[于]?([^，。]{2,10})，(?:下(?:至|在|出于)|前在)[于]?([^，。]{2,10})', t33):
    shu[m.group(1)] = (m.group(2), m.group(3))
for h in hai:
    k = h['海'].replace('之海', '')
    h['上輸'], h['下輸'] = shu.get(k, ('—', '—'))
# 有餘不足
yubu = {}
for k in ['氣海', '血海', '水穀之海', '髓海']:
    my = re.search(k + r'有餘[者]?[，]?([^；。]+)', t33)
    mz = re.search(k + r'不足[，則]*([^；。]+)', t33)
    yubu[k] = (my.group(1) if my else '—', mz.group(1) if mz else '—')
for h in hai:
    k = h['海']
    key = k if k in yubu else (k + '之海' if k + '之海' in yubu else None)
    if key:
        h['有餘'], h['不足'] = yubu[key]

PUNC = '，。、；：？！'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())
# 驗證：定義文字確實見於原文
for t in terms + six:
    assert sp(t['定義']) in sp(T(t['篇序'])), t['術語']

mod = {
    '模組': '術語卡',
    '出處': [{'篇序': 8, '篇名': '本神'}, {'篇序': 30, '篇名': '決氣'}, {'篇序': 33, '篇名': '海論'}],
    '說明': '只取「篇內義」；他篇義與後世義待補，不可混用',
    '本神十義': terms, '決氣六氣': six, '六脫候': tuo, '四海': hai,
}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_術語.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '17_術語卡.md'), 'w', encoding='utf-8') as f:
    f.write('# 術語卡（C 型）\n\n')
    f.write('> 只取**篇內義**——即該詞在這一篇裡的定義。\n')
    f.write('> 同一詞在別篇、或在後世可能有不同意思，那是另外兩欄，不可混用。\n\n---\n\n')
    f.write('## 一、本神十義（《本神第八》）\n\n')
    f.write('| 術語 | 篇內義 |\n|---|---|\n')
    for t in terms:
        f.write(f"| **{t['術語']}** | {t['定義']} |\n")
    f.write('\n> 這十個詞是一條發生鏈：精→神→魂→魄→心→意→志→思→慮→智。'
            '不是十個孤立的名詞。\n\n')
    f.write('## 二、決氣六氣（《決氣第三十》）\n\n')
    f.write('| 術語 | 篇內義 |\n|---|---|\n')
    for t in six:
        f.write(f"| **{t['術語']}** | {t['定義']} |\n")
    f.write('\n### 六脫候\n\n| 脫 | 候 |\n|---|---|\n')
    for t in tuo:
        f.write(f"| {t['術語']} | {t['候']} |\n")
    f.write('\n## 三、四海（《海論第三十三》）\n\n')
    f.write('| 海 | 主體 | 上輸 | 下輸 |\n|---|---|---|---|\n')
    for h in hai:
        f.write(f"| {h['海']} | {h['主體']} | {h.get('上輸','—')} | {h.get('下輸','—')} |\n")
    f.write('\n### 四海有餘與不足\n\n| 海 | 有餘 | 不足 |\n|---|---|---|\n')
    for h in hai:
        f.write(f"| {h['海']} | {h.get('有餘','—')} | {h.get('不足','—')} |\n")
    f.write('\n---\n\n## 四、使用規則\n\n')
    f.write('1. 背卡時**先背篇內義**，不要一開始就摻後世解釋。\n')
    f.write('2. 「精」「氣」「血」這類詞，在《靈樞》不同篇有不同定義——遇到衝突，先確認是哪一篇。\n')
    f.write('3. 本表未收他篇義與後世義，這是**刻意留白**，不是遺漏。\n')

print('本神', len(terms), '｜六氣', len(six), '｜六脫', len(tuo), '｜四海', len(hai))
for t in terms: print('  ', t['術語'], '=', t['定義'][:26])
for h in hai: print('  ', h)
