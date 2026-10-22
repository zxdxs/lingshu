#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽〈經别〉〈經筋〉〈十五絡〉三套通道資料，寫出 data/經别.json、data/經筋.json、data/絡脉.json。

三篇各是一套模板：
  〈經别〉十二正：別入→合，六組「一合」（篇 11）
  〈經筋〉十二筋：起止→其病→治在燔鍼劫刺，名曰某痹（篇 13）
  〈十五絡〉十五別：名曰某穴→起止→實則…虛則…（篇 10 後段）

所有文句取自句索引，不改字；抽不到預期條數直接失敗。

用法：python3 scripts/build_channels.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JU = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句索引.json'), encoding='utf-8'))['句']


def rows(seq):
    return [s for s in JU if s['seq'] == seq]


def clean(t):
    return t.lstrip('○')


def meridian_name(raw):
    m = re.match(r'^([\u4e00-\u9fff]{1,4})(手|足)(太陰|陽明|少陽|太陽|厥陰|少陰)$', raw)
    if not m:
        return raw
    zang, limb, yin = m.groups()
    return f'{limb}{yin}{zang}'


# ── 經别 ──
def build_jingbie():
    rs = [s for s in rows(11) if '之正' in s['text']]
    if len(rs) != 12:
        raise SystemExit(f'經别應 12，實得 {len(rs)}')
    out = []
    for i, s in enumerate(rs):
        raw = clean(s['text']).split('之正')[0]
        out.append({'序': i + 1, '經': meridian_name(raw), '原名': raw,
                    '文': s['text'], 'id': s['id']})
    # 依序兩兩成合（陽／陰）
    for i in range(0, 12, 2):
        out[i]['合'] = i // 2 + 1
        out[i + 1]['合'] = i // 2 + 1
    return {'說明': {'來源': '篇 11〈經别〉', '模板': '別入→合；六組為一合', '條數': 12}, '正': out}


# ── 經筋 ──
def build_jingjin():
    rs = rows(13)
    blocks, cur = [], None
    for s in rs:
        t = clean(s['text'])
        if '之筋' in t[:12] and '起于' in t:
            cur = {'start': s, 'body': []}
            blocks.append(cur)
        elif cur:
            cur['body'].append(s)
    out = []
    for b in blocks:
        raw = clean(b['start']['text']).split('之筋')[0]
        body = b['body']
        bing = next((x for x in body if '其病' in x['text']), None)
        zhi = next((x for x in body if '治在' in x['text']), None)
        extra = [x for x in body if x is not bing and x is not zhi and x['text'].strip('○') not in ('。', '')]
        item = {'序': len(out) + 1, '經': meridian_name(raw), '原名': raw,
                '起止': {'id': b['start']['id'], '文': b['start']['text']},
                '病': {'id': bing['id'], '文': bing['text']} if bing else None,
                '治': {'id': zhi['id'], '文': zhi['text']} if zhi else None}
        if extra:
            item['附'] = [{'id': x['id'], '文': x['text']} for x in extra]
        out.append(item)
    if len(out) != 12:
        raise SystemExit(f'經筋應 12，實得 {len(out)}')
    return {'說明': {'來源': '篇 13〈經筋〉', '模板': '起止→其病→治在燔鍼劫刺，名曰某痺', '條數': 12}, '筋': out}


# ── 十五絡 ──
def build_luomai():
    rs = rows(10)
    blocks, cur = [], None
    for s in rs:
        t = s['text']
        if ('之別' in t[:14] or '之大絡' in t[:14]) and '名曰' in t:
            cur = {'name': s, 'body': []}
            blocks.append(cur)
        elif cur:
            cur['body'].append(s)
    out = []
    for b in blocks:
        raw = clean(b['name']['text'])
        nm = raw.split('名曰')[-1].strip('。')
        head = raw.split('，名曰')[0]
        body = [x for x in b['body'] if x['text'].strip('○') not in ('。', '')]
        out.append({'序': len(out) + 1, '別': head, '穴': nm,
                    '名': {'id': b['name']['id'], '文': b['name']['text']},
                    '起止': {'id': body[0]['id'], '文': body[0]['text']} if body else None,
                    '病': {'id': body[1]['id'], '文': body[1]['text']} if len(body) > 1 else None})
    if len(out) != 15:
        raise SystemExit(f'十五絡應 15，實得 {len(out)}')
    total = next((s for s in rs if '凡此十五絡者' in s['text']), None)
    return {'說明': {'來源': '篇 10〈經脉〉後段', '模板': '名曰某穴→起止→實則…虛則…', '條數': 15},
            '絡': out, '總結': {'id': total['id'], '文': total['text']} if total else None}


def main():
    for name, fn in (('經别', build_jingbie), ('經筋', build_jingjin), ('絡脉', build_luomai)):
        data = fn()
        p = os.path.join(ROOT, 'data', f'{name}.json')
        json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        n = data.get('條數') or len(data.get('正') or data.get('筋') or data.get('絡'))
        print(f'寫出 {p}：{data["說明"]["條數"]} 條')


if __name__ == '__main__':
    main()
