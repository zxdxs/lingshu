#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從八十一篇抽出「定義句」候選池，寫出 data/定義句.json。

用途：通則（data/通則.json）是編者挑過的；這一支是**機器抽出、未經挑選**的候選池，
讓下一個人（或下一輪）不必從零重掃。判準全部寫在 REGEX 裡，可重算。

用法：python3 scripts/build_definitions.py
"""
import json, os, re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

# 三種定義句式：X者，Y也／所謂X者…／何謂X
PATTERNS = {
    '者…也': re.compile(r'[^，。；]{2,14}者，[^。]{4,80}也。?$'),
    '所謂…者': re.compile(r'所謂[^。]{2,40}者'),
    '何謂': re.compile(r'^[^。]{0,8}何謂'),
}

# 粗略分桶（只為了導覽；一條句子可落多桶）
BUCKETS = {
    '神': ['神', '魂', '魄', '意', '志', '思', '慮', '智'],
    '氣血津液': ['氣', '血', '津', '液', '精', '脉'],
    '營衛': ['營', '衛'],
    '藏府': ['藏', '府', '五藏', '六府', '三焦'],
    '經脈': ['經', '脉', '絡', '谿', '節'],
    '診法': ['色', '脉', '尺', '診', '候'],
    '刺法': ['鍼', '刺', '寫', '補', '留'],
    '病變': ['病', '痛', '死', '傳', '痺', '積'],
    '時間': ['日', '月', '時', '嵗', '歲', '晝', '夜'],
    '傳承': ['傳', '教', '言', '授', '禁'],
}


def main():
    hits = []
    for s in JU:
        t = s['text']
        if len(t) < 8 or len(t) > 90:
            continue
        kinds = [k for k, p in PATTERNS.items() if p.search(t)]
        if not kinds:
            continue
        buckets = [b for b, kws in BUCKETS.items() if any(k in t for k in kws)]
        hits.append({'id': s['id'], '篇': s['pian'], 'seq': s['seq'],
                     '文': t, '句式': kinds, '桶': buckets})
    per_pian = Counter(h['篇'] for h in hits)
    per_bucket = Counter(b for h in hits for b in h['桶'])
    data = {
        '說明': {'來源': '底本/靈樞經_句索引.json',
                 '方法': '三種句式正則（見腳本 PATTERNS）＋關鍵字分桶；未經人工挑選',
                 '用途': '擴充通則時的候選池；正式通則見 data/通則.json'},
        '候選數': len(hits),
        '每篇': per_pian.most_common(),
        '分桶': per_bucket.most_common(),
        '句': hits,
    }
    out = os.path.join(ROOT, 'data', '定義句.json')
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {out}：候選 {len(hits)} 句；最多的篇 {per_pian.most_common(3)}')


if __name__ == '__main__':
    main()
