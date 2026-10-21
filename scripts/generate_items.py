#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S7：題目生成（規則式，每題帶原文出處，可回溯）

題型：
  A 五輸穴填空   —— 由《本輸》五輸表生成
  B 腧穴歸經     —— 由五輸表 + 經脈詞典生成
  C 循行起點辨識 —— 由《經脈》十二經脈條文生成，干擾項取自他經（非編造）

輸出：data/題庫_示例.json、docs/10_題庫示例.md
"""
import json, os, re, random, csv
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
WU = json.load(open(os.path.join(ROOT, 'demo', '本輸_五輸穴示例.json'), encoding='utf-8'))['表']

def quote_with_blank(seq, answer, max_back=24):
    """從句讀層切出一段「以答案結尾」的連續原文，答案換成 ____。

    起點優先取最近的「為／爲」，其次「出／溜／注／行／入／過」；都沒有就往前 max_back 字。
    回傳 None 表示找不到；呼叫端要自行退回到舊寫法。
    """
    from check_quotes import norm as _n
    txt = J.get(seq, {}).get('句讀', '')
    if not txt or not answer:
        return None
    idxs = [(i, ch) for i, ch in enumerate(txt) if _n(ch)]
    joined = ''.join(_n(ch) for _, ch in idxs)   # 以異體收斂後的字串比對
    key = _n(answer)
    pos = joined.find(key)
    if pos < 0:
        return None
    end = idxs[pos + len(key) - 1][0] + 1
    start = idxs[pos][0]
    back = txt[max(0, start - max_back):start]
    m = None
    for mm in re.finditer(r'[為爲]', back):
        m = mm
    if m is None:
        for mm in re.finditer(r'[出溜注行入過]', back):
            m = mm
    if m:
        start = start - (len(back) - m.start())
    quote = txt[start:end]
    cut = quote.rfind(answer)
    if cut <= 0:
        return None
    return quote[:cut] + '____'


def _mai_stem(r):
    """五藏脈變題面：優先用「藏脉X者，為____」，否則用「X，為____」並把藏脉放到引號外。"""
    from check_quotes import norm as _n
    base = _n(S[4]['正規化'])
    head = f"{r['藏']}脉{r['脈']}"
    if _n(head + '者') in base:
        return f"《靈樞·邪氣藏府病形》：「{head}者，為____。」"
    if _n(head) in base:
        return f"《靈樞·邪氣藏府病形》：「{head}，為____。」"
    if _n(r['脈'] + '為') in base:
        return f"《靈樞·邪氣藏府病形》{r['藏']}脉：「{r['脈']}，為____。」"
    return f"《靈樞·邪氣藏府病形》：「{r['藏']}脉{r['脈']}____。」"

def split_gloss(t):
    """把「文字（白話註）」拆成（文字, 白話註）。題面只引文字，註留給 note。"""
    m = re.match(r'^(.*?)（([^）]*)）\s*$', t)
    return (m.group(1), m.group(2)) if m else (t, '')


def punct_of(seq, raw):
    """用句讀層把一段無標點的原文還原成帶標點版本；找不到就原樣回傳。
    比對時展開異體字（榖／穀、脉／脈…），否則看似同一句卻對不上。"""
    from check_quotes import norm
    key = norm(raw)
    for c in re.split(r'[。；\n]', J.get(seq, {}).get('句讀', '')):
        c = c.strip()
        if c and key in norm(c):
            return c
    return raw

random.seed(42)

items = []

# ---------- A 五輸穴填空 ----------
LABEL = {'井': '井穴', '滎': '滎穴', '輸': '輸穴', '原': '原穴', '經': '經穴', '合': '合穴'}
VERB = {'井': '出於', '滎': '溜於', '輸': '注於', '原': '過於', '經': '行於', '合': '入於'}
# 五輸穴名在底本作「大」，教材用「太」；兩者互收
ALIAS = {'太淵': '大淵', '太衝': '大衝', '太谿': '大谿'}
for r in WU:
    for k in ['井', '滎', '輸', '原', '經', '合']:
        v = r.get(k, '—')
        if v in ('—', '', None):
            continue
        note = f"{r['歸屬']}之{LABEL[k]}"
        if r['歸屬'] == '心':
            note += '（《本輸》此段以心包經穴表述手少陰心）'
        ctx = f"{r['歸屬']}經"          # 經名放在引號外：原文的溜／注／行／入前面沒有藏名
        if k == '井':
            _organ = r['歸屬']
            if _organ + '出於' in S[2]['原文']:
                stem = f"《靈樞·本輸》「{_organ}出於____」"
            elif _organ + '出于' in S[2]['原文']:
                stem = f"《靈樞·本輸》「{_organ}出于____」"
            else:
                stem = f"《靈樞·本輸》{ctx}：「出於____」"
        else:
            _q = quote_with_blank(2, ALIAS.get(v, v))
            stem = (f"《靈樞·本輸》{ctx}：「{_q}」" if _q and len(_q) >= 6
                    else f"《靈樞·本輸》{ctx}：「{VERB[k]}____」")
        items.append({'item_id': f"Q-LS002-{r['歸屬']}-{k}",
                      'type': 'fill_blank', 'bloom': 'remember',
                      'stem': stem, 'answer': ALIAS.get(v, v),
                      'distractors': [], 'source': {'篇序': 2, '篇名': '本輸'},
                      'note': note, 'auto_grading': 'exact',
                      **({'可接受答案': [v]} if v in ALIAS else {})})

# ---------- B 腧穴歸經 ----------
ACU = {}
for r in WU:
    for k in ['井', '滎', '輸', '原', '經', '合']:
        v = r.get(k, '—')
        if v not in ('—', '', None):
            ACU[v] = r['歸屬']
mers = sorted(set(ACU.values()))
for name, mer in ACU.items():
    others = [m for m in mers if m != mer]
    random.shuffle(others)
    items.append({'item_id': f"Q-LS002-MER-{name}",
                  'type': 'mcq', 'bloom': 'understand',
                  'stem': f"腧穴『{name}』歸屬於下列哪一經？",
                  'answer': mer, 'distractors': others[:3],
                  'source': {'篇序': 2, '篇名': '本輸'},
                  'note': '歸經判斷', 'auto_grading': 'exact'})

# ---------- C 循行起點辨識 ----------
MER_LIST = ['肺手太陰', '大腸手陽明', '胃足陽明', '脾足太陰', '心手少陰', '小腸手太陽',
            '膀胱足太陽', '腎足少陰', '心主手厥陰', '三焦手少陽', '膽足少陽', '肝足厥陰']
j10 = J[10]['句讀']
starts = {}
for m in MER_LIST:
    i = j10.find(m + '之脉')
    if i < 0:
        i = j10.find(m + '之脈')
    if i < 0:
        i = j10.find(m)
    if i < 0:
        continue
    seg = j10[i:i + 90]
    mm = re.search(r'(起[於于][^，。；]{2,14})', seg)
    if mm:
        starts[m] = mm.group(1)
items_c = []
for m, fact in starts.items():
    others = [v for k, v in starts.items() if k != m]
    if not others:
        continue
    wrong = random.sample(others, min(3, len(others)))
    items_c.append({'item_id': f"Q-LS010-XUN-{m}",
                    'type': 'error_identification', 'bloom': 'evaluate',
                    'stem': f"《靈樞·經脈》所述「{m}」，其循行起點為何？",
                    'answer': fact, 'distractors': wrong,
                    'source': {'篇序': 10, '篇名': '經脉'},
                    'note': '循行起點；干擾項取自他經原文', 'auto_grading': 'exact'})
items.extend(items_c)

# ---------- D 證—治配對（需先跑 extract_disease_relations.py） ----------
ZZ = os.path.join(ROOT, 'data', '關係_證治.csv')
if os.path.exists(ZZ):
    rows = [r for r in csv.DictReader(open(ZZ, encoding='utf-8-sig')) if r['取穴']]
    all_acu = [r['取穴'] for r in rows]
    for idx, r in enumerate(rows, 1):
        ans = r['取穴']; n = int(r['篇序'])
        others = [x for x in all_acu if x != ans]
        random.shuffle(others)
        items.append({'item_id': f"Q-LS{n:03d}-ZHENGZHI-{idx}",
                      'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·{r['篇名']}》：「{r['證']}」，當取何穴？",
                      'answer': ans, 'distractors': others[:3],
                      'source': {'篇序': n, '篇名': r['篇名'], '位置': int(r['位置'])},
                      'note': '證—治配對；干擾項取自同篇其他證之取穴',
                      'auto_grading': 'exact'})


# ---------- E 五心痛模組（需先跑 build_module_five_heart_pains.py） ----------
MOD = os.path.join(ROOT, 'data', '模組_五心痛.json')
if os.path.exists(MOD):
    M = json.load(open(MOD, encoding='utf-8'))
    cases = M['證型']; names = [c['名'] for c in cases]
    for idx, c in enumerate(cases, 1):
        others = [x for x in names if x != c['名']]
        random.shuffle(others)
        items.append({'item_id': f"Q-LS024-FHP-DX-{idx}", 'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·厥病》：「{c.get('原文要點') or c['要點'][0]}」，屬五心痛中的哪一型？",
                      'answer': c['名'], 'distractors': others[:3],
                      'source': {'篇序': 24, '篇名': '厥病', '位置': c['位置']},
                      'note': '辨證要點→證型', 'auto_grading': 'exact'})
        ans = '、'.join(d['穴'] for d in c['取穴明細'])
        pool = ['、'.join(d['穴'] for d in x['取穴明細']) for x in cases if x['名'] != c['名']]
        random.shuffle(pool)
        items.append({'item_id': f"Q-LS024-FHP-RX-{idx}", 'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·厥病》：「{c['名']}」，當取何穴？",
                      'answer': ans, 'distractors': pool[:3],
                      'source': {'篇序': 24, '篇名': '厥病', '位置': c['位置']},
                      'note': '證型→取穴', 'auto_grading': 'exact'})
    # 錯謬辨識（人工撰寫，干擾項皆為常見誤解）
    items += [
        {'item_id': 'Q-LS024-FHP-ERR-1', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '有人主張「胃心痛當取足陽明胃經」。依《靈樞·厥病》，此說有何問題？',
         'answer': '經文取的是足太陰脾經（大都、太白），不是足陽明胃經',
         'distractors': ['經文取的是手厥陰心包經', '經文取的是足少陰腎經', '經文未載胃心痛'],
         'source': {'篇序': 24, '篇名': '厥病'}, 'note': '腑病取藏經；勿望文生義',
         'auto_grading': 'rubric'},
        {'item_id': 'Q-LS024-FHP-ERR-2', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '有人說「五心痛都按五行生剋配穴」。依《靈樞·厥病》，此說是否成立？',
         'answer': '不成立：五組中只有部分符合表裡關係；脾心痛取腎經穴，注家未有定論',
         'distractors': ['成立，五組皆嚴格依五行生剋', '成立，但僅限腎心痛與胃心痛', '經文未涉及配穴'],
         'source': {'篇序': 24, '篇名': '厥病'}, 'note': '勿以後世理論倒灌原文',
         'auto_grading': 'rubric'},
    ]


# ---------- F A 型表格題（需先跑 build_tables_a.py） ----------
def load_csv(name):
    p = os.path.join(ROOT, 'data', name)
    return list(csv.DictReader(open(p, encoding='utf-8-sig'))) if os.path.exists(p) else []

bd = load_csv('表_骨度.csv')
vals = [r['長'] for r in bd]
for i, r in enumerate(bd, 1):
    dis = [v for v in vals if v != r['長']]
    random.shuffle(dis)
    items.append({'item_id': f'Q-LS014-BD-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                  # 用表裡的「原文」逐字，不拼接「起至訖」——拼接會造出原文沒有的句子（docs/82）
                  'stem': f"《靈樞·骨度》：「{r['原文'].replace(r['長'], '____', 1)}」",
                  'answer': r['長'], 'distractors': [],
                  'source': {'篇序': 14, '篇名': '骨度'}, 'note': '骨度分寸',
                  'auto_grading': 'exact'})

md = load_csv('表_脈度.csv')
for i, r in enumerate(md, 1):
    items.append({'item_id': f'Q-LS017-MD-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': f"《靈樞·脈度》：「{(r.get('原文') or (r['經脉'] + '，長' + r['單側長'])).replace(r['單側長'], '____', 1)}",
                  'answer': r['單側長'], 'distractors': [],
                  'source': {'篇序': 17, '篇名': '脈度'}, 'note': '脈度長短',
                  'auto_grading': 'exact'})

jz = load_csv('表_九鍼.csv')
for i, r in enumerate(jz, 1):
    items.append({'item_id': f'Q-LS001-JZ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': f"《靈樞·九鍼十二原》：「{r['序']}曰{r['鍼']}，長____。」",
                  'answer': r['長'], 'distractors': [],
                  'source': {'篇序': 1, '篇名': '九鍼十二原'}, 'note': f"九鍼形制：{r['功能'][:12]}",
                  'auto_grading': 'exact'})

bs = load_csv('表_背腧.csv')
places = [r['位置'] for r in bs]
for i, r in enumerate(bs, 1):
    dis = [v for v in places if v != r['位置']]
    random.shuffle(dis)
    items.append({'item_id': f'Q-LS051-BS-{i}', 'type': 'mcq', 'bloom': 'remember',
                  'stem': f"《靈樞·背腧》：「{r['腧穴']}」在何處？",
                  'answer': r['位置'], 'distractors': dis[:3],
                  'source': {'篇序': 51, '篇名': '背腧'}, 'note': '背俞定位',
                  'auto_grading': 'exact'})


# ---------- G 體質剖面題（需先跑 build_module_constitution.py） ----------
CON = os.path.join(ROOT, 'data', '模組_體質.json')
if os.path.exists(CON):
    M = json.load(open(CON, encoding='utf-8'))
    wu = M['五態']; names = [x['名'] for x in wu]
    for i, c in enumerate(wu, 1):
        others = [x for x in names if x != c['名']]
        random.shuffle(others)
        if c['形態']:
            items.append({'item_id': f'Q-LS072-WT-X-{i}', 'type': 'mcq', 'bloom': 'understand',
                          'stem': f"《靈樞·通天》：「{c['形態']}」，屬五態人中的哪一型？",
                          'answer': c['名'], 'distractors': others[:3],
                          'source': {'篇序': 72, '篇名': '通天'}, 'note': '形態→五態',
                          'auto_grading': 'exact'})
        if c['性情']:
            items.append({'item_id': f'Q-LS072-WT-Q-{i}', 'type': 'mcq', 'bloom': 'understand',
                          'stem': f"《靈樞·通天》：「{c['性情'][:28]}」，屬五態人中的哪一型？",
                          'answer': c['名'], 'distractors': others[:3],
                          'source': {'篇序': 72, '篇名': '通天'}, 'note': '性情→五態',
                          'auto_grading': 'exact'})
    for i, c in enumerate(M['膏脂肉'], 1):
        others = [x['名'] for x in M['膏脂肉'] if x['名'] != c['名']]
        items.append({'item_id': f'Q-LS059-GZR-{i}', 'type': 'mcq', 'bloom': 'understand',
                      'stem': f"《靈樞·衛氣失常》：「{c['判別']}」，此為何種體質？",
                      'answer': c['名'], 'distractors': others,
                      'source': {'篇序': 59, '篇名': '衛氣失常'}, 'note': '膏脂肉三型',
                      'auto_grading': 'exact'})
    for i, c in enumerate(M['肥瘦壯嬰'], 1):
        others = [x['刺法'] for x in M['肥瘦壯嬰'] if x['刺法'] != c['刺法']]
        random.shuffle(others)
        items.append({'item_id': f'Q-LS038-FS-{i}', 'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·逆順肥瘦》：「{c['判別']}」，其刺法為何？",
                      'answer': c['刺法'], 'distractors': others[:3],
                      'source': {'篇序': 38, '篇名': '逆順肥瘦'}, 'note': '體質→刺法',
                      'auto_grading': 'exact'})
    for i, st in enumerate(M['天年'], 1):
        items.append({'item_id': f'Q-LS054-TN-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·天年》：「{st['齡']}，____。」",
                      'answer': st['描述'], 'distractors': [],
                      'source': {'篇序': 54, '篇名': '天年'}, 'note': '生命週期',
                      'auto_grading': 'fuzzy'})


# ---------- H 癲狂模組（需先跑 build_module_diankuang.py） ----------
DK = os.path.join(ROOT, 'data', '模組_癲狂.json')
if os.path.exists(DK):
    M = json.load(open(DK, encoding='utf-8'))
    allc = M['癲疾'] + M['狂']
    names = [c['名'] for c in allc]
    for i, c in enumerate(allc, 1):
        others = [x for x in names if x != c['名']]
        random.shuffle(others)
        items.append({'item_id': f'Q-LS022-DK-DX-{i}', 'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·癲狂》：「{split_gloss(c['證'])[0]}」，屬下列哪一型？",
                      'answer': c['名'], 'distractors': others[:3],
                      'source': {'篇序': 22, '篇名': '癲狂'},
                      'note': '證候→型' + (('；' + split_gloss(c['證'])[1]) if split_gloss(c['證'])[1] else ''),
                      'auto_grading': 'exact'})
        if c['取經']:
            pool = [x['取經'] for x in allc if x['取經'] and x['取經'] != c['取經']]
            random.shuffle(pool)
            items.append({'item_id': f'Q-LS022-DK-RX-{i}', 'type': 'mcq', 'bloom': 'remember',
                          'stem': f"《靈樞·癲狂》：「{split_gloss(c['名'])[0].replace('狂言驚笑', '狂言驚善笑')}」，當取何經？",
                          'answer': c['取經'], 'distractors': pool[:3],
                          'source': {'篇序': 22, '篇名': '癲狂'}, 'note': '型→取經',
                          'auto_grading': 'exact'})
    items += [
        {'item_id': 'Q-LS022-DK-ERR-1', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '有人說「癲與狂是同一種病的兩個名稱」。依《靈樞·癲狂》，此說是否成立？',
         'answer': '不成立：癲與狂是兩類病，起病證候不同，但可轉化（癲疾發如狂者死不治）',
         'distractors': ['成立，只是程度輕重之別', '成立，二者取穴完全相同', '經文未區分二者'],
         'source': {'篇序': 22, '篇名': '癲狂'}, 'note': '概念區分', 'auto_grading': 'rubric'},
        {'item_id': 'Q-LS022-DK-ERR-2', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '《靈樞·癲狂》反覆出現「嘔多沃沫，氣下泄，不治」。這句話的意義是什麼？',
         'answer': '是預後判斷：脾胃氣絕之候，屬不治，不是取穴指引',
         'distractors': ['是取穴指引，應取脾胃經', '是描述癲疾發作時的常見症狀', '是說病人會嘔吐，需先止嘔'],
         'source': {'篇序': 22, '篇名': '癲狂'}, 'note': '預後≠治法', 'auto_grading': 'rubric'},
    ]


# ---------- I 術語卡（需先跑 build_module_terms.py） ----------
TM = os.path.join(ROOT, 'data', '模組_術語.json')
if os.path.exists(TM):
    M = json.load(open(TM, encoding='utf-8'))
    terms = M['本神十義'] + M['決氣六氣']
    for i, t in enumerate(terms, 1):
        # 定義欄可能含「何謂氣？岐伯曰：」的問句；留著就等於把答案寫在題幹裡
        _def = re.sub(r'^何謂[^？]*？\s*(岐伯)?[曰答]?：?', '', t['定義']).strip('，。 ')
        _conn = '謂之' if t['篇'] == '本神' else '是謂'
        items.append({'item_id': f'Q-TERM-DEF-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·{t['篇']}》：「{_def}，{_conn}____。」",
                      'answer': t['術語'], 'distractors': [],
                      'source': {'篇序': t['篇序'], '篇名': t['篇']}, 'note': '術語定義',
                      'auto_grading': 'exact'})
    for i, h in enumerate(M['四海'], 1):
        if h.get('上輸') and h['上輸'] != '—':
            _raw = punct_of(33, h.get('原文') or f"{h['主體']}者，{h['海']}之海，其輸上在{h['上輸']}")
            items.append({'item_id': f'Q-TERM-HAI-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                          'stem': f"《靈樞·海論》：「{_raw.replace(h['上輸'], '____', 1)}」",
                          'answer': h['上輸'], 'distractors': [],
                          'source': {'篇序': 33, '篇名': '海論'}, 'note': '四海輸穴',
                          'auto_grading': 'exact'})
    for i, t in enumerate(M['六脫候'], 1):
        items.append({'item_id': f'Q-TERM-TUO-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·決氣》：「{t['術語']}者，____。」",
                      'answer': t['候'], 'distractors': [],
                      'source': {'篇序': 30, '篇名': '決氣'}, 'note': '六脫候',
                      'auto_grading': 'fuzzy'})


# ---------- J 概念卡第二批（需先跑 build_module_concepts2.py） ----------
C2 = os.path.join(ROOT, 'data', '模組_概念2.json')
if os.path.exists(C2):
    M = json.load(open(C2, encoding='utf-8'))
    for i, w in enumerate(M['五味所走'], 1):
        items.append({'item_id': f'Q-LS056-WW-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五味》：「穀味{w['味']}，先走____。」",
                      'answer': w['走'], 'distractors': [],
                      'source': {'篇序': 56, '篇名': '五味'}, 'note': '五味所走',
                      'auto_grading': 'exact'})
    for i, w in enumerate(M['五藏所禁'], 1):
        items.append({'item_id': f'Q-LS056-WJ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五味》：「{w['藏']}病禁____。」",
                      'answer': w['禁'], 'distractors': [],
                      'source': {'篇序': 56, '篇名': '五味'}, 'note': '五藏所禁',
                      'auto_grading': 'exact'})
    for i, b in enumerate(M['病因三部'], 1):
        items.append({'item_id': f'Q-LS066-BY-{i}', 'type': 'mcq', 'bloom': 'understand',
                      'stem': f"《靈樞·百病始生》：「{b['部']}」所致之病，起於何處？",
                      'answer': b['起'], 'distractors': [x['起'] for x in M['病因三部'] if x['起'] != b['起']],
                      'source': {'篇序': 66, '篇名': '百病始生'}, 'note': '病因三部',
                      'auto_grading': 'exact'})
    order = [c['舍'] for c in M['邪氣傳舍']]
    items.append({'item_id': 'Q-LS066-CS-1', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·百病始生》邪氣傳舍的次序（以「→」連接）：皮膚→____→經→輸→伏衝之脉→腸胃→募原之間。',
                  'answer': order[1] if len(order) > 1 else '', 'distractors': [],
                  'source': {'篇序': 66, '篇名': '百病始生'}, 'note': '傳變路徑',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS018-YW-1', 'type': 'error_identification', 'bloom': 'evaluate',
                  'stem': '有人說「營衛只是兩種氣，與睡眠無關」。依《靈樞·營衛生會》，此說是否成立？',
                  'answer': '不成立：壯者營衛之行不失其常故晝精夜瞑；老者營氣衰少、衛氣內伐故晝不精夜不瞑',
                  'distractors': ['成立，營衛只與汗出有關', '成立，睡眠由心主司與營衛無關', '經文未論及睡眠'],
                  'source': {'篇序': 18, '篇名': '營衛生會'}, 'note': '營衛與睡眠',
                  'auto_grading': 'rubric'})


# ---------- K 診法卡（需先跑 build_module_diagnostics.py） ----------
DG = os.path.join(ROOT, 'data', '模組_診法.json')
if os.path.exists(DG):
    M = json.load(open(DG, encoding='utf-8'))
    for i, c in enumerate(M['目色'], 1):
        items.append({'item_id': f'Q-LS074-MU-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·論疾診尺》：「目{c['色']}色者，病在____。」",
                      'answer': c['藏'], 'distractors': [],
                      'source': {'篇序': 74, '篇名': '論疾診尺'}, 'note': '目色主藏（非靈樞原文，出題後剔除）',
                      'auto_grading': 'exact'})
    for i, c in enumerate(M['五色主病'], 1):
        items.append({'item_id': f'Q-LS049-WS-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五色》：「{c['色']}為____。」",
                      'answer': c['主'], 'distractors': [],
                      'source': {'篇序': 49, '篇名': '五色'}, 'note': '五色主病',
                      'auto_grading': 'exact'})
    for i, c in enumerate(M['明堂五部'], 1):
        items.append({'item_id': f'Q-LS049-MT-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五色》：「{c['部']}」指____。",
                      'answer': c['位'], 'distractors': [],
                      'source': {'篇序': 49, '篇名': '五色'}, 'note': '明堂五部',
                      'auto_grading': 'fuzzy'})
    for i, c in enumerate([x for x in M['尺膚'] if x['主病'] and '總綱' not in x['主病']][:6], 1):
        items.append({'item_id': f'Q-LS074-CHI-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·論疾診尺》：「尺膚{c['尺膚']}」，主何病？",
                      'answer': c['主病'].split('；')[0], 'distractors': [],
                      'source': {'篇序': 74, '篇名': '論疾診尺'}, 'note': '尺膚診',
                      'auto_grading': 'fuzzy'})


# ---------- L 時間醫學（需先跑 build_module_time.py） ----------
TI = os.path.join(ROOT, 'data', '模組_時間.json')
if os.path.exists(TI):
    M = json.load(open(TI, encoding='utf-8'))
    for i, r in enumerate(M['日四時'], 1):
        items.append({'item_id': f'Q-LS044-R4-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': (f"《靈樞·順氣一日分為四時》：「朝則為____。」" if r['時段'] == '朝'
                               else f"《靈樞·順氣一日分為四時》：「{r['時段']}為____。」"),
                      'answer': r['配'], 'distractors': [],
                      'source': {'篇序': 44, '篇名': '順氣一日分為四時'}, 'note': '一日配四時',
                      'auto_grading': 'exact'})
        items.append({'item_id': f'Q-LS044-BS-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·順氣一日分為四時》：病於「{r['時段']}」多見____。",
                      'answer': r['病勢'], 'distractors': [],
                      'source': {'篇序': 44, '篇名': '順氣一日分為四時'}, 'note': '病勢節律',
                      'auto_grading': 'exact'})
    for i, w in enumerate(M['五變五輸'], 1):
        items.append({'item_id': f'Q-LS044-WB-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·順氣一日分為四時》：「{w['所主']}主{w['時']}」，刺____。",
                      'answer': w['刺'], 'distractors': [],
                      'source': {'篇序': 44, '篇名': '順氣一日分為四時'}, 'note': '五變五輸',
                      'auto_grading': 'exact'})
    for i, y in enumerate(M['十二月配足經'], 1):
        items.append({'item_id': f'Q-LS041-YUE-{i}', 'type': 'mcq', 'bloom': 'remember',
                      'stem': f"《靈樞·陰陽繫日月》：「{y['地支']}者，{y['月']}月」，主何經？",
                      'answer': y['左右'] + y['經'],
                      'distractors': [x['左右'] + x['經'] for x in M['十二月配足經']
                                      if (x['左右'] + x['經']) != (y['左右'] + y['經'])][:3],
                      'source': {'篇序': 41, '篇名': '陰陽繫日月'}, 'note': '十二月配足經',
                      'auto_grading': 'exact'})


# ---------- M F 型觀點題（需先跑 build_module_excerpts.py） ----------
EX = os.path.join(ROOT, 'data', '模組_摘句.json')
if os.path.exists(EX):
    items += [
        {'item_id': 'Q-F-VIEW-1', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '「上工治未病」出自《靈樞·逆順》，其原本語境是什麼？',
         'answer': '講刺的時機：上工刺其未生、未盛、已衰，不是泛泛的養生口號',
         'distractors': ['講養生：未病時要調攝', '講用藥：未病時先服補藥', '講診斷：未病時先察色脈'],
         'source': {'篇序': 55, '篇名': '逆順'}, 'note': '勿脫離語境', 'auto_grading': 'rubric'},
        {'item_id': 'Q-F-VIEW-2', 'type': 'mcq', 'bloom': 'understand',
         'stem': '《靈樞·外揣》以日月、水鏡、鼓響為喻，所要說明的是什麼？',
         'answer': '內在變化會在外表留下準確對應（司外揣內）',
         'distractors': ['醫者應如日月般光明', '診斷需借助器物', '聲音與形影不可分離'],
         'source': {'篇序': 45, '篇名': '外揣'}, 'note': '方法論比喻', 'auto_grading': 'exact'},
        {'item_id': 'Q-F-VIEW-3', 'type': 'mcq', 'bloom': 'understand',
         'stem': '《靈樞·官能》「得其人乃言，非其人勿傳」講的是什麼？',
         'answer': '教學與傳授的倫理：要判斷對方是否適合',
         'distractors': ['醫術不可外傳', '病人不問則不說', '針法只能口傳'],
         'source': {'篇序': 73, '篇名': '官能'}, 'note': '教學倫理', 'auto_grading': 'exact'},
        {'item_id': 'Q-F-VIEW-4', 'type': 'mcq', 'bloom': 'understand',
         'stem': '《靈樞·刺節真邪》「用針之類，在於調氣」意在強調什麼？',
         'answer': '針刺的本質是調氣，不是機械地扎針',
         'distractors': ['針刺越多越好', '針刺只看穴位', '針刺必須用九針'],
         'source': {'篇序': 75, '篇名': '刺節真邪'}, 'note': '針刺本質', 'auto_grading': 'exact'},
        {'item_id': 'Q-F-VIEW-5', 'type': 'error_identification', 'bloom': 'evaluate',
         'stem': '有人說「《靈樞》認為針刺效果與體質無關」。依《行鍼》，此說是否成立？',
         'answer': '不成立：百姓血氣各不同形，有六種不同針感反應，重陽之人神動而氣先行',
         'distractors': ['成立，針刺效果只取決於穴位', '成立，體質只影響用藥', '經文未討論體質'],
         'source': {'篇序': 67, '篇名': '行鍼'}, 'note': '個體差異', 'auto_grading': 'rubric'},
    ]


# ---------- N A 型第二批（需先跑 build_tables_a2.py） ----------
A2 = os.path.join(ROOT, 'data', '模組_A2.json')
if os.path.exists(A2):
    M = json.load(open(A2, encoding='utf-8'))
    for i, r in enumerate(M['九針所宜'], 1):
        items.append({'item_id': f'Q-LS007-JZ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·官鍼》：病在『{r['病所']}』者，取以____。",
                      'answer': r['用鍼'], 'distractors': [],
                      'source': {'篇序': 7, '篇名': '官鍼'}, 'note': '九針所宜',
                      'auto_grading': 'exact'})
    for i, r in enumerate(M['九刺'], 1):
        items.append({'item_id': f'Q-LS007-JIU-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·官鍼》九刺之「{r['序']}曰____」。",
                      'answer': r['名'], 'distractors': [],
                      'source': {'篇序': 7, '篇名': '官鍼'}, 'note': '九刺',
                      'auto_grading': 'exact'})
    for i, r in enumerate(M['十二節'][:8], 1):
        items.append({'item_id': f'Q-LS007-SJ-{i}', 'type': 'mcq', 'bloom': 'understand',
                      'stem': f"《靈樞·官鍼》十二節之「{r['名']}」，其法為何？",
                      'answer': r['法'][:30], 'distractors': [x['法'][:30] for x in M['十二節'] if x['名'] != r['名']][:3],
                      'source': {'篇序': 7, '篇名': '官鍼'}, 'note': '十二節',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['根結'], 1):
        items.append({'item_id': f'Q-LS005-GJ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·根結》：「{r['經']}根于{r['根']}，結于____。」",
                      'answer': r['結'], 'distractors': [],
                      'source': {'篇序': 5, '篇名': '根結'}, 'note': '根結',
                      'auto_grading': 'exact'})
    for i, r in enumerate(M['六陽根溜注入'], 1):
        items.append({'item_id': f'Q-LS005-LIU-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·根結》：「{r['經']}根于{r['根']}，溜于____。」",
                      'answer': r['溜'], 'distractors': [],
                      'source': {'篇序': 5, '篇名': '根結'}, 'note': '根溜注入',
                      'auto_grading': 'exact'})


# ---------- O A 型第三批（需先跑 build_module_a3.py） ----------
A3 = os.path.join(ROOT, 'data', '模組_A3.json')
if os.path.exists(A3):
    M = json.load(open(A3, encoding='utf-8'))
    for i, r in enumerate(M['五禁'], 1):
        items.append({'item_id': f'Q-LS061-WJ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五禁》：「{r['日干']}日自乘」，____。",
                      'answer': r['禁'], 'distractors': [],
                      'source': {'篇序': 61, '篇名': '五禁'}, 'note': '五禁',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['經水'], 1):
        items.append({'item_id': f'Q-LS012-JS-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·經水》：「{r['經']}外合____。」",
                      'answer': r['經水'], 'distractors': [],
                      'source': {'篇序': 12, '篇名': '經水'}, 'note': '十二經水',
                      'auto_grading': 'exact'})
    for i, r in enumerate(M['標本'], 1):
        items.append({'item_id': f'Q-LS052-BB-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·衛氣》：「{r['經']}之本，在{r['本']}，標在____。」",
                      'answer': r['標'], 'distractors': [],
                      'source': {'篇序': 52, '篇名': '衛氣'}, 'note': '十二經標本',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['八風'], 1):
        items.append({'item_id': f'Q-LS077-BF-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·九宮八風》：「{r['名']}」從{r['方位']}來，內舍於____。",
                      'answer': r['內舍'], 'distractors': [],
                      'source': {'篇序': 77, '篇名': '九宮八風'}, 'note': '八風',
                      'auto_grading': 'exact'})


# ---------- P 陰陽二十五人（需先跑 build_module_25.py） ----------
T25 = os.path.join(ROOT, 'data', '模組_二十五人.json')
if os.path.exists(T25):
    M = json.load(open(T25, encoding='utf-8'))
    for i, w in enumerate(M['五形'], 1):
        items.append({'item_id': f'Q-LS064-WX-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·陰陽二十五人》：「{w['形']}形之人，比於{w['名']}」，所比之經為____。",
                      'answer': w['比'], 'distractors': [],
                      'source': {'篇序': 64, '篇名': '陰陽二十五人'}, 'note': '五形所比',
                      'auto_grading': 'exact'})
        items.append({'item_id': f'Q-LS064-XX-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·陰陽二十五人》：「{w['形']}形之人」的性情特徵是____。",
                      'answer': w['性情'][:24], 'distractors': [],
                      'source': {'篇序': 64, '篇名': '陰陽二十五人'}, 'note': '五形性情',
                      'auto_grading': 'fuzzy'})
    for i, (f_, n, b, t) in enumerate(M['二十五變'], 1):
        items.append({'item_id': f'Q-LS064-B{ i }', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': (f"《靈樞·陰陽二十五人》：{'「' if n.split('（')[0] != '少徵' else '『'}{n.split('（')[0]}"
                               + ('之為人' if n.split('（')[0] in ('衆', '桎') else '之人')
                               + ('，比於____。」' if n.split('（')[0] != '少徵' else '，比於____。』（底本缺，據類經補）')),
                      'answer': (b[:4] + '，' + b[2:4] + b[4:]) if len(b) >= 6 else b,
                      'distractors': [],
                      **({'可接受答案': [b]} if len(b) >= 6 else {}),
                      'source': {'篇序': 64, '篇名': '陰陽二十五人'}, 'note': f'{f_}形之變',
                      'auto_grading': 'fuzzy'})


# ---------- Q C 型收尾（需先跑 build_module_c2.py） ----------
C2M = os.path.join(ROOT, 'data', '模組_C2.json')
if os.path.exists(C2M):
    M = json.load(open(C2M, encoding='utf-8'))
    for i, c in enumerate(M['五官'], 1):
        items.append({'item_id': f'Q-LS037-GUAN-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五閱五使》：「{c['官']}者，____之官也。」",
                      'answer': c['藏'], 'distractors': [],
                      'source': {'篇序': 37, '篇名': '五閱五使'}, 'note': '五官',
                      'auto_grading': 'exact'})
    for i, c in enumerate(M['十二盛'], 1):
        items.append({'item_id': f'Q-LS043-MENG-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·淫邪發夢》：「{c['氣']}{'俱' if c['氣'] == '陰陽' else ''}盛，則夢____。」",
                      'answer': c['夢'], 'distractors': [],
                      'source': {'篇序': 43, '篇名': '淫邪發夢'}, 'note': '十二盛之夢',
                      'auto_grading': 'fuzzy'})


# ---------- R B 型補遺（需先跑 build_module_b2.py） ----------
B2 = os.path.join(ROOT, 'data', '模組_B2.json')
if os.path.exists(B2):
    M = json.load(open(B2, encoding='utf-8'))
    for i, r in enumerate(M['五亂'], 1):
        items.append({'item_id': f'Q-LS034-LUAN-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五亂》：「亂於{r['亂於']}，則____。」",
                      'answer': r['證'], 'distractors': [],
                      'source': {'篇序': 34, '篇名': '五亂'}, 'note': '五亂之證',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['五亂治法'], 1):
        items.append({'item_id': f'Q-LS034-ZHI-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': (f"《靈樞·五亂》：「氣在于{r['氣在']}，取之____。」" if r['氣在'] == '臂足'
                               else f"《靈樞·五亂》：「氣在於{r['氣在']}者，取之____。」"),
                      'answer': r['取'], 'distractors': [],
                      'source': {'篇序': 34, '篇名': '五亂'}, 'note': '五亂治法',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['病傳'], 1):
        items.append({'item_id': f'Q-LS042-CHUAN-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·病傳》：「病先發於{r['首發']}，____。」",
                      'answer': r['傳變'][:26], 'distractors': [],
                      'source': {'篇序': 42, '篇名': '病傳'}, 'note': '五藏相傳',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['水脹'], 1):
        items.append({'item_id': f'Q-LS057-SHUI-{i}', 'type': 'mcq', 'bloom': 'understand',
                      'stem': f"《靈樞·水脹》：「{(r.get('原文') or r['候'][:26])}」，此為何病？",
                      'answer': r['病'], 'distractors': [x['病'] for x in M['水脹'] if x['病'] != r['病']][:3],
                      'source': {'篇序': 57, '篇名': '水脹'}, 'note': '水脹鑑別',
                      'auto_grading': 'exact'})


# ---------- S 剩餘篇章（一）（需先跑 build_module_r1.py） ----------
R1 = os.path.join(ROOT, 'data', '模組_R1.json')
if os.path.exists(R1):
    M = json.load(open(R1, encoding='utf-8'))
    for i, r in enumerate(M['癰疽'], 1):
        items.append({'item_id': f'Q-LS081-YONG-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·癰疽》：「發於{r['部位']}，名曰____。」",
                      'answer': r['名'], 'distractors': [],
                      'source': {'篇序': 81, '篇名': '癰疽'}, 'note': '癰疽名候',
                      'auto_grading': 'exact'})
    for i, r in enumerate(M['八虛'], 1):
        items.append({'item_id': f'Q-LS071-BX-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·邪客》：「{r['藏']}有邪，其氣{('流' if r['藏'] == '肝' else '留')}於____。」",
                      'answer': r['位'], 'distractors': [],
                      'source': {'篇序': 71, '篇名': '邪客'}, 'note': '八虛',
                      'auto_grading': 'exact'})


# ---------- T 剩餘篇章（二）（需先跑 build_module_r2.py） ----------
R2 = os.path.join(ROOT, 'data', '模組_R2.json')
if os.path.exists(R2):
    M = json.load(open(R2, encoding='utf-8'))
    for i, r in enumerate(M['五味所走'], 1):
        items.append({'item_id': f'Q-LS063-WW-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·五味論》：「{r['味']}走{r['走']}，多食之，令人____。」",
                      'answer': r['多食之害'], 'distractors': [],
                      'source': {'篇序': 63, '篇名': '五味論'}, 'note': '五味所走',
                      'auto_grading': 'exact'})
    for i, r in enumerate([x for x in M['人迎寸口'] if x.get('足經病')], 1):
        items.append({'item_id': f'Q-LS048-YR-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': (f"《靈樞·禁服》：「人迎大{r['倍']}倍于寸口」，病在____。" if r['倍'] == '一'
                               else f"《靈樞·禁服》：「人迎{r['倍']}倍」，病在____。"),
                      'answer': r['足經病'], 'distractors': [],
                      'source': {'篇序': 48, '篇名': '禁服'}, 'note': '人迎寸口',
                      'auto_grading': 'exact'})


# ---------- U 剩餘篇章（三）（需先跑 build_module_r3.py） ----------
R3 = os.path.join(ROOT, 'data', '模組_R3.json')
if os.path.exists(R3):
    M = json.load(open(R3, encoding='utf-8'))
    for i, r in enumerate(M['五藏脈變'], 1):
        items.append({'item_id': f'Q-LS004-MAI-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': _mai_stem(r),
                      'answer': r['病'][:20], 'distractors': [],
                      'source': {'篇序': 4, '篇名': '邪氣藏府病形'}, 'note': '五藏脈變',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(M['五變'], 1):
        items.append({'item_id': f'Q-LS046-BIAN-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·五變》：「{r['體質']}」，善病____。",
                      'answer': r['易病'], 'distractors': [],
                      'source': {'篇序': 46, '篇名': '五變'}, 'note': '體質易病',
                      'auto_grading': 'exact'})


# ---------- V 短篇三則（需先跑 build_module_r4.py） ----------
import random as _rnd
_rd = _rnd.Random(20240101)


def _pick_distractors(pool, correct, n=3):
    """干擾項一律取自同書他篇原文，不編造。"""
    cand = [x for x in pool if x and x != correct and x not in correct and correct not in x]
    seen, out = set(), []
    for x in _rd.sample(cand, min(len(cand), n * 3)):
        if x[:12] in seen:
            continue
        seen.add(x[:12])
        out.append(x)
        if len(out) == n:
            break
    return out


R4 = os.path.join(ROOT, 'data', '模組_R4.json')
if os.path.exists(R4):
    _cards = json.load(open(R4, encoding='utf-8'))['卡']
    _pool = [c['機'] for c in _cards]
    for c in _cards:
        items.append({'item_id': f"Q-LS{c['篇序']:03d}-KAPPA-1", 'type': 'mcq', 'bloom': 'understand',
                      # 病名是標籤不是原文，故用『』（docs/82）
                      'stem': f"《靈樞·{c['篇名']}》所論的『{c['病']}』，其病機為何？",
                      'answer': c['機'][:40],
                      'distractors': _pick_distractors(_pool, c['機'][:40]),
                      'source': {'篇序': c['篇序'], '篇名': c['篇名']}, 'note': '病機',
                      'auto_grading': 'fuzzy'})


# ---------- W 剩餘篇章摘要（需先跑 build_module_r5.py） ----------
R5 = os.path.join(ROOT, 'data', '模組_R5.json')
if os.path.exists(R5):
    _cards5 = json.load(open(R5, encoding='utf-8'))['卡']
    _pool5 = [c['主旨'] for c in _cards5]
    for c in _cards5:
        items.append({'item_id': f"Q-LS{c['n']:03d}-SUM-1", 'type': 'mcq', 'bloom': 'understand',
                      'stem': f"《靈樞·{c['名']}》的主旨是？",
                      'answer': c['主旨'],
                      'distractors': _pick_distractors(_pool5, c['主旨']),
                      'source': {'篇序': c['n'], '篇名': c['名']}, 'note': '篇旨',
                      'auto_grading': 'fuzzy'})

# ---------- X 度量與換算（需先跑 build_module_measure.py） ----------
MEAS = os.path.join(ROOT, 'data', '模組_度量.json')
if os.path.exists(MEAS):
    _m = json.load(open(MEAS, encoding='utf-8'))
    for i, r in enumerate([x for x in _m['腸胃'] if x['寸'] != ''][:22], 1):
        items.append({'item_id': f'Q-LS031-DU-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      # 用模組「原文」逐字，避免「部位＋項目」拼出原文沒有的句子（docs/82）
                      'stem': f"《靈樞·腸胃》：「{(r.get('原文') or r['部位']+r['項目']).replace(r['數值'], '____', 1)}」",
                      'answer': r['數值'], 'distractors': [],
                      'source': {'篇序': 31, '篇名': '腸胃'}, 'note': '腸胃度量',
                      'auto_grading': 'exact'})
    for i, r in enumerate(_m['五十營'], 1):
        if r['項目'] == '氣行' and r['數值'] in ('六寸', '六尺', '十六丈二尺'):
            items.append({'item_id': f'Q-LS015-YING-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                          'stem': f"《靈樞·五十營》：「{(r.get('原文') or (r['息數'] + '氣行' + r['數值'])).replace(r['數值'], '____', 1)}",
                          'answer': r['數值'], 'distractors': [],
                          'source': {'篇序': 15, '篇名': '五十營'}, 'note': '五十營',
                          'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS015-YING-9', 'type': 'fill_blank', 'bloom': 'apply',
                  'stem': '《靈樞·五十營》：一息氣行六寸，一萬三千五百息共行多少？（原文末句有總數）',
                  'answer': '八百一十丈', 'distractors': [],
                  'source': {'篇序': 15, '篇名': '五十營'}, 'note': '推算：6寸×13500息',
                  'auto_grading': 'exact'})
    _n = 0
    for r in _m['骨度']:
        if r['類型'] != '縱向長度' or not r['占身長%']:
            continue
        _n += 1
        items.append({'item_id': f'Q-LS014-DU-{_n}', 'type': 'fill_blank', 'bloom': 'apply',
                      'stem': f"《靈樞·骨度》：「{r['原文']}」——"
                              f"以「人長七尺五寸」計，此段占人身高的百分之幾？（答到小數一位）",
                      'answer': f"{r['占身長%']}%", 'distractors': [],
                      'source': {'篇序': 14, '篇名': '骨度'}, 'note': f"換算：{r['寸']}寸/75寸",
                      'auto_grading': 'fuzzy'})

# ---------- Y 治則（需先跑 build_module_zhize.py） ----------
Z = os.path.join(ROOT, 'data', '模組_治則.json')
if os.path.exists(Z):
    _z = json.load(open(Z, encoding='utf-8'))
    # 題面用句讀層的標點版本（較可讀），再只挖掉答案那一處。
    # 不用「條件＋者」拼接：那會造出原文沒有的虛詞（見 docs/80）。
    _clauses = [c.strip() for c in re.split(r'[。；\n]', J[25]['句讀']) if c.strip()]
    _han = lambda t: ''.join(ch for ch in t if re.match(r'[\u3400-\u9fff]', ch))

    def _punctuated(raw):
        key = _han(raw)
        for c in _clauses:
            if key in _han(c):
                return c
        return raw

    for i, r in enumerate(_z['規則'], 1):
        _raw = _punctuated(r['原文'])
        if '本而標之' in _raw:
            _stem_txt = _raw.replace('本而標之', '____', 1)
            _ans, _note = '本而標之', '有餘：先本後標'
        elif '標而本之' in _raw:
            _stem_txt = _raw.replace('標而本之', '____', 1)
            _ans, _note = '標而本之', '不足：先標後本'
        elif '治其本' in _raw or '治其標' in _raw:
            _stem_txt = _raw.replace('治其本', '治其____').replace('治其標', '治其____')
            _ans = '本' if r['治法'].startswith('治其本') else '標'
            _note = '標本先後'
        else:
            continue
        items.append({'item_id': f'Q-LS025-ZZ-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·病本》：「{_stem_txt}」",
                      'answer': _ans, 'distractors': [],
                      'source': {'篇序': 25, '篇名': '病本'}, 'note': _note,
                      'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS025-ZZ-15', 'type': 'mcq', 'bloom': 'understand',
                  'stem': '《靈樞·病本》「本而標之」，對應下列哪一種情況？',
                  'answer': '病發而有餘', 'distractors': ['病發而不足', '大小便不利', '先病而後中滿'],
                  'source': {'篇序': 25, '篇名': '病本'}, 'note': '本而標之＝先本後標',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS025-ZZ-16', 'type': 'mcq', 'bloom': 'understand', '層級': 'L1',
                  'stem': '《靈樞·病本》「間者并行，甚為獨行」，其意為何？',
                  'answer': '病緩者可標本並治，病急者須專治一處',
                  'distractors': ['病輕者用針，病重者用藥', '間日服藥，甚日停藥',
                                  '病在表者並治，病在裏者獨治'],
                  'source': {'篇序': 25, '篇名': '病本'}, 'note': '治則通例',
                  'auto_grading': 'fuzzy'})

# ---------- XL 血絡論（39）——需先有 data/模組_血絡.json ----------
_XL = os.path.join(ROOT, 'data', '模組_血絡.json')
if os.path.exists(_XL):
    _x = json.load(open(_XL, encoding='utf-8'))
    _n = 0
    for r in _x.get('定義', []) + _x.get('診法', []) + _x.get('操作', []):
        _n += 1
        items.append({'item_id': f'Q-LS039-XL-{_n}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·血絡論》：「{r['原文'].replace(r['挖'], '____', 1)}」",
                      'answer': r['挖'], 'distractors': [],
                      'source': {'篇序': 39, '篇名': '血絡論'}, 'note': r.get('說明', ''),
                      'auto_grading': 'exact'})
    _pool = [r['答'] for r in _x['現象']]
    for i, r in enumerate(_x['現象'], 1):
        _dis = [a for a in _pool if a != r['答']][:3]
        items.append({'item_id': f'Q-LS039-XL-X{i}', 'type': 'mcq', 'bloom': 'apply',
                      'stem': f"《靈樞·血絡論》：「{r['問']}？」",
                      'answer': r['答'], 'distractors': _dis,
                      'source': {'篇序': 39, '篇名': '血絡論'},
                      'note': '針下所見→氣血狀態：' + r.get('說明', ''),
                      'auto_grading': 'exact'})

# ---------- QZ 陰陽清濁（40）——需先有 data/模組_清濁.json ----------
_QZ = os.path.join(ROOT, 'data', '模組_清濁.json')
if os.path.exists(_QZ):
    _q = json.load(open(_QZ, encoding='utf-8'))
    for i, r in enumerate(_q['規則'], 1):
        items.append({'item_id': f'Q-LS040-QZ-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·陰陽清濁》：「{r['原文'].replace(r['挖'], '____', 1)}」",
                      'answer': r['挖'], 'distractors': [],
                      'source': {'篇序': 40, '篇名': '陰陽清濁'},
                      'note': r['條'] + '：' + r.get('說明', ''),
                      'auto_grading': 'exact'})

# ---------- Z 營氣／平人絕穀／津液（需先跑 build_module_batch1.py） ----------
_Y = os.path.join(ROOT, 'data', '模組_營氣.json')
if os.path.exists(_Y):
    _y = json.load(open(_Y, encoding='utf-8'))
    for i, r in enumerate(_y['循行'], 1):
        items.append({'item_id': f'Q-LS016-YQ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      # 經名是可替換的標籤，不是原文，故用『』；避免「」被當成逐字引文（docs/82）
                      'stem': f"《靈樞·營氣》：營氣從『{r['前']}』出，注『____』。",
                      # 原文只寫經名（手陽明），藏名是教材加的；故答案取前三字，全稱列可接受
                      'answer': r['後'][:3], 'distractors': [],
                      'source': {'篇序': 16, '篇名': '營氣'}, 'note': '營氣循行次序：' + r['後'],
                      **({'可接受答案': [r['後']]} if len(r['後']) > 3 else {}),
                      'auto_grading': 'fuzzy'})
    items.append({'item_id': 'Q-LS016-YQ-13', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': '《靈樞·營氣》：營氣「其支別者，上額循巔，下項中，循脊入骶」，這是哪一條脈？',
                  'answer': '督脈', 'distractors': [],
                  'source': {'篇序': 16, '篇名': '營氣'}, 'note': '督脈支',
                  'auto_grading': 'exact'})
_P = os.path.join(ROOT, 'data', '模組_平人絕穀.json')
if os.path.exists(_P):
    _p = json.load(open(_P, encoding='utf-8'))
    for i, r in enumerate(_p['數據'], 1):
        items.append({'item_id': f'Q-LS032-PR-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·平人絕穀》：「{(r.get('原文') or r['部位']+r['項目']).replace(r['數值'], '____', 1)}」",
                      'answer': r['數值'], 'distractors': [],
                      'source': {'篇序': 32, '篇名': '平人絕穀'}, 'note': '腸胃容量',
                      'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS032-PR-13', 'type': 'fill_blank', 'bloom': 'apply',
                  'stem': '《靈樞·平人絕穀》：平人日再後、後二升半，七日共排出多少？（即絕穀七日所盡之數）',
                  'answer': '三斗五升', 'distractors': [],
                  'source': {'篇序': 32, '篇名': '平人絕穀'}, 'note': '推算：2.5升×2次×7日',
                  'auto_grading': 'exact'})
_J = os.path.join(ROOT, 'data', '模組_五癃津液別.json')
if os.path.exists(_J):
    _j = json.load(open(_J, encoding='utf-8'))
    for i, r in enumerate(_j['五別'], 1):
        items.append({'item_id': f'Q-LS036-JY-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·五癃津液別》：「{(r.get('原文') or (r['因'] + '，則為' + r['果'])).replace(r['果'], '____', 1)}",
                      'answer': r['果'], 'distractors': [],
                      'source': {'篇序': 36, '篇名': '五癃津液別'}, 'note': '津液五別',
                      'auto_grading': 'fuzzy'})
    items.append({'item_id': 'Q-LS036-JY-6', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·五癃津液別》：三焦出氣，温肌肉、充皮膚者，謂之____。',
                  'answer': '津', 'distractors': [],
                  'source': {'篇序': 36, '篇名': '五癃津液別'}, 'note': '津＝可外達者',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS036-JY-7', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·五癃津液別》：其流而不外行者，謂之____。',
                  'answer': '液', 'distractors': [],
                  'source': {'篇序': 36, '篇名': '五癃津液別'}, 'note': '液＝流而不行者',
                  'auto_grading': 'exact'})

# ---------- AA 寒熱病／師傳（需先跑 build_module_batch2.py） ----------
_H = os.path.join(ROOT, 'data', '模組_寒熱病.json')
if os.path.exists(_H):
    _h = json.load(open(_H, encoding='utf-8'))
    for i, r in enumerate(_h['五部主治'], 1):
        items.append({'item_id': f'Q-LS021-HR-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·寒熱病》：「{r['病']}」，取____。",
                      'answer': r['取'], 'distractors': [],
                      'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '天牖五部主治',
                      'auto_grading': 'fuzzy'})
    items.append({'item_id': 'Q-LS021-HR-6', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': '《靈樞·寒熱病》：身有五部——伏兔一、腓二、背三、____四、項五。',
                  'answer': '五藏之腧', 'distractors': [],
                  'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '身五部（校本作背三）',
                  'auto_grading': 'fuzzy'})
    items.append({'item_id': 'Q-LS021-HR-7', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·寒熱病》：身五部「有癰疽者」預後如何？',
                  'answer': '死', 'distractors': [],
                  'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '身五部預後',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS021-HR-8', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·寒熱病》：骨寒熱，齒未槁者取少陰于陰股之絡；齒已槁則____。',
                  'answer': '死不治', 'distractors': [],
                  'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '骨寒熱預後',
                  'auto_grading': 'exact'})
    for i, r in enumerate(_h['四時刺法'], 1):
        items.append({'item_id': f'Q-LS021-SS-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·寒熱病》：「{r['時']}取____。」",
                      'answer': r['所取'], 'distractors': [],
                      'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '四時刺法',
                      'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS021-SS-5', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': '《靈樞·寒熱病》：下齒齲，取____。',
                  'answer': '大迎', 'distractors': [],
                  'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '齲齒取穴',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS021-SS-6', 'type': 'fill_blank', 'bloom': 'remember',
                  'stem': '《靈樞·寒熱病》：上齒齲，取____。',
                  'answer': '角孫', 'distractors': [],
                  'source': {'篇序': 21, '篇名': '寒熱病'}, 'note': '齲齒取穴',
                  'auto_grading': 'exact'})
_S = os.path.join(ROOT, 'data', '模組_師傳.json')
if os.path.exists(_S):
    _s = json.load(open(_S, encoding='utf-8'))
    items.append({'item_id': 'Q-LS029-SZ-1', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·師傳》：「入國問俗，入家問諱，上堂問禮，臨病人問____。」',
                  'answer': '所便', 'distractors': [],
                  'source': {'篇序': 29, '篇名': '師傳'}, 'note': '四問',
                  'auto_grading': 'exact'})
    items.append({'item_id': 'Q-LS029-SZ-2', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·師傳》：「春夏先治其____，後治其____；秋冬先治其本，後治其標。」',
                  'answer': '標；本', 'distractors': [],
                  'source': {'篇序': 29, '篇名': '師傳'}, 'note': '治序隨時令',
                  'auto_grading': 'fuzzy'})
    items.append({'item_id': 'Q-LS029-SZ-3', 'type': 'fill_blank', 'bloom': 'understand',
                  'stem': '《靈樞·師傳》：「告之以其敗，語之以其善，導之以其所便，開之以其____。」',
                  'answer': '所苦', 'distractors': [],
                  'source': {'篇序': 29, '篇名': '師傳'}, 'note': '勸導四法',
                  'auto_grading': 'exact'})
    for i, r in enumerate(_s['藏府之候'], 1):
        items.append({'item_id': f'Q-LS029-ZF-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·師傳》：五藏六府中，「{r['藏']}」的職能是「____」。",
                      'answer': r['職'], 'distractors': [],
                      'source': {'篇序': 29, '篇名': '師傳'}, 'note': '藏府之候',
                      'auto_grading': 'fuzzy'})

# ---------- AB 四時氣／雜病／衛氣行／歲露論（需先跑 build_module_batch3.py） ----------
def _load(name):
    fp = os.path.join(ROOT, 'data', name)
    return json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else None


_m = _load('模組_四時氣.json')
if _m:
    for i, r in enumerate(_m['四時刺法'], 1):
        items.append({'item_id': f'Q-LS019-SS-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·四時氣》：「{r['時']}取____。」",
                      'answer': r['所取'], 'distractors': [],
                      'source': {'篇序': 19, '篇名': '四時氣'}, 'note': '四時刺法',
                      'auto_grading': 'fuzzy'})
    for i, r in enumerate(_m['病取'], 1):
        items.append({'item_id': f'Q-LS019-BQ-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·四時氣》：「{split_gloss(r['病'])[0]}」，如何治？",
                      'answer': r['治'], 'distractors': [],
                      'source': {'篇序': 19, '篇名': '四時氣'}, 'note': '病取',
                      'auto_grading': 'fuzzy'})

_m = _load('模組_雜病.json')
if _m:
    for i, r in enumerate(_m['病取'], 1):
        # 用模組「原文」，把「取X」的 X 挖空；原文缺失才退回舊寫法
        _raw = r.get('原文') or ''
        _zq = None
        for _verb in ('取', '刺'):
            if _raw and (_verb + r['取']) in _raw:
                _zq = _raw.replace(_verb + r['取'], _verb + '____', 1)
                break
        _zq = _zq or (r['病'] + '，取____')
        items.append({'item_id': f'Q-LS026-ZB-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·雜病》：「{_zq}」",
                      'answer': r['取'], 'distractors': [],
                      'source': {'篇序': 26, '篇名': '雜病'}, 'note': '病→經',
                      'auto_grading': 'exact'})

_m = _load('模組_衛氣行.json')
if _m:
    for i, r in enumerate(_m['數'], 1):
        items.append({'item_id': f'Q-LS076-WQ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·衛氣行》：「{(r.get('原文') or r['項']) .replace(r['值'], '____', 1) if r.get('原文') else r['項'] + '____'}",
                      'answer': r['值'], 'distractors': [],
                      'source': {'篇序': 76, '篇名': '衛氣行'}, 'note': '衛氣週期',
                      'auto_grading': 'fuzzy'})

_m = _load('模組_歲露論.json')
if _m:
    for i, r in enumerate(_m['要點'], 1):
        items.append({'item_id': f'Q-LS079-SL-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·歲露論》：『{r['問']}』？",
                      'answer': r['答'], 'distractors': [],
                      'source': {'篇序': 79, '篇名': '嵗露論'}, 'note': '歲露要點',
                      'auto_grading': 'fuzzy'})

# ---------- AC 小鍼解／口問／九鍼論／終始（需先跑 build_module_batch4.py） ----------
_m = _load('模組_小鍼解.json')
if _m:
    for i, r in enumerate(_m['術語'], 1):
        items.append({'item_id': f'Q-LS003-XZ-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·小鍼解》：所謂「{r['語']}」者，何謂也？",
                      'answer': r['釋'], 'distractors': [],
                      'source': {'篇序': 3, '篇名': '小鍼解'}, 'note': '術語自注',
                      'auto_grading': 'fuzzy'})

_m = _load('模組_口問.json')
if _m:
    for i, r in enumerate(_m['十二邪'], 1):
        items.append({'item_id': f'Q-LS028-KW-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': f"《靈樞·口問》：人之「{r['症']}」者，治當如何？",
                      'answer': r['治'], 'distractors': [],
                      'source': {'篇序': 28, '篇名': '口問'}, 'note': '十二邪取治',
                      'auto_grading': 'fuzzy'})

_m = _load('模組_九鍼論.json')
if _m:
    for i, r in enumerate(_m['九鍼'], 1):
        items.append({'item_id': f'Q-LS078-JZ-{i}', 'type': 'fill_blank', 'bloom': 'remember',
                      'stem': f"《靈樞·九鍼論》：{r['序']}曰{r['名']}，長____，{r['主']}。",
                      'answer': r['長'], 'distractors': [],
                      'source': {'篇序': 78, '篇名': '九鍼論'}, 'note': '九鍼長度',
                      'auto_grading': 'exact'})

_m = _load('模組_終始.json')
if _m:
    for i, r in enumerate(_m['經終'], 1):
        items.append({'item_id': f'Q-LS009-ZS-{i}', 'type': 'fill_blank', 'bloom': 'understand',
                      'stem': (f"《靈樞·終始》：「{r['經']}之脉，其終也，____。」" if r['經'] == '太陽'
                               else f"《靈樞·終始》：「{r['經']}終者，____。」"),
                      'answer': r['候'], 'distractors': [],
                      'source': {'篇序': 9, '篇名': '終始'}, 'note': '五經之終',
                      'auto_grading': 'fuzzy'})

# ---------- AD 注→經題（需先跑 build_items_from_notes.py） ----------
ZJ = os.path.join(ROOT, 'data', '題庫_注經.json')
if os.path.exists(ZJ):
    _zj = json.load(open(ZJ, encoding='utf-8'))['題']
    for _it in _zj:
        items.append(_it)

# ---------- 章級校記提示：讓學習者知道這篇的底本有問題 ----------
_BASE = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
_XJ = {int(p['序']): p['校記'] for p in _BASE if isinstance(p.get('校記'), str) and p['校記'].strip()}
for _it in items:
    _n = (_it.get('source') or {}).get('篇序')
    if _n and int(_n) in _XJ:
        _it['章校記'] = _XJ[int(_n)]

# ---------- 後處理：長答案填空改為要點評分 ----------
import re as _re
_CJK = _re.compile(r'[\u4e00-\u9fff]')
for _it in items:
    _a = ''.join(_CJK.findall(_it['answer']))
    if _it['type'] == 'fill_blank' and len(_a) > 20 and _it['auto_grading'] != 'rubric':
        _it['auto_grading'] = 'rubric'
        _it['note'] = (_it.get('note') or '') + '｜答案較長，改按要點評分'

# ---------- 標註知識層級：L0 原文可直引／L1 概括歸納 ----------
_L1_MARK = ('-SUM-', '-KAPPA-', '-VIEW-', '-ERR-', '-TN-', '-YW-', 'Q-F-')
for _it in items:
    if _it.get('層級'):
        continue
    _id = _it['item_id']
    _is_l1 = any(m in _id for m in _L1_MARK) or _it['type'] == 'error_identification'
    _it['層級'] = 'L1' if _is_l1 else 'L0'
    _it['證據類型'] = ('歸納（由本庫結構化資料概括）' if _is_l1 else '直引（答案為原文字串或原文標籤）')

# ---------- 可接受答案：異體與簡體，不擴及同義詞 ----------
_AV = {}
_avp = os.path.join(ROOT, 'data', '同義答案表.csv')
if os.path.exists(_avp):
    for _r in csv.DictReader(open(_avp, encoding='utf-8-sig')):
        _AV.setdefault(_r['答案'], []).append(_r['可接受'])
from check_quotes import VAR as _VAR
_grp = {}
for _c, _k in _VAR.items():
    _grp.setdefault(_k, set()).add(_c)


def _variants(ans):
    """以本庫異體字表，逐字換寫，產生所有等價寫法。"""
    out = set()
    for i, ch in enumerate(ans):
        for alt in _grp.get(_VAR.get(ch), ()):
            if alt != ch:
                out.add(ans[:i] + alt + ans[i + 1:])
    out.discard(ans)
    return out


_T2S = {}
_t2s_p = os.path.join(ROOT, 'data', '繁簡映射.csv')
if os.path.exists(_t2s_p):
    for _r in csv.DictReader(open(_t2s_p, encoding='utf-8-sig')):
        _T2S[_r['繁']] = _r['簡']


def _simp(s):
    return ''.join(_T2S.get(ch, ch) for ch in s)


for _it in items:
    if _it['type'] != 'fill_blank':
        continue
    _acc = set(_AV.get(_it['answer'], [])) | set(_it.get('可接受答案') or [])
    if _simp(_it['answer']) != _it['answer']:
        _acc.add(_simp(_it['answer']))
    _acc |= _variants(_it['answer'])
    _acc.discard(_it['answer'])
    if _acc:
        _it['可接受答案'] = sorted(_acc)

# ---------- 節引標記：題面「」內的文字若非該篇連續原文，就在 note 註明 ----------
from check_quotes import norm as _norm


def _contiguous(seg, txt):
    return _norm(seg) in txt


def _subseq(s, txt):
    it = iter(txt)
    return all(ch in it for ch in s)


def mark_excerpts(items):
    marked = 0
    for it in items:
        seq = it['source']['篇序']
        txt = _norm(S[seq]['正規化'])
        for quote in re.findall(r'「([^」]{2,})」', it['stem']):
            for seg in [x for x in re.split(r'_+', quote) if len(_norm(x)) >= 2]:
                s_ = _norm(seg)
                if _contiguous(seg, txt):
                    continue
                if _subseq(s_, txt):
                    if '節引' not in it.get('note', ''):
                        it['note'] = (it.get('note', '') + '；題面引文為節引').strip('；')
                        marked += 1
                break
    return marked


# 剔除：題面所引不见於靈樞底本者（目色 4 題、金形 2 題、歲露 1 題），保留紀錄於 docs/88、docs/90
_DROP = {'Q-LS074-MU-2', 'Q-LS074-MU-3', 'Q-LS074-MU-4', 'Q-LS074-MU-5',
         'Q-LS064-WX-4', 'Q-LS064-XX-4',
         'Q-LS079-SL-1'}   # 歲露論 SL-1「衛氣大會於風府」不見於靈樞（出素問）
items = [i for i in items if i['item_id'] not in _DROP]


# ---------- 篇名統一：一律用底本的規範篇名（docs/95） ----------
_SEQ_NAME = {p['序']: p['篇名_規範'] for p in list(S.values())}
for _it in items:
    _src = _it.get('source') or {}
    if _src.get('篇序') in _SEQ_NAME:
        _src['篇名'] = _SEQ_NAME[_src['篇序']]

# ---------- 答案類型：原文／推算／整理語（docs/94） ----------
from check_quotes import norm as _an


def _answer_kind(seq, ans):
    a = _an(ans)
    if not a:
        return '推算'
    base = _an(S[seq]['正規化'])
    if a in base:
        return '原文'
    return '整理語'


for _it in items:
    if _it['type'] != 'fill_blank':
        continue
    _k = _answer_kind(_it['source']['篇序'], _it['answer'])
    _it['答案類型'] = _k
    if _k == '整理語' and '整理語' not in _it.get('note', ''):
        _it['note'] = ((_it.get('note') or '') + '；答案為整理語（非原文連續字串）').strip('；')

# ---------- 去重：完全相同的題面只留第一筆（docs/95） ----------
_seen, _uniq, _dups = set(), [], []
for _it in items:
    key = _it['stem']
    if key in _seen:
        _dups.append(_it['item_id'])
        continue
    _seen.add(key); _uniq.append(_it)
items = _uniq

_n_mark = mark_excerpts(items)


json.dump({'說明': '規則式生成，每題附原文出處；干擾項取自同書他處，非編造',
           '題數': len(items),
           '層級分布': dict(__import__('collections').Counter(i['層級'] for i in items)),
           '題型分布': dict(__import__('collections').Counter(i['type'] for i in items)),
           '已知限制': [
               'E2 31 題 L1 答案為自撰，無外部權威（題內「依據類型」已標）',
               'E1 19 題註家配對未逐題人工複核；其中 5 題屬「段末注」，已知不精確',
               'E4 7 題干擾項長度與答案失配，可憑形式猜中',
               'E5 61 題為單字答案，依賴 fuzzy 評分',
               'E12 難度全為先驗值，無任何實測作答',
               '全部限制見 data/能力邊界.csv 與 docs/42',
           ],
           '題': items},
          open(os.path.join(ROOT, 'data', '題庫_示例.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# ---------- 輸出 markdown 樣例 ----------
with open(os.path.join(ROOT, 'docs', '10_題庫示例.md'), 'w', encoding='utf-8') as f:
    f.write('# 題庫示例（規則式生成）\n\n')
    f.write(f"> 共生成 **{len(items)}** 題。全部由結構化資料產生，每題附原文出處；干擾項取自同書他處原文，非編造。\n\n")
    f.write('## A 五輸穴填空（樣例 8 題）\n\n')
    for it in [x for x in items if x['type'] == 'fill_blank'][:8]:
        # 樣例文件不承擔「引號即原文」的公約：題面內的「」改成『』，避免與檢查器混淆
        _stem = it['stem'].replace('「', '『').replace('」', '』')
        f.write(f"- **{it['item_id']}**　{_stem}　答：**{it['answer']}**\n")
    f.write('\n## B 腧穴歸經（樣例 6 題）\n\n')
    for it in [x for x in items if x['type'] == 'mcq'][:6]:
        opts = [it['answer']] + it['distractors']
        random.shuffle(opts)
        f.write(f"- **{it['item_id']}**　{it['stem']}\n")
        f.write("  - " + "／".join(opts) + f"　→ 答：**{it['answer']}**\n")
    f.write('\n## C 循行起點辨識（樣例 4 題）\n\n')
    for it in [x for x in items if x['type'] == 'error_identification'][:4]:
        f.write(f"- **{it['item_id']}**　{it['stem']}\n")
        f.write(f"  - 答：**{it['answer']}**\n")
        f.write(f"  - 干擾（皆為他經原文）：{'／'.join(it['distractors'])}\n")

print(f"生成 {len(items)} 題（去重 {len(_dups)}）；題面節引 {_n_mark} 題；有可接受答案 {sum(1 for i in items if i.get(chr(21487)+chr(25509)+chr(21463)+chr(31572)+chr(26696)))} 題")
print("題型:", {t: sum(1 for i in items if i['type'] == t) for t in set(i['type'] for i in items)})
print("循行起點:", starts)
