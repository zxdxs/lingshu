#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨書引文稽核：檢查 data/異同_敘述.json 的每一條引文，是否真在所標來源裡。

與 check_quotes.py 的差別：那一支只認《靈樞》一篇對一篇；這一支要比對三種來源——
靈樞、素問、類經，各自一份語料，並用同一張異體字表（VAR）。

用法：python3 scripts/audit_cross_quotes.py [--json]
"""
import csv, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CORPUS_FILES = {
    '靈樞': os.path.join(ROOT, '底本', '靈樞經_81篇.json'),
    '素問': os.path.join(ROOT, '底本', '素問_經文.json'),
}


def load_corpora():
    out = {}
    ch = json.load(open(CORPUS_FILES['靈樞'], encoding='utf-8'))['篇']
    out['靈樞'] = norm(''.join(p['經文'] for p in ch))
    sw = json.load(open(CORPUS_FILES['素問'], encoding='utf-8'))['卷']
    out['素問'] = norm(''.join(j['文本'] for j in sw))
    lj = ''.join(open(f, encoding='utf-8').read()
                 for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '*.txt'))))
    out['類經'] = norm(lj)
    return out


def source_of(label):
    for k in ('靈樞', '素問', '類經'):
        if k in label:
            return k
    return None


def main():
    corpora = load_corpora()
    data = json.load(open(os.path.join(ROOT, 'data', '異同_敘述.json'), encoding='utf-8'))
    rows, bad = [], 0
    for item in data.get('名實', []):
        src = source_of(item['來源'])
        q = item['引']
        ok = bool(src) and norm(q) in corpora[src]
        rows.append({'來源': item['來源'], '語料': src or '?', '引': q, '結果': '相符' if ok else '不符'})
        bad += 0 if ok else 1
    # 敘述層裡所有「…」也一併驗（只驗看起來像原文的長句，避免把自撰詞誤判）
    for key in ('引言', '怎麼用', '未做'):
        val = data.get(key)
        texts = [val] if isinstance(val, str) else (val or [])
        for t in texts:
            for q in __import__('re').findall(r'「([^」]{6,})」', t):
                hit = [k for k in corpora if norm(q) in corpora[k]]
                rows.append({'來源': '（敘述層）', '語料': hit[0] if hit else '?', '引': q,
                             '結果': '相符' if hit else '不符'})
                bad += 0 if hit else 1
    if '--json' in sys.argv:
        print(json.dumps({'不符': bad, '條目': rows}, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print(f"  {'✓' if r['結果'] == '相符' else '✗'} {r['語料']:<4} {r['引'][:34]}")
        print(f"跨書引文：{len(rows)} 條，不符 {bad}")
    return 0 if bad == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
