#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""概念檔案（concept dossier）：把一個概念在原文中的「用法」系統地攤開。

目的：讓「本真」的判斷建立在可查的分類上，而不是憑印象挑句子。
每個概念輸出四類：
  1. 定義型句   —— 何謂X／所謂X／X者…也／謂之X
  2. 對舉句     —— 同一句裡 X 與另一概念並列（判斷邊界）
  3. 動態句     —— 含 行/伏/浮/出/入/上/下/間/內/外/藏/舍 等位置與運動詞
  4. 搭配      —— X 前後的字（看它「被當作什麼」使用）
"""
import json, os, re, csv
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONCEPTS = [
    '氣', '血', '神', '精', '津', '液', '脈', '經', '絡',
    '營', '衛', '宗氣', '邪', '虛', '實', '陰', '陽',
    '藏', '府', '三焦', '筋', '骨', '皮', '肉', '志', '魂', '魄',
]

MOTION = re.compile(r'[行伏浮出入上下間內外藏舍守流行環轉注合]')
DEF_PAT = ['何謂{}', '所謂{}', '{}者', '謂之{}', '是謂{}', '名為{}', '名曰{}']


def norm(s):
    return (s.replace('脉', '脈').replace('隂', '陰').replace('爲', '為')
             .replace('穀', '穀').replace('藏', '藏'))


def load():
    d = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']
    out = []
    for p in d:
        for s in re.split(r'(?<=[。！？])', p['句讀']):
            s = s.strip()
            if s:
                out.append((p['序'], p['篇名'], s))
    return out


def main():
    sents = load()
    os.makedirs(os.path.join(ROOT, 'data', '概念檔案'), exist_ok=True)
    summary = []

    for c in CONCEPTS:
        hit = [(n, pn, s) for n, pn, s in sents if c in norm(s)]
        if not hit:
            continue
        defs, motion = [], []
        for n, pn, s in hit:
            if any(pat.format(c) in s for pat in DEF_PAT):
                defs.append({'篇序': n, '篇名': pn, '句': s})
            if MOTION.search(s):
                motion.append({'篇序': n, '篇名': pn, '句': s})

        # 對舉：與其他概念共現於同一句（排除自身）
        co = Counter()
        for n, pn, s in hit:
            t = norm(s)
            for o in CONCEPTS:
                if o != c and o in t:
                    co[o] += 1

        # 搭配：概念前後各一字
        before, after = Counter(), Counter()
        for n, pn, s in hit:
            t = norm(s)
            i = t.find(c)
            while i >= 0:
                if i > 0:
                    before[t[i - 1]] += 1
                if i + len(c) < len(t):
                    after[t[i + len(c)]] += 1
                i = t.find(c, i + 1)

        dossier = {
            '概念': c, '出現次數': len(hit), '出現篇數': len({x[0] for x in hit}),
            '定義型句': defs[:40],
            '動態句': motion[:40],
            '共現概念': co.most_common(10),
            '前接字': before.most_common(12),
            '後接字': after.most_common(12),
        }
        json.dump(dossier, open(os.path.join(ROOT, 'data', '概念檔案', f'{c}.json'),
                                'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        summary.append({
            '概念': c, '次數': len(hit), '篇數': len({x[0] for x in hit}),
            '定義型': len(defs), '動態': len(motion),
            '主要共現': '、'.join(f'{k}{v}' for k, v in co.most_common(4)),
            '主要後接': '、'.join(f'{k}{v}' for k, v in after.most_common(4)),
        })

    with open(os.path.join(ROOT, 'data', '概念總覽.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['概念', '次數', '篇數', '定義型', '動態', '主要共現', '主要後接'])
        w.writeheader()
        w.writerows(summary)

    print(f"{'概念':<4}{'次數':>5}{'篇':>4}{'定義':>5}{'動態':>5}  主要共現")
    for r in summary:
        print(f"{r['概念']:<4}{r['次數']:>5}{r['篇數']:>4}{r['定義型']:>5}{r['動態']:>5}  {r['主要共現']}")


if __name__ == '__main__':
    main()
