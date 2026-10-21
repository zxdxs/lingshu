#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句讀層建置：把工作區既有的現代標點本，轉移到 SBCK 權威底本上。

原理：兩者同屬趙府居敬堂本系統，實測相似度 0.95、字數幾乎相同，
差異僅在字形（於/于、脉/脈、荅/答、粗/麤）。因此以字元級對齊
做「標點轉移」，而非重新標點。

輸出：底本/靈樞經_句讀層.json
      底本/靈樞經_SBCK_底本_句讀.md
"""
import json, re, os, glob, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "底本")
PUNC = set('，。、；：？！「」『』（）〈〉《》—…·,.;:?!()[]')

def cn2int(s):
    d = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    if s == '十': return 10
    if '十' in s:
        a, _, b = s.partition('十')
        return (d.get(a,1))*10 + (d.get(b,0) if b else 0)
    return d.get(s, 0)

# ---------- 讀入標點本 ----------
punc = {}
for f in glob.glob(os.path.join(ROOT, '灵枢经正文_一至八十一篇', '*.md')):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'^## (.+?)第([一二三四五六七八九十]+)(?:〈(.+?)〉)?\s*$(.*?)(?=^## |\Z)',
                         t, re.M | re.S):
        n = cn2int(m.group(2))
        body = m.group(4)
        body = re.sub(r'^\s*$', '', body, flags=re.M)
        punc[n] = body.strip()
print("標點本篇數:", len(punc))

ALIGN = str.maketrans('於荅脉税麤眞敎靑徳恵兎悦虗桒内户黄別絶爲并竝敍',
                      '于答脈稅粗真教青德惠兔悅虛桑內戶黃別絕為並並敘')

def anorm(s):
    return s.translate(ALIGN)

def strip_p(s):
    return ''.join(c for c in s if c not in PUNC and not c.isspace())

def punct_after(s):
    """回傳與 strip_p(s) 等長的字串，每個位置存該字之後的標點與分段"""
    out, buf = [], ''
    for c in s:
        if c in PUNC:
            buf += c
        elif c.isspace():
            buf += '\n' if c == '\n' else ''
        else:
            out.append(buf); buf = ''
    out.append(buf)
    # 合併：把標點掛到前一個字
    res = [''] * len(out)
    for i in range(len(out) - 1):
        res[i] = out[i + 1]
    return ''.join(x.lstrip('\n') if False else x for x in res)

base = json.load(open(os.path.join(OUT, '靈樞經_81篇.json'), encoding='utf-8'))['篇']
result = []
for ch in base:
    n = ch['序']
    A = ch['正規化'].replace('\n', '')
    if n not in punc:
        result.append({'序': n, '篇名': ch['篇名_規範'], 'status': '無標點本', '句讀': A})
        continue
    B_orig = punc[n]
    B = strip_p(B_orig)
    # 標點掛載表：pa[i] = 第 i 個字「之後」的標點
    pa = [''] * (len(B) + 1)
    idx = -1
    buf = ''
    for c in B_orig:
        if c in PUNC:
            buf += c
        elif c.isspace():
            if c == '\n':
                buf += '\n'
        else:
            if idx >= 0:
                pa[idx] = buf
            buf = ''
            idx += 1
    if idx >= 0:
        pa[idx] = buf
    Aa, Ba = anorm(A), anorm(B)
    sm = difflib.SequenceMatcher(None, Aa, Ba, autojunk=False)
    out = []
    ratio = sm.ratio()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                out.append(A[i1 + k] + pa[j1 + k])
        elif tag == 'replace':
            seg = A[i1:i2]
            # 逐字盡量對齊掛點
            for k in range(i2 - i1):
                j = j1 + k if (j1 + k) < j2 else j2 - 1
                pp = pa[j] if 0 <= j < len(pa) else ''
                out.append(A[i1 + k] + pp)
        elif tag == 'delete':
            out.append(A[i1:i2])
        # insert: B 多出的字，忽略
    text = ''.join(out)
    text = re.sub(r'\n{2,}', '\n', text)
    result.append({'序': n, '篇名': ch['篇名_規範'], 'status': 'ok',
                   '對齊相似度': round(ratio, 4), '句讀': text})

ok = [r for r in result if r['status'] == 'ok']
print(f"成功 {len(ok)}/{len(base)}｜平均相似度 {sum(r['對齊相似度'] for r in ok)/max(1,len(ok)):.4f}")
print(f"最低相似度: {min(ok,key=lambda r:r['對齊相似度'])['篇名']} {min(r['對齊相似度'] for r in ok)}")

json.dump({'說明': '現代標點自既有標點本轉移至 SBCK 底本；標點屬詮釋，未經人工複核',
           '層級': 'modern_punctuation (transferred)',
           '篇': result},
          open(os.path.join(OUT, '靈樞經_句讀層.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, '靈樞經_SBCK_底本_句讀.md'), 'w', encoding='utf-8') as f:
    f.write('# 黃帝素問靈樞經（四部叢刊本）· 句讀層\n\n')
    f.write('> **底本**：四部叢刊本《黃帝素問靈樞經》（SBCK / Kanripo KR3e0002）。\n')
    f.write('> **句讀**：現代標點，自工作區既有標點本**轉移**而來，非重新標點。\n')
    f.write('> **性質**：標點屬詮釋層（`modern_punctuation`），**未經人工逐句複核**。原文層見 `靈樞經_SBCK_底本.md`。\n\n---\n\n')
    for r in result:
        f.write(f"## {r['序']}. {r['篇名']}\n\n{r['句讀']}\n\n")
print("已輸出句讀層")
