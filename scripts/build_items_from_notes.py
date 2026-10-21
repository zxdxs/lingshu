#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由《類經》張介賓注生成「注→經」理解題。

題型：給一段注，問它解釋的是哪一句經文。
  - 答案取自經文原文，可逐字驗證；
  - 干擾項取自同一條的其他經句；
  - 全程不生成內容，只做配對。

刻意排除兩種不好出的情況：
  1. 注與經高度重疊（注幾乎照抄經文）——太容易；
  2. 經句過長或過短——選項難讀。
"""
import json, os, re, argparse, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 等價類：把版本間的異寫、章際用字差異歸一（只為比對，不改原文）
COLLAPSE = {
    '於': 'A', '于': 'A', '扵': 'A',
    '爲': 'B', '為': 'B',
    '隂': 'C', '陰': 'C',
    '荅': 'D', '答': 'D',
    '圎': 'E', '圓': 'E',
    '緻': 'F', '致': 'F',
    '閲': 'G', '閱': 'G',
    '舎': 'H', '舍': 'H',
    '徃': 'I', '往': 'I',
    '黄': 'J', '黃': 'J',
    '黒': 'K', '黑': 'K',
    '眞': 'L', '真': 'L',
    '徧': 'M', '遍': 'M',
    '痺': 'N', '痹': 'N',
    '脉': 'O', '脈': 'O',
    '衞': 'P', '衛': 'P',
    '夀': 'Q', '壽': 'Q',
    '嵗': 'R', '歲': 'R', '歳': 'R',
    '别': 'S', '別': 'S',
    '絶': 'T', '絕': 'T',
    '㑹': 'U', '會': 'U',
    '榖': 'V', '穀': 'V',
    '竒': 'W', '奇': 'W',
    '靣': 'X', '面': 'X',
    '䐜': 'Y', '脹': 'Y',
    '寫': 'Z', '瀉': 'Z',
}
VAR = COLLAPSE


def vn(s):
    """寬歸一（含章際用字），只用於標點比對與篇名比對。"""
    s = s.strip('○　 ')
    return ''.join(VAR.get(c, c) for c in s)


SIM = {'隂': '陰', '别': '別', '絶': '絕', '脉': '脈', '衞': '衛', '爲': '為',
       '痺': '痹', '夀': '壽', '嵗': '歲', '榖': '穀', '荅': '答', '眞': '真'}


def vn_sim(s):
    """窄歸一（僅明顯異寫），用於相似度判定，避免把不同句子算成相同。"""
    return ''.join(SIM.get(c, c) for c in s)


def grams(t, k=4):
    t = vn_sim(t)
    return {t[i:i + k] for i in range(max(1, len(t) - k + 1))}


def containment(a, b):
    """a 有多少比例出現在 b。"""
    ga = grams(a)
    if not ga:
        return 0.0
    return len(ga & grams(b)) / len(ga)


CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
_PUNCT_CACHE = {}


def _punct_index():
    """把 81 篇的句讀層拼成一條帶標點的長字串，並記錄每個漢字的原位置。"""
    if 'idx' in _PUNCT_CACHE:
        return _PUNCT_CACHE['idx']
    d = json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))
    text = '\n'.join(p['句讀'] for p in d['篇'])
    chars, pos = [], []
    for i, ch in enumerate(text):
        if CJK.match(ch):
            chars.append(VAR.get(ch, ch))
            pos.append(i)
    _PUNCT_CACHE['idx'] = (text, ''.join(chars), pos)
    return _PUNCT_CACHE['idx']


BOUND = set('，。；：？！、\n　 ')


def punctuate(q):
    """把無標點的類經經句對回句讀層。

    兩道驗證，避免誤接：
      1. 必須落在句讀層的句界上（前後為標點或行首尾）；
      2. 接出來的片段本身必須含標點。
    任一不符即放棄，交由規則層處理。
    """
    text, clean, pos = _punct_index()
    qn = ''.join(VAR.get(c, c) for c in q if CJK.match(c))
    if not qn:
        return None
    i = clean.find(qn)
    if i < 0:
        return None
    a, b = pos[i], pos[i + len(qn) - 1]
    before = text[a - 1] if a > 0 else '\n'
    after = text[b + 1] if b + 1 < len(text) else '\n'
    if before not in BOUND or after not in BOUND:
        return None
    seg = text[a:b + 1]
    if not re.search(r'[，。；：？！、]', seg):
        return None
    return seg


NAME_VAR = {'隂': '陰', '别': '別', '絶': '絕', '痩': '瘦', '㑹': '會', '閲': '閱',
            '榖': '穀', '夀': '壽', '嵗': '歲', '歳': '歲', '痺': '痹', '脉': '脈',
            '衞': '衛', '爲': '為'}


RULE_END = re.compile(r'([也矣焉耳哉])(?=[^，。；：？！、])')
RULE_YUE = re.compile(r'(曰)(?=[^，。；：？！、「])')


def rule_punct(q):
    """規則層標點：只做兩件低風險的事——「曰」後加冒號、句末語氣詞後加句號。

    這是詮釋，不是原文。全題組一律套用，以保證同一題內四個選項的標點狀態一致
    （否則「有沒有標點」會變成辨認答案的線索）。
    """
    q = RULE_YUE.sub(r'\1：', q)
    q = RULE_END.sub(r'\1。', q)
    return q


def style_set(opts):
    """一題四選項的標點必須同源：全都能對上句讀層才用真標點，否則四個都用規則層。

    否則「有沒有標點」「標點多不多」會變成辨認答案的線索（實測確實發生過）。
    """
    hit = [punctuate(o) for o in opts]
    if all(hit):
        return hit
    out = []
    for o in opts:
        t = rule_punct(o)
        if not re.search(r'[，。；：？！、]$', t):
            t += '。'
        out.append(t)
    return out


def pian_of(e):
    """取類經出處所引靈樞篇名。此處不可用 COLLAPSE（會把字換成代號）。"""
    s = e['出處']
    i = s.find('靈樞')
    if i < 0:
        return None
    name = re.split(r'[篇連全此與○]', s[i + 2:])[0]
    return ''.join(NAME_VAR.get(c, c) for c in name) or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--out', default='data/題庫_注經_樣本.json')
    ap.add_argument('--min-jing', type=int, default=8)
    ap.add_argument('--max-jing', type=int, default=40)
    ap.add_argument('--per-tiao', type=int, default=2)
    ap.add_argument('--local-only', action='store_true', help='干擾項只取同條，不足則不出題')
    ap.add_argument('--min-zhu', type=int, default=40)
    ap.add_argument('--max-overlap', type=float, default=0.5)
    a = ap.parse_args()

    tiao = json.load(open(os.path.join(ROOT, 'data', '類經條目.json'), encoding='utf-8'))['條目']
    pian = {p['篇名_規範']: int(p['序']) for p in
            json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}

    lp = [e for e in tiao if '靈樞' in e['出處']]
    by_cat = {}
    for e in lp:
        by_cat.setdefault(e['類'], []).append(e)

    items, seen, gused = [], set(), {}

    for e in lp:
        pn = pian_of(e)
        if not pn or pn not in pian:
            continue
        used_distractors = set()
        made = 0
        pairs = [{'經': p['經'].strip('○　 '), '注': p['注'].strip('○　 ')}
                 for p in (e.get('對注') or []) if len(p['注'].strip('○　 ')) >= a.min_zhu]
        jings = [p['經'] for p in pairs if a.min_jing <= len(p['經']) <= a.max_jing]
        for p in pairs:
            j, z = p['經'], p['注']
            if not (a.min_jing <= len(j) <= a.max_jing):
                continue
            if containment(j, z) >= a.max_overlap:
                continue          # 注幾乎照抄經文，太容易
            if j in seen:
                continue
            # 干擾項分兩層：同條優先，不足才向同類取；兩層內部再按「未用過、長度相近」排
            def rank(x):
                return (gused.get(x, 0), abs(len(x) - len(j)))
            local = sorted([x for x in jings if x != j and containment(x, j) < 0.5
                            and abs(len(x) - len(j)) <= 18], key=rank)
            pool = local[:3]
            if len(pool) < 3 and not a.local_only:
                remote = []
                for o in by_cat.get(e['類'], []):
                    if o is e:
                        continue
                    for q in (o.get('對注') or []):
                        cj = q['經'].strip('○　 ')
                        if a.min_jing <= len(cj) <= a.max_jing and cj != j \
                                and containment(cj, j) < 0.5 and cj not in pool:
                            remote.append(cj)
                pool += sorted(remote, key=rank)[:3 - len(pool)]
            if len(pool) < 3:
                continue
            pool = pool[:3]
            for x in pool:
                gused[x] = gused.get(x, 0) + 1
            used_distractors.update(pool)
            made += 1
            seen.add(j)
            items.append({
                'item_id': f'Q-ZJ-{len(items) + 1:03d}',
                'type': 'mcq', 'bloom': 'understand', '層級': 'L0',
                'stem': f"《類經·{e['類']}》張介賓注：「{z}」此注所釋，為下列哪一句？",
                'answer': None,
                'distractors': None,
                'source': {'篇序': pian[pn], '篇名': pn},
                'note': '注→經',
                '註家參照': {'來源': '類經', '類': e['類'], '條題': e['條題'],
                             '條號': f"{e['出處']}○{e['條號']}"},
                'auto_grading': 'exact',
            })
            _st = style_set([j] + pool[:3])
            items[-1]['answer'] = _st[0]
            items[-1]['distractors'] = _st[1:]
            if len(items) >= a.limit or made >= a.per_tiao:
                break
        if len(items) >= a.limit:
            break

    json.dump({'說明': '由類經張介賓注生成的「注→經」題；答案為經文原文，干擾項為同條其他經句',
               '題數': len(items), '題': items},
              open(os.path.join(ROOT, a.out), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'生成 {len(items)} 題 → {a.out}')
    for it in items[:3]:
        print('\n', it['item_id'], it['stem'][:80], '...')
        print('  ✔', it['answer'][:40])
        for d in it['distractors']:
            print('  ✘', d[:40])


if __name__ == '__main__':
    main()
