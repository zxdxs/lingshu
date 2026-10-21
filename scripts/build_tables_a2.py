#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 型第二批：官鍼（九針所宜、九刺、十二節）、根結（三陰三陽根結、六陽根溜注入）

輸出：data/表_官鍼.csv、表_九刺.csv、表_十二節.csv、表_根結.csv
      data/模組_A2.json、docs/23_A型第二批.md
"""
import json, os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

t7, t5 = T(7), T(5)

# ---------- 九針所宜 ----------
YI = []
for m in re.finditer(r'病(?:在|為|爲)?([^。]{1,16}?)者?[，]取以([^，。]{1,6}鍼)', t7):
    YI.append({'病所': m.group(1), '用鍼': m.group(2)})

# ---------- 九刺 / 十二節（以編號標記分割） ----------
def parse_numbered(seg, nums):
    ordered = sorted(nums, key=len, reverse=True)
    chunks = re.split(r'(?=(?:' + '|'.join(ordered) + r')曰)', seg)
    out = []
    for c in chunks:
        m = re.match(r'(' + '|'.join(ordered) + r')曰([^，。]{1,8})[，]\2者[，]?(.*)', c, re.S)
        if m:
            out.append({'序': m.group(1), '名': m.group(2), '法': m.group(3).strip('。')})
    seen, uniq = set(), []
    for r in out:
        if r['序'] not in seen:
            seen.add(r['序']); uniq.append(r)
    return uniq

i = t7.find('凡刺有九')
seg9 = t7[i:t7.find('凡刺有十二節', i)]
JIU = parse_numbered(seg9, list('一二三四五六七八九'))

SHI = [
 dict(序='一', 名='偶刺', 法='以手直心若背，直痛所，一刺前，一刺後，以治心痹'),
 dict(序='二', 名='報刺', 法='刺痛無常處也，上下行者，直內無拔鍼，以左手隨病所按之，乃出鍼復刺之'),
 dict(序='三', 名='恢刺', 法='恢刺直刺傍之，舉之前後，恢筋急，以治筋痹'),
 dict(序='四', 名='齊刺', 法='直入一，傍入二，以治寒氣小深者'),
 dict(序='五', 名='揚刺', 法='正內一，傍內四，而浮之，以治寒氣之愽大者'),
 dict(序='六', 名='直鍼刺', 法='引皮乃刺之，以治寒氣之淺者'),
 dict(序='七', 名='輸刺', 法='直入直出，稀發鍼而深之，以治氣盛而熱者'),
 dict(序='八', 名='短刺', 法='刺骨痹，稍摇而深之，致鍼骨所，以上下摩骨'),
 dict(序='九', 名='浮刺', 法='傍入而浮之，以治肌急而寒者'),
 dict(序='十', 名='陰刺', 法='左右率刺之，以治寒厥'),
 dict(序='十一', 名='傍鍼刺', 法='直刺傍刺各一，以治留痹久居者'),
 dict(序='十二', 名='賛刺', 法='直入直出，數發鍼而淺之，出血，是謂治癰腫'),
]
for r in SHI:
    assert sp(r['名']) in sp(t7), r['名']
    assert sp(r['法'].split('，')[0]) in sp(t7), r['名']

# ---------- 根結 ----------
GEN = []
for m in re.finditer(r'(太陽|陽明|少陽|太陰|少陰|厥陰)根于([^，。]{1,6})[，]結于([^，。]{1,6})', t5):
    GEN.append({'經': m.group(1), '根': m.group(2), '結': m.group(3)})
KAITA = []
for m in re.finditer(r'(太陽|陽明|少陽|太陰|厥陰)為(開|闔|樞)', t5):
    KAITA.append({'經': m.group(1), '用': m.group(2)})
LIU = []
for m in re.finditer(r'(足太陽|足少陽|足陽明|手太陽|手少陽|手陽明)根于([^，。]{1,4})[，]溜于([^，。]{1,4})[，]注于([^，。]{1,4})[，]入于([^，。]{1,10})', t5):
    LIU.append({'經': m.group(1), '根': m.group(2), '溜': m.group(3), '注': m.group(4), '入': m.group(5)})

def dump(name, rows, fields):
    with open(os.path.join(ROOT, 'data', name), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

dump('表_官鍼_所宜.csv', YI, ['病所', '用鍼'])
dump('表_九刺.csv', JIU, ['序', '名', '法'])
dump('表_十二節.csv', SHI, ['序', '名', '法'])
dump('表_根結.csv', GEN, ['經', '根', '結'])

mod = {'模組': 'A 型第二批', '出處': [{'篇序': 7, '篇名': '官鍼'}, {'篇序': 5, '篇名': '根結'}],
       '九針所宜': YI, '九刺': JIU, '十二節': SHI, '根結': GEN, '開闔樞': KAITA, '六陽根溜注入': LIU}
json.dump(mod, open(os.path.join(ROOT, 'data', '模組_A2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '23_A型第二批.md'), 'w', encoding='utf-8') as f:
    f.write('# A 型第二批：官鍼與根結\n\n')
    f.write('> 出處：《靈樞》官鍼第七、根結第五。\n\n---\n\n')
    f.write('## 一、九針所宜（官鍼）\n\n| 病所 | 用鍼 |\n|---|---|\n')
    for r in YI: f.write(f"| {r['病所']} | {r['用鍼']} |\n")
    f.write('\n## 二、九刺（官鍼）\n\n| 序 | 名 | 法 |\n|---|---|---|\n')
    for r in JIU: f.write(f"| {r['序']} | {r['名']} | {r['法'][:40]} |\n")
    f.write('\n## 三、十二節（官鍼）\n\n| 序 | 名 | 法 |\n|---|---|---|\n')
    for r in SHI: f.write(f"| {r['序']} | {r['名']} | {r['法'][:40]} |\n")
    f.write('\n## 四、三陰三陽根結（根結）\n\n| 經 | 根 | 結 |\n|---|---|---|\n')
    for r in GEN: f.write(f"| {r['經']} | {r['根']} | {r['結']} |\n")
    f.write('\n## 五、開闔樞（根結）\n\n')
    f.write('、'.join(f"{r['經']}為{r['用']}" for r in KAITA) + '\n\n')
    f.write('## 六、六陽根溜注入（根結）\n\n| 經 | 根 | 溜 | 注 | 入 |\n|---|---|---|---|---|\n')
    for r in LIU: f.write(f"| {r['經']} | {r['根']} | {r['溜']} | {r['注']} | {r['入']} |\n")

print('九針所宜', len(YI), '｜九刺', len(JIU), '｜十二節', len(SHI),
      '｜根結', len(GEN), '｜開闔樞', len(KAITA), '｜根溜注入', len(LIU))
for r in JIU: print('  ', r['序'], r['名'], '|', r['法'][:26])
for r in SHI[:6]: print('  ', r['序'], r['名'], '|', r['法'][:26])
