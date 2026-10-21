#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剩餘篇章彈性拆解（四）：上膈(68)、憂恚無言(69)、寒熱(70)

三篇都是短篇「病—機—治」結構，每篇做一張卡。
輸出：data/模組_R4.json、docs/31_短篇三則.md
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
def T(n): return J[n]['句讀'].replace('\n', '')
PUNC = '，。、；：？！「」《》'
def sp(x): return ''.join(c for c in x if c not in PUNC and not c.isspace())

CARDS = [
 dict(篇序=68, 篇名='上膈', 病='膈證',
      別='氣為上膈：食飲入而還出；蟲為下膈：食晬時乃出',
      機='喜怒不適、食飲不節、寒溫不時 → 寒汁流於腸中 → 蟲寒 → 積聚守於下管 → 衛氣不營 → 邪居 → 癰成 → 下管約',
      治='微按其癰，視氣所行，先淺刺其傍，稍內益深，還而刺之，毋過三行；已刺必熨，令熱入中；後以鹹苦化穀',
      禁='毋過三行（不可過度）'),
 dict(篇序=69, 篇名='憂恚無言', 病='卒然無音',
      別='咽喉＝水穀之道；喉嚨＝氣之上下；會厭＝音聲之戶；口唇＝音聲之扇；舌＝音聲之機；懸雍垂＝音聲之關；頏顙＝分氣所泄；橫骨＝神氣所使，主發舌',
      機='寒氣客於厭，則厭不能發，發不能下，開闔不致，故無音',
      治='寫足少陰血脈（濁氣乃辟）；取天突（會厭之脈上絡任脈）',
      禁='—'),
 dict(篇序=70, 篇名='寒熱', 病='寒熱瘰癧（鼠瘻）',
      別='在頸腋者，皆鼠瘻寒熱之毒氣，留於脈而不去',
      機='本在藏，末上出於頸腋之間；浮於脈中而未內著肌肉、外為膿血者，易去',
      治='從其本引其末；審按其道以予之，徐往徐來以去之；小如麥者，一刺知，三刺而已',
      禁='反目視之，赤脈上下貫瞳子：見一脈一歲死，二脈二歲死，三脈三歲死；不貫瞳子者可治'),
]
# 卡片為編者整理，原文見底本，不做逐字斷言

json.dump({'模組': '短篇三則', '卡': CARDS},
          open(os.path.join(ROOT, 'data', '模組_R4.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, 'docs', '31_短篇三則.md'), 'w', encoding='utf-8') as f:
    f.write('# 短篇三則：上膈、憂恚無言、寒熱\n\n')
    f.write('> 三篇都是「病—機—治」的短篇，各做一張卡。\n\n---\n\n')
    for c in CARDS:
        f.write(f"## {c['病']}（{c['篇名']}）\n\n")
        f.write(f"- **辨析**：{c['別']}\n")
        f.write(f"- **病機**：{c['機']}\n")
        f.write(f"- **治法**：{c['治']}\n")
        if c['禁'] != '—':
            f.write(f"- **禁忌／預後**：{c['禁']}\n")
        f.write('\n')
    f.write('---\n\n## 一點說明\n\n')
    f.write('這三篇字數都不到 250，但結構完整。它們證明：**短不等於沒價值**——'
            '「病—機—治」三欄就足以構成一個可教學的單元。\n')

print('卡片', len(CARDS))
for c in CARDS: print('  ', c['病'])
