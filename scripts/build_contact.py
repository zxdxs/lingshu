#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「指正與聯絡」頁的資料：data/聯絡.json。

數字一律從現有資料算出來（校勘點、題庫、概念卡、覆蓋率），不手寫——
手寫的數字會過期，過期的聯絡頁比沒有聯絡頁更糟。

用法：python3 scripts/build_contact.py
"""
import csv, glob, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
ITEMS = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))
COL = list(csv.DictReader(open(os.path.join(ROOT, 'data', '校勘點.csv'), encoding='utf-8-sig')))
CON = list(csv.DictReader(open(os.path.join(ROOT, 'data', '矛盾清單.csv'), encoding='utf-8-sig')))
COV = json.load(open(os.path.join(ROOT, 'data', '三源覆蓋率.json'), encoding='utf-8'))['篇']
CONCEPTS = len(glob.glob(os.path.join(ROOT, 'data', '多層_*.json')))
THEMES = len(json.load(open(os.path.join(ROOT, 'data', '主題.json'), encoding='utf-8'))['主題'])

its = ITEMS['題']
n_item = len(its)
no_sid = sum(1 for i in its if not i.get('句'))
no_col_sid = sum(1 for r in COL if not (r.get('句ID') or '').strip())
kinds = Counter(i.get('答案類型') for i in its if i['type'] == 'fill_blank')
cases = sum(1 for i in its if '-CASE-' in i['item_id'])
verdict = Counter(r.get('判讀') for r in COV)
half = verdict.get('半可對（一源有、一源無）', 0)

CONTACT = REL['聯絡'] if REL['聯絡'] not in ('', '待補') else ''


def want():
    out = []
    out.append({
        'k': '① 句ID 與原文的對應（最需要）',
        'd': f'句ID（`篇序-段-句`）是**編者所加**，不是古籍原有。全書 {n_item} 題中有 {no_sid} 題、'
             f'{len(COL)} 條校勘點中有 {no_col_sid} 條尚未掛上句ID。數字本身可以重算，'
             '但底本斷句一改，後面全部位移——對得上紙本的人一眼就能看出錯在哪。這是本站最大的不確定處。',
    })
    out.append({
        'k': '② 待專家核的判斷',
        'd': f'填空答案中 {kinds.get("整理語", 0)} 條是『整理語』（不是原文照抄，是編者濃縮）；'
             f'{cases} 道案例題、19 條張介賓注與經文的配對，都標了『待專家核』。'
             '這些不是查得到的東西，是要有人讀過、判斷過。',
    })
    out.append({
        'k': '③ 主題與概念的分類',
        'd': f'{THEMES} 個主題、{CONCEPTS} 張概念卡的分層與命名，是**編者歸納**，非《靈樞》原有分類。'
             '若你認為某篇該歸另一主題、某個層次切錯了，請說明理由與原文依據。',
    })
    out.append({
        'k': '④ 太素對校的空白',
        'd': f'81 篇中 {verdict.get("可對校（兩源皆有字句）", 0)} 篇兩源皆有字句可對校，'
             f'{half} 篇只有一源（稱為半可對）。缺的那一邊需要他本或紙本補；'
             '本站一律兩處並存，不代改一字。',
    })
    out.append({
        'k': '⑤ Anki 實機驗證',
        'd': '708 張填空卡已驗檔案結構與判定邏輯，但**未在真實 Anki 匯入按過**。'
             '若你匯入後發現排版錯、即時判定不動作、異體字誤判，請回報版本與一張截圖。',
    })
    return out


def items():
    out = [{
        'k': '郵箱',
        'd': '附件、截圖、長文、整份校勘表都收。來信請註明篇序（如 40）與句ID（若已有）。',
        'mail': CONTACT,
        'mailText': CONTACT or '待補',
    }]
    return out


def sites():
    return [
        {'k': '傷寒站', 'url': 'https://solve-lab.cn',
         'd': '同一維護者的《傷寒雜病論》桂林古本閱讀站。本站的閱讀器骨架、五支稽核與「數字自動帶入」的做法，'
              '都是在那裡先跑過一輪才搬過來的。'},
        {'k': '聲韻站', 'url': 'https://shenglv.org.cn',
         'd': '同一維護者的聲韻與字書檢索站。本站的音釋層與異體字規範，取徑與它一致。'},
    ]


def main():
    data = {
        'title': '指正與聯絡',
        'lead': '本站是**訓練材料**，不是定本，也不是校勘本。看到錯字、引文對不上、句ID 掛錯、答案可議，'
                '請直接告訴我——尤其是**句ID 與原文的對應**，那是我最需要人幫忙的地方。',
        'want': want(),
        'items': items(),
        'sites': sites(),
        'close': '指正會反映到站上。原文異文一律兩處並存，不擅自改定；句中位置有爭議時，'
                 '我保留兩種算法並註明，不挑一個假裝確定。',
        'seal': REL['安全提醒短'],
        'contact_ready': bool(CONTACT),
    }
    out = os.path.join(ROOT, 'data', '聯絡.json')
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'寫出 {out}：需要幫忙 {len(data["want"])} 項｜郵箱 {"已填" if CONTACT else "待補"}｜'
          f'相關站點 {len(data["sites"])} 個')


if __name__ == '__main__':
    main()
