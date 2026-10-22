#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""算「八十一篇被哪幾層收錄」，寫出 data/篇_收錄.json。

層：通則、病候、經脉諸層（經脉/經别/經筋/十五絡/經水/五輸/十二原）、概念、模組、題、異同、癰疽。
只做計數，不評價值；用途是找出「只有題目、沒有解讀層」的篇，作為下一批挖掘的清單。

用法：python3 scripts/build_coverage_map.py
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
NAME = {p['序']: p['篇名_規範'] for p in CH}


def sid2seq(sid):
    try:
        return int(str(sid).split('-')[0])
    except Exception:
        return None


def main():
    cov = {p['序']: set() for p in CH}

    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    for g in law['組']:
        for x in g['條']:
            for q in x['引']:
                s = sid2seq(q['id'])
                if s in cov:
                    cov[s].add('通則')

    bh = json.load(open(os.path.join(ROOT, 'data', '病候.json'), encoding='utf-8'))
    for g in bh['組']:
        for x in g['條']:
            for q in x['證'] + x['治']:
                s = sid2seq(q['id'])
                if s in cov:
                    cov[s].add('病候')

    for f, key, tag in [('十二經病候.json', '經', '經脉'), ('五輸.json', '輸', '五輸'),
                        ('經水.json', '水', '經水'), ('經别.json', '正', '經别'),
                        ('經筋.json', '筋', '經筋'), ('絡脉.json', '絡', '十五絡'),
                        ('十二原.json', '原', '十二原'), ('癰疽死期.json', '癰疽', '癰疽')]:
        p = os.path.join(ROOT, 'data', f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for x in d.get(key, []):
            sid = x.get('id')
            if not sid and isinstance(x.get('起止'), dict):
                sid = x['起止'].get('id')
            if not sid and isinstance(x.get('名'), dict):
                sid = x['名'].get('id')
            s = sid2seq(sid)
            if s in cov:
                cov[s].add(tag)

    for f in glob.glob(os.path.join(ROOT, 'data', '多層_*.json')):
        d = json.load(open(f, encoding='utf-8'))
        for L in (d.get('組') or [{}])[0].get('層', []):
            m = re.search(r'第?\s*(\d+)\s*篇', L.get('出處', ''))
            if m and int(m.group(1)) in cov:
                cov[int(m.group(1))].add('概念')

    for f in glob.glob(os.path.join(ROOT, 'data', '模組_*.json')):
        d = json.load(open(f, encoding='utf-8'))
        srcs = d.get('出處', [])
        if isinstance(srcs, dict):
            srcs = [srcs]
        for src in srcs:
            if isinstance(src, dict):
                s = src.get('篇序')
            else:
                s = int(str(src).strip()) if str(src).strip().isdigit() else None
            if s in cov:
                cov[s].add('模組')

    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    for i in items:
        cov[i['source']['篇序']].add('題')

    suwen = json.load(open(os.path.join(ROOT, 'data', '異同_敘述.json'), encoding='utf-8'))
    # 異同頁引文若落在某篇，即記一筆（以引文字串比對）
    ROWS = [{'序': s, '篇': NAME[s], '層': sorted(v),
             '只有題': sorted(v) == ['題']} for s, v in sorted(cov.items())]
    onlyq = [r for r in ROWS if r['只有題']]

    # 任務線：把 81 篇分成七條線，看每條線覆蓋到哪
    LINES = [
     ('L1 病因發病', '邪從哪裡來、為什麼發病', [66, 46, 58, 34, 59]),
     ('L2 診法', '看什麼、怎麼看', [49, 37, 29, 28, 51, 65]),
     ('L3 刺法', '用什麼、什麼時候停', [7, 67, 75, 68, 26, 55]),
     ('L4 病候', '病的寫法與界限', [23, 70, 22, 69, 35, 57]),
     ('L5 體質', '什麼人先病', [6, 72, 64, 38, 50, 53]),
     ('L6 氣機', '氣怎麼走、在哪裡匯', [16, 76, 52, 62, 33, 36]),
     ('L7 傳承方法', '誰能學、怎麼傳', [48, 73, 60, 42]),
    ]
    covmap = {r['序']: r for r in ROWS}
    lines = []
    for name, desc, seqs in LINES:
        got = [s for s in seqs if not covmap[s]['只有題']]
        lines.append({'線': name, '說明': desc,
                      '篇': [{'序': s, '篇': NAME[s], '狀態': ('有' if not covmap[s]['只有題'] else '只有題')}
                             for s in seqs],
                      '已': len(got), '共': len(seqs)})
    data = {'說明': {'層': '通則／病候／經脉諸層（含八籤）／概念／模組／題',
                     '用途': '找「只有題目、沒有解讀層」的篇'},
            '統計': {'篇': len(ROWS),
                     '有解讀層': sum(1 for r in ROWS if not r['只有題']),
                     '只有題': len(onlyq)},
            '只有題的篇': [{'序': r['序'], '篇': r['篇']} for r in onlyq],
            '任務線': lines,
            '存而不論': [{'序': 77, '篇': '九宫八風',
                          '理由': '九宫八風是占術系統（九宫、八風、太一移日），與針灸原理不同層；'
                                  '硬抽成一條「原則」會失真。本站收其文，不強作通則。'}] if 77 in cov else [],
            '篇': ROWS}
    p = os.path.join(ROOT, 'data', '篇_收錄.json')
    json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {p}：{len(ROWS)} 篇；有解讀層 {data["統計"]["有解讀層"]}、只有題 {len(onlyq)}')


if __name__ == '__main__':
    main()
