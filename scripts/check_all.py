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
        '重複題面': sum(v - 1 for v in stems.values() if v > 1),
        '篇名不一致': names,
        '句索引': len(json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']),
        '題目有句ID': sum(1 for i in its if i.get('句')),
        '文件引文待核': docs_pending(),
        '文件數': len(glob.glob(os.path.join(ROOT, 'docs', '*.md'))),
        '發布待決': release_pending(),
        '跨書引文不符': cross_quotes_bad(),
        '安全提醒缺漏': safety_gaps(),
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
