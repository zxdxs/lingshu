#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""題目校準（item calibration）——在沒有作答資料的前提下，能做的與不能做的。

能做：
  1. 內容可追溯性：每題是否落在一個具體原文 span 上（有 source 且 answer 見於該篇經文）
  2. 形式健全性：答案洩漏、空答案、干擾項數量、重複題
  3. 先驗難度（prior difficulty）：由答案長度、題型、Bloom 層級、干擾項同質性合成
不能做：
  4. 難度參數（IRT b）、區辨度（a）、猜測參數（c）—— 全需作答資料，本階段一律空缺，不以估計值冒充

輸出的「先驗難度」是設計指標，不是實測難度；欄位名刻意與 IRT 參數分開。
"""
import json, os, re, csv
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')

# 穴名、藏府名在版本間常用的異體／別寫。只用於「可追溯性」判定，不改動題面答案。
ALIAS = [('太', '大'), ('俞', '腧'), ('腧', '輸'), ('谿', '溪'), ('臟', '藏'),
         ('宮', '宫'), ('朿', '束'), ('抒', '杼'), ('楡', '俞'), ('脉', '脈'),
         ('别', '別'), ('卽', '即'), ('麤', '粗'), ('痠', '酸'),
         ('乗', '乘'), ('虛', '虚'), ('髪', '髮'), ('眞', '真'), ('髎', '窌'), ('痺', '痹'), ('癉', '疸')]


def var_ok(a, t):
    """可追溯性判定：容許版本異體、虛詞增刪與語序微差。

    先試直引與異體替換，再退到 2-gram 覆蓋率 ≥0.8
    （處理「主左足之少陽」對「左足少陽」這類壓縮標籤）。
    """
    a, t = _vn(a), _vn(t)
    if a in t:
        return True
    for x, y in ALIAS:
        for s_, d_ in ((x, y), (y, x)):
            if s_ in a and a.replace(s_, d_) in t:
                return True
    if len(a) < 2:
        return False
    g = [a[i:i + 2] for i in range(len(a) - 1)]
    return sum(1 for x in g if x in t) / len(g) >= 0.8


def han(s):
    return ''.join(ch for ch in s if CJK.match(ch))


# 章際用字與異寫的等價類（僅供比對）
_COLLAPSE = {'於': 'A', '于': 'A', '扵': 'A', '爲': 'B', '為': 'B', '隂': 'C', '陰': 'C',
             '荅': 'D', '答': 'D', '圎': 'E', '圓': 'E', '緻': 'F', '致': 'F', '閲': 'G',
             '閱': 'G', '舎': 'H', '舍': 'H', '徃': 'I', '往': 'I', '黄': 'J', '黃': 'J',
             '黒': 'K', '黑': 'K', '眞': 'L', '真': 'L', '徧': 'M', '遍': 'M', '痺': 'N',
             '痹': 'N', '脉': 'O', '脈': 'O', '衞': 'P', '衛': 'P', '夀': 'Q', '壽': 'Q',
             '嵗': 'R', '歲': 'R', '歳': 'R', '别': 'S', '別': 'S', '絶': 'T', '絕': 'T',
             '㑹': 'U', '會': 'U', '榖': 'V', '穀': 'V', '竒': 'W', '奇': 'W', '靣': 'X',
             '面': 'X', '寫': 'Z', '瀉': 'Z'}


def _cl(s):
    return ''.join(_COLLAPSE.get(c, c) for c in s)


def _overlap4(a, b):
    ga = {a[i:i + 4] for i in range(max(1, len(a) - 3))}
    gb = {b[i:i + 4] for i in range(max(1, len(b) - 3))}
    return len(ga & gb) / len(ga) if ga else 0.0


_VT = {}
with open(os.path.join(ROOT, '底本', '異體字規範表.csv'), encoding='utf-8-sig') as _f:
    for _r in csv.DictReader(_f):
        if len(_r['原始字形']) == 1 and len(_r['規範字形']) == 1:
            _VT[_r['原始字形']] = _r['規範字形']


def _vn(s):
    return ''.join(_VT.get(c, c) for c in s)


def load():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    pian = {int(p['序']): p for p in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
    return items, pian


BLOOM = {'remember': 0, 'understand': 1, 'apply': 2, 'evaluate': 3}
TYPE = {'mcq': 0, 'fill_blank': 1, 'error_identification': 2}


def ans_band(n):
    if n < 4:
        return 0
    if n < 10:
        return 1
    if n < 20:
        return 2
    return 3


def prior_difficulty(it):
    a = ans_band(len(it['answer']))
    t = TYPE.get(it['type'], 1)
    if it['auto_grading'] == 'rubric':
        t = 3
    elif it['auto_grading'] == 'fuzzy' and it['type'] == 'fill_blank':
        t = 2
    b = BLOOM.get(it['bloom'], 1)
    raw = a + t + b
    # 干擾項若全取自同篇，辨義更難
    same = False
    if it['type'] == 'mcq' and it.get('distractors'):
        same = True  # 生成時干擾項皆取自同書他處；同篇與否另計
    score = 1 + min(4, raw / 3.0)  # 1.0 – 5.0
    return round(score, 1), same


def flags(it, pian):
    f = []
    ans = han(it['answer'])
    if it['type'] == 'fill_blank' and len(ans) > 20 and it['auto_grading'] != 'rubric':
        f.append('F1 答案過長而未轉評分制')
    if it['type'] == 'fill_blank' and 0 < len(ans) <= 1:
        _alt = it.get('可接受答案') or []
        f.append('F5 單字答案：正解面寬，已用 fuzzy'
                 + (f'，已列 {len(_alt)} 個可接受異體' if _alt else '，僅收原字（未列異體）'))
    if it['type'] == 'mcq':
        ds = it.get('distractors') or []
        if len(ds) < 2:
            f.append('F2 干擾項不足兩項')
        la = len(han(it['answer']))
        # 長句選項（如注→經題）不適用長度提示判定
        if 0 < la < 8:
            for d in ds:
                ld = len(han(d))
                if abs(ld - la) >= max(6, la):
                    f.append('F3 干擾項長度失配，可憑形式猜中')
                    break
    # F6 循環提示：答案直接出現在題面（去掉篇名後仍出現者）
    _s2 = re.sub(r'《[^》]*》', '', it['stem'])
    if ans and ans in _s2:
        f.append('F6 循環提示：答案見於題面')
    src = it.get('source') or {}
    n = src.get('篇序')
    txt = pian.get(int(n), {}).get('正規化', '') if n else ''
    # 注→經題的答案出自《類經》該條的經文，未必逐字等同於本專案底本；
    # 其出處已記於「註家參照·條號」，故不以底本字串判其可追溯性。
    if it.get('note') == '注→經':
        r = _overlap4(_cl(han(it['answer'])), _cl(han(txt)))
        if r < 0.9:
            f.append(f'F4b 類經引文與底本該篇重合 {r:.2f}＜0.9，須核')
        return f
    if n and ans and len(ans) >= 8:
        # 長句答案以整句比對（標點與異體先歸一），不逐詞切
        if _vn(han(it['answer'])) in _vn(han(txt)):
            return f
        f.append('F4b 長句答案未能在所註篇逐字比對，須人工核')
        return f
    if n and ans:
        # 題面若直引原文，只要引文見於該篇，即算題目有錨點（答案可為壓縮標籤）
        layer = it.get('層級', 'L0')
        quotes = re.findall(r'「([^」]{4,})」', it['stem'])
        if any(var_ok(''.join(CJK.findall(q)), txt) for q in quotes):
            return f
        if layer == 'L1':
            # 概括題的答案本就是改寫，字串法只能做一個極弱的 sanity check：
            # 至少要有一個三字片段在本篇出現。達不到才提示人工核。
            core = ''.join(c for c in ans if c not in set('的與之其為是有會在不而也者所則以於即皆乃'))
            g3 = [core[i:i + 3] for i in range(len(core) - 2)]
            if not g3 or any(_vn(x) in _vn(txt) for x in g3):
                return f
            f.append('F4c 概括題與本篇幾無共同字串，建議人工核對篇旨')
            return f
        # 逐詞核：答案若為多穴／多項並列，各詞皆須見於該篇
        toks = [x for x in re.split(r'[、，／/；;：:（）()\s]+', it['answer']) if x]
        miss = [x for x in toks if not var_ok(x, txt)]
        if miss:
            if it['type'] == 'error_identification' or it['auto_grading'] == 'rubric' \
                    or any(len(x) > 12 for x in toks):
                f.append('F4b 合成答案，非原文字串，須人工核其出處')
            else:
                f.append('F4a 答案詞不見於所註篇：' + '/'.join(miss[:2]))
    return f


def main():
    items, pian = load()
    rows = []
    for it in items:
        score, same = prior_difficulty(it)
        fl = flags(it, pian)
        rows.append({
            'item_id': it['item_id'],
            '篇序': (it.get('source') or {}).get('篇序'),
            '篇名': (it.get('source') or {}).get('篇名'),
            '類型': it['type'],
            'bloom': it['bloom'],
            '自動評分': it['auto_grading'],
            '答案字數': len(han(it['answer'])),
            '干擾項數': len(it.get('distractors') or []),
            '先驗難度': score,
            '註家依據': it.get('依據類型', '') if it.get('層級') == 'L1' else '',
            '旗標': '；'.join(fl),
            'IRT_b': '',
            'IRT_a': '',
        })

    with open(os.path.join(ROOT, 'data', '題目校準.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"題數 {len(rows)}")
    print('先驗難度分布:', dict(sorted(Counter(r['先驗難度'] for r in rows).items())))
    print('旗標統計:', dict(Counter(k.split()[0] for r in rows for k in r['旗標'].split('；') if k)))
    cov = len({r['篇序'] for r in rows})
    l1 = [r for r in rows if r['註家依據']]
    if l1:
        from collections import Counter as _C
        c = _C('有註家對應注' if '有註家對應注' in r['註家依據'] else '自撰' for r in l1)
        print('L1 依據:', dict(c))
    print(f"覆蓋篇數 {cov}/81")
    miss = [n for n in pian if n not in {r['篇序'] for r in rows}]
    print('無題之篇:', ' '.join(f"{n}" for n in sorted(miss)))
    top = Counter(r['篇序'] for r in rows).most_common(6)
    print('題量最多:', top)
    print()
    for k in ('F1', 'F2', 'F3', 'F4', 'F5'):
        ex = [r['item_id'] for r in rows if k in r['旗標']][:4]
        n = sum(1 for r in rows if k in r['旗標'])
        if n:
            print(f"{k}: {n} 例 {ex}")

    json.dump({'題數': len(rows), '覆蓋篇數': cov, '無題篇': sorted(miss),
               '先驗難度分布': dict(sorted(Counter(r['先驗難度'] for r in rows).items()))},
              open(os.path.join(ROOT, 'data', '題目校準_摘要.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
