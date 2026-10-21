#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""度量三篇（骨度、腸胃、五十營）的重建與換算。

為什麼要重建：
  1. 舊的 data/表_腸胃.csv 多數行沒有器官名（原文省略主語），且「容三斗」與原文「容三斗五升」不符。
  2. 三篇都只有「幾尺幾寸」，沒有任何一條換算，而這是全書唯一可驗算的部分。

原則：每一條數值都必須能在原文字串中找到，否則腳本報錯終止（比照十二節的處理）。
"""
import json, os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIAN = {int(p['序']): p for p in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}

# ---------------- 腸胃（第31篇）----------------
# (部位, 項目, 數值, 原文片段)
CHANGWEI = [
    ('脣至齒', '長', '九分', '脣至齒長九分'),
    ('口', '廣', '二寸半', '口廣二寸半'),
    ('齒以後至會厭', '深', '三寸半', '齒以後至會厭深三寸半'),
    ('口腔', '容', '五合', '大容五合'),
    ('舌', '重', '十兩', '舌重十兩'),
    ('舌', '長', '七寸', '長七寸'),
    ('舌', '廣', '二寸半', '廣二寸半'),
    ('咽門', '重', '十兩', '咽門重十兩'),
    ('咽門', '廣', '一寸半', '廣一寸半'),
    ('咽門至胃', '長', '一尺六寸', '至胃長一尺六寸'),
    ('胃', '長', '二尺六寸', '之長二尺六寸'),
    ('胃', '大', '一尺五寸', '大一尺五寸'),
    ('胃', '徑', '五寸', '徑五寸'),
    ('胃', '容', '三斗五升', '大容三斗五升'),
    ('小腸', '大', '二寸半', '大二寸半'),
    ('小腸', '徑', '八分（分之少半）', '徑八分'),
    ('小腸', '長', '三丈二尺', '長三丈二尺'),
    ('迴腸', '大', '四寸', '大四寸'),
    ('迴腸', '徑', '一寸（寸之少半）', '徑一寸'),
    ('迴腸', '長', '二丈一尺', '長二丈一尺'),
    ('廣腸', '大', '八寸', '大八寸'),
    ('廣腸', '徑', '二寸（寸之大半）', '徑二寸'),
    ('廣腸', '長', '二尺八寸', '長二尺八寸'),
    ('腸胃總', '長', '六丈四寸四分', '長六丈四寸四分'),
    ('腸胃總', '迴曲', '三十二曲', '三十二曲'),
]

# ---------------- 五十營（第15篇）----------------
WUSHIYING = [
    ('一息', '氣行', '六寸', '呼吸定息氣行六寸'),
    ('十息', '氣行', '六尺', '十息氣行六尺'),
    ('二百七十息', '氣行', '十六丈二尺', '二百七十息氣行十六丈二尺'),
    ('五百四十息', '氣行', '再周於身', '五百四十息氣行再周于身'),
    ('二千七百息', '氣行', '十周於身', '二千七百息氣行十周于身'),
    ('一萬三千五百息', '氣行', '五十營於身', '一萬三千五百息氣行五十營于身'),
    ('五十營', '總行', '八百一十丈', '凡行八百一十丈也'),
    ('周身經脉', '長', '十六丈二尺', '二十八脉周身十六丈二尺'),
]

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
      '百': 100, '千': 1000, '萬': 10000}


def cn2int(s):
    """中文數字轉整數，處理到萬位（如「二萬七千」「一萬三千五百」）。"""
    s = s.strip()
    total, section, num = 0, 0, 0
    for ch in s:
        if ch in CN:
            v = CN[ch]
            if v == 10000:
                section = (section + num) * 10000
                total += section
                section, num = 0, 0
            elif v >= 100:
                section += (num or 1) * v
                num = 0
            elif v == 10:
                section += (num or 1) * 10
                num = 0
            else:
                num = v
    return total + section + num


def cun_of(text):
    """把「二尺六寸」「九寸八分」「六丈四寸四分」換算成寸。"""
    total = 0.0
    m = re.search(r'([一二三四五六七八九十百千萬]+)丈', text)
    if m:
        total += cn2int(m.group(1)) * 100
    m = re.search(r'([一二三四五六七八九十百]+)尺', text)
    if m:
        total += cn2int(m.group(1)) * 10
    m = re.search(r'([一二三四五六七八九十]+)寸', text)
    if m:
        total += cn2int(m.group(1))
    m = re.search(r'([一二三四五六七八九十]+)分', text)
    if m:
        total += cn2int(m.group(1)) / 10
    # 「六寸半」「一尺二寸半」的「半」不可丟——丟了會把 6.5 寸算成 6 寸
    if re.search(r'(丈|尺|寸|分)半', text):
        total += 0.5
    return round(total, 2)


def main():
    t31 = PIAN[31]['正規化']
    t15 = PIAN[15]['正規化']
    t14 = PIAN[14]['正規化']

    # 驗證：每條都須見於原文
    bad = [r for r in CHANGWEI if r[3] not in t31]
    bad += [r for r in WUSHIYING if r[3] not in t15]
    if bad:
        for b in bad:
            print('✗ 不見於原文:', b)
        raise SystemExit(f'校驗失敗 {len(bad)} 條')

    rows = [{'部位': a, '項目': b, '數值': c, '寸': cun_of(c) if '曲' not in c else '',
             '原文': d} for a, b, c, d in CHANGWEI]
    with open(os.path.join(ROOT, 'data', '表_腸胃_重建.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['部位', '項目', '數值', '寸', '原文'])
        w.writeheader()
        w.writerows(rows)

    rows15 = [{'息數': a, '項目': b, '數值': c, '寸': cun_of(c), '原文': d} for a, b, c, d in WUSHIYING]
    with open(os.path.join(ROOT, 'data', '表_五十營_重建.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['息數', '項目', '數值', '寸', '原文'])
        w.writeheader()
        w.writerows(rows15)

    # 骨度換算：以「人長七尺五寸」＝75寸為分母（原文自明）
    gd = list(csv.DictReader(open(os.path.join(ROOT, 'data', '表_骨度.csv'), encoding='utf-8-sig')))
    out = []
    for r in gd:
        c = cun_of(r['長'])
        if not c:
            out.append({**r, '寸': '', '占身長%': '', '類型': '非長度'})
            continue
        kind = '圍度' if r['起'] in ('頭之大骨', '胸', '腰') else '縱向長度'
        pct = round(c / 75 * 100, 1) if kind == '縱向長度' else ''
        out.append({**r, '寸': c, '占身長%': pct, '類型': kind})
    with open(os.path.join(ROOT, 'data', '表_骨度_換算.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['起', '訖', '長', '寸', '占身長%', '類型', '原文'])
        w.writeheader()
        w.writerows(out)

    mod = {
        '模組': '度量與換算',
        '出處': [{'篇序': 14, '篇名': '骨度'}, {'篇序': 15, '篇名': '五十營'}, {'篇序': 31, '篇名': '腸胃'}],
        '學習目標': ['記住骨度分段與其比例', '知道腸胃各部的長短容量',
                 '會用「人長七尺五寸」把骨度換成比例', '知道一息六寸如何推出五十營'],
        '說明': '數值皆見於原文；寸與比例為計算所得，非原文自帶',
        '腸胃': rows, '五十營': rows15, '骨度': out,
    }
    json.dump(mod, open(os.path.join(ROOT, 'data', '模組_度量.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('腸胃', len(rows), '條｜五十營', len(rows15), '條｜骨度', len(out), '條')
    print('驗算：一息六寸 × 13500 息 =', 6 * 13500 / 100, '丈（原文「凡行八百一十丈」）')
    print('驗算：五十營一周 =', cun_of('十六丈二尺'), '寸 ×50 =', cun_of('十六丈二尺') * 50 / 100, '丈')


if __name__ == '__main__':
    main()
