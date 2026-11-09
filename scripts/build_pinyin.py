#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""為誦讀頁生成逐字拼音（帶聲調）。

資料來源：底本/靈樞經_句索引.json（3,289 句）。
生成器：pypinyin（0.55）。經文多音字、古讀不少，所以另立一張校訂表：
  · 詞組級：五藏、藏象、少陰、中風、惡血、更發、乾薑、內穀…
  · 單字級：寫→xiè（即「瀉」）、俞→shù、溺→niào
校訂只收「明顯讀錯會影響意思」的，其餘照生成器；不做全面古音考證。

輸出：data/拼音.json {統計, 句: {id: "huáng dì wèn…"}}
"""
import json
import os
import re
import sys

from pypinyin import pinyin, Style, load_phrases_dict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')

PHRASES = {
    '五藏': [['wǔ'], ['zàng']], '五藏六府': [['wǔ'], ['zàng'], ['liù'], ['fǔ']],
    '藏象': [['zàng'], ['xiàng']], '藏氣': [['zàng'], ['qì']], '藏府': [['zàng'], ['fǔ']],
    '少陰': [['shào'], ['yīn']], '少陽': [['shào'], ['yáng']], '少氣': [['shào'], ['qì']],
    '少腹': [['shào'], ['fù']], '少商': [['shào'], ['shāng']], '少澤': [['shào'], ['zé']],
    '少衝': [['shào'], ['chōng']], '少府': [['shào'], ['fǔ']], '少海': [['shào'], ['hǎi']],
    '中風': [['zhòng'], ['fēng']], '中於': [['zhòng'], ['yú']], '中人也': [['zhòng'], ['rén'], ['yě']],
    '惡血': [['wù'], ['xuè']], '惡寒': [['wù'], ['hán']], '更發': [['gēng'], ['fā']],
    '更止': [['gēng'], ['zhǐ']], '更居': [['gēng'], ['jū']], '更起': [['gēng'], ['qǐ']],
    '乾薑': [['gān'], ['jiāng']], '內穀': [['nà'], ['gǔ']], '大淵': [['tài'], ['yuān']],
    '大衝': [['tài'], ['chōng']], '大谿': [['tài'], ['xī']], '大白': [['tài'], ['bái']],
    '大陰': [['tài'], ['yīn']], '大陽': [['tài'], ['yáng']], '數刺': [['shuò'], ['cì']],
    '數欠': [['shuò'], ['qiàn']], '長養': [['zhǎng'], ['yǎng']],
}
SINGLE = {'寫': 'xiè', '俞': 'shù', '溺': 'niào'}


def main():
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    load_phrases_dict({k: v for k, v in PHRASES.items()})
    out = {}
    bad = 0
    unknown = {}
    for s in ju:
        text = s['text']
        chars = [c for c in text if CJK.match(c)]
        syl = []
        for ch in chars:
            if ch in SINGLE:
                syl.append(SINGLE[ch])
                continue
            r = pinyin(ch, style=Style.TONE, heteronym=False)
            v = r[0][0] if r and r[0] else ch
            if not re.fullmatch(r"[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüńňǹê]+", v):
                unknown[ch] = unknown.get(ch, 0) + 1
            syl.append(v)
        if len(syl) != len(chars):
            bad += 1
        out[s['id']] = ' '.join(syl)
    data = {
        '說明': '逐字拼音（帶聲調），與句索引的漢字一一對應；非漢字（標點、數字）不標。'
                '多音字與古讀以校訂表處理，未全面考證；遇罕字可能保留原字。',
        '生成': 'pypinyin 0.55.0，校訂詞組 %d 條、單字 %d 個' % (len(PHRASES), len(SINGLE)),
        '統計': {'句': len(out), '對齊失敗': bad, '未收字數': len(unknown),
                 '未收字': dict(sorted(unknown.items(), key=lambda kv: -kv[1])[:30])},
        '句': out,
    }
    json.dump(data, open(os.path.join(ROOT, 'data', '拼音.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print(data['統計'])


if __name__ == '__main__':
    main()
