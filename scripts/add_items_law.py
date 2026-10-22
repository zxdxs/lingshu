#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""為「引文重疊為 0」的通則補題：每條 2 題填空，題面直接取該條的引文。

規則：
  - 題面 = 《靈樞·篇名》「引文，其中一段換成 ____」；引文逐字取自句索引，不改字。
  - 答案 = 被挖掉的那一段，必為原文子串（答案類型：原文）。
  - 挖空段取「逗號分段中最長的一段」，且該段不可在句內重複、不可含標點。
  - 只補 type=fill_blank、層級 L0；每題在 note 標明對應通則。

用法：python3 scripts/add_items_law.py [--write]
不帶 --write 只試跑並印出結果。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import norm

JU = {s['id']: s for s in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'),
                                          encoding='utf-8'))['句']}
CH = {p['序']: p for p in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'),
                                         encoding='utf-8'))['篇']}
LAW = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
ITEMS_PATH = os.path.join(ROOT, 'data', '題庫_示例.json')

WRITE = '--write' in sys.argv

# 少數條目自動挖空不理想，人工指定：通則號 → {第幾段引文: (句ID, 空白段)}
OVERRIDE = {
    35: {0: ('47-2-3', '小大長短厚薄結直緩急')},
    45: {0: ('7-3-2', '刺諸經滎輸藏腧也'), 1: ('7-3-9', '左取右')},
    39: {0: ('65-1-1', '調右手太陽上')},
}
# 需要額外接受的異體寫法
ALIAS = {'割臂㰱血之盟也': ['割臂歃血之盟也']}


def pick_span(text):
    """挑一個可挖的段落：以，；。斷開，取最長的 CJK 段（4–10 字），且在句內唯一。"""
    parts = [p for p in re.split(r'[，；。]', text) if p]
    BAD = ('：', '曰', '荅', '答', '？', '！')
    HEAD = ('岐伯', '黃帝', '帝曰', '雷公', '伯高', '少師', '少俞')
    cands = [p for p in parts
             if 3 <= len(p) <= 10 and p in text and text.count(p) == 1
             and not any(b in p for b in BAD) and not p.startswith(HEAD)]
    if not cands:
        return None
    return max(cands, key=len)


def t2s(s):
    try:
        from opencc import OpenCC
        return OpenCC('t2s').convert(s)
    except Exception:
        return s


def main():
    data = json.load(open(ITEMS_PATH, encoding='utf-8'))
    items = data['題']
    have = {i['item_id'] for i in items}
    zero = [(x['n'], x['名'], x['引']) for g in LAW['組'] for x in g['條']
            if x['相關題']['重疊'] == 0]
    added, skipped = [], []
    for n, name, quotes in zero:
        made = 0
        for qi, q in enumerate(quotes):
            if made >= 2:
                break
            ov = OVERRIDE.get(n, {}).get(qi)
            sid, forced = (ov if ov else (q['id'], None))
            s = JU.get(sid)
            if not s:
                continue
            span = forced or pick_span(s['text'])
            if not span or span not in s['text']:
                continue
            stem_text = s['text'].replace(span, '____', 1)
            stem = f"《靈樞·{s['pian']}》「{stem_text}」"
            if not forced and len(norm(stem_text)) < 6:
                continue
            iid = f"Q-LAW{n:02d}-{made + 1}"
            if iid in have:
                continue
            item = {
                'item_id': iid, 'type': 'fill_blank', 'bloom': 'remember',
                'stem': stem, 'answer': span, 'distractors': [],
                'source': {'篇序': s['seq'], '篇名': s['pian']},
                'note': f"對應通則第 {n} 條「{name}」",
                'auto_grading': 'exact', '層級': 'L0',
                '證據類型': '直引（答案為原文字串或原文標籤）',
                '句': sid, '答案類型': '原文',
            }
            acc = []
            simple = t2s(span)
            if simple != span:
                acc.append(simple)
            acc.extend(ALIAS.get(span, []))
            if acc:
                item['可接受答案'] = acc
            items.append(item)
            added.append(item)
            made += 1
        if made == 0:
            skipped.append((n, name))

    print(f'可補 {len(added)} 題；條數 {len(zero)}；未補到的條：{skipped}')
    if not WRITE:
        for a in added[:5]:
            print('  例：', a['item_id'], a['answer'], '|', a['stem'][:40])
        return
    data['題數'] = len(items)
    dist = {}
    for i in items:
        dist[i['type']] = dist.get(i['type'], 0) + 1
    data['題型分布'] = dist
    json.dump(data, open(ITEMS_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'已寫入：題數 {data["題數"]}、分布 {dist}')


if __name__ == '__main__':
    main()
