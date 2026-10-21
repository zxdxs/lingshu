#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""匯出：Anki 牌組、全題表、實體索引。

為什麼要做：題庫只存在 JSON 裡，學習者拿不到。做完才算「用得上」。
"""
import csv, json, os, random, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'export')
os.makedirs(OUT, exist_ok=True)

CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')


def tag_safe(s):
    s = re.sub(r'[\\s，。、；：？！（）()《》「」/]+', '_', str(s))
    return re.sub(r'_+', '_', s).strip('_') or 'x'


def stable_shuffle(opts, key):
    """依 item_id 決定性洗牌，重複匯出順序不變。"""
    rnd = random.Random(int(hashlib.md5(key.encode()).hexdigest()[:8], 16))
    idx = list(range(len(opts)))
    rnd.shuffle(idx)
    return [opts[i] for i in idx]


def main():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    rows, flat = [], []

    for it in items:
        src = it.get('source') or {}
        pian = src.get('篇名', '')
        where = f"《靈樞·{pian}》" if pian else ''
        note = it.get('note', '')
        tags = [f"靈樞", f"篇_{tag_safe(pian)}", f"型_{it['type']}",
                f"層_{it.get('層級', 'L0')}", f"Bloom_{it['bloom']}"]
        if note:
            tags.append(f"類_{tag_safe(note)}")

        extra = ''
        if it.get('註家參照'):
            z = it['註家參照']
            extra = f"<br><br><i>註家：{z.get('條號', '')}（{z.get('類', '')}類·{z.get('條題', '')}）</i>"
        if it.get('章校記'):
            extra += f"<br><br><b>【底本校記】</b>{it['章校記']}"

        if it['type'] == 'mcq':
            opts = stable_shuffle([it['answer']] + list(it.get('distractors') or []), it['item_id'])
            letters = 'ABCD'
            body = '<br>'.join(f"{letters[i]}. {o}" for i, o in enumerate(opts))
            front = f"{it['stem']}<br><br>{body}"
            k = opts.index(it['answer'])
            back = f"<b>正解：{letters[k]}. {it['answer']}</b><br><br>{where}"
            flat_ans = it['answer']
            flat_dis = ' ／ '.join(it.get('distractors') or [])
        else:
            front = it['stem']
            back = f"<b>{it['answer']}</b><br><br>{where}"
            flat_ans, flat_dis = it['answer'], ''

        back += extra
        rows.append({'front': front, 'back': back, 'tags': ' '.join(tags)})
        flat.append({
            'item_id': it['item_id'], '篇序': src.get('篇序', ''), '篇名': pian,
            '題型': it['type'], 'bloom': it['bloom'], '層級': it.get('層級', ''),
            '題面': it['stem'], '答案': flat_ans, '干擾項': flat_dis,
            '說明': note, '校記': it.get('章校記', ''),
            '註家': (it.get('註家參照') or {}).get('條號', ''),
            '依據': it.get('依據類型', ''), '配對精度': (it.get('註家參照') or {}).get('配對精度', ''),
            '可接受答案': '、'.join(it.get('可接受答案') or []),
            '答案類型': it.get('答案類型', ''), '句': it.get('句', ''),
        })

    # 1) Anki 匯入檔（逗號分隔 + 表頭指令）
    with open(os.path.join(OUT, 'anki_靈樞.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        f.write('#separator:Comma\n#html:true\n#tags column:3\n')
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for r in rows:
            w.writerow([r['front'], r['back'], r['tags']])

    # 2) 全題表（供 Excel 篩選）
    with open(os.path.join(OUT, '題庫_全.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
        w.writeheader()
        w.writerows(flat)

    # 3) 實體索引
    idx = []
    for fn, name_col, kind in (('實體_腧穴', '穴', '腧穴'), ('實體_經脈', '經脈簡稱', '經脈'),
                               ('實體_臟腑', '名', '藏府'), ('實體_九鍼', '鍼', '九鍼')):
        p = os.path.join(ROOT, 'data', fn + '.csv')
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8-sig')):
            idx.append({'類': kind, '名': r.get(name_col, ''), '篇序': r.get('篇序', ''),
                        '篇名': r.get('篇名', ''), '位置': r.get('位置', '')})

    # 篇一覽
    pian = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    qn = {}
    for r in flat:
        qn[r['篇序']] = qn.get(r['篇序'], 0) + 1
    for p in pian:
        idx.append({'類': '篇', '名': p['篇名_規範'], '篇序': int(p['序']), '篇名': p['篇名_規範'],
                    '位置': f"經文 {p['經文字數']} 字／題 {qn.get(int(p['序']), 0)}"})

    with open(os.path.join(OUT, '索引.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['類', '名', '篇序', '篇名', '位置'])
        w.writeheader()
        w.writerows(sorted(idx, key=lambda x: (x['類'], str(x['名']))))

    print(f'Anki {len(rows)} 張｜全題 {len(flat)} 行｜索引 {len(idx)} 條 → export/')


if __name__ == '__main__':
    main()
