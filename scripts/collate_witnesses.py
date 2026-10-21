#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三源對校：SBCK 底本 × 太素（唐·楊上善）× 類經（明·張介賓）

用途一：篇級覆蓋率 —— 每一篇有多少比例的 12-gram 能在另兩個見證本中找到。
        這決定「哪些篇做得了三源對校、哪些只有孤證」。
用途二：校勘點逐條檢索 —— 對已知疑讀，看兩源各作何字。

原則：太素、類經均為類編本，只作「見證」，不作底本；
      命中只表示「該讀法在此源出現」，不表示「此源如此作」。
"""
import json, os, re, csv, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 字形規範 ----------
VAR = {}
with open(os.path.join(ROOT, '底本', '異體字規範表.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        VAR[r['原始字形']] = r['規範字形']
# 補：見證本常見而底本表未收者
VAR.update({'隂': '陰', '為': '為', '衆': '眾', '來': '來', '眀': '明',
            '濇': '澀', '鍼': '鍼', '曚': '矇', '髙': '高', '蔵': '藏',
            '舎': '舍', '脱': '脫', '宫': '宮', '黒': '黑', '竒': '奇',
            '麤': '粗', '痺': '痹', '癉': '疸', '䐜': '脹', '俞': '腧',
            '兪': '腧', '輸': '腧', '寫': '瀉', '冩': '瀉', '補': '補',
            '敍': '敘', '閒': '間', '閒': '間', '彊': '強', '强': '強',
            '鬪': '鬥', '鬭': '鬥', '胷': '胸', '胷': '胸', '脇': '脅',
            '脇': '脅', '刾': '刺', '剌': '刺', '𥼶': '釋', '竝': '並',
            '并': '並', '葢': '蓋', '盖': '蓋', '卽': '即', '旣': '既',
            '敎': '教', '冐': '冒', '冐': '冒', '衇': '脈', '脉': '脈',
            '衞': '衛', '冲': '衝', '衝': '衝', '麪': '麵', '緫': '總',
            '冦': '寇', '冦': '寇', '冝': '宜', '冝': '宜', '冓': '冓',
            '冡': '冢', '冣': '最', '冭': '太', '冸': '泮', '冺': '泯',
            '凖': '準', '凢': '凡', '凣': '凡', '凥': '居', '凬': '風',
            '凮': '風', '刄': '刃', '刅': '創', '刋': '刊', '刦': '劫',
            '刧': '劫', '刬': '剗', '刼': '劫', '刽': '劊', '刾': '刺',
            '剏': '創', '剳': '札', '剺': '剺', '劒': '劍', '劔': '劍',
            '劕': '質', '劖': '劖', '劗': '劗', '劘': '劘', '劙': '劙',
            })

CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')


def norm(s: str) -> str:
    """只留漢字，統一異體。標點、空格、換行一律去除。"""
    out = []
    for ch in s:
        if not CJK.match(ch):
            continue
        out.append(VAR.get(ch, ch))
    return ''.join(out)


def load_base():
    d = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))
    return d['篇']


def read_all(path):
    with open(path, encoding='utf-8') as f:
        return norm(f.read())


TAISU = os.path.join(ROOT, 'vendor', 'KR3ea031_太素', '太素全文.txt')
LEIJING = os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '類經全文.txt')
ZHENGWEN = os.path.join(ROOT, '底本', '靈樞經_SBCK_底本.md')

# 兩個 n-gram 長度並用：K=12 測「連續可對」，K=4 測「字句有據」。
# 太素經文被楊上善注逐句割裂，K=12 會系統性低估，故必須同時報 K=4。
KS = (4, 12)


def grams(s, k, stride=3):
    return [s[i:i + k] for i in range(0, max(1, len(s) - k + 1), stride)]


def classify(row, names):
    """三源對校的可及性判讀。"""
    vals = {n: (row.get(n + 'K4', 0), row.get(n + 'K12', 0)) for n in names}
    k4s = [v[0] for v in vals.values()]
    if all(v < 10 for v in k4s):
        return '孤證（兩源皆不入）'
    if all(v[0] >= 30 for v in vals.values()):
        return '可對校（兩源皆有字句）'
    if all(v[1] >= 25 for v in vals.values()):
        return '可對校（兩源皆成段）'
    return '半可對（一源有、一源無）'


def main():
    pian = load_base()
    wit = {}
    if os.path.exists(TAISU):
        wit['太素'] = read_all(TAISU)
    if os.path.exists(LEIJING):
        wit['類經'] = read_all(LEIJING)

    rows = []
    for p in pian:
        base = norm(p['正規化'])
        if not base:
            continue
        row = {'篇序': int(p['序']), '篇名': p['篇名_規範'], '字數': len(base)}
        for name, txt in wit.items():
            for k in KS:
                g = grams(base, k)
                hit = sum(1 for x in g if x in txt)
                row[f'{name}K{k}'] = round(hit / len(g) * 100, 1)
        # 判讀：K4 高而 K12 低 ＝ 該源有字句依據但經文不連續（注文割裂）
        row['判讀'] = classify(row, list(wit))
        rows.append(row)

    with open(os.path.join(ROOT, 'data', '三源覆蓋率.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hdr = f"{'篇':<4}{'篇名':<11}{'字數':>6}"
    for name in wit:
        hdr += f"{name[:2] + 'K4':>8}{name[:2] + 'K12':>8}"
    print(hdr + '  判讀')
    for r in rows:
        line = f"{r['篇序']:<4}{r['篇名']:<11}{r['字數']:>6}"
        for name in wit:
            line += f"{r[name + 'K4']:>8}{r[name + 'K12']:>8}"
        print(line + '  ' + r['判讀'])

    # 匯總
    print('\n=== 匯總 ===')
    for name in wit:
        k4 = [r[name + 'K4'] for r in rows]
        k12 = [r[name + 'K12'] for r in rows]
        print(f"{name}: K4 平均 {sum(k4)/len(k4):.1f}%｜K12 平均 {sum(k12)/len(k12):.1f}%"
              f"｜K4≥30% 的篇 {sum(1 for v in k4 if v >= 30)}"
              f"｜K4<10%（疑不入此源）{sum(1 for v in k4 if v < 10)}")
    from collections import Counter
    print('判讀分布:', dict(Counter(r['判讀'] for r in rows)))

    json.dump({'KS': list(KS), 'stride': 3, '見證本': list(wit), '篇': rows},
              open(os.path.join(ROOT, 'data', '三源覆蓋率.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
