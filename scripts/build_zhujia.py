#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽取《類經》的條目結構與張介賓注。

《類經》體例（四庫本）：
    ＸＸ類                                  ← 十二類之一
    ＸＸＸＸ(素問／靈樞某篇○條號)            ← 條題＋出處
    經文(注文)經文(注文)…                   ← 注文用半角括號包裹

因此可機械分離：括號外為經文，括號內為張介賓注。
這正是先前完全沒有利用的層——L1 歸納題本來應該站在它上面，而不是站在我的概括上。
"""
import glob, json, os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'vendor', 'KR3e0085_類經')

CATS = ['攝生', '陰陽', '藏象', '脉色', '經絡', '標本', '氣味', '論治',
        '疾病', '鍼刺', '運氣', '會通']

TIAO_RE = re.compile(r'^(.{2,60}?)\(([^()]*?)○([^()]*?)\)$')
# 另一種體例：條題只帶條號，出處藏在第一條注的開頭，如「刺灸癲狂(三十七)」
TIAO2_RE = re.compile(r'^(.{2,40}?)\(([一二三四五六七八九十百]{1,3})\)$')
SRC_IN_NOTE = re.compile(r'^(素問|靈樞)(.{1,20}?)○')


def clean(line):
    line = re.sub(r'<pb:[^>]*>', '', line)
    line = line.replace('¶', '').replace('\u3000', '').strip()
    return line


def split_pairs(text):
    """回傳 [(括號前的經文, 括號內注文), ...]，保留兩者的相鄰關係。

    這一步是關鍵：類經的注緊跟所注經文之後，所以「注」的意義由它前面那段經文決定。
    只把注抽出來、不記它注的是哪一句，得到的是一堆無主的評論。
    """
    pairs, seg, buf, depth, pending = [], [], [], 0, []
    for ch in text:
        if ch == '(':
            depth += 1
            if depth == 1:
                buf = []
                continue
        elif ch == ')':
            depth = max(0, depth - 1)
            if depth == 0:
                pairs.append((''.join(pending), ''.join(buf)))
                pending = []
                continue
        if depth:
            buf.append(ch)
        else:
            pending.append(ch)
    if pending:
        pairs.append((''.join(pending), ''))
    return pairs


def split_parens(text):
    """回傳 (括號外文字, [括號內文字...])。支援半角括號，不跨行。"""
    out, notes, buf, depth = [], [], [], 0
    for ch in text:
        if ch == '(':
            depth += 1
            if depth == 1:
                buf = []
                continue
        elif ch == ')':
            depth = max(0, depth - 1)
            if depth == 0:
                notes.append(''.join(buf))
                continue
        if depth:
            buf.append(ch)
        else:
            out.append(ch)
    return ''.join(out), notes


def main():
    entries = []
    cur_cat = ''
    for f in sorted(glob.glob(os.path.join(SRC, 'KR3e0085_0*.txt'))):
        juan = os.path.basename(f).split('_')[1].split('.')[0]
        raw = open(f, encoding='utf-8').read()
        lines = [clean(l) for l in raw.split('\n')]
        lines = [l for l in lines if l]
        # 換頁處會把一行切斷（括號未閉），先把括號不平衡的行與下一行接回
        merged, carry = [], ''
        for l in lines:
            l = carry + l
            if l.count('(') != l.count(')'):
                carry = l
                continue
            carry = ''
            merged.append(l)
        if carry:
            merged.append(carry)
        lines = merged
        cur = None
        buf = []

        def flush():
            nonlocal cur, buf
            if cur is not None:
                body, notes = split_parens(''.join(buf))
                pairs = split_pairs(''.join(buf))
                notes = [n for n in notes if n]
                # 出處藏在首注開頭者，此處析出
                if not cur['出處'] and notes:
                    m2 = SRC_IN_NOTE.match(notes[0])
                    if m2:
                        cur['出處'] = m2.group(1) + m2.group(2)
                        rest = notes[0][m2.end():]
                        notes[0] = rest
                        notes = [n for n in notes if n]
                cur['經文'] = body
                cur['注'] = notes
                cur['對注'] = [{'經': a, '注': b} for a, b in pairs if b]
                entries.append(cur)
            cur, buf = None, []

        for l in lines:
            if l.startswith('#') or l.startswith('='):
                continue
            m = TIAO_RE.match(l)
            if len(l) <= 6 and l.endswith('類') and l[:-1].replace('隂', '陰') in CATS:
                flush()
                cur_cat = l[:-1].replace('隂', '陰')
                continue
            if re.match(r'^類經卷', l) or l.startswith('欽定四庫全書') or l == '類經':
                flush()
                continue
            m2 = TIAO2_RE.match(l)
            if m2 and not m:
                flush()
                cur = {'卷': juan, '類': cur_cat, '條題': m2.group(1), '出處': '',
                       '條號': m2.group(2).strip(), '經文': '', '注': []}
                buf = []
                continue
            if m and len(m.group(1)) <= 40:
                flush()
                cur = {'卷': juan, '類': cur_cat, '條題': m.group(1),
                       '出處': m.group(2), '條號': m.group(3).strip(),
                       '經文': '', '注': []}
                buf = []
                continue
            if cur is not None:
                buf.append(l)
        flush()

    # 去掉明顯誤判：出處須為書名（素問/靈樞/…），否則多為注文中的「○音切」被誤認為條號
    BOOKS = ('素問', '靈樞', '鍼經', '難經', '甲乙', '傷寒', '金匱', '脉經', '中藏')
    good = [e for e in entries
            if len(e['經文']) >= 8 and any(b in e['出處'] for b in BOOKS)]
    print(f'抽出條目 {len(good)}（原始 {len(entries)}）')
    from collections import Counter
    print('分類分布:', dict(Counter(e['類'] for e in good)))
    src = Counter()
    for e in good:
        t = e['出處']
        if '素問' in t:
            src['素問'] += 1
        elif '靈樞' in t or '鍼經' in t or '九鍼' in t:
            src['靈樞'] += 1
        else:
            src['他書/未標'] += 1
    print('出處來源:', dict(src))
    for e in good[:3]:
        print(f"  [{e['類']}] {e['條題']}｜{e['出處']}○{e['條號']}｜經{len(e['經文'])}字 注{sum(len(x) for x in e['注'])}字")

    json.dump({'說明': '類經四庫本條目結構；經文與張介賓注已分離',
               '條數': len(good), '條目': good,
               '已知限制': [
                   'C3 抽出 348 條，四庫提要稱 390 條；會通類未解析出條目',
                   '注文內可能混入少量校語（非張介賓語），未逐條區分',
                   '條目以「出處含書名」過濾，出處未標書名者被排除',
                   '詳見 data/能力邊界.csv 與 docs/42',
               ]},
              open(os.path.join(ROOT, 'data', '類經條目.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
