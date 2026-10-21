#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把說明文件裡「不是《靈樞》原文」的「」改成『』，並產出待人工處理清單。

公約：「」只給《靈樞》原文；『』給其他典籍、注家、自撰詞。
分類（可機器判定）：
  他書     該段見於類經／素問／太素
  靈樞節引 該段是靈樞底本的子序列（字都在、順序對、不連續）→ 不自動改，留人工
  近似     與底本差一個字 → 不自動改，留人工（可能是漏收的異體字）
  自撰     其餘 → 改成『』

用法：python3 scripts/clean_quotes.py [--write]
"""
import glob, json, os, re, sys, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

base_txt = ''.join(norm(p['正規化']) for p in
                   json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇'])
other_txt = ''
for pat in ('vendor/KR3e0085_類經/*.txt', 'vendor/KR3e0001_素問/*', 'vendor/KR3ea031_太素/*.yaml'):
    for f in glob.glob(os.path.join(ROOT, pat)):
        other_txt += norm(open(f, encoding='utf-8', errors='ignore').read())


def subseq(s, t):
    it = iter(t)
    return all(ch in it for ch in s)


def cover4(s, t):
    """q 的 4-gram 有多少比例見於底本：判「這段是不是原文摘錄」。"""
    s = s if len(s) >= 4 else s
    if len(s) < 4:
        return 0.0
    grams = [s[i:i + 4] for i in range(len(s) - 3)]
    return sum(1 for g in grams if g in t) / len(grams)


def near(s, t, w=6):
    """s 與 t 中某段長度相近者差 ≤1 字。"""
    L = len(s)
    for i in range(0, max(1, len(t) - L + 3)):
        seg = t[i:i + L]
        if abs(len(seg) - L) > 1:
            continue
        d = sum(1 for a, b in zip(s, seg) if a != b) + abs(len(s) - len(seg))
        if d <= 1:
            return True
    return False


def classify(q):
    s = norm(q)
    if not s:
        return '空白'
    if s in base_txt:
        return '原文'
    if s in other_txt:
        return '他書'
    if len(s) >= 6 and cover4(s, base_txt) >= 0.6:
        return '靈樞節引'
    if len(s) >= 6 and near(s, base_txt):
        return '近似'
    return '自撰'


def main():
    write = '--write' in sys.argv
    rows = []
    files = sorted(glob.glob(os.path.join(ROOT, 'docs', '*.md'))) + \
            [os.path.join(ROOT, 'README.md'), os.path.join(ROOT, 'export', 'README.md')]
    total = changed = 0
    for path in files:
        text = open(path, encoding='utf-8').read()
        for m in re.finditer(r'「([^」]{4,})」', text):
            q = m.group(1)
            if '…' in q:
                continue
            k = classify(q)
            if k == '原文':
                continue
            total += 1
            rows.append({'檔': os.path.relpath(path, ROOT), '引文': q[:60], '類型': k})
        if write:
            def repl(mm):
                q = mm.group(1)
                if '…' in q:
                    return mm.group(0)
                if classify(q) in ('他書', '自撰'):
                    return '『' + q + '』'
                return mm.group(0)
            new = re.sub(r'「([^」]{4,})」', repl, text)
            if new != text:
                open(path, 'w', encoding='utf-8').write(new)
                changed += 1
    from collections import Counter
    c = Counter(r['類型'] for r in rows)
    print('不符公約引文', total, dict(c), '｜改寫檔案', changed)
    out = os.path.join(ROOT, 'data', '引號稽核.csv')
    with open(out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['檔', '引文', '類型'])
        w.writeheader(); w.writerows(rows)
    print('清單', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
