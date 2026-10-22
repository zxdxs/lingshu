#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把清·張志聰《黃帝內經靈樞集註》(殆知閣本) 去注分經。

做法：以本項目 81 篇 經文為基準，逐篇與集註全文做序列比對。
比對得上的是「經文」，比對不上的殘餘是「注文」；殘餘落在哪一句之後，
就把該段注文繫到那一句。輸出只做索引與節錄（注文全文留在 vendor，不隨站發布）。

字形比對用「一字對一字」的正規化，並記住正規化位置→原字位置，
所以節錄時取回的是原排印字，不是正規化字。

輸出：data/張注.json
"""
import json
import os
import re
import sys

from zhconv import convert

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
# 繁簡與異體：一律併到單一代表字，保持一字對一字
V = {
    '於': '于', '扵': '于', '于': '于',
    '爲': '为', '為': '为', '爲': '为',
    '隂': '阴', '陰': '阴', '阴': '阴',
    '荅': '答', '答': '答', '圎': '圆', '圓': '圆',
    '閲': '阅', '閱': '阅', '舎': '舍', '舍': '舍',
    '徃': '往', '往': '往', '黄': '黄', '黃': '黄',
    '黒': '黑', '黑': '黑', '眞': '真', '真': '真',
    '徧': '遍', '遍': '遍', '痺': '痹', '痹': '痹',
    '脉': '脉', '脈': '脉', '衇': '脉',
    '衞': '卫', '衛': '卫', '夀': '寿', '壽': '寿',
    '嵗': '岁', '歲': '岁', '歳': '岁',
    '别': '别', '別': '别', '絶': '绝', '絕': '绝',
    '㑹': '会', '會': '会', '会': '会',
    '榖': '谷', '穀': '谷', '谷': '谷',
    '竒': '奇', '奇': '奇', '靣': '面', '面': '面',
    '寫': '泻', '瀉': '泻', '泻': '泻',
    '蔵': '脏', '藏': '脏', '臟': '脏', '脏': '脏',
    '敎': '教', '教': '教', '虛': '虚', '虚': '虚',
    '竅': '窍', '窍': '窍', '專': '专', '耑': '专', '専': '专', '专': '专',
    '𡵨': '岐', '岐': '岐', '榦': '干', '幹': '干',
    '渉': '涉', '涉': '涉', '脱': '脱', '脫': '脱',
    '眀': '明', '朙': '明', '明': '明',
    '高': '高', '髙': '高', '欬': '咳', '咳': '咳',
    '乗': '乘', '乘': '乘', '徴': '征',
    '朿': '束', '束': '束', '逺': '远', '遠': '远', '远': '远',
    '矇': '蒙', '曚': '蒙', '蒙': '蒙',
    '眾': '众', '衆': '众', '众': '众',
    '強': '强', '强': '强', '强': '强',
    '針': '针', '针': '针', '鍼': '针',
    '渇': '渴', '渴': '渴', '卧': '卧', '臥': '卧',
    '輸': '输', '腧': '输', '俞': '输', '输': '输',
    '并': '并', '並': '并', '并': '并',
    '宫': '宫', '宮': '宫', '宫': '宫',
    '渗': '渗', '滲': '渗', '关': '关', '闗': '关', '關': '关',
    '廹': '迫', '迫': '迫', '玊': '玉', '玉': '玉',
    '盖': '盖', '蓋': '盖', '横': '横', '橫': '横',
    '効': '效', '效': '效', '内': '内', '內': '内', '内': '内',
    '温': '温', '溫': '温', '浄': '净', '淨': '净', '净': '净',
    '宛': '宛', '菀': '宛', '蟁': '蚊', '蚊': '蚊',
    '况': '况', '況': '况', '膓': '肠', '腸': '肠', '肠': '肠',
    '狭': '狭', '狹': '狭', '狭': '狭',
    '㡬': '几', '幾': '几', '几': '几',
    '壹': '壹', '隠': '隐', '隱': '隐', '隐': '隐',
    '胷': '胸', '胸': '胸', '脇': '胁', '脅': '胁', '胁': '胁',
    '刾': '刺', '剌': '刺', '刺': '刺',
    '痠': '酸', '酸': '酸', '麤': '粗', '粗': '粗',
    '鬰': '郁', '欝': '郁', '郁': '郁', '鬱': '郁',
    '虻': '虻', '鼈': '鳖', '鼈': '鳖',
}


def canon(c):
    """單字正規化：先轉繁簡（單字），再併異體。仍是一字對一字。"""
    c = V.get(c, c)
    if c in V:
        return V[c]
    t = convert(c, 'zh-cn')
    if len(t) == 1:
        return V.get(t, t)
    return c


def norm_map(s):
    """回傳 (正規化字串, 每個正規化位置對應的原字位置)。"""
    out = []
    idx = []
    for i, ch in enumerate(s):
        if not CJK.match(ch):
            continue
        out.append(canon(ch))
        idx.append(i)
    return ''.join(out), idx


def clean_note(s):
    """去掉注文切口殘留：開頭若是音釋括注的尾巴（前 15 字內有「）」）就從「）」後起；
    再削去兩端零碎標點。"""
    head = s.find('）')
    if 0 <= head <= 15:
        s = s[head + 1:]
    s = s.strip('。）,、；：·…」')
    if len(s) > 4 and s[-1] in '，、；：·':
        s = s[:-1]
    return s


CN = {c: i for i, c in enumerate('一二三四五六七八九', 1)}


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十')
        return CN[a] * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s)


def load_jizhu():
    path = os.path.join(ROOT, 'vendor', '張志聰_靈樞集註', 'text.txt')
    lines = [l.strip() for l in open(path, encoding='utf-8') if l.strip()]
    head = re.compile(r'^(?:卷[一二三四五六七八九十]+)?(.+?)第([一二三四五六七八九十]+)$')
    run = re.compile(r'^卷[一二三四五六七八九十]+\S*第[一二三四五六七八九十]+$')
    secs = {}
    cur = None
    for l in lines:
        if l == '序':
            cur = None
            continue
        if re.fullmatch(r'卷[一二三四五六七八九十]+', l):
            continue
        m = head.fullmatch(l)
        if m and not run.fullmatch(l):
            n = cn2int(m.group(2))
            cur = n
            secs.setdefault(n, {'名': m.group(1), '文': []})
            continue
        if cur is None or run.fullmatch(l):
            continue
        secs[cur]['文'].append(l)
    return secs


def main():
    import difflib
    base = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
    ju = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']
    by_pian = {}
    for s in ju:
        by_pian.setdefault(s['pian'], []).append(s)
    secs = load_jizhu()

    out = {'說明': '清·張志聰《黃帝內經靈樞集註》注文索引：去注分經後，把注文繫到經文句。'
                   '注文為節錄，原文全文不隨站發布。',
           '來源': '殆知閣·醫藏《黃帝內經靈樞集註》（康熙壬子 1672 張隱庵序）'
                   ' https://daizhige.org/醫藏/黄帝内经灵枢集注.html',
           '取用': '2025-10-23 抓取；殆知閣為簡體排印，此處照錄不改字',
           '方法': '逐篇 difflib 序列比對：比對得者為經文，殘餘為注文；'
                   '注文落在某句之後，即繫於該句',
           '局限': '一、殆知閣為簡體排印，照錄未改字，故注文作簡體；'
                   '二、去注分經是機器比對，注文切口可能留有零碎字；'
                   '三、只取節錄，未與影印本逐字校；'
                   '四、注文只代表張志聰，不代表原文。',
           '篇': []}
    tot_note = tot_len = 0
    for p in base:
        n = p['序']
        sec = secs.get(n)
        name = p['篇名']
        if not sec:
            out['篇'].append({'序': n, '篇': name, '狀態': '未取到'})
            continue
        jl = by_pian.get(name) or by_pian.get(p['篇名_規範']) or []
        jl = sorted(jl, key=lambda x: x['seq'])
        B, pos2id = [], []
        for s in jl:
            nb, _ = norm_map(s['text'])
            B.append(nb)
            pos2id.extend([s['id']] * len(nb))
        B = ''.join(B)
        raw = ''.join(sec['文'])
        Z, zidx = norm_map(raw)
        sm = difflib.SequenceMatcher(None, B, Z, autojunk=False)
        blocks = sm.get_matching_blocks()
        notes = []
        for k in range(len(blocks) - 1):
            a, b, size = blocks[k]
            gap = Z[b + size:blocks[k + 1][1]]
            if len(gap) < 10:
                continue
            at = a + size
            sid = pos2id[at] if at < len(pos2id) else (pos2id[-1] if pos2id else None)
            rs, re_ = zidx[b + size], zidx[blocks[k + 1][1] - 1] + 1
            text = re.sub(r'\s+', '', raw[rs:re_])
            notes.append({'句': sid, '注': clean_note(text)})
        merged = {}
        for x in notes:
            merged.setdefault(x['句'], []).append(x['注'])
        item = {'序': n, '篇': name,
                '注段': len(notes), '注字': sum(len(x['注']) for x in notes),
                '經文字': len(B), '集註字': len(Z),
                '比對率': round(100.0 * sum(b[2] for b in blocks) / max(1, len(B)), 1)}
        item['注'] = {k: '…'.join(v)[:200] for k, v in merged.items()}
        out['篇'].append(item)
        tot_note += len(merged)
        tot_len += item['注字']

    ju_text = {s['id']: s['text'] for s in ju}
    # 每篇取一條最長的注作示例
    cases = []
    for x in out['篇']:
        if not x.get('注'):
            continue
        sid, txt = max(x['注'].items(), key=lambda kv: len(kv[1]))
        cases.append({'序': x['序'], '篇': x['篇'], 'id': sid,
                      '文': ju_text.get(sid, ''), '注': txt})
    # 通則：只列有張注的條
    law = json.load(open(os.path.join(ROOT, 'data', '通則.json'), encoding='utf-8'))
    zh_map = {k: v for x in out['篇'] for k, v in x.get('注', {}).items()}
    laws = []
    for g in law['組']:
        for t in g['條']:
            qs = [q for q in t['引'] if q['id'] in zh_map]
            if not qs:
                continue
            laws.append({'n': t['n'], '組': g['組'], '名': t['名'],
                         '引': [{'id': q['id'], '篇': q['篇'], '文': q['文'],
                                 '注': zh_map[q['id']]} for q in qs]})
    out['例'] = cases
    out['通則'] = laws
    out['統計'] = {'有注句數': tot_note, '注文總字': tot_len,
                   '篇': sum(1 for x in out['篇'] if x.get('注')),
                   '通則引有注': sum(1 for t in laws for _ in t['引']),
                   '通則條有注': len(laws),
                   '最低比對率': min(x['比對率'] for x in out['篇'] if '比對率' in x)}
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', '張注.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('統計', out['統計'])
    for x in out['篇'][:6]:
        print(x['序'], x['篇'], x['比對率'], x['注段'], len(x['注']))
    low = [(x['序'], x['篇'], x['比對率']) for x in out['篇'] if x.get('比對率', 0) < 85]
    print('比對率 <85 的篇', low)
    # 抽樣
    zh = {k: v for x in out['篇'] for k, v in x.get('注', {}).items()}
    for i in ['1-6-6', '7-4-1', '45-7-5']:
        print(i, '|', zh.get(i, '')[:110])


if __name__ == '__main__':
    main()
