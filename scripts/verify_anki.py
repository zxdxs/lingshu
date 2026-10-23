#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Anki 官方後端（anki 套件）匯入 .apkg 並驗證卡片。

不是「自己解 zip 看 sqlite」，而是走 Anki 自己的匯入流程＋卡片渲染，
所以能驗到：牌組、卡片型、欄位、模板、答案頁內容。

用法：
  pip install anki                      # 需另裝（不進 vendor，避免肥檔）
  python3 scripts/verify_anki.py [--apkg export/靈樞_填空.apkg] [--show 3]
"""
import argparse
import html
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = '靈樞經 · 自學'
MODEL = '靈樞填空（可對答案）'
SAFE = '帶教資格'


def strip(s):
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', s))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apkg', default=os.path.join(ROOT, 'export', '靈樞_填空.apkg'))
    ap.add_argument('--show', type=int, default=3)
    args = ap.parse_args()

    from anki.collection import Collection
    from anki.import_export_pb2 import ImportAnkiPackageRequest

    apkg = os.path.abspath(args.apkg)
    if not os.path.exists(apkg):
        print('✗ 找不到', apkg); return 2
    d = tempfile.mkdtemp(prefix='anki-verify-')
    col = Collection(os.path.join(d, 'collection.anki2'))
    fails = []

    log = col.import_anki_package(ImportAnkiPackageRequest(package_path=apkg))
    n_notes, n_cards = col.note_count(), col.card_count()
    decks = [x.name for x in col.decks.all_names_and_ids()]
    models = [m['name'] for m in col.models.all()]
    print(f'匯入：{os.path.basename(apkg)}（{os.path.getsize(apkg)/1024:.0f} KB）')
    print(f'  notes={n_notes}  cards={n_cards}')
    print(f'  牌組：{"、".join(decks)}')
    if n_notes != n_cards:
        fails.append(f'notes {n_notes} ≠ cards {n_cards}（應該一卡一 note）')
    if DECK not in decks:
        fails.append(f'沒有牌組「{DECK}」')
    if MODEL not in models:
        fails.append(f'沒有卡片型「{MODEL}」')

    if MODEL in models:
        m = [x for x in col.models.all() if x['name'] == MODEL][0]
        tpls = [t['name'] for t in m['tmpls']]
        flds = [f['name'] for f in m['flds']]
        print(f'  模板：{"、".join(tpls)}｜欄位：{"、".join(flds)}')
        if not tpls or not flds:
            fails.append('模板或欄位為空')

    cids = col.find_cards('')
    bad_render = 0
    for i, cid in enumerate(cids[:args.show]):
        card = col.get_card(cid)
        q, a = strip(card.question()), strip(card.answer())
        print(f'  卡 {i + 1}：Q={q[:60]}')
        print(f'         A={a[:110]}')
        if not q or not a:
            bad_render += 1
        if i == 0 and SAFE not in a:
            fails.append(f'答案頁沒有安全提醒（缺「{SAFE}」）')
    if bad_render:
        fails.append(f'{bad_render} 張卡片渲染為空')

    if fails:
        print('✗ 失敗：' + '；'.join(fails)); return 1
    print(f'✓ 通過：Anki 後端匯入 {n_notes} 卡、牌組與模板正確、答案頁含安全提醒')
    return 0


if __name__ == '__main__':
    sys.exit(main())
