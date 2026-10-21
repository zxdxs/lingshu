#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修復史崧音釋的欄序。

底本卷末音釋為雙欄排印，轉錄時被線性化成「字(後欄/前欄)」。
即：括號內斜線**後**的半段是音注的前半，斜線**前**的半段是後半。
例：(切/戸當) → 戸當切；(皮/音) → 音皮；(又音毫/莫高切) → 莫高切又音毫。

修復：把每個括號內的兩段對調後接回，並處理一字多括號（如「恇(王/曲)(謂不足也/切謹按恇)」）。
"""
import json, os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '底本', '音釋層.json')
OUT = os.path.join(ROOT, 'data', '音釋層_修復.json')

HEAD = re.compile(r'([\u3400-\u9fff]{1,4})((?:\([^()]*\))+)')
PAREN = re.compile(r'\(([^()]*)\)')
SLASH = re.compile(r'^(.*?)/(.*)$')


def fix_paren(inner):
    """單一括號：對調兩段。無斜線者原樣保留。"""
    m = SLASH.match(inner)
    if not m:
        return inner
    before, after = m.group(1), m.group(2)
    return after + before


def parse(text):
    out = []
    for m in HEAD.finditer(text):
        word, groups = m.group(1), m.group(2)
        parts = [fix_paren(g) for g in PAREN.findall(groups)]
        note = '；'.join(p for p in parts if p)
        # 雙字詞的音注常以「上…下…」分述，拆成兩條才可用
        m2 = re.match(r'^上(.+?)下(.+)$', note)
        if len(word) == 2 and m2:
            out.append({'字': word[0], '音注': m2.group(1)})
            out.append({'字': word[1], '音注': m2.group(2)})
        else:
            out.append({'字': word, '音注': note})
    return out


def main():
    d = json.load(open(SRC, encoding='utf-8'))['音釋']
    allrows, stat = [], []
    for x in d:
        ents = parse(x['音釋'])
        stat.append({'卷': x['卷'], '條數': len(ents)})
        for e in ents:
            allrows.append({'卷': x['卷'], '字': e['字'], '音注': e['音注']})

    # 校驗：罕字表已人工確認的九條反切
    known = {}
    with open(os.path.join(ROOT, 'data', '罕字表.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            v = (r['反切(史崧音釋)'] or '').strip()
            if v:
                known[r['字']] = v
    got = {}
    for r in allrows:
        got.setdefault(r['字'], []).append(r['音注'])
    ok = bad = 0
    ALT = {'㰱': '歃'}   # 罕字表作擴充A區字，底本音釋用通行字
    for ch, want in known.items():
        key = ch if ch in got else ALT.get(ch, ch)
        cand = ' '.join(v for k, vs in got.items() if key in k for v in vs)
        if want.replace('切', '') and want.replace('切', '') in cand:
            ok += 1
        else:
            bad += 1
            print(f'  ✗ {ch} 期望「{want}」得「{cand[:40]}」')
    print(f'校驗：{ok}/{ok + bad} 條與罕字表相符')
    print('各卷條數:', {s['卷']: s['條數'] for s in stat}, '合計', len(allrows))
    # 有多少佔比含「切」或「音」
    fanqie = sum(1 for r in allrows if r['音注'].endswith('切'))
    zhiyin = sum(1 for r in allrows if r['音注'].startswith('音') and not r['音注'].endswith('切'))
    gloss = len(allrows) - fanqie - zhiyin
    print(f'反切 {fanqie}｜直音 {zhiyin}｜其他（訓釋/異文） {gloss}｜合計 {len(allrows)}')
    print(f'  已可讀（反切+直音）：{fanqie+zhiyin}/{len(allrows)} = {(fanqie+zhiyin)/len(allrows)*100:.1f}%')

    json.dump({'說明': '史崧音釋，欄序已修復（原(後/前)→前後）',
               '來源': '底本/音釋層.json', '條數': len(allrows),
               '各卷': stat, '音釋': allrows},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'data', '音釋層_修復.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['卷', '字', '音注'])
        w.writeheader()
        w.writerows(allrows)


if __name__ == '__main__':
    main()
