#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""引文驗證：把文件中所有「……」引文逐字對回底本。

用途：專章裡的每一句〔原〕都必須能在底本找到；找不到的，
      要嘛是引錯，要嘛是跨版本異文，要嘛根本不是原文。
用法：python3 scripts/check_quotes.py docs/49_概念釐清.md
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U0002A6DF]')
VAR = {'於': 'A', '于': 'A', '扵': 'A', '爲': 'B', '為': 'B', '隂': 'C', '陰': 'C',
       '荅': 'D', '答': 'D', '圎': 'E', '圓': 'E', '緻': 'F', '致': 'F', '閲': 'G',
       '閱': 'G', '舎': 'H', '舍': 'H', '徃': 'I', '往': 'I', '黄': 'J', '黃': 'J',
       '黒': 'K', '黑': 'K', '眞': 'L', '真': 'L', '徧': 'M', '遍': 'M', '痺': 'N',
       '痹': 'N', '脉': 'O', '脈': 'O', '衞': 'P', '衛': 'P', '夀': 'Q', '壽': 'Q',
       '嵗': 'R', '歲': 'R', '歳': 'R', '别': 'S', '別': 'S', '絶': 'T', '絕': 'T',
       '㑹': 'U', '會': 'U', '榖': 'V', '穀': 'V', '竒': 'W', '奇': 'W', '靣': 'X',
       '面': 'X', '寫': 'Z', '瀉': 'Z', '蔵': '藏', '藏': '藏', '敎': '教', '虛': '虚', '衇': 'O', '竅': '竅',
       '專': '專', '耑': '專', '専': '專', '𡵨': '岐', '榦': '幹', '渉': '涉', '脱': '脫', '眀': '明', '高': '髙', '欬': '咳', '乗': '乘', '徴': '徵', '朿': '束', '遠': '逺', '矇': '曚', '眾': '衆', '強': '强', '針': '鍼', '渇': '渴', '卧': '臥', '輸': '腧', '俞': '腧', '并': '並', '宫': '宮', '渗': '滲', '闗': '關', '廹': '迫', '玊': '玉', '盖': '蓋', '横': '橫', '効': '效', '内': '內', '温': '溫', '浄': '淨', '宛': '菀', '蟁': '蚊', '虻': '虻', '况': '況', '况': '況', '膓': '腸', '遍': '遍', '狭': '狹', '㡬': '幾', '幹': '幹', '壹': '一', '隠': '隱', '胷': '胸', '脇': '脅', '刾': '刺', '剌': '刺', '痠': '酸'}


def norm(s):
    return ''.join(VAR.get(c, c) for c in s if CJK.match(c))


def main():
    if len(sys.argv) < 2:
        print('用法：python3 scripts/check_quotes.py <markdown 檔>')
        return 1
    path = sys.argv[1]
    base = ''.join(p['正規化'] for p in
                   json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇'])
    B = norm(base)
    text = open(path, encoding='utf-8').read()

    quotes = re.findall(r'「([^」]{4,})」', text)
    # 含省略號者視為節引：明示了刪節，不要求逐字連續
    excerpt = [q for q in quotes if '…' in q]
    quotes = [q for q in quotes if '…' not in q]
    ok = miss = 0
    for q in quotes:
        n = norm(q)
        if not n:
            continue
        if n in B:
            ok += 1
        else:
            miss += 1
            print(f'✗ 找不到：{q[:60]}')
    # 另檢引文塊（以 > 開頭的行）：去掉引號、強調與篇名註後逐字比對。
    # 先判「這行像不像原文」：4-gram 覆蓋率 < 0.6 者視為說明文字，不核。
    def _cover4(s):
        if len(s) < 8:
            return 0.0
        g = [s[i:i + 4] for i in range(len(s) - 3)]
        return sum(1 for x in g if x in B) / len(g)

    blk_ok = blk_miss = blk_skip = 0
    for line in text.split('\n'):
        if not line.startswith('>'):
            continue
        if '<!--異文-->' in line or '<!--節引-->' in line:
            blk_skip += 1
            continue
        body = re.sub(r'（〈[^〉]+〉）|（並〈[^〉]+〉）', '', line)
        body = body.lstrip('> ').replace('**', '').replace('「', '').replace('」', '')
        body = re.sub(r'^[^：]{1,8}：', '', body)   # 去掉「原文：」「要訣：」這類前綴
        body = body.strip('。 ')
        if '…' in body:                            # 節引：已明示刪節，不逐字核
            blk_skip += 1
            continue
        parts = [x for x in body.split('／') if len(norm(x)) >= 8]
        if not parts:
            parts = [body]
        for part in parts:
            n = norm(part)
            if len(n) < 8:
                continue
            if n not in B and _cover4(n) < 0.6:
                blk_skip += 1
                continue
            if n in B:
                blk_ok += 1
            else:
                blk_miss += 1
                print(f'✗ 引文塊待核：{part[:60]}')

    print(f'\n短引 {len(quotes)} 條：相符 {ok}｜待核 {miss}')
    print(f'引文塊 {blk_ok + blk_miss} 條：相符 {blk_ok}｜待核 {blk_miss}' + (f'｜說明文字 {blk_skip}（不核）' if blk_skip else ''))
    return 0 if miss == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
