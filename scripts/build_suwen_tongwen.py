#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""靈樞 × 素問 同文表：哪一篇靈樞，和哪一篇素問說同樣的話。

做法（不靠人手配對）：
1. 素問按「篇」切出正文（用卷文本的篇首偏移）。缺名之篇（26/46/50/72）照樣切，標「未名篇」。
2. 靈樞每篇 vs 素問每篇，算 4-gram 重合率，取前三。
3. 逐句核同文：靈樞每句（併字後 ≥8 字）若能在該素問篇找到逐字片段，記一段同文。
4. 只報「重合率 ≥10%」的篇對；句級同文另給例子。

輸出：data/素問同文.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_zhangzhu import norm_map  # noqa: E402


def suwen_pian():
    d = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))
    out = []
    for j in d['卷']:
        text = j['文本']
        ps = j['篇']
        for i, p in enumerate(ps):
            end = ps[i + 1]['起'] if i + 1 < len(ps) else len(text)
            body = text[p['起']:end]
            name = p['名'] or ''
            if not name:
                name = '（卷%d未名篇 %d）' % (j['卷'], p['序'])
            out.append({'序': p['序'], '名': name, '卷': j['卷'],
                        'norm': norm_map(body)[0]})
    return out


def grams(s, n=4):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def longest_blocks(a, b, minlen=12):
    import difflib
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [x for x in sm.get_matching_blocks() if x.size >= minlen]


def main():
    import difflib
    ch = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    byp = {}
    for s0 in ju:
        byp.setdefault(s0['pian'], []).append(s0)

    sq = suwen_pian()
    sq_g = [(x, grams(x['norm'])) for x in sq]
    sq_by_name = {x['名']: x for x in sq}

    # 1) 逐句同文（逐字相同者）
    same = []
    for s0 in ju:
        n = norm_map(s0['text'])[0]
        if len(n) < 8:
            continue
        for p in sq:
            if n in p['norm']:
                same.append({'id': s0['id'], '靈樞篇': s0['pian'], '文': s0['text'][:70],
                             '素問': p['名'], '素問卷': p['卷']})
                break

    # 2) 篇對：4-gram 重合 ≥3% 者，另算長同文段
    pairs = []
    for p in ch:
        a = norm_map(p['正規化'])[0]
        gn = grams(a)
        if not gn:
            continue
        for x, g in sq_g:
            if not g:
                continue
            ov = len(gn & g) / len(gn)
            if ov < 0.03:
                continue
            blocks = longest_blocks(a, x['norm'])
            cnt = sum(1 for y in byp.get(p['篇名'], [])
                      if len(norm_map(y['text'])[0]) >= 8 and norm_map(y['text'])[0] in x['norm'])
            pairs.append({'靈樞序': p['序'], '靈樞': p['篇名'],
                          '素問': x['名'], '素問卷': x['卷'],
                          '重合': round(ov * 100, 1), '段數': len(blocks),
                          '同文句': cnt,
                          '例': [{'字數': b.size, '文': a[b.a:b.a + b.size][:80]} for b in blocks[:3]]})
    pairs.sort(key=lambda y: -y['重合'])

    data = {'說明': '靈樞 × 素問同文表：①逐字相同的句子；②4-gram 重合 ≥3% 的篇對（附 ≥12 字的長同文段）。'
                   '「重合」分母是靈樞該篇的 4-gram 數。',
            '來源': '底本/靈樞經_81篇.json、底本/素問_經文.json（注已剝離）',
            '方法': '4-gram 重合率 ＋ difflib 長同文段（≥12 字）；素問缺名之篇照切，標「未名篇」',
            '統計': {'同文句': len(same), '篇對': len(pairs),
                     '重合≥30%的篇對': sum(1 for x in pairs if x['重合'] >= 30),
                     '段數合計': sum(x['段數'] for x in pairs)},
            '句': same, '篇對': pairs}
    json.dump(data, open(os.path.join(ROOT, 'data', '素問同文.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(data['統計'])
    for x in pairs[:6]:
        print(f"{x['靈樞']}（{x['重合']}%）↔ {x['素問']}：段 {x['段數']}、句 {x['同文句']}")




if __name__ == '__main__':
    main()
