#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""算「靈樞 vs 素問」的五條差別裡可以量的部分，寫出 data/異同_量化.json。

五條差別本身是編者的判斷（見 docs/118）；這一支只負責把能算的算出來，
並且**刻意去找反證**——例如「靈樞更坦白界限」在詞頻上並不成立（素問的『死』更多）。

用法：python3 scripts/analyze_essence.py
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
SW = json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))['卷']
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

LP = norm(''.join(p['經文'] for p in CH))
SWN = norm(''.join(j['文本'] for j in SW))

# 應答者（含異寫）
ANSWERERS = {'岐伯': ['岐伯', '歧伯'], '伯高': ['伯高'], '少俞': ['少俞'],
             '雷公': ['雷公'], '少師': ['少師']}

# 量化單位：尺寸類與時間類分開，因為「量身體」與「算日子」不是同一種量化
UNITS_BODY = '寸尺丈分度周里斤兩斗升合龠'
UNITS_TIME = '日刻息壯遍宿'

TERM_SETS = {
    '時間（日週期）': ['晝', '夜', '旦', '夕', '日'],
    '時間（年與甲子）': ['歲', '年', '六十', '一紀', '朞'],
    '個體差異': ['肥', '瘦', '壯', '嬰', '老人', '布衣', '大人', '勇', '怯'],
    '界限與死期': ['死', '不治', '不可治', '死不治'],
    '師承痕跡': ['師', '岐伯', '雷公'],
}


def rate(term, text):
    k = norm(term)
    n = text.count(k)
    return n, round(n * 10000 / len(text), 1)


def answerers():
    tot = Counter()
    per = []
    for p in CH:
        c = {k: sum(p['經文'].count(v) for v in vs) for k, vs in ANSWERERS.items()}
        for k, v in c.items():
            tot[k] += v
        if any(c.values()):
            main = max(c, key=c.get)
            per.append({'序': p['序'], '篇': p['篇名_規範'], '主答': main,
                        '次數': c[main], '總': sum(c.values())})
    non = [x for x in per if x['主答'] != '岐伯']
    return [{'名': k, '次數': v} for k, v in tot.most_common()], non


def quantify(units):
    """句級：一句之內出現「數字＋單位」即算一條量化條文。規則寫死，可重算。"""
    pat = re.compile('[' + '一二三四五六七八九十百千萬半' + ']+(' + '|'.join(units) + ')')
    c = Counter()
    for s in JU:
        if pat.search(s['norm']):
            c[(s['pian'], s['seq'])] += 1
    return [{'篇': k[0], '序': k[1], '條': v} for k, v in c.most_common(12)]


def main():
    ans, non = answerers()
    data = {
        '應答者': {'總次數': ans, '非岐伯主答篇數': len(non), '非岐伯主答篇': non},
        '量化': {'量身體（寸尺丈分度…）': quantify(UNITS_BODY),
                 '量時間（日刻息壯遍宿）': quantify(UNITS_TIME),
                 '規則': '以句索引的每一句為單位；句內出現「數字＋下列單位」即計一條。'
                         'units 見腳本常數，可自行重算。'},
        '詞頻': {k: [{'詞': t, '靈樞': rate(t, LP)[0], '素問': rate(t, SWN)[0],
                      '靈樞萬字': rate(t, LP)[1], '素問萬字': rate(t, SWN)[1]} for t in ts]
                 for k, ts in TERM_SETS.items()},
    }
    out = os.path.join(ROOT, 'data', '異同_量化.json')
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {out}：應答者 {len(ans)} 人、非岐伯主答 {len(non)} 篇、'
          f'量化榜前 3：{[x["篇"] for x in data["量化"]["量身體（寸尺丈分度…）"][:3]]}')


if __name__ == '__main__':
    main()
