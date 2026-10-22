#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨書引文稽核：檢查 data/異同_敘述.json 的每一條引文，是否真在所標來源裡。

與 check_quotes.py 的差別：那一支只認《靈樞》一篇對一篇；這一支比對五種語料——
靈樞經文、素問經文、素問注（含王冰注與新校正）、類經、靈樞史崧序，
並用同一張異體字表（VAR）。

用法：python3 scripts/audit_cross_quotes.py [--json]
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm


def load_corpora():
    out = {}
    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    out['靈樞'] = norm(''.join(p['經文'] for p in ch))
    sw = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))['卷']
    out['素問'] = norm(''.join(j['文本'] for j in sw))
    raw = ''.join(open(f, encoding='utf-8').read()
                  for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3e0001_素問', '*.txt'))))
    out['素問注'] = norm(raw)
    out['類經'] = norm(''.join(open(f, encoding='utf-8').read()
                            for f in sorted(glob.glob(os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '*.txt')))))
    out['靈樞序'] = norm(open(os.path.join(ROOT, 'vendor', 'KR3e0002-master', 'KR3e0002_000.txt'),
                          encoding='utf-8').read())
    return out


def source_of(label):
    """由來源字串決定該比對哪份語料。順序重要：先具體、後一般。"""
    if '史崧' in label or '靈樞》序' in label:
        return '靈樞序'
    if '新校正' in label:
        return '素問注'
    if '類經' in label:
        return '類經'
    if '素問' in label:
        return '素問'
    if '靈樞' in label:
        return '靈樞'
    return None


def check(items, corpora, rows):
    bad = 0
    for it in items:
        src = source_of(it['來源'])
        q = it['引']
        ok = bool(src) and norm(q) in corpora[src]
        rows.append({'來源': it['來源'], '語料': src or '?', '引': q, '結果': '相符' if ok else '不符'})
        bad += 0 if ok else 1
    return bad


def main():
    corpora = load_corpora()
    data = json.load(open(os.path.join(ROOT, 'data', '異同_敘述.json'), encoding='utf-8'))
    rows, bad = [], 0

    bad += check(data.get('名實', []), corpora, rows)
    bad += check(data.get('來歷', []), corpora, rows)
    for d in data.get('差別', []):
        bad += check(d.get('證據', []), corpora, rows)

    # 敘述層（引言／怎麼用／未做／各條的「說」與「反證」）裡的「」也要有出處
    prose = [data.get('引言', '')] + list(data.get('怎麼用', [])) + list(data.get('未做', []))
    for d in data.get('差別', []):
        prose += [d.get('說', ''), d.get('反證', ''), d.get('更正', ''), d.get('例外', '')]
    for t in prose:
        for q in re.findall(r'「([^」]{4,})」', t or ''):
            hit = [k for k in corpora if norm(q) in corpora[k]]
            rows.append({'來源': '（敘述層）', '語料': hit[0] if hit else '?', '引': q,
                         '結果': '相符' if hit else '不符'})
            bad += 0 if hit else 1

    if '--json' in sys.argv:
        print(json.dumps({'不符': bad, '條目': rows}, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print(f"  {'✓' if r['結果'] == '相符' else '✗'} {r['語料']:<4} {r['引'][:36]}")
        print(f"跨書引文：{len(rows)} 條，不符 {bad}")
    return 0 if bad == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
