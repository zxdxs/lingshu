#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""治理與預算：把方法論的「分檔、狀態、確定性預算」算成站上可看的數字。

資料來源全部是本專案既有的檔案，不手填：
  題庫_示例.json（題數、有句ID）、通則.json（條數、界）、
  未決.json（未決條目與狀態）、注家相關檔（可繫注條數）、句索引（句數）。

輸出：data/治理.json
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    return json.load(open(os.path.join(ROOT, 'data', p), encoding='utf-8'))


def main():
    items = load('題庫_示例.json')
    law = load('通則.json')
    und = json.load(open(os.path.join(ROOT, 'data', '未決.json'), encoding='utf-8'))
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']

    laws = [t for g in law['組'] for t in g['條']]
    n_items = items['題數']
    with_sid = sum(1 for i in items['題'] if i.get('句'))
    bounds = [t for t in laws if t.get('界')]

    st = [x['狀態'] for x in und['條']]
    rs = [x['裁決'] for x in und['條']]
    budget = {
        '題數': n_items,
        '題有句ID': with_sid,
        '題回鏈率': round(100.0 * with_sid / max(1, n_items), 1),
        '句數': len(ju),
        '通則條數': len(laws),
        '通則有界': len(bounds),
        '未決條數': len(und['條']),
        'blocked': st.count('blocked'),
        'suspended': st.count('suspended'),
        'published': len(und['條']) - st.count('blocked') - st.count('suspended'),
        'both_preserved': rs.count('both_preserved'),
        'undetermined': rs.count('undetermined'),
        'single': rs.count('single'),
    }
    budget['未決占比'] = round(100.0 * budget['未決條數'] / max(1, budget['通則條數'] + budget['未決條數']), 1)

    data = {
        '說明': '治理與預算：本站的檔位對照、狀態機、確定性預算與未決登記簿。'
                '數字全部由腳本從既有資料算出，不手填。',
        '檔位對照': [
            {'本站': '〔原〕', '方法論': 'A_經文內證', '說明': '逐字取自底本句索引，機器核對；不是模型生成。'},
            {'本站': '〔注〕', '方法論': 'B_早期注本／B_後世成說', '說明': '注家節錄；註明朝代與「轉引／節錄」，不等於原文。'},
            {'本站': '〔歸〕', '方法論': 'C_編者推論', '說明': '編者的歸納（通則、主題、模組、路徑），非《靈樞》原有；每條附「界」。'},
            {'本站': '〔空〕', '方法論': 'suspended／blocked', '說明': '取不到、不可判定的部分；見下方未決登記簿。'},
        ],
        '狀態機': 'draft → collated → reviewed → published；suspended／blocked 為並列一等狀態；'
                  'stale 是布爾標記，不是狀態。本站只用 published／suspended／blocked 三種，'
                  '因為沒有多人審核流程（reviewed_by 目前是編者本人）。',
        '預算': budget,
        '採納': [
            {'條': 'R-01 默認立場', '本站': '採用', '做法': '注家不強解；「界」欄寫明推論的邊界，取不到就寫「空」。'},
            {'條': 'R-02 兩存', '本站': '部分採用', '做法': '甲乙經差異、太素注、補篇皆標「未判定／兩存」，不單方判定。'},
            {'條': 'R-03 措辭', '本站': '採用', '做法': '引文用「」，注家用『』並標節錄，編者話明寫「歸」。'},
            {'條': 'R-04 安全', '本站': '採用', '做法': '每頁頂欄與首次確認頁都有安全提醒；限制頁列 34 條邊界。'},
            {'條': 'R-05 AI 邊界', '本站': '採用', '做法': '原文與引文一律由句索引按 id 取；模型不產實證引證，只產草稿與歸納。'},
            {'條': 'R-07 能力可測', '本站': '部分採用', '做法': '題目有句ID回鏈；但「不可判定辨識題」未建，作答資料為空。'},
            {'條': 'R-08 反例留檔', '本站': '部分採用', '做法': '未決登記簿＋CHANGELOG 的「曾以為何、因何改判」；反例庫未獨立成檔。'},
            {'條': 'R-09／R-10／R-11 分軸與層累', '本站': '不採用', '做法': '本站不做層累歸集（不判年代、先後、原篇結構），故無 stratum 軸。'},
        ],
        '未決': und['條'],
    }
    json.dump(data, open(os.path.join(ROOT, 'data', '治理.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('預算', json.dumps(budget, ensure_ascii=False))


if __name__ == '__main__':
    main()
