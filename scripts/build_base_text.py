#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立《靈樞經》權威底本（方案 A：換底本）

底本：四部叢刊本《黃帝素問靈樞經》（SBCK，明趙府居敬堂本系統，12 卷 81 篇）
來源：Kanripo 漢籍リポジトリ GitHub 鏡像 kanripo/KR3e0002（四部叢刊影印本錄文）
授權：所據底本為 1919–1936 年影印之公有領域古籍；錄文由 Kanripo 計畫製作

三層輸出，對應方法論的 L0／L1／L2：
  L0  原文   —— 含小字夾註，逐字保留
  L1  經文   —— 剝離夾註與音釋後的正文
  L2  音釋   —— 史崧音釋（反切、異文），獨立保存
另出「正規化」層，僅作字形規範，供檢索用。

輸出：
  底本/靈樞經_SBCK_底本.md      人類可讀（正規化經文）
  底本/靈樞經_81篇.json         結構化（原文／經文／正規化／夾註／分段）
  底本/音釋與夾註.json          L2 註釋層
  底本/異體字規範表.csv
"""
import re, json, csv, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("KR_DIR", os.path.join(ROOT, "vendor", "KR3e0002-master"))
OUT = os.path.join(ROOT, "底本")
os.makedirs(OUT, exist_ok=True)

CJK = r'\u3400-\u4dbf\u4e00-\u9fff'
PAREN = re.compile(r'\([^)]*\)')
ENTITY = re.compile(r'&KR\d+;')

# ---------------------------------------------------------------- 1. 讀取（含音釋剝離）
YS = re.compile(r'\([^)]*\)')
ENTITY = re.compile(r'&KR\d+;')

def is_yinshi(l):
    """純音釋行：含括號與斜線，且除去括註後殘文極短"""
    if '(' not in l or '/' not in l:
        return False
    return len(YS.sub('', l).strip('\u3000 ')) <= 12

def read_volume(path):
    lines = []
    for l in open(path, encoding='utf-8'):
        if l.startswith('#'):
            continue
        l = re.sub(r'<pb:[^>]*>', '', l).replace('¶', '').replace('\n', '')
        l = ENTITY.sub('□', l)
        if not l.strip():
            continue
        lines.append(l)
    body, ys = [], []
    for l in lines:
        if re.search(r'[黃黄]帝素問靈樞經[卷巻](?:第)?之', l):
            continue                                   # 卷末題
        if '\u3000' in l:
            pre, _, post = l.rpartition('\u3000')
            if ('(' in post and not post.startswith(('〇', '○'))
                    and len(YS.sub('', post).strip('\u3000 ')) <= 12):   # 同行接音釋
                if pre.strip():
                    body.append(pre)
                ys.append(post)
                continue
        if is_yinshi(l):
            ys.append(l)
            continue
        body.append(l)
    return ''.join(body), ''.join(ys)

files = [f'KR3e0002_{i:03d}.txt' for i in range(1, 13)]
body_parts, yinshi_all = [], []
for f in files:
    b, y = read_volume(os.path.join(SRC, f))
    body_parts.append(b)
    if y:
        yinshi_all.append({'卷': f[-7:-4], '音釋': ENTITY.sub('', y).replace('¶', ''),
                         '音釋_純文': ENTITY.sub('', PAREN.sub('', y)).replace('¶', '')})
body = ''.join(body_parts)

front = ''.join(l.rstrip('\n') for l in open(os.path.join(SRC, 'KR3e0002_000.txt'), encoding='utf-8')
                if not l.startswith('#'))
front = re.sub(r'<pb:[^>]*>', '', front).replace('¶', '\n').replace('\ufeff', '')

# ---------------------------------------------------------------- 2. 目錄
i = front.find('黃帝素問靈樞經目錄')
toc, juan = [], 0
for raw in (front[i:] if i >= 0 else '').split('\n'):
    l = raw.strip().replace('\u3000', '')
    if not l:
        continue
    mj = re.match(r'^卷之([一二三四五六七八九十]+)$', l)
    if mj:
        juan += 1
        continue
    m = re.match(r'^(.+?)第([一二三四五六七八九十]+)(?:\(([^)]*)\))?$', l)
    if m:
        toc.append({'name': m.group(1), 'num_cn': m.group(2), 'juan': juan,
                    'annotation': m.group(3) or ''})
assert len(toc) == 81, f"目錄篇數異常：{len(toc)}"

# ---------------------------------------------------------------- 3. 正文分篇
num_pat = re.compile(r'([%s]{1,12}?)第([一二三四五六七八九十]{1,3})(?:\(([^)]*)\))?' % CJK)
cands = list(num_pat.finditer(body))
head_positions = []
for t in toc:
    found = None
    for m in cands:
        if m.group(2) == t['num_cn'] and m.start() > (head_positions[-1] if head_positions else -1):
            found = m
            break
    assert found, f"找不到第{t['num_cn']}篇標題"
    head_positions.append(found.start())
    t['body_name'] = found.group(1)
    t['annotation_body'] = found.group(3) or ''

chapters = []
for k, t in enumerate(toc):
    start = head_positions[k]
    end = head_positions[k + 1] if k + 1 < len(head_positions) else len(body)
    seg = body[start:end]
    seg = re.sub(r'^[%s]{1,12}?第[一二三四五六七八九十]{1,3}(?:\([^)]*\))?' % CJK, '', seg, count=1)
    seg = seg.lstrip('〇○ \u3000').rstrip('〇○ \u3000')
    t['raw'] = ENTITY.sub('', seg).strip()
    chapters.append(t)

# ---------------------------------------------------------------- 4. 字形正規化
GLYPH = {
    '朙': '明', '㑹': '會', '麤': '粗', '胷': '胸', '榖': '穀', '糓': '穀',
    '絶': '絕', '别': '別', '䧟': '陷', '㬥': '暴', '㢘': '廉', '㣲': '微',
    '乆': '久', '竆': '窮', '漑': '溉', '閲': '閱', '眞': '真', '冩': '寫',
    '煖': '暖', '衂': '衄', '痺': '痹', '欬': '咳', '决': '決',
    '䖟': '虻', '㢮': '弛', '㝠': '冥', '䑕': '鼠', '䔖': '菱',
    '黄': '黃', '内': '內', '户': '戶', '兎': '兔', '悦': '悅',
    '虗': '虛', '桒': '桑', '隂': '陰', '敍': '敘',
}
WORD = [('歧伯', '岐伯'), ('衛氣夫常', '衛氣失常'), ('癲狂病', '癲狂')]
NAME_FIX = {'衛氣夫常': '衛氣失常'}
NAME_NOTE = {
    22: '第22篇篇名｜目錄作「癲狂病」。「病」為衍字，《類經》引「癲狂篇」三見，據刪；正文標題本作「癲狂」，是也。',
    36: '底本作「五癃津液别」。「别」為底本通用字形，規範作「別」。',
    43: '目錄作「滛邪發夢」，正作「淫邪發夢」。',
    59: '第59篇篇名｜底本正文標題作「衛氣夫常」、目錄作「衛風失常」，皆形近之訛。《類經》引「衛氣失常」九見，據定作「衛氣失常」。',
    75: '目錄作「剌節眞邪」；「剌」為「刺」之形訛，「眞」為「真」之古體。',
    79: '目錄作「歳露論」；「歳」為「歲」之異體。',
    21: '第21篇｜底本作「眥三」。太素作「背三」，類經作「背三」並註「背三中行……」，二源一致，當作「背三」（五部：伏兔、腓、背、五藏之腧、項）。底本原字保留於 L0，教學層用「背三」。見 docs/33 K06。',
    81: '第81篇｜底本作「爲則不足」。類經作「瀉則不足」，並註「是瀉則不足也」，當作「寫（瀉）」。底本原字保留於 L0，教學層用「瀉」。見 docs/33 K08。',
}

def norm(s):
    s = ''.join(GLYPH.get(c, c) for c in s)
    for a, b in WORD:
        s = s.replace(a, b)
    return s

# ---------------------------------------------------------------- 5. 夾註分離 + 分段
SPEAK = re.compile(r'(?=(?:黃帝|岐伯|歧伯|雷公|少師|少俞|伯高)(?:問|曰|答|對))')

for t in chapters:
    t['notes'] = PAREN.findall(t['raw'])
    txt = PAREN.sub('', t['raw']).replace('\u3000', '\n')
    paras = [x for x in txt.split('\n') if x.strip()]
    # 清尾部音釋殘片（極短且無句末語氣詞）
    while paras and len(paras[-1]) <= 5 and not re.search(r'[也矣焉乎哉耳者曰]$', paras[-1]):
        paras.pop()
    t['text'] = '\n'.join(paras)

    # 補頁：底本實體缺頁／誤植（見 data/補頁記錄.json）
    PF = os.path.join(ROOT, 'data', '補頁記錄.json')
    if os.path.exists(PF):
        for pp in json.load(open(PF, encoding='utf-8'))['補頁']:
            if pp['篇序'] != chapters.index(t) + 1:
                continue
            A = t['text'].replace('\n', '')
            a = A.find(pp['刪起'])
            b = A.find(pp['刪訖'], a)
            if a >= 0 and b > a:
                t['text'] = A[:a] + pp['補文'] + A[b + len(pp['刪訖']):]
                t.setdefault('name_note', '')
                t['name_note'] = (t['name_note'] + '｜' + pp['說明']).strip('｜')

    t['norm'] = norm(t['text'])
    t['name_norm'] = norm(NAME_FIX.get(t['body_name'], t['body_name']))
    _nn = NAME_NOTE.get(chapters.index(t) + 1, '')
    t['name_note'] = '｜'.join(x for x in [_nn, t.get('name_note', '')] if x)
    segs = []
    for para in t['text'].split('\n'):
        if not para:
            continue
        ps = [p for p in SPEAK.split(para) if p]
        if len(ps) > 1 and not SPEAK.match(ps[0]):
            ps = [ps[0] + ps[1]] + ps[2:]
        segs.extend(ps)
    off = 0
    t['segments'] = []
    for si, s in enumerate(segs, 1):
        t['segments'].append({'id': f"LS-{chapters.index(t)+1:03d}-{si:02d}",
                              'text': s, 'norm': norm(s),
                              'char_start': off, 'char_end': off + len(s)})
        off += len(s)

# ---------------------------------------------------------------- 6. 輸出
idx = []
for k, t in enumerate(chapters, 1):
    idx.append({
        '序': k, '篇名': t['body_name'], '篇名_規範': t['name_norm'], '目錄篇名': t['name'],
        '卷': t['juan'], '法象': t['annotation'], '校記': t['name_note'],
        '原始字數': len(t['raw']), '經文字數': len(t['text']), '正規化字數': len(t['norm']),
        '夾註數': len(t['notes']), '分段數': len(t['segments']),
        '原文': t['raw'], '經文': t['text'], '正規化': t['norm'],
        '夾註': t['notes'], '段': t['segments'],
    })
json.dump({'底本': '四部叢刊本《黃帝素問靈樞經》(SBCK)',
           '來源': 'https://github.com/kanripo/KR3e0002',
           '說明': 'L0 原文含夾註；L1 經文剝離夾註；正規化僅字形規範',
           '篇數': len(idx), '篇': idx},
          open(os.path.join(OUT, '靈樞經_81篇.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

json.dump({'說明': '史崧音釋（反切、異文），自各卷卷末剝離後獨立保存',
           '卷數': len(yinshi_all), '音釋': yinshi_all},
          open(os.path.join(OUT, '音釋層.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

CN = ['','一','二','三','四','五','六','七','八','九','十','十一','十二']
with open(os.path.join(OUT, '靈樞經_SBCK_底本.md'), 'w', encoding='utf-8') as f:
    f.write('# 黃帝素問靈樞經（四部叢刊本）\n\n')
    f.write('> **底本**：四部叢刊本《黃帝素問靈樞經》，明趙府居敬堂本系統，12 卷 81 篇。\n')
    f.write('> **來源**：Kanripo 漢籍リポジトリ `kanripo/KR3e0002`（四部叢刊影印本錄文）。\n')
    f.write('> **狀態**：未加句讀。¶ 為原書行末、`<pb:>` 為頁碼、`〇` 為篇首符號，均已移除。\n')
    f.write('> **字形**：已依「異體字規範表」正規化；底本原始字形見 JSON 的 `原文` 欄。\n')
    f.write('> **夾註**：底本小字校注（如「(遊/一作)」）已自正文剝離，存於 JSON 的 `夾註` 欄與 `音釋層.json`。\n\n---\n\n')
    for k, t in enumerate(chapters, 1):
        f.write(f"## {k}. {t['name_norm']}第{t['num_cn']}" +
                (f"（{t['annotation']}）" if t['annotation'] else '') +
                f"　〔卷之{CN[t['juan']]}〕\n\n")
        if t['name_note']:
            f.write(f"> **校記**：{t['name_note']}\n\n")
        for s in t['segments']:
            f.write(s['norm'] + '\n\n')

with open(os.path.join(OUT, '異體字規範表.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['原始字形', 'Unicode', '規範字形', '底本出現次數'])
    cnt = Counter(re.findall(r'[%s]' % CJK, body))
    for a, b in sorted(GLYPH.items(), key=lambda x: -cnt.get(x[0], 0)):
        w.writerow([a, f'U+{ord(a):04X}', b, cnt.get(a, 0)])
    for a, b in WORD:
        w.writerow([a, '（詞）', b, body.count(a)])

print(f"篇數 {len(chapters)}｜卷數 {juan}")
print(f"原始漢字 {len(re.findall(r'[%s]' % CJK, body))}")
print(f"音釋卷數 {len(yinshi_all)}")
print(f"輸出 {OUT}")
