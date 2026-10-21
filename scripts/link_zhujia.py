#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《類經》張介賓注接到 L1（歸納層）題目上。

問題：L1 題的答案全是自撰概括，沒有外部權威（見 docs/34 M3）。
解法：為每道 L1 題找出其所屬篇在《類經》中的對應條與注，作為「註家參照」。

注意用詞：欄位叫「註家參照」而非「依據」。它表示「此篇有張介賓注可參」，
         **不**表示「此注即此題答案之出處」。前者可機械判定，後者需人工裁決。
         `依據類型` 誠實區分兩者。
"""
import json, os, re, csv
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VAR = {'隂': '陰', '别': '別', '絶': '絕', '痩': '瘦', '㑹': '會', '閲': '閱',
       '榖': '穀', '㑹': '會', '壽': '壽', '夀': '壽', '嵗': '歲', '為': '為',
       '藏': '藏', '經': '經', '脉': '脈', '痺': '痹', '衞': '衛', '爲': '為',
       '減': '滅', '减': '滅', '歩': '步', '悞': '誤', '嵗': '歲', '靣': '面'}


def vn(s):
    return ''.join(VAR.get(c, c) for c in s)


def load():
    tiao = json.load(open(os.path.join(ROOT, 'data', '類經條目.json'), encoding='utf-8'))['條目']
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))['題']
    pian = {int(p['序']): p for p in
            json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}
    return tiao, items, pian


def src_pian(e):
    """從類經出處取出所引靈樞篇名（去書名、去『篇全』『連前章』等尾巴）。"""
    s = e['出處']
    i = s.find('靈樞')
    if i < 0:
        return None
    s = s[i + 2:]
    s = re.split(r'[篇連全此與○]', s)[0]
    return vn(s) or None


def main():
    tiao, items, pian = load()
    idx = defaultdict(list)
    for e in tiao:
        k = src_pian(e)
        if k:
            idx[k].append(e)

    def grams(t, k=4, stride=2):
        return {t[i:i + k] for i in range(0, max(1, len(t) - k + 1), stride)}

    def overlap(a, b):
        ga, gb = grams(a), grams(b)
        if not ga or not gb:
            return 0.0
        return len(ga & gb) / min(len(ga), len(gb))

    CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')

    def han(s):
        return ''.join(CJK.findall(s))

    # 候選配對：(條, 該條中被注的經文句, 注文)
    # 同篇約束：只接受出處篇名與題目所屬篇一致者。
    # 否則「起于小指之下」會同時命中經脈與經筋，把經筋的注安到經脈的題上。
    tiao_pian = {id(e): vn(src_pian(e) or '') for e in tiao}
    cand = []
    for e in tiao:
        for pr in e.get('對注') or []:
            cand.append((e, vn(pr['經']), pr['注']))

    stat = defaultdict(int)
    for it in items:
        if it.get('層級') != 'L1':
            continue
        pn = vn((it.get('source') or {}).get('篇名') or '')
        quotes = [han(q) for q in re.findall(r'「([^」]{2,})」', it['stem'])]
        ans = han(it['answer'])

        best, best_score, how = None, 0.0, ''
        for e, jing, note in cand:
            if not jing or tiao_pian.get(id(e)) != pn:
                continue
            # 題面引文優先：引文與被注經文的重疊
            for q in quotes:
                if len(q) < 4:
                    sc = 0.95 if q in jing else 0.0
                else:
                    sc = overlap(q, jing)
                if sc > best_score or (sc == best_score and best and len(jing) < len(best[1])):
                    best, best_score, how = (e, jing, note), sc, '題面引文'
            # 次選：答案字串直接出現在被注經文裡
            if ans:
                if ans in jing:
                    sc = 0.98
                elif len(ans) >= 8 and overlap(ans, jing) >= 0.5:
                    # 明文包含 > 重疊；重疊上限壓到 0.85，避免偶然高重疊蓋過正確句
                    sc = min(0.85, overlap(ans, jing))
                else:
                    sc = 0.0
                if sc > best_score or (sc == best_score and best and len(jing) < len(best[1])):
                    best, best_score, how = (e, jing, note), sc, '答案見於經文'

        if best is None or best_score < 0.5:
            it['依據類型'] = '自撰（無外部權威）'
            it.pop('註家參照', None)
            stat['無對應注'] += 1
            continue

        e, jing, note = best
        # 精度：類經有時間隔數句才給一注，注只解釋段末。長段不可當作逐句注釋。
        prec = '句注' if len(jing) <= 60 else '段末注（未必針對本題所問之句）'
        it['註家參照'] = {
            '來源': '類經', '類': e['類'], '條題': e['條題'],
            '條號': f"{e['出處']}○{e['條號']}",
            '所注經文': jing[-40:],
            '配對方式': how,
            '配對精度': prec,
            '注節錄': note[:170],
        }
        it['依據類型'] = '有註家對應注可參'
        stat['有對應注'] += 1
        stat[f'　其中{how}'] += 1
        stat[f'　精度·{prec}'] += 1

    json.dump({'說明': '規則式生成，每題附原文出處；干擾項取自同書他處，非編造',
               '題數': len(items),
               '層級分布': dict(__import__('collections').Counter(i['層級'] for i in items)),
               '依據分布': dict(stat),
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

    n_l1 = sum(1 for i in items if i.get('層級') == 'L1')
    print(f'L1 題 {n_l1}｜有對應注 {stat["有對應注"]}｜無 {stat["無對應注"]}')
    for k, v in sorted(stat.items()):
        if k.startswith('　'):
            print(' ', k, v)
    # 列出無註家者所在篇，供後續補
    miss = defaultdict(int)
    for it in items:
        if it.get('層級') == 'L1' and it.get('依據類型', '').startswith('自撰'):
            miss[(it.get('source') or {}).get('篇名')] += 1
    print('無對應注之篇:', dict(miss))


if __name__ == '__main__':
    main()
