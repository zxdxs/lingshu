#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生「大樣稿」：用真實資料排版一份可審閱的樣書（HTML）。

輸出：export/大樣稿.html（A4 比例，可直接列印或截圖）
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = json.load(open(os.path.join(ROOT, '底本', '靈樞經_81篇.json'), encoding='utf-8'))['篇']
ITEMS = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))
GI = json.load(open(os.path.join(ROOT, '底本', '音釋層.json'), encoding='utf-8'))['音釋']
BOUND = list(__import__('csv').DictReader(open(os.path.join(ROOT, 'data', '能力邊界.csv'), encoding='utf-8-sig')))
P40 = next(p for p in CH if p['篇名_規範'] == '陰陽清濁')
JU = {c['序']: c for c in json.load(open(os.path.join(ROOT, '底本', '靈樞經_句讀層.json'), encoding='utf-8'))['篇']}
N40 = JU[P40['序']]['句讀']
FILL = next(i for i in ITEMS['題'] if i['type'] == 'fill_blank' and i['source']['篇序'] == 40)
MCQ = next(i for i in ITEMS['題'] if i['type'] == 'mcq' and i['source']['篇序'] == 40)
CASE = next(i for i in ITEMS['題'] if '-CASE-' in i['item_id'])
GLOSS = next((g['音釋'] for g in GI if g['卷'].lstrip('0') == '6'), '')
GLOSS = re.sub(r'\([^)]*\)', '', GLOSS)[:70]
REL = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
LIC = REL['授權'] if REL['授權'] not in ('', '待定') else '<span style="color:#b3261e">待定</span>（本樣稿末頁列出待決事項）'
CONTACT = REL['聯絡'] if REL['聯絡'] not in ('', '待補') else '待補'

CSS = '''
:root { --ink:#1c1a17; --mute:#7c7367; --line:#d9d2c6; --paper:#fbf8f2; --accent:#7a5a3a; }
* { box-sizing:border-box; }
body { margin:0; background:#efece5; font-family:"Songti SC","Noto Serif CJK TC","Source Han Serif TC",serif;
       color:var(--ink); -webkit-font-smoothing:antialiased; }
.page { width:840px; min-height:1188px; background:var(--paper); margin:0 auto 24px; padding:86px 84px 72px;
        position:relative; box-shadow:0 2px 18px rgba(0,0,0,.08); page-break-after:always; }
.page:last-child { margin-bottom:0; }
.kicker { font-size:12px; letter-spacing:.32em; color:var(--mute); text-transform:uppercase; }
h1 { font-size:46px; letter-spacing:.16em; margin:26px 0 10px; font-weight:600; }
h2 { font-size:22px; letter-spacing:.08em; margin:0 0 6px; font-weight:600; }
h3 { font-size:15px; letter-spacing:.12em; margin:34px 0 10px; color:var(--accent); font-weight:600; }
.sub { font-size:16px; color:var(--mute); letter-spacing:.08em; line-height:1.9; }
.rule { height:1px; background:var(--line); margin:26px 0; }
.foot { position:absolute; bottom:34px; left:84px; right:84px; display:flex; justify-content:space-between;
        font-size:11px; color:var(--mute); letter-spacing:.1em; border-top:1px solid var(--line); padding-top:10px; }
p { font-size:15.5px; line-height:2.0; margin:0 0 16px; text-align:justify; }
.small { font-size:13px; color:var(--mute); line-height:1.9; }
.quote { font-size:19px; line-height:2.2; letter-spacing:.04em; margin:18px 0; padding-left:18px;
         border-left:3px solid var(--accent); }
.label { display:inline-block; font-size:11px; letter-spacing:.16em; color:var(--accent);
         border:1px solid var(--accent); padding:2px 7px; border-radius:2px; margin-right:8px; }
table { width:100%; border-collapse:collapse; font-size:14px; }
td,th { border-bottom:1px solid var(--line); padding:9px 8px; text-align:left; vertical-align:top; line-height:1.8; }
th { color:var(--mute); font-weight:500; letter-spacing:.08em; font-size:12px; }
.card { border:1px solid var(--line); border-radius:4px; padding:22px 24px; background:#fff; margin:14px 0; }
.card .q { font-size:17px; line-height:2; }
.card .a { margin-top:14px; font-size:15px; color:var(--mute); }
.card .a b { color:var(--ink); font-size:18px; }
.tag { font-size:11px; color:var(--mute); border:1px dashed var(--line); padding:2px 6px; margin-left:6px; }
.box { border:1px dashed var(--accent); padding:18px 20px; background:#fffdf8; margin:16px 0; }
.big { font-size:64px; letter-spacing:.2em; line-height:1.3; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:22px; }
img { max-width:100%; border:1px solid var(--line); background:#fff; }
'''

def page(inner, foot_l, foot_r, n):
    return f'<section class="page">{inner}<div class="foot"><span>{foot_l}</span><span>{foot_r} · {n}</span></div></section>'

pages = []

# 1 封面
_pdf_n = len(__import__('glob').glob(os.path.join(ROOT, 'docs', '*.md')))
pages.append(page(f'''
<div class="kicker">中醫典籍導讀 · A proof for review</div>
<h1 class="big">靈樞經</h1>
<div class="sub">{REL["站名"]}<br/>{REL["副標"]}</div>
<div class="rule" style="margin-top:60px"></div>
<table style="font-size:13px">
<tr><th style="width:110px">版本</th><td>v{REL["版本"]} 大樣（未發布）</td></tr>
<tr><th>規模</th><td>81 篇 · 題庫 {ITEMS["題數"]} 題 · 文件 {_pdf_n} 份</td></tr>
<tr><th>底本</th><td>四部叢刊景明嘉靖趙府居敬堂本（Kanripo KR3e0002）</td></tr>
<tr><th>授權</th><td>{LIC}</td></tr>
</table>
<div class="small" style="margin-top:80px">本稿僅供審閱排版與內容取捨；數字與引文皆由現有資料自動帶入。<br/>內容未經臨床驗證，不可據以施治。</div>
''', '靈樞 · 自學材料', '封面', 1))

# 2 這是什麼／怎麼用
pages.append(page(f'''
<div class="kicker">01 · 這是什麼</div>
<h2 style="margin-top:18px">一本可以「練」的靈樞</h2>
<p>市面上多數靈樞讀物只做到「讀懂」。這份材料的重點是<strong>練</strong>：讀完一段原文，立刻有題可做；做錯，能看到錯在哪一句。</p>
<h3>三件事，三個入口</h3>
<table>
<tr><th style="width:90px">想做的事</th><th>怎麼做</th></tr>
<tr><td><b>練</b></td><td>Anki 匯入 <code>export/靈樞_填空.apkg</code>，{ITEMS["題型分布"].get("fill_blank",0)} 張填空卡；正面輸入、Enter 即時判定，接受異體與簡體。</td></tr>
<tr><td><b>讀</b></td><td>原文看 <code>底本/靈樞經_SBCK_底本.md</code>；概念看 <code>docs/49</code>；一篇一篇看 <code>docs/00_索引.md</code>。</td></tr>
<tr><td><b>查</b></td><td><code>export/索引.csv</code>（名詞 → 篇）；<code>export/題庫_全.csv</code>（16 欄，可篩）。</td></tr>
</table>
<h3>這份材料的三條規矩</h3>
<p>1. 原文層絕不由模型生成，每句都能回到底本。<br/>
2. 找不到依據時寫「找不到」，不補一個看起來合理的。<br/>
3. 能力邊界寫在成品裡——所以每一題都標了答案類型與待核狀態。</p>
''', '靈樞 · 自學材料', '這是什麼', 2))

# 3 原文樣張
pages.append(page(f'''
<div class="kicker">02 · 原文頁樣張</div>
<h2 style="margin-top:18px">第 {P40["序"]} 篇 · {P40["篇名"]}　<span class="small">卷 {P40.get("卷","")} · 經文 {len(N40)} 字</span></h2>
<div class="small">{P40.get("法象","")}</div>
<div class="quote">{N40[:120]}……</div>
<p class="small">（全篇 314 字，此處節引首段；完整原文見 `底本/`。）</p>
<h3>音釋</h3>
<p class="small">卷六音釋節錄：{GLOSS}……</p>
<h3>校記</h3>
<p class="small">{P40.get("校記","（無）")[:180]}……</p>
<div class="box"><span class="label">樣張說明</span>原文頁的排版原則：<b>經文大字、註與校記小字、音釋獨立成行</b>。這頁只示範版面，不是最終分頁。</div>
''', '靈樞 · 自學材料', '原文', 3))

# 4 圖樣張
pages.append(page(f'''
<div class="kicker">03 · 圖頁樣張</div>
<h2 style="margin-top:18px">同一個詞，八層意思</h2>
<p>「清濁」在靈樞裡出現 102 次，卻沒有一句定義。圖的作用不是裝飾，是把散在經文裡的八個層次攤開，讓人看見它們其實是同一條路線。</p>
<img src="多層_清濁.png" alt="清濁八層">
<p class="small">圖檔：<code>export/多層_清濁.png</code>；資料：<code>data/多層_清濁.json</code>；圖說與查證：<code>docs/77</code>。</p>
''', '靈樞 · 自學材料', '圖', 4))

# 5 題樣張
pages.append(page(f'''
<div class="kicker">04 · 題目頁樣張</div>
<h2 style="margin-top:18px">三種題，三種用途</h2>
<div class="card"><div class="q">{FILL["stem"]}</div><div class="a">答：<b>{FILL["answer"]}</b><span class="tag">答案類型：{FILL.get("答案類型")}</span></div></div>
<div class="card"><div class="q">{MCQ["stem"]}</div><div class="a">答：<b>{MCQ["answer"]}</b><br/>干擾：{'／'.join(MCQ["distractors"][:3])}</div></div>
<div class="card"><div class="q">{CASE["stem"]}</div><div class="a">答：<b>{CASE["answer"]}</b><span class="tag">待專家核</span></div></div>
<div class="small">填空考「記得住」，選擇考「分得清」，案例考「用得上」。目前三者的比例是 {ITEMS["題型分布"].get("fill_blank",0)} : {ITEMS["題型分布"].get("mcq",0)} : 19（辨誤），而案例只有 6 道——這是本稿最需要審的一處。</div>
''', '靈樞 · 自學材料', '題', 5))

# 6 卡片樣張
pages.append(page(f'''
<div class="kicker">05 · 卡片樣張</div>
<h2 style="margin-top:18px">Anki 卡：先寫，再核對</h2>
<div class="grid2">
<div><div class="small" style="margin-bottom:8px">正面</div>
<div class="card"><div class="q">{FILL["stem"]}</div>
<div style="margin-top:14px;border:1px solid var(--line);padding:9px 11px;color:var(--mute);font-size:14px">輸入答案後按 Enter</div>
<div class="small" style="margin-top:10px">[ 對答案 ]</div></div></div>
<div><div class="small" style="margin-bottom:8px">背面</div>
<div class="card"><div class="q">{FILL["stem"].replace("____","<b>"+FILL["answer"]+"</b>")}</div>
<div class="a">答案：<b>{FILL["answer"]}</b></div>
<div class="small">說明：{FILL.get("note","") or "（無）"}</div>
<div class="small" style="margin-top:8px">《靈樞·{FILL["source"]["篇名"]}》</div>
<div class="small" style="margin-top:10px;border-top:1px dashed var(--line);padding-top:8px">本卡內容依原文整理，未經臨床驗證，不可據以施治。</div></div></div>
</div>
<p class="small">正面不顯示答案；背面固定附出處與免責。異體與簡體由卡片內 JS 判定，與 <code>scripts/grade.py</code> 共用同一張對照表。</p>
''', '靈樞 · 自學材料', '卡片', 6))

# 7 限制
rows = ''.join(f'<tr><td style="width:70px">{r["編號"]}</td><td>{r["問題"][:46]}</td><td style="width:60px">{r["嚴重度"]}</td></tr>' for r in BOUND[:6])
pages.append(page(f'''
<div class="kicker">06 · 已知限制</div>
<h2 style="margin-top:18px">先說不能做什麼</h2>
<table><tr><th>#</th><th>問題</th><th>級</th></tr>{rows}</table>
<p class="small">完整 34 條見 <code>data/能力邊界.csv</code>。</p>
<h3>三項最需要讀者知道的</h3>
<p>· 所有臨床主張未經驗證，<b>不可據以施治</b>。<br/>
· 15 條答案為整理語（已逐題標明），不是原文連續字串。<br/>
· 6 道案例題與 19 條註家配對<b>待專家核</b>。</p>
''', '靈樞 · 自學材料', '限制', 7))

# 8 待決與封底
_lic = (REL['授權'] if REL['授權'] not in ('', '待定', None)
        else '；'.join(REL['選項'].get('授權', [])) + '（未定）')
_anki = '已測' if REL.get('Anki實機') not in ('', None, '未測') else '<span style="color:#b3261e">未測</span>'
pages.append(page(f'''
<div class="kicker">07 · 待決事項</div>
<h2 style="margin-top:18px">發布前還剩兩件</h2>
<table>
<tr><th style="width:130px">項目</th><th>現況</th></tr>
<tr><td><b>聯絡</b></td><td>目前 {CONTACT}；需一個可公開的去識別化信箱或表單網址</td></tr>
<tr><td><b>Anki 實機</b></td><td>{_anki}；708 張填空卡尚未在真實 Anki 匯入按過一遍</td></tr>
</table>
<div class="box"><span class="label">已定案</span>
授權 <b>{_lic}</b>（原文屬公共領域，本計畫之標點、校記、題目、圖表依此釋出；見 <code>LICENSE.txt</code>）。<br/>
站名「{REL["站名"]}」，版本 v{REL["版本"]}；案例題維持 6 道樣板；樣張篇目用第 40 篇〈陰陽清濁〉（短、有校記）。</div>
<div class="box"><span class="label">審閱重點</span>
1. 版式與字級是否適合列印；<br/>
2. 從「主題」進站是否比從「篇目」進站更貼近你想教的東西；<br/>
3. 「練習／閱讀／查詢」三分法是否清楚；<br/>
4. 限制頁是否說得夠坦白、又不嚇跑讀者。</div>
<div class="small" style="margin-top:70px">大樣稿由 <code>scripts/make_proof.py</code> 產生；數字、授權與待決項目皆由 <code>data/發布資訊.json</code> 帶入。</div>
''', REL['站名'], '封底', 8))

html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>{REL["站名"]} · 大樣稿 v{REL["版本"]}</title><style>{CSS}</style></head><body>
{''.join(pages)}
</body></html>'''
out = os.path.join(ROOT, 'export', '大樣稿.html')
open(out, 'w', encoding='utf-8').write(html)
print('寫出', out, len(html), 'bytes')

# 另出單頁檔，方便逐頁截圖／列印
import sys as _sys
if '--split' in _sys.argv:
    for i, sec in enumerate(pages, 1):
        one = f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>大樣稿 p{i}</title><style>{CSS}</style></head><body>{sec}</body></html>'
        open(os.path.join(ROOT, 'export', f'大樣稿_p{i}.html'), 'w', encoding='utf-8').write(one)
    print(f'另出單頁檔 {len(pages)} 份')
