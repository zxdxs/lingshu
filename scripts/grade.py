#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""填空題評分器（可測）。

比對前先正規化：
  1 去空白、標點、引號
  2 全形轉半形（數字、英文字母）
  3 以本庫異體字表把字收斂（隂→陰、榖→穀、爲→為…）

於是「脉」「脈」「衇」在比對時是同一個字；「清氣」與「清」仍然不同。

用法：
  python3 scripts/grade.py --selftest        # 用題庫自我測試
  from grade import is_correct; is_correct('隂谷', item)
"""
import json, os, re, sys, unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from check_quotes import VAR

KEEP = re.compile(r'[0-9A-Za-z\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002A6DF]')


def _load_t2s():
    """繁→簡 單字對照（data/繁簡映射.csv，由 OpenCC 產生後抽成表）。"""
    import csv
    p = os.path.join(ROOT, 'data', '繁簡映射.csv')
    if not os.path.exists(p):
        return {}
    return {r['繁']: r['簡'] for r in csv.DictReader(open(p, encoding='utf-8-sig'))}


T2S = _load_t2s()


def normalize(s):
    s = unicodedata.normalize('NFKC', str(s or ''))
    s = ''.join(ch for ch in s if KEEP.match(ch))
    s = ''.join(VAR.get(ch, ch) for ch in s)
    return ''.join(T2S.get(ch, ch) for ch in s)


def is_correct(student, item):
    a = normalize(student)
    if not a:
        return False
    if a == normalize(item['answer']):
        return True
    for alt in item.get('可接受答案') or []:
        if a == normalize(alt):
            return True
    return False


def selftest():
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    fill = [i for i in items if i['type'] == 'fill_blank']
    by_pian = {}
    for i in fill:
        by_pian.setdefault(i['source']['篇序'], []).append(i['answer'])

    ok = bad = 0
    fails = []
    # 1 正解必過
    for i in fill:
        if is_correct(i['answer'], i):
            ok += 1
        else:
            bad += 1; fails.append(('正解未過', i['item_id'], i['answer']))
    # 2 可接受答案必過
    acc_n = 0
    for i in fill:
        for alt in i.get('可接受答案') or []:
            acc_n += 1
            if not is_correct(alt, i):
                bad += 1; fails.append(('異體未過', i['item_id'], alt))
    # 3 同篇他題答案必不過（若與本題等價則略過）
    neg_n = neg_ok = 0
    for i in fill:
        for other in by_pian[i['source']['篇序']]:
            if normalize(other) == normalize(i['answer']):
                continue
            neg_n += 1
            if is_correct(other, i):
                neg_ok += 1; fails.append(('誤收', i['item_id'], other))
    # 4 簡體與異體混寫：抽樣檢查
    simp_cases = [('阴谷', '陰谷'), ('鱼际', '魚際'), ('肾', '腎'), ('经渠', '經渠'),
                  ('气', '氣'), ('乱气', '亂氣')]
    sp = 0
    for stu, ans in simp_cases:
        item = next((i for i in fill if i['answer'] == ans), None)
        if not item:
            continue
        sp += 1
        if not is_correct(stu, item):
            bad += 1; fails.append(('簡體未過', item['item_id'], stu))
    print(f'填空題 {len(fill)}｜正解通過 {ok}｜異體樣本 {acc_n}｜簡體樣本 {sp}｜'
          f'負樣本 {neg_n}（誤收 {neg_ok}）｜失敗 {bad}')
    for f in fails[:8]:
        print('  ✗', f)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(selftest())
