#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""算《靈樞》與《素問》的異同，寫出 data/素問對照.json。

原則：能算的都算，算不出來的不寫。
  - 規模、用字、篇名結構 → 直接計數
  - 逐字重出 → 靈樞句索引逐句在素問經文裡找（正規化後完全相同才算）
  - 平行篇 → 四字串覆蓋率（雙向），不靠印象配對

用法：python3 scripts/build_suwen.py && python3 scripts/compare_suwen.py
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

SW = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))
CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

# 素問：切篇（篇名行到下一篇名行；最後一篇到卷末）
SW_PIAN = []
for j in SW['卷']:
    heads = j['篇']
    for k, h in enumerate(heads):
        start = h['起']
        end = heads[k + 1]['起'] if k + 1 < len(heads) else len(j['文本'])
        seg = j['文本'][start:end]
        SW_PIAN.append({'名': h['名'], '序': h['序'], '卷': j['卷'], '文': seg, 'norm': norm(seg)})

SW_FULL = '\n'.join(j['文本'] for j in SW['卷'])
SW_NORM = norm(SW_FULL)


def grams(s, n=4):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def locate(word_norm):
    """回傳該片段在素問的（卷, 篇名）；找不到篇名就只給卷。"""
    pos = 0
    for j in SW['卷']:
        jn = norm(j['文本'])
        k = jn.find(word_norm)
        if k >= 0:
            name = None
            for h in j['篇']:
                # 篇名位置以原始文本計，先換算成 norm 位置
                pass
            return j['卷'], None
    return None, None


def shared_sentences(minlen=8):
    out = []
    for s in JU:
        n = s['norm']
        if len(n) < minlen or n not in SW_NORM:
            continue
        # 定位：逐卷找，並取該卷內位置前最近的篇名（以 norm 位置近似原文位置）
        where = None
        for p in SW_PIAN:
            if n in p['norm']:
                where = (p['卷'], p['名'])
                break
        out.append({'id': s['id'], 'pian': s['pian'], 'seq': s['seq'],
                    '文': s['text'], '素問卷': where[0] if where else None,
                    '素問篇': where[1] if where else None})
    # 去重（同一段文字可能被切成多句）
    seen, uniq = set(), []
    for x in out:
        k = x['文']
        if k in seen:
            continue
        seen.add(k)
        uniq.append(x)
    return uniq


def parallel_pian(top=6):
    res = []
    for p in CH:
        gs = grams(norm(p['正規化']))
        if len(gs) < 100:
            continue
        for q in SW_PIAN:
            gq = grams(q['norm'])
            if len(gq) < 100:
                continue
            inter = len(gs & gq)
            if not inter:
                continue
            cov_l = inter / len(gs)
            cov_s = inter / len(gq)
            if max(cov_l, cov_s) >= 0.05:
                res.append({'靈樞': p['篇名_規範'], '靈樞序': p['序'], '素問': q['名'],
                            '素問序': q['序'], '卷': q['卷'], '四字串': inter,
                            '覆蓋靈樞': round(cov_l * 100), '覆蓋素問': round(cov_s * 100)})
    res.sort(key=lambda x: (-max(x['覆蓋靈樞'], x['覆蓋素問']), -x['四字串']))
    return res[:top]


TERMS = ['鍼', '刺', '脉', '隂', '陽', '藏', '府', '運氣', '五運', '六氣', '天', '人',
         '病', '死', '熱', '寒', '虚', '實', '寫', '補', '骨', '筋', '血', '氣', '道']


def term_rates():
    """以 norm 後的鍵計數，異體（䤴/針、剌/刺、脉/脈、隂/陰）自動合併。"""
    lp = norm(''.join(p['經文'] for p in CH))
    sw = norm(SW_FULL)
    out = []
    for t in TERMS:
        k = norm(t)
        a, b = lp.count(k), sw.count(k)
        out.append({'詞': t, '靈樞': a, '素問': b,
                    '靈樞萬字': round(a * 10000 / len(lp), 1),
                    '素問萬字': round(b * 10000 / len(sw), 1)})
    return out


def main():
    lp_chars = sum(len(p['經文']) for p in CH)
    lp_norm = norm(''.join(p['正規化'] for p in CH))
    sw_norm = norm(SW_FULL)
    names_l = [p['篇名_規範'] for p in CH]
    names_s = [p['名'][:-1] if p['名'].endswith('篇') else p['名'] for p in SW['篇名']]

    def cjk(s):
        return len([c for c in s if '\u4e00' <= c <= '\u9fff'])

    shared = shared_sentences()
    data = {
        '統計': {
            '靈樞': {'篇': len(CH), '字': lp_chars, '卷': 24,
                     '篇名以論結尾': sum(1 for n in names_l if n.endswith('論')),
                     '篇名有論字': sum(1 for n in names_l if '論' in n)},
            '素問': {'篇': len(SW['篇名']), '字': cjk(SW_FULL), '卷': SW['統計']['卷數'],
                     '篇名以論結尾': sum(1 for n in names_s if n.endswith('論')),
                     '篇名有論字': sum(1 for n in names_s if '論' in n),
                     '亡篇': '刺法論（第七十二）',
                     '篇名行缺': SW['統計']['缺篇名']},
        },
        '重出句': shared,
        '平行篇': parallel_pian(),
        '用字': term_rates(),
        '篇名樣本': {'靈樞': names_l[:6], '素問': names_s[:6]},
    }
    out = os.path.join(ROOT, 'data', '素問對照.json')
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {out}：重出句 {len(shared)} 條、平行篇 {len(data["平行篇"])} 組、'
          f'靈樞 {lp_chars:,} 字 / 素問 {cjk(SW_FULL):,} 字')


if __name__ == '__main__':
    main()
