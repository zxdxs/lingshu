#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3/S4：實體抽取與關係抽取（規則式，全程可回溯，不用生成式模型）

輸入：底本/靈樞經_81篇.json（L1 經文）
      demo/本輸_五輸穴示例.json（五輸穴表）
輸出：data/實體_腧穴.csv、實體_經脈.csv、實體_九針.csv、實體_臟腑.csv
      data/關係_五輸.csv、data/實體統計.json
"""
import json, os, re, csv
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
WU = json.load(open(os.path.join(ROOT, 'demo', '本輸_五輸穴示例.json'), encoding='utf-8'))['表']

def text_of(ch):
    return ch['經文'].replace('\n', '')

# ---------------- 詞典 ----------------
MER = {
    '手太陰': '肺', '手陽明': '大腸', '足陽明': '胃', '足太陰': '脾',
    '手少陰': '心', '手太陽': '小腸', '足太陽': '膀胱', '足少陰': '腎',
    '手厥陰': '心主', '手少陽': '三焦', '足少陽': '膽', '足厥陰': '肝',
}
MER_ALIAS = {'心主手厥陰': '心主', '心包': '心主', '膻中': '心主'}
ZANG = ['肝', '心', '脾', '肺', '腎', '心主']
FU = ['膽', '胃', '大腸', '小腸', '膀胱', '三焦']
NINE = ['鑱鍼', '員鍼', '鍉鍼', '鋒鍼', '鈹鍼', '員利鍼', '毫鍼', '長鍼', '大鍼']
NINE_ALIAS = {'鑱針': '鑱鍼', '員針': '員鍼', '鍉針': '鍉鍼', '鋒針': '鋒鍼',
              '鈹針': '鈹鍼', '員利針': '員利鍼', '毫針': '毫鍼', '長針': '長鍼', '大針': '大鍼'}

# 異名對照：底本作「大」，規範作「太」
ALIAS = {'大淵': '太淵', '大衝': '太衝', '大谿': '太谿'}

# 腧穴詞典（自《本輸》五輸表 + 十二原）
ACU = {}
for r in WU:
    mer = r['歸屬']
    for k in ['井', '滎', '輸', '原', '經', '合']:
        v = r.get(k, '—')
        if v in ('—', '', None):
            continue
        ACU.setdefault(v, {'經脈': mer, '五輸': k})
# 十二原（九鍼十二原）
YUAN = {'太淵': ('肺', '原'), '大陵': ('心主', '原'), '太衝': ('肝', '原'),
        '太白': ('脾', '原'), '太谿': ('腎', '原'), '鳩尾': ('膏', '原'),
        '脖胦': ('肓', '原')}
for k, v in YUAN.items():
    ACU.setdefault(k, {'經脈': v[0], '五輸': v[1]})

# ---------------- 抽取 ----------------
def scan(patterns, kind, allow_overlap=False):
    """回傳 [(實體, 篇序, 位置, 上下文)]"""
    out = []
    for ch in S:
        t = text_of(ch)
        for name, canon in patterns:
            for m in re.finditer(re.escape(name), t):
                out.append((canon, ch['序'], m.start(),
                            t[max(0, m.start() - 6):m.start() + len(name) + 6]))
    return out

# 腧穴（規範名 + 異寫皆掃）
REV = {}
for a, b in ALIAS.items():
    REV.setdefault(b, []).append(a)
acu_hits = []
for name, meta in ACU.items():
    forms = [name] + REV.get(name, [])
    for form in forms:
        for ch in S:
            t = text_of(ch)
            for m in re.finditer(re.escape(form), t):
                acu_hits.append({'穴': name, '原文寫法': form, '異寫': '是' if form != name else '',
                                 '經脈': meta['經脈'], '五輸': meta['五輸'],
                                 '篇序': ch['序'], '篇名': ch['篇名_規範'],
                                 '位置': m.start()})
# 經脈（以「手太陰」等簡稱計）
mer_hits = []
for short, zang in MER.items():
    for ch in S:
        t = text_of(ch)
        for m in re.finditer(re.escape(short), t):
            mer_hits.append({'經脈簡稱': short, '所屬藏府': zang,
                             '篇序': ch['序'], '篇名': ch['篇名_規範'], '位置': m.start()})
# 九鍼
nine_hits = []
for a, canon in list(NINE_ALIAS.items()) + [(n, n) for n in NINE]:
    for ch in S:
        t = text_of(ch)
        for m in re.finditer(re.escape(a), t):
            nine_hits.append({'鍼': canon, '原作': a, '篇序': ch['序'],
                              '篇名': ch['篇名_規範'], '位置': m.start()})
# 藏府
zf_hits = []
for g, lst in (('藏', ZANG), ('府', FU)):
    for name in lst:
        for ch in S:
            t = text_of(ch)
            c = t.count(name)
            if c:
                zf_hits.append({'名': name, '類': g, '篇序': ch['序'],
                                '篇名': ch['篇名_規範'], '次數': c})

def dump(path, rows, fields):
    with open(os.path.join(ROOT, 'data', path), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

dump('實體_腧穴.csv', acu_hits, ['穴', '原文寫法', '異寫', '經脈', '五輸', '篇序', '篇名', '位置'])
dump('實體_經脈.csv', mer_hits, ['經脈簡稱', '所屬藏府', '篇序', '篇名', '位置'])
dump('實體_九鍼.csv', nine_hits, ['鍼', '原作', '篇序', '篇名', '位置'])
dump('實體_臟腑.csv', zf_hits, ['名', '類', '篇序', '篇名', '次數'])

# 關係：腧穴—經脈—五輸
rel = []
for name, meta in ACU.items():
    rel.append({'主體': name, '關係': '歸經', '客體': meta['經脈']})
    rel.append({'主體': name, '關係': '五輸分類', '客體': meta['五輸']})
    rel.append({'主體': meta['經脈'], '關係': '所屬', '客體': meta['經脈']})
dump('關係_五輸.csv', rel, ['主體', '關係', '客體'])

# 統計
stat = {
    '腧穴詞條': len(ACU),
    '腧穴出現次數': len(acu_hits),
    '腧穴出現篇數': len(set(h['篇序'] for h in acu_hits)),
    '經脈出現次數': len(mer_hits),
    '九鍼出現次數': len(nine_hits),
    '關係三元組': len(rel),
    '高頻腧穴': Counter(h['穴'] for h in acu_hits).most_common(10),
}
json.dump(stat, open(os.path.join(ROOT, 'data', '實體統計.json'), 'w'),
          ensure_ascii=False, indent=1)
print(json.dumps(stat, ensure_ascii=False, indent=1))
