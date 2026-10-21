#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S4b：病證—治法關係抽取（《熱病》《厥病》《癲狂》三篇試點）

作法：以句讀層切句 → 找第一個治法動詞 → 前為證、後為治
      → 自「治」中抽腧穴、經脈、治法類型
全程保留原句與字元位置，可回溯。

輸出：data/關係_證治.csv、data/病證統計.json
"""
import json, os, re, csv
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
S = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
WU = json.load(open(os.path.join(ROOT, 'demo', '本輸_五輸穴示例.json'), encoding='utf-8'))['表']

ACU = set()
for r in WU:
    for k in ['井', '滎', '輸', '原', '經', '合']:
        v = r.get(k, '—')
        if v not in ('—', '', None):
            ACU.add(v)
ACU |= {'京骨', '崑崙', '然谷', '大都', '太白', '大衝', '行間', '大淵', '魚際',
        '曲泉', '天柱', '耳中', '大杼', '窮骨', '骨骶', '骶骨'}
ALIAS = {'大淵': '太淵', '大衝': '太衝', '大谿': '太谿', '大抒': '大杼'}

MER_RE = re.compile(r'(手|足)(太陰|少陰|厥陰|太陽|少陽|陽明)')
VERB_RE = re.compile(r'(取之|取|刺|治之|灸|寫|補|燔|砭|巨鍼|大鍼|小鍼)')
TREAT_CH = re.compile(r'[取刺灸寫補鍼燔砭]')
BAD = re.compile(r'^(不治|可治|難治|死不治|勿刺|不可刺)')
DISEASE_RE = re.compile(r'(癲疾|狂|風逆|厥逆|熱病|偏枯|痱|厥頭痛|真頭痛|頭痛|頭半寒痛|厥心痛|真心痛|心痛|耳聾|耳鳴|耳痛|痿厥|尸厥|癲|癇|瘧|脹|痺|癰|疽|瘕|蛟蛕|嘔|泄|衄|喘|咳)')

TREAT_TYPE = [('放血', r'血變|出血|見血|寫出其血|去血|盡刺'),
              ('灸', r'灸'),
              ('針具', r'第[一二三四五六七八九]鍼|巨鍼|大鍼|小鍼|員利鍼|毫鍼'),
              ('取穴', r'取'),
              ('刺', r'刺')]

rows = []
proh = []
prev_sent = ''
B_CH = [int(r['篇序']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', '體裁分類.csv'), encoding='utf-8-sig')) if r['體裁碼'] == 'B']
for n in B_CH:
    t = J[n]['句讀']
    # 切句並保留位置
    pos = 0
    for sent in re.split(r'(?<=[。！？])', t):
        s = sent.strip()
        if not s:
            pos += len(sent); continue
        start = t.find(s, pos)
        pos = start + len(s) if start >= 0 else pos
        _prev = prev_sent
        prev_sent = s
        # 跨句承接：本句以治法動詞開頭，則證取自上一句
        if VERB_RE.match(s) and _prev and DISEASE_RE.search(_prev):
            s_use, zheng_pre = _prev + s, _prev
        else:
            s_use, zheng_pre = s, None
        m = None
        for cand in VERB_RE.finditer(s_use):
            if cand.start() == 0 and zheng_pre is None:
                continue
            if s_use[cand.start() - 1] in '鍼錐':
                continue        # 「錐鍼刺其心」屬比喻，非處置
            m = cand
            break
        if not m:
            continue
        if s_use[m.start():m.start() + 3] == '取之處':
            continue
        zheng = s_use[:m.start()].strip('，。； ')
        zhi = s_use[m.start():].strip('。')
        if BAD.match(zhi) or not TREAT_CH.search(zhi) or len(zhi) < 3:
            continue
        # 品質過濾：問答標記、空泛治法
        if re.search(r'[曰問]', zheng):
            continue
        if re.fullmatch(r'[寫補取刺灸]{1,3}', zhi):
            continue
        # 禁忌：動詞前有 不／勿／不可／皆不可
        if re.search(r'[不勿]$', zheng) or re.search(r'(不可|勿)$', s_use[:m.start()]):
            proh.append({'篇序': n, '篇名': J[n]['篇名'],
                         '禁': s_use.strip('。'), '證': re.sub(r'[不勿]$', '', zheng),
                         '位置': start})
            continue
        if len(zheng) < 2 or len(zheng) > 80:
            continue
        if not DISEASE_RE.search(zheng):
            continue
        if re.match(r'^(其|故|凡|此|是以|所以|若夫)', zheng):
            continue
        forms = list(ACU) + list(ALIAS)
        aps = [ALIAS.get(f, f) for f in forms if f in zhi]
        mers = [a + b for a, b in MER_RE.findall(zhi)]
        types = [k for k, p in TREAT_TYPE if re.search(p, zhi)]
        grade = '高' if (aps or mers or re.search(r'[取刺]' + r'[^，。]{2,}', zhi)) else '中'
        rows.append({'篇序': n, '篇名': J[n]['篇名'], '證': zheng, '治': zhi,
                     '可信度': grade,
                     '取穴': '、'.join(sorted(set(aps))), '取經': '、'.join(dict.fromkeys(mers)),
                     '治法類型': '、'.join(dict.fromkeys(types)),
                     '原文': s_use, '位置': start})

with open(os.path.join(ROOT, 'data', '關係_證治.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

with open(os.path.join(ROOT, 'data', '關係_禁忌.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=['篇序', '篇名', '證', '禁', '位置'])
    w.writeheader(); w.writerows(proh)

stat = {'證治筆數': len(rows), '禁忌筆數': len(proh),
        '分篇': dict(Counter(r['篇序'] for r in rows)),
        '有取穴': sum(1 for r in rows if r['取穴']),
        '有取經': sum(1 for r in rows if r['取經']),
        '治法類型分布': dict(Counter(t for r in rows for t in r['治法類型'].split('、') if t))}
json.dump(stat, open(os.path.join(ROOT, 'data', '病證統計.json'), 'w'),
          ensure_ascii=False, indent=1)
print(json.dumps(stat, ensure_ascii=False, indent=1))
print("\n--- 樣本 ---")
for r in rows[:6]:
    print(f"[{r['篇序']}] 證：{r['證'][:34]}")
    print(f"     治：{r['治'][:46]}")
    print(f"     穴：{r['取穴'] or '—'}｜經：{r['取經'] or '—'}｜類：{r['治法類型']}")
