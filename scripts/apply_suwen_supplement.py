#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data/素問補篇.json 的三篇（26／46／50）補進 底本/素問_經文.json。

為什麼不直接在 build_suwen.py 裡混來源：底本要可追溯。所以補篇另存一檔（記來源、取用日期、
簡體照錄），再用這支腳本插進對應的卷與位置；插完重算統計，並檢查 篇序 是否連續。

插法：
  26 → 卷 8，插在篇 27 之前
  46 → 卷 13，插在篇 47 之前
  50 → 卷 14，插在篇 51 之前
插入後，後面各篇的「起」偏移一併後移。

用法：python3 scripts/apply_suwen_supplement.py [--dry]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUP = os.path.join(ROOT, 'data', '素問補篇.json')
DST = os.path.join(ROOT, '底本', '素問_經文.json')


def main():
    dry = '--dry' in sys.argv
    d = json.load(open(DST, encoding='utf-8'))
    sup = json.load(open(SUP, encoding='utf-8'))
    have = {p['序'] for j in d['卷'] for p in j['篇']}
    todo = [x for x in sup['篇'] if x['序'] not in have]
    if not todo and '--refresh' not in sys.argv:
        print('三篇都已在底本裡，無事可做')
        return 0

    for item in todo:
        vol = [j for j in d['卷'] if j['卷'] == item['卷']][0]
        later = [p for p in vol['篇'] if p['序'] > item['序']]
        if later:
            at = min(p['起'] for p in later)
        else:
            at = len(vol['文本'])
        block = '\n' + item['名'] + '第' + str(item['序']) + '\n' + item['文本'] + '\n'
        vol['文本'] = vol['文本'][:at] + block + vol['文本'][at:]
        for p in vol['篇']:
            if p['起'] >= at:
                p['起'] += len(block)
        vol['篇'].append({'名': item['名'], '序': item['序'], '起': at})
        vol['篇'].sort(key=lambda p: p['起'])
        print(f"補入卷 {item['卷']}：{item['名']}（第 {item['序']} 篇，{item['字數']} 字）")

    # 篇名清單也從卷內重建（補篇只改了卷，容易漏更新這裡）
    d['篇名'] = sorted([{'序': p['序'], '名': p['名'], '卷': j['卷']}
                        for j in d['卷'] for p in j['篇']], key=lambda x: x['序'])
    allseq = sorted(p['序'] for j in d['卷'] for p in j['篇'])
    chars = len(['' for _ in range(0)])  # 佔位
    import re
    total = sum(len(re.findall(r'[\u4e00-\u9fff]', j['文本'])) for j in d['卷'])
    d['統計']['篇名數'] = len(allseq)
    d['統計']['經文字'] = total
    d['統計']['缺篇名'] = [i for i in range(1, 82) if i not in allseq]
    d['統計']['補篇'] = [x['序'] for x in sup['篇']]
    d['統計']['補篇來源'] = sup['來源']
    print('篇名', len(allseq), '經文', total, '缺', d['統計']['缺篇名'])
    if not dry:
        json.dump(d, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('已寫入', DST)
    return 0


if __name__ == '__main__':
    sys.exit(main())
