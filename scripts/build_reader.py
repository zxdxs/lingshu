#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成離線閱讀器資料：reader/assets/data.js（window.LS）。

資料全部取自現有 JSON/CSV，不手寫內容。
用法：python3 scripts/build_reader.py
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'reader', 'assets')


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


def main():
    ch = load('底本/靈樞經_81篇.json')['篇']
    ju = {c['序']: c for c in load('底本/靈樞經_句讀層.json')['篇']}
    items = load('data/題庫_示例.json')
    lim = list(csv.DictReader(open(os.path.join(ROOT, 'data', '能力邊界.csv'), encoding='utf-8-sig')))
    con = list(csv.DictReader(open(os.path.join(ROOT, 'data', '矛盾清單.csv'), encoding='utf-8-sig')))
    col = list(csv.DictReader(open(os.path.join(ROOT, 'data', '校勘點.csv'), encoding='utf-8-sig')))
    nd = list(csv.DictReader(open(os.path.join(ROOT, 'data', '表_九鍼.csv'), encoding='utf-8-sig')))
    sidx = load('底本/靈樞經_句索引.json')['句']
    byseq = {}
    for x in sidx:
        byseq.setdefault(x['seq'], []).append(x)
    themes = load('data/主題.json')['主題']
    for t in themes:
        for qq in t.get('句', []):
            n = __import__('check_quotes').norm(qq['文'])
            hit = ''
            for x in byseq.get(qq['篇'], []):
                if n and (n in x['norm'] or (len(x['norm']) >= 6 and x['norm'] in n)):
                    hit = x['id']; break
            qq['id'] = hit
        t['篇名'] = [next((p['篇名_規範'] for p in ch if p['序'] == s), '') for s in t.get('篇', [])]
        for st in t.get('路線', []):
            n = __import__('check_quotes').norm(st['證'])
            st['id'] = next((x['id'] for x in byseq.get(66, []) if n and (n in x['norm'] or (len(x['norm']) >= 6 and x['norm'] in n))), '')
    import glob as _g
    cpts = []
    for f in sorted(_g.glob(os.path.join(ROOT, 'data', '多層_*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        g = (d.get('組') or [{}])[0]
        cpts.append({'t': d.get('標題', ''), 's': d.get('副標', ''), 'w': g.get('字', ''),
                     'note': g.get('註', ''), 'layers': [{'ctx': L.get('語境', ''), 'txt': L.get('式', ''),
                                                          'src': L.get('出處', '')} for L in g.get('層', [])],
                     'png': '多層_' + g.get('字', '') + '.png'})

    juan = {}
    for p in ch:
        j = p.get('卷') or ''
        juan.setdefault(j, []).append(p)

    from collections import Counter as _C
    per = _C(i['source']['篇序'] for i in items['題'])
    pian = []
    for p in ch:
        seq = p['序']
        pian.append({
            'seq': seq, 'name': p['篇名_規範'], 'juan': p.get('卷', ''),
            'chars': len(p['經文']),
            'text': ju.get(seq, {}).get('句讀', p['經文']),
            'note': p.get('校記', ''),
            'items': per.get(seq, 0),
        })

    its = []
    for i in items['題']:
        its.append({
            'id': i['item_id'], 'seq': i['source']['篇序'], 'pian': i['source']['篇名'],
            'type': i['type'], 'bloom': i['bloom'], 'level': i.get('層級', ''),
            'stem': i['stem'], 'answer': i['answer'],
            'acc': i.get('可接受答案') or [],
            'note': i.get('note', ''), 'kind': i.get('答案類型', ''),
            'dis': i.get('distractors') or [],
            'case': '-CASE-' in i['item_id'], 'sid': i.get('句', ''),
        })

    rel = load('data/發布資訊.json')

    contact = load('data/聯絡.json')
    law = load('data/通則.json')
    mer = load('data/十二經病候.json')
    jb = load('data/經别.json')
    jj = load('data/經筋.json')
    luo = load('data/絡脉.json')
    js = load('data/經水.json')
    ws = load('data/五輸.json')
    bh = load('data/病候.json')
    yuan = load('data/十二原.json')
    yw = load('data/營衛.json')
    wuci = load('data/五刺.json')
    wuxie = load('data/五邪.json')
    bounds = load('data/界限分級.json')
    abscess = load('data/癰疽死期.json')
    covmap = load('data/篇_收錄.json')
    jiugong = load('data/九宫八風.json')
    zhujia = load('data/注家.json')
    jiayi = load('data/甲乙經.json')
    # 集註：data/張注.json 存全部 772 條注（節錄），data.js 只帶統計、81 條示例與通則對讀
    zz = load('data/張注.json')
    jizhu = {'說明': zz['說明'], '來源': zz['來源'], '取用': zz['取用'],
             '方法': zz['方法'], '局限': zz.get('局限', ''), '統計': zz['統計'],
             '篇': [{k: v for k, v in x.items() if k != '注'} for x in zz['篇']],
             '例': zz['例'], '通則': zz['通則']}
    leizhu = load('data/類經注.json')
    bianti = load('data/變體.json')
    dfn = load('data/定義句.json')
    defs = {'n': dfn['候選數'], 'pian': dfn['每篇'][:5], 'bucket': dfn['分桶'][:6]}
    suwen = {'narr': load('data/異同_敘述.json'), 'calc': load('data/素問對照.json'),
             'quant': load('data/異同_量化.json')}

    # 全站搜尋索引：只放標題與短摘要，避免 data.js 暴增
    VMAP = {}
    for canon, forms in load('export/異體映射.json')['映射'].items():
        for f in forms:
            VMAP[f] = canon

    def _n(x):
        return ''.join(VMAP.get(c, c) for c in x)

    search = []
    for p in ch:
        search.append({'k': '篇', 't': p['篇名_規範'], 'd': p['經文'][:40],
                       'n': _n(p['篇名_規範'] + p['經文'][:40]),
                       'h': '#/read?seq=' + str(p['序'])})
    for i in items['題']:
        search.append({'k': '題', 't': i['stem'][:44], 'd': i['source']['篇名'],
                       'n': _n(i['stem'][:44] + i['source']['篇名']),
                       'h': '#/items?seq=' + str(i['source']['篇序'])})
    for t in themes:
        search.append({'k': '主題', 't': t['題'], 'd': t['一句'][:40], 'h': '#/themes'})
    for q in law['組']:
        for x in q['條']:
            search.append({'k': '通則', 't': x['名'], 'd': x['原則'][:40],
                           'n': _n(x['名'] + x['原則'][:40]), 'h': '#/law?n=' + str(x['n'])})
    for x in mer['經']:
        search.append({'k': '十二經', 't': x['經'], 'd': (x['是動']['文'][:40] if x['是動'] else ''),
                       'h': '#/meridian?tab=jing&n=' + str(x['序'])})
    for q in bh['組']:
        for x in q['條']:
            search.append({'k': '病候', 't': x['病'], 'd': q['組'], 'h': '#/binghou'})
    for x in lim:
        search.append({'k': '限制', 't': x.get('問題', '')[:30], 'd': x.get('範疇', ''),
                       'h': '#/limits'})
    # 其餘頁面的條目（概念、九鍼、校勘、異同、十二原、五輸、經水、營衛、界限、癰疽）
    for c in cpts:
        search.append({'k': '概念', 't': c['w'] or c['t'], 'd': c['s'][:36],
                       'n': _n((c['w'] or c['t']) + c['s'][:36]), 'h': '#/concept'})
    for n in nd:
        search.append({'k': '九鍼', 't': n.get('鍼', ''), 'd': n.get('功能', '')[:34],
                       'n': _n(n.get('鍼', '') + n.get('功能', '')[:34]), 'h': '#/prep'})
    for r in col:
        search.append({'k': '校勘', 't': (r.get('錨點') or r.get('篇名', ''))[:34],
                       'd': (r.get('判定', '') or '')[:30],
                       'n': _n((r.get('錨點') or '') + (r.get('判定') or '')[:30]), 'h': '#/collation'})
    for x in suwen.get('narr', {}).get('差別', []):
        search.append({'k': '異同', 't': x['題'], 'd': x['主張'][:36],
                       'n': _n(x['題'] + x['主張'][:36]), 'h': '#/suwen'})
    for x in yuan.get('原', []):
        search.append({'k': '十二原', 't': x['藏'] + '之原：' + x['原'], 'd': x.get('屬性', ''),
                       'n': _n(x['藏'] + x['原']), 'h': '#/meridian?tab=yuan'})
    for x in ws.get('輸', []):
        names = '、'.join(v['穴'] for v in x['五輸'].values())
        search.append({'k': '五輸', 't': x['經'], 'd': names[:36],
                       'n': _n(x['經'] + names), 'h': '#/meridian?tab=shu'})
    for x in js.get('水', []):
        search.append({'k': '經水', 't': x['經'] + '—' + x['水'], 'd': x['內屬'][:20],
                       'n': _n(x['經'] + x['水'] + x['內屬']), 'h': '#/meridian?tab=shui'})
    for x in yw.get('營氣', {}).get('次序', []):
        search.append({'k': '營氣次序', 't': x['步'] + '. ' + x['經'], 'd': x['據'][:34],
                       'n': _n(x['經'] + x['據'][:34]), 'h': '#/meridian?tab=yw'})
    for x in bounds.get('級', []):
        search.append({'k': '界限', 't': x['級'] + ' ' + x['名'], 'd': x['說明'][:34],
                       'n': _n(x['名'] + x['說明'][:34]), 'h': '#/limits'})
    for x in abscess.get('癰疽', []):
        search.append({'k': '癰疽', 't': x['名'], 'd': x['部位'] + ('，' + x['死期'] if x['死期'] else ''),
                       'n': _n(x['名'] + x['部位'] + (x['死期'] or '')), 'h': '#/binghou'})


    data = {
        'meta': {
            'title': rel['站名'],
            'release': rel,
            'bendi': '四部叢刊景明嘉靖趙府居敬堂本（Kanripo KR3e0002）',
            'stats': {'pian': len(ch), 'chars': sum(len(p['經文']) for p in ch),
                      'quote_seg': sum(len(__import__('re').findall(r'「([^」]{2,})」', i['stem'])) for i in items['題']),
                      'items': items['題數'], 'fill': items['題型分布'].get('fill_blank', 0),
                      'mcq': items['題型分布'].get('mcq', 0),
                      'err': items['題型分布'].get('error_identification', 0),
                      'limits': len(lim), 'contradictions': len(con),
                      'ans_yuanwen': sum(1 for i in items['題'] if i.get('答案類型') == '原文'),
                      'ans_tuisuan': sum(1 for i in items['題'] if i.get('答案類型') == '推算'),
                      'ans_zhengli': sum(1 for i in items['題'] if i.get('答案類型') == '整理語'),
                      'ju': len(sidx)},
            'warn': rel['安全提醒短'],
            'safety': rel['安全提醒'],
            'safety_note': '原文與題目皆經逐字比對；校記與限制公開列出。臨床主張未經驗證。',
        },
        'juan': [{'no': k, 'label': ('卷' + str(k)) if k != '' else '卷首', 'n': len(v),
                  'chaps': [{'seq': p['序'], 'name': p['篇名_規範']} for p in v]}
                 for k, v in sorted(juan.items(), key=lambda x: (x[0] == '', str(x[0])))],
        'pian': pian,
        'items': its,
        'limits': [{'id': r.get('編號', ''), 'cat': r.get('範疇', ''), 'issue': r.get('問題', ''),
                    'sev': r.get('嚴重度', ''), 'status': r.get('現狀', '')} for r in lim],
        'contradictions': [{'id': r.get('編號', ''), 'type': r.get('類型', ''), 'point': r.get('爭點', ''),
                            'verdict': r.get('判定', '')} for r in con],
        'collation': [{'id': r.get('編號', ''), 'seq': r.get('篇序', ''), 'pian': r.get('篇名', ''),
                       'anchor': r.get('錨點', ''), 'sid': r.get('句ID', ''),
                       'base': r.get('底本讀法', ''), 'taisu': r.get('太素', '') or '—',
                       'leijing': r.get('類經', '') or '—', 'verdict': r.get('判定', ''),
                       'basis': r.get('依據', ''), 'impact': r.get('影響', '')} for r in col],
        'themes': themes,
        'needles': [{'no': r.get('序', ''), 'name': r.get('鍼', ''), 'len': r.get('長', ''),
                     'use': r.get('功能', ''), 'src': r.get('原文', '')} for r in nd],
        'concepts': cpts,
        'contact': contact,
        'search': search,
        'varmap': VMAP,
        'law': law,
        'mer': mer,
        'jingbie': jb, 'jingjin': jj, 'luomai': luo, 'jingshui': js, 'wushu': ws, 'binghou': bh,
        'shier_yuan': yuan, 'yingwei': yw,
        'wuci': wuci, 'wuxie': wuxie,
        'bounds': bounds, 'abscess': abscess, 'covmap': covmap, 'jiugong': jiugong, 'zhujia': zhujia, 'bianti': bianti,
        'jizhu': jizhu, 'leizhu': leizhu, 'jiayi': jiayi,
        'defs': defs,
        'suwen': suwen,
    }
    os.makedirs(OUT, exist_ok=True)
    js = '/* 由 scripts/build_reader.py 生成，請勿手改。 */\nwindow.LS = ' + \
         json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8').write(js)
    print(f"寫出 reader/assets/data.js：{len(js)/1024:.0f} KB｜篇 {len(pian)}｜題 {len(its)}")


if __name__ == '__main__':
    main()
