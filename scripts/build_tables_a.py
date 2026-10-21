#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 型（定額表格型）蒸餾：把可量化的篇章抽成資料表。

處理：骨度(14)、腸胃(31)、脈度(17)、五十營(15)、背腧(51)、九鍼形制(1)
輸出：data/表_骨度.csv、表_腸胃.csv、表_脈度.csv、表_五十營.csv、
      data/表_背腧.csv、表_九鍼.csv，彙總 data/表_彙總.json
"""
import json, os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
S = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
CN = '一二三四五六七八九十百'
NUM = r'(?=[' + CN + r'])(?:[' + CN + r']+(?:丈|尺|寸|分)){1,3}半?'

def clauses(n):
    return [x.strip() for x in re.split(r'[，。；：？！]', J[n]['句讀']) if x.strip()]

def dump(name, rows, fields):
    with open(os.path.join(ROOT, 'data', name), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

summary = {}
CLS = '[' + CN + ']'          # 漢數字元類
T = lambda n: J[n]['句讀'].replace('\n', '')
SP = r'[^，。；：？！]'

# ---------------- 骨度 ----------------
rows = []
for m in re.finditer(r'(' + SP + r'{1,12})至(' + SP + r'{1,12})[，]?長?(' + NUM + r')', T(14)):
    rows.append({'起': m.group(1), '訖': m.group(2), '長': m.group(3), '原文': m.group(0)})
for m in re.finditer(r'(' + SP + r'{1,10}?)(圍|廣|深|大容)[，]?(' + NUM + r'|' + CLS + r'+[斗升合兩])', T(14)):
    rows.append({'起': m.group(1), '訖': '（單一部位）', '長': m.group(3), '原文': m.group(0)})
dump('表_骨度.csv', rows, ['起', '訖', '長', '原文'])
summary['骨度'] = len(rows)

# ---------------- 腸胃 ----------------
rows = []
t31 = T(31)
for m in re.finditer(r'(長|大|徑|容|重|廣|深)[，]?(' + NUM + r'|' + CLS + r'+[斗升合兩])', t31):
    pre = t31[max(0, m.start() - 10):m.start()]
    organ = re.split(r'[，。；：]', pre)[-1].strip()
    rows.append({'部位': organ, '項目': m.group(1), '數值': m.group(2), '原文': m.group(0)})
dump('表_腸胃.csv', rows, ['部位', '項目', '數值', '原文'])
summary['腸胃'] = len(rows)

# ---------------- 脈度 ----------------
rows = []
for m in re.finditer(r'(手之六[陽陰]|足之六[陽陰]|蹻脉|督脉、任脉)[各]?[，]?(?:從' + SP + r'{2,10})?[，]?長?(' + NUM + r')', T(17)):
    rows.append({'經脉': m.group(1), '單側長': m.group(2), '原文': m.group(0)})
dump('表_脈度.csv', rows, ['經脉', '單側長', '原文'])
summary['脈度'] = len(rows)

# ---------------- 五十營 ----------------
rows = []
for m in re.finditer(r'(' + CLS + r'+)息[，]?氣行(' + NUM + r')', T(15)):
    seg = T(15)[m.start():m.start() + 70]
    m3 = re.search(r'下水(' + CLS + r'+)刻', seg)
    rows.append({'息數': m.group(1), '氣行': m.group(2),
                 '水下刻': m3.group(1) if m3 else '', '原文': m.group(0)})
dump('表_五十營.csv', rows, ['息數', '氣行', '水下刻', '原文'])
summary['五十營'] = len(rows)

# ---------------- 背腧 ----------------
rows = []
for m in re.finditer(r'(胸中大腧|肺腧|心腧|膈腧|肝腧|脾腧|腎腧)在(' + SP + r'{2,12}?)(?:之間|之端)', T(51)):
    rows.append({'腧穴': m.group(1), '位置': m.group(2), '原文': m.group(0)})
dump('表_背腧.csv', rows, ['腧穴', '位置', '原文'])
summary['背腧'] = len(rows)

# ---------------- 九鍼 ----------------
rows = []
for m in re.finditer(r'([一二三四五六七八九])曰(' + SP + r'{1,3}鍼)[，]?長(' + NUM + r')', T(1)):
    rows.append({'序': m.group(1), '鍼': m.group(2), '長': m.group(3), '原文': m.group(0)})
func = {}
for m in re.finditer(r'(鑱鍼|員鍼|鍉鍼|鋒鍼|鈹鍼|員利鍼|毫鍼|長鍼|大鍼)者[，](.+?)(?=。|$)', T(1)):
    func[m.group(1)] = m.group(2)
for r in rows:
    r['功能'] = func.get(r['鍼'], '')
dump('表_九鍼.csv', rows, ['序', '鍼', '長', '功能', '原文'])
summary['九鍼'] = len(rows)

json.dump(summary, open(os.path.join(ROOT, 'data', '表_彙總.json'), 'w'),
          ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
for k in ['骨度', '腸胃', '脈度', '五十營', '背腧']:
    print(f"--- {k} ---")
    for r in list(csv.DictReader(open(os.path.join(ROOT, 'data', f'表_{k}.csv'), encoding='utf-8-sig')))[:4]:
        print("   ", list(r.values())[:3])
