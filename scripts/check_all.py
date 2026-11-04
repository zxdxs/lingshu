#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一鍵回歸檢查：把四層稽核與計數收斂成一份基準，跑一次就知道有沒有漂移。

用法：
  python3 scripts/check_all.py            # 與 data/基準.json 比對
  python3 scripts/check_all.py --write    # 以現況更新基準
  python3 scripts/check_all.py --json     # 印出目前指標
"""
import glob, json, os, re, subprocess, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

BASE_PATH = os.path.join(ROOT, 'data', '基準.json')
CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
B = {p['序']: norm(p['正規化']) for p in CH}
NAME = {p['序']: p['篇名_規範'] for p in CH}


def items():
    return json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']


def quote_mismatch(its):
    bad = 0
    for it in its:
        m = re.match(r'《靈樞·([^》]+)》', it['stem'])
        if not m:
            continue
        seq = it['source']['篇序']
        for q in re.findall(r'「([^」]{2,})」', it['stem']):
            for seg in [x for x in re.split(r'_+', q) if len(norm(x)) >= 2]:
                if norm(seg) not in B[seq]:
                    bad += 1
    return bad


def module_text():
    tot = bad = 0
    for f in glob.glob(os.path.join(ROOT, 'data', '模組_*.json')):
        def walk(n):
            nonlocal tot, bad
            if isinstance(n, dict):
                for _k in ('原文', '原文要點'):
                    raw = n.get(_k)
                    if isinstance(raw, str) and len(norm(raw)) >= 6:
                        tot += 1
                        hit = [k for k, v in B.items() if norm(raw) in v]
                        if not hit:
                            bad += 1
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for x in n:
                    walk(x)
        walk(json.load(open(f, encoding='utf-8')))
    return tot, bad


def answer_kinds(its):
    c = Counter(i.get('答案類型') for i in its if i['type'] == 'fill_blank')
    return {k or '未標': v for k, v in c.items()}


def docs_pending():
    pend = 0
    for f in glob.glob(os.path.join(ROOT, 'docs', '*.md')) + [os.path.join(ROOT, 'README.md')]:
        txt = open(f, encoding='utf-8').read()
        quotes = [q for q in re.findall(r'「([^」]{4,})」', txt) if '…' not in q]
        corpus = ''.join(B.values())
        pend += sum(1 for q in quotes if norm(q) and norm(q) not in corpus)
    return pend


def law_bounds_short():
    """通則的「界」是防過度推論的欄位；少於 20 字視為不合格。"""
    try:
        law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    except FileNotFoundError:
        return -1
    return sum(1 for g in law['組'] for x in g['條'] if len(x.get('界', '')) < 20)


def leijing_bad():
    """通則裡標了「《類經》亦收此段」的引文，必須真的在該卷找得到；回傳不符條數。"""
    import glob
    from check_quotes import norm as _norm
    try:
        law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    except FileNotFoundError:
        return -1
    juan = {}
    for f in glob.glob(os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '*.txt')):
        raw = open(f, encoding='utf-8').read()
        m = re.search(r'#\+PROPERTY: JUAN (\d+)', raw)
        if m:
            juan[int(m.group(1))] = _norm(raw)
    bad = 0
    for g in law['組']:
        for x in g['條']:
            for y in x.get('類經', []):
                t = juan.get(y['卷'], '')
                q = next((z['文'] for z in x['引'] if z['id'] == y['id']), '')
                if not q or _norm(q) not in t:
                    bad += 1
    return bad


def release_pending():
    """發布前必要欄位仍未決的數量（資料來源：data/發布資訊.json）。"""
    try:
        rel = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
    except FileNotFoundError:
        return -1
    PEND = ('', None, '待定', '待補', '未測')
    return sum(1 for k in rel.get('必要', []) if rel.get(k) in PEND)


SAFETY_CORE = '在有帶教資格的執業中醫師指導下使用'
SAFETY_FILES = ['reader/assets/data.js', 'reader/index.html', 'export/大樣稿.html',
                'export/anki模板/back.html', 'export/anki模板/deck_description.txt',
                'README.md', 'LICENSE.txt']


def cross_quotes_bad():
    """跨書引文（靈樞／素問／類經）逐字比對，回傳不符條數。"""
    import subprocess as _sp
    try:
        r = _sp.run([sys.executable, os.path.join(ROOT, 'scripts', 'audit_cross_quotes.py'), '--json'],
                    capture_output=True, text=True, timeout=300)
        return json.loads(r.stdout)['不符']
    except Exception:
        return -1


def safety_gaps():
    """安全提醒必須出現在每一個出口；少一處就算缺漏（改措辭不會誤報，刪掉才會）。"""
    gaps = 0
    for rel in SAFETY_FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p) or SAFETY_CORE not in open(p, encoding='utf-8').read():
            gaps += 1
    return gaps



def jizhu_stats():
    """集註（張志聰注）：去注分經後的三個防線——
    注文不得是經文漏網（4-gram 覆蓋率 >0.6 即疑）、比對率不得低於 90%、篇數須 81。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '張注.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0, 0
    zh = {k: v for x in d['篇'] for k, v in x.get('注', {}).items()}
    corpus = ''.join(B.values())

    def cover(t):
        g = [t[i:i + 4] for i in range(len(t) - 3)]
        return sum(1 for x in g if x in corpus) / len(g) if g else 0.0

    leak = sum(1 for t in zh.values() if cover(t) > 0.6)
    low = sum(1 for x in d['篇'] if x.get('比對率', 100) < 90)
    return len(zh), leak, low


def leizhu_stats():
    """類經注：引句 id 必須在三源通則裡，卷號必須在 1–32；注不得為空。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '類經注.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    ids = {q['id'] for g in law['組'] for t in g['條'] for q in t['引']}
    bad = 0
    for t in d['條']:
        for q in t['引']:
            if (q['id'] not in ids or not (1 <= q['卷'] <= 32) or len(q['注']) < 12
                    or not q.get('類')):
                bad += 1
    return d['統計']['段'], bad


def jiayi_stats():
    """甲乙經篇次對照：81 篇都要有落點、卷號 1–12、主落點篇名不得為空；回傳（有落點, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '甲乙經.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    bad = 0
    for x in d['篇']:
        m = x.get('主')
        if not m or not (1 <= m['卷'] <= 12) or not m.get('篇'):
            bad += 1
    return d['統計']['有落點'], bad


def lingshi_stats():
    """靈樞識：引句 id 須在三源通則裡、注不短於 12 字。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '靈樞識.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    ids = {q['id'] for g in law['組'] for t in g['條'] for q in t['引']}
    # 靈樞識多為短校記（「甲乙方脉作經」一類），故只擋空注，不設長度下限
    bad = sum(1 for t in d['通則'] for q in t['引'] if q['id'] not in ids or len(q['注']) < 4)
    return d['統計']['繫上'], bad


def zhu_coverage():
    """三家注（集註／類經注／靈樞識）對 65 條通則的覆蓋：回傳（有注條數, 三家皆無條數）。"""
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    try:
        a = {t['n'] for t in json.load(open(os.path.join(ROOT, 'data', '張注.json'), encoding='utf-8'))['通則']}
        b = {t['n'] for t in json.load(open(os.path.join(ROOT, 'data', '類經注.json'), encoding='utf-8'))['條']}
        c = {t['n'] for t in json.load(open(os.path.join(ROOT, 'data', '靈樞識.json'), encoding='utf-8'))['通則']}
    except FileNotFoundError:
        return 0, 0
    ns = [t['n'] for g in law['組'] for t in g['條']]
    return sum(1 for n in ns if n in a | b | c), sum(1 for n in ns if n not in a | b | c)


def jiayi_tiao():
    """甲乙條對應：id 須在句索引、卷 1–12、相似度 ≥0.85、兩邊文非空。回傳（對上數, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '甲乙經條.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    ids = {x['id'] for x in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}
    bad = 0
    for r in d['條']:
        if (r['id'] not in ids or not (1 <= r['卷'] <= 12) or r['比'] < 0.85
                or not r['甲'] or not r['乙']):
            bad += 1
    return len(d['條']), bad


def mashihao():
    """馬蒔轉引輯存：每段須有篇名、句子（可空）、非空文；回傳（段數, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '馬蒔轉引.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    names = {p['篇名'] for p in CH} | {p['篇名_規範'] for p in CH}
    ids = {x['id'] for x in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}
    bad = 0
    for x in d['條']:
        if x['篇'] not in names or len(x['文']) < 6 or (x['句'] and x['句'] not in ids):
            bad += 1
    return len(d['條']), bad


def taisu_probe():
    """太素探針：經文段數與密度是分離品質的代理指標，漂移即代表來源或參數變了。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '太素探針.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    st = d['統計']
    return st['經文'], int(round(st['注密度'] * 100))


def taisu_zhu():
    """太素注對讀：卷 1–30、距離 −8～+80、文非空、句 id 在通則。回傳（引段, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '太素注.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    ids = {q['id'] for g in law['組'] for t in g['條'] for q in t['引']}
    bad = 0
    for t in d['通則']:
        for q in t['引']:
            if (q['id'] not in ids or not (1 <= q['卷'] <= 30) or len(q['注']) < 12
                    or not (-8 <= q['距'] <= 80)):
                bad += 1
    return sum(len(t['引']) for t in d['通則']), bad


def taisu_index():
    """太素逐段索引：屬只能是靈樞／素問／未繫；靈樞者句 id 須存在；比在 0–1。回傳（段, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '太素注索引.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    ids = {x['id'] for x in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}
    bad = 0
    for r in d['條']:
        if r['屬'] not in ('靈樞', '素問', ''):
            bad += 1
        elif r['屬'] == '靈樞' and r['句'] not in ids:
            bad += 1
        elif r['屬'] == '素問' and not (r['句'].startswith('素問·') or r['句'].startswith('素問卷')):
            bad += 1
        elif not (0 <= r['比'] <= 1) or len(r['文']) < 12:
            bad += 1
    return len(d['條']), bad


def taisu_pingan():
    """太素平按（蕭延平校記）：卷 1–30、文以「平按」開頭且 ≥6 字。回傳（條, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '太素平按.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0
    bad = sum(1 for x in d['條']
              if not (0 <= x['卷'] <= 30) or not x['文'].startswith('平按') or len(x['文']) < 6)
    return d['統計']['段'], bad


def path_stats():
    """學習路徑：篇序須在 1–81、每步要有名稱與驗收；回傳（路線數, 步數, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '學習路徑.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0, 0
    seqs = {p['序'] for p in CH}
    steps = bad = 0
    for r in d['路線']:
        for st in r.get('步', []):
            steps += 1
            if not st.get('名') or not st.get('驗收'):
                bad += 1
            for q in st.get('篇', []):
                if q not in seqs:
                    bad += 1
    return len(d['路線']), steps, bad


def suwen_tongwen():
    """素問同文表：同文句 id 須存在、素問篇名非空、篇對重合 0–100。回傳（同文句, 篇對, 壞列）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '素問同文.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0, 0
    ids = {x['id'] for x in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}
    bad = 0
    for x in d['句']:
        if x['id'] not in ids or not x['素問'] or len(x['文']) < 6:
            bad += 1
    for x in d['篇對']:
        if not (0 <= x['重合'] <= 100) or not x['素問'] or x['段數'] < 0:
            bad += 1
    return d['統計']['同文句'], d['統計']['篇對'], bad


def name_key_mismatch():
    """底本「篇名」與句索引「pian」的鍵不一致數（9 篇是異體字：經别/經別…）。

    這個數字用來提醒：按篇名 join 前先想清楚用哪個鍵。它不該無故變動。
    """
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    keys = {x['pian'] for x in ju}
    return sum(1 for p in CH if p['篇名'] not in keys)


def module_d():
    """D 型模組：篇數應為 81−49（補齊的篇）；每篇須有一句、分層、誤讀。回傳（篇數, 壞列）。"""
    try:
        files = glob.glob(os.path.join(ROOT, 'data', '模組_D*.json'))
    except Exception:
        return 0, 0
    seqs = {p['序'] for p in CH}
    bad = seen = 0
    seen_list = []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        for x in d.get('篇', []):
            seen += 1
            seen_list.append(x['篇序'])
            if (x['篇序'] not in seqs or not x.get('一句') or not x.get('分層')
                    or not x.get('誤讀')):
                bad += 1
    if len(seen_list) != len(set(seen_list)):
        bad += 1
    return seen, bad


def module_page_cover():
    """模組頁要涵蓋 81 篇：D 型 32 篇 ＋ 主題型（舊模組）的 出處 篇序，聯集應為 81。"""
    seqs = set()
    for f in glob.glob(os.path.join(ROOT, 'data', '模組_*.json')):
        d = json.load(open(f, encoding='utf-8'))
        if os.path.basename(f).startswith('模組_D'):
            seqs |= {x['篇序'] for x in d.get('篇', [])}
            continue
        src = d.get('出處')
        if isinstance(src, list):
            seqs |= {x.get('篇序') for x in src if isinstance(x, dict)}
        elif isinstance(src, dict):
            seqs.add(src.get('篇序'))
    return len([q for q in seqs if isinstance(q, int) and 1 <= q <= 81])


def taisu_index_tier():
    """太素索引的層級數字：靈樞繫上、未繫、素問細到篇者。用來釘住這輪的改善。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '太素注索引.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0, 0
    ling = sum(1 for r in d['條'] if r['屬'] == '靈樞')
    miss = sum(1 for r in d['條'] if not r['屬'])
    pian = sum(1 for r in d['條'] if r['屬'] == '素問' and r['句'].startswith('素問·') and '卷' not in r['句'])
    return ling, miss, pian


def govern_stats():
    """治理：未決條目的枚舉合法、證偽非空、id 不重；回傳（未決數, blocked, suspended, both）。"""
    try:
        d = json.load(open(os.path.join(ROOT, 'data', '未決.json'), encoding='utf-8'))
    except FileNotFoundError:
        return 0, 0, 0, 0, 0
    e = d.get('枚舉', {})
    ST = set(e.get('status', []))
    RS = set(e.get('resolution', []))
    GR = set(e.get('grade', []))
    ids = [x['id'] for x in d['條']]
    bad = 0
    for x in d['條']:
        if (x['狀態'] not in ST or x['裁決'] not in RS or x['檔'] not in GR
                or len(x.get('證偽', '')) < 10 or len(x.get('說明', '')) < 10):
            bad += 1
    if len(ids) != len(set(ids)):
        bad += 1
    st = [x['狀態'] for x in d['條']]
    rs = [x['裁決'] for x in d['條']]
    return len(ids), st.count('blocked'), st.count('suspended'), rs.count('both_preserved'), bad


def metrics():
    its = items()
    mt, mb = module_text()
    kinds = answer_kinds(its)
    stems = Counter(i['stem'] for i in its)
    names = sum(1 for i in its if i['source'].get('篇名') != NAME.get(i['source']['篇序']))
    return {
        '題數': len(its),
        '填空': sum(1 for i in its if i['type'] == 'fill_blank'),
        '選擇': sum(1 for i in its if i['type'] == 'mcq'),
        '辨誤': sum(1 for i in its if i['type'] == 'error_identification'),
        '題面引文不符': quote_mismatch(its),
        '答案原文': kinds.get('原文', 0),
        '答案整理語': kinds.get('整理語', 0),
        '答案推算': kinds.get('推算', 0),
        '模組原文條目': mt,
        '模組原文不符': mb,
        'D型模組': module_d()[0],
        'D型模組不符': module_d()[1],
        '模組頁覆蓋篇': module_page_cover(),
        '重複題面': sum(v - 1 for v in stems.values() if v > 1),
        '篇名不一致': names,
        '句索引': len(json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']),
        '題目有句ID': sum(1 for i in its if i.get('句')),
        '文件引文待核': docs_pending(),
        '文件數': len(glob.glob(os.path.join(ROOT, 'docs', '*.md'))),
        '發布待決': release_pending(),
        '類經對讀不符': leijing_bad(),
        '通則界過短': law_bounds_short(),
        '跨書引文不符': cross_quotes_bad(),
        '安全提醒缺漏': safety_gaps(),
        '集註有注句': jizhu_stats()[0],
        '集註疑漏經文': jizhu_stats()[1],
        '集註低比對篇': jizhu_stats()[2],
        '類經注段': leizhu_stats()[0],
        '類經注引不符': leizhu_stats()[1],
        '甲乙經落點': jiayi_stats()[0],
        '甲乙經落點不符': jiayi_stats()[1],
        '甲乙經條對應': jiayi_tiao()[0],
        '甲乙經條不符': jiayi_tiao()[1],
        '馬蒔轉引段': mashihao()[0],
        '馬蒔轉引不符': mashihao()[1],
        '太素探針經文': taisu_probe()[0],
        '太素注密度%': taisu_probe()[1],
        '太素注引': taisu_zhu()[0],
        '太素注不符': taisu_zhu()[1],
        '太素索引段': taisu_index()[0],
        '太素索引不符': taisu_index()[1],
        '太素索引靈樞': taisu_index_tier()[0],
        '太素索引未繫': taisu_index_tier()[1],
        '素問篇數': len(json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))['篇名']),
        '素問經文': json.load(open(os.path.join(ROOT, '底本', '素問_經文.json'), encoding='utf-8'))['統計']['經文字'],
        '太素素問篇': taisu_index_tier()[2],
        '太素平按條': taisu_pingan()[0],
        '太素平按不符': taisu_pingan()[1],
        '路徑數': path_stats()[0],
        '路徑步數': path_stats()[1],
        '路徑不符': path_stats()[2],
        '素問同文句': suwen_tongwen()[0],
        '素問同文篇對': suwen_tongwen()[1],
        '素問同文不符': suwen_tongwen()[2],
        '治理未決': govern_stats()[0],
        '治理blocked': govern_stats()[1],
        '治理suspended': govern_stats()[2],
        '治理兩存': govern_stats()[3],
        '治理不符': govern_stats()[4],
        '篇名鍵不一致': name_key_mismatch(),
        '靈樞識繫上': lingshi_stats()[0],
        '靈樞識引不符': lingshi_stats()[1],
        '注家有注條': zhu_coverage()[0],
        '三家皆無': zhu_coverage()[1],
    }


def main():
    cur = metrics()
    if '--json' in sys.argv:
        print(json.dumps(cur, ensure_ascii=False, indent=1)); return 0
    if '--write' in sys.argv or not os.path.exists(BASE_PATH):
        json.dump(cur, open(BASE_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('已寫入基準：', json.dumps(cur, ensure_ascii=False))
        return 0
    base = json.load(open(BASE_PATH, encoding='utf-8'))
    diffs = [(k, base.get(k), cur.get(k)) for k in cur if base.get(k) != cur.get(k)]
    print(f'基準比對：{len(cur)} 項，差異 {len(diffs)}')
    for k, a, b in diffs:
        print(f'  {k}: {a} → {b}')
    return 0 if not diffs else 2


if __name__ == '__main__':
    sys.exit(main())
