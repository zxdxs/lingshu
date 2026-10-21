#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校勘點逐條檢：對每個疑讀，印出三源各自的上下文，供人工裁定。

用法：python3 scripts/probe_variants.py [代號...]
"""
import json, os, re, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('cw', os.path.join(ROOT, 'scripts', 'collate_witnesses.py'))
cw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cw)

VAR = cw.VAR
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
KEEP = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff，。；：？！、○□「」（）]')


def norm_keep(s):
    """保留標點與 ○□ 佔位符，統一異體；丟掉換行、¶、頁碼標記、空白。"""
    out = []
    for ch in s:
        if KEEP.match(ch):
            out.append(VAR.get(ch, ch) if CJK.match(ch) else ch)
    return ''.join(out)


def load_witness():
    w = {}
    t = open(os.path.join(ROOT, 'vendor', 'KR3ea031_太素', '太素全文.txt'), encoding='utf-8').read()
    w['太素'] = norm_keep(t)
    k = open(os.path.join(ROOT, 'vendor', 'KR3e0085_類經', '類經全文.txt'), encoding='utf-8').read()
    k = re.sub(r'<pb:[^>]*>', '', k)
    w['類經'] = norm_keep(k)
    z = open(os.path.join(ROOT, '底本', '靈樞經_SBCK_底本_句讀.md'), encoding='utf-8').read()
    w['句讀本'] = norm_keep(z)
    return w


PIAN = {int(p['序']): p for p in json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']}

# (代號, 篇序, 爭議字串在底本中的前文8字, 說明)
POINTS = [
    ('A', 2,  '心出於', '本輸：心出於中衝 —— 手少陰心／手厥陰心主之別'),
    ('B', 81, '從虚去實', '癰疽：爲則不足 疑作「寫則不足」'),
    ('C', 21, '腓者腨也', '寒熱病：眥三 疑作「背三」'),
    ('D', 64, '少宫之人', '陰陽二十五人：土形作少宫，火形少徵有無'),
    ('E', 24, '脾心痛', '厥病：脾心痛取然谷太谿（足少陰）之可疑'),
    ('F', 22, '癲疾始生', '癲狂：篇名與病名'),
    ('G', 51, '背腧', '背腧：篇名「腧」作「俞」'),
    ('H', 59, '衛氣', '衛氣失常：篇名存否'),
    ('I', 9,  '中膺', '終始：背腧作背俞'),
    ('J', 1,  '六府有', '九鍼十二原：十二原'),
]


def windows(wit, anchor, half=30):
    """以錨點在前文搜索，回傳命中處前後文。"""
    out = []
    for name, txt in wit.items():
        idx = txt.find(anchor)
        if idx < 0:
            # 退而求其次：取錨點後半段
            idx = txt.find(anchor[2:]) if len(anchor) > 3 else -1
        if idx < 0:
            out.append((name, None))
            continue
        s = max(0, idx - 12)
        out.append((name, txt[s:idx + len(anchor) + half]))
    return out


def base_window(n, anchor, half=30):
    t = PIAN[n]['正規化']
    i = t.find(anchor)
    if i < 0:
        return None
    return t[max(0, i - 12):i + len(anchor) + half]


def main():
    want = set(sys.argv[1:]) or None
    wit = load_witness()
    for code, n, anchor, note in POINTS:
        if want and code not in want:
            continue
        p = PIAN[n]
        print(f"\n{'='*72}\n[{code}] 第{n}篇《{p['篇名_規範']}》｜{note}")
        print(f"  底本：{base_window(n, anchor)}")
        for name, w in windows(wit, anchor):
            print(f"  {name}：{w if w else '（未檢得）'}")


if __name__ == '__main__':
    main()
