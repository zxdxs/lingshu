#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 SBCK 轉錄抽取《素問》經文（去王冰注、新校正、頁碼、卷末音釋），供「靈樞與素問的異同」對照。

為什麼要另建一份：本站主體只有《靈樞》，素問僅作對照（見 docs/117）。但對照不能靠印象，
所以把素問經文抽乾淨、算過字數，再讓靈樞的句子去比對——重出的段落是算出來的，不是舉例舉出來的。

已知限制：SBCK 轉錄有 3 篇（第 26、46、50）缺篇名行，該處只記到卷，不硬猜篇。
輸出：底本/素問_經文.json

用法：python3 scripts/build_suwen.py
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, 'vendor', 'KR3e0001_素問')
CN = '一二三四五六七八九十'


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.index(s[1]) + 1
    if '十' in s:
        a, b = s.split('十')
        return (CN.index(a) + 1) * 10 if b == '' else (CN.index(a) + 1) * 10 + CN.index(b) + 1
    return CN.index(s) + 1


def clean(raw):
    """去頁碼、注、卷首目錄、卷末音釋；回傳（經文行, 篇名行位置）。"""
    t = re.sub(r'<pb:[^>]*>', '', raw)
    t = '\n'.join(l for l in t.split('\n') if not l.startswith('#'))
    t = re.sub(r'\([^)]*\)', '', t).replace('¶', '')
    lines = [l.strip('　 ').strip() for l in t.split('\n')]
    keep, body_started, cut = [], False, False
    for l in lines:
        if '重廣' in l and '卷' in l:          # 卷首／卷末題名
            if body_started:
                cut = True                     # 卷末之後是音釋，整段丟
            continue
        if cut or '啓玄子次注' in l:
            continue
        if '\u3000' in l and '篇第' not in l:  # 卷首目錄行（多篇名以全角空格分隔）
            continue
        if '篇第' in l and len(l) < 20:
            body_started = True
        keep.append(l)
    return '\n'.join(keep)


def main():
    juan_list = []
    for path in sorted(glob.glob(os.path.join(VENDOR, 'KR3e0001_0*.txt'))):
        raw = open(path, encoding='utf-8').read()
        juan = int(re.search(r'#\+PROPERTY: JUAN (\d+)', raw).group(1))
        if juan == 0:
            continue                            # 000 為序文，不算經文
        body = clean(raw)
        heads = []
        for m in re.finditer(r'(?m)^([\u3400-\u4dbf\u4e00-\u9fff]{2,14}?篇)第([一二三四五六七八九十]+)$', body):
            heads.append({'名': m.group(1), '序': cn2int(m.group(2)), '起': m.start()})
        juan_list.append({'卷': juan, '文本': body, '篇': heads})
    juan_list.sort(key=lambda x: x['卷'])

    names = [{'序': h['序'], '名': h['名'], '卷': j['卷']} for j in juan_list for h in j['篇']]
    names.sort(key=lambda x: x['序'])
    seen, uniq = set(), []
    for n in names:
        if n['序'] in seen:
            continue
        seen.add(n['序'])
        uniq.append(n)

    text = '\n'.join(j['文本'] for j in juan_list)
    chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    missing = [i for i in range(1, 82) if i not in seen]
    out = {'卷': juan_list, '篇名': uniq,
           '統計': {'卷數': len(juan_list), '篇名數': len(uniq), '經文字': chars,
                    '缺篇名': missing}}
    json.dump(out, open(os.path.join(ROOT, '底本', '素問_經文.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print(f"素問：{len(juan_list)} 卷、篇名 {len(uniq)} 個（缺 {missing}）、經文 {chars:,} 字")


if __name__ == '__main__':
    main()
