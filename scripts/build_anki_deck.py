#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生可匯入 Anki 的 .apkg（填空卡，正面可即時對答案）。

- 卡片模板在 export/anki模板/（front.html、back.html、style.css）
- 異體映射在 export/異體映射.json，注入模板 JS，與 scripts/grade.py 同一張表
- 需要 genanki；本庫安裝在 vendor/pylib（pip install --target）

用法：python3 scripts/build_anki_deck.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'vendor', 'pylib'))
try:
    import genanki
except ImportError:
    print('缺 genanki：pip install --target ./vendor/pylib genanki'); sys.exit(1)

TPL = os.path.join(ROOT, 'export', 'anki模板')
MODEL_ID = 1729000001          # 固定，重跑不新增牌組類型
DECK_ID = 1729000002
DECK_NAME = '靈樞經 · 自學'


def var_js():
    d = json.load(open(os.path.join(ROOT, 'export', '異體映射.json'), encoding='utf-8'))['映射']
    m = {}
    for chars in d.values():
        for ch in chars:
            m[ch] = chars[0]
    return json.dumps(m, ensure_ascii=False)


def main():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    fill = [i for i in items if i['type'] == 'fill_blank']

    front = open(os.path.join(TPL, 'front.html'), encoding='utf-8').read().replace('__VAR_MAP__', var_js())
    back = open(os.path.join(TPL, 'back.html'), encoding='utf-8').read()
    css = open(os.path.join(TPL, 'style.css'), encoding='utf-8').read()

    model = genanki.Model(MODEL_ID, '靈樞填空（可對答案）',
                          fields=[{'name': n} for n in ('題面', '答案', '可接受', '說明', '出處')],
                          templates=[{'name': '填空', 'qfmt': front, 'afmt': back}],
                          css=css)
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    for i in fill:
        src = i['source']
        deck.add_note(genanki.Note(model=model, fields=[
            i['stem'], i['answer'], '、'.join(i.get('可接受答案') or []),
            i.get('note', ''),
            f"《靈樞·{src['篇名']}》" + (f"（第 {src['篇序']} 篇" + (f"，句 {i['句']}" if i.get('句') else '') + "）" if src.get('篇序') else ''),
        ]))
    out = os.path.join(ROOT, 'export', '靈樞_填空.apkg')
    genanki.Package(deck).write_to_file(out)
    print(f'寫出 {out}：{len(fill)} 張填空卡')


if __name__ == '__main__':
    main()
