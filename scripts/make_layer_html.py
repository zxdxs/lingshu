#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由 JSON 規格產生「同名多層」資訊圖的 HTML。

用法：python3 scripts/make_layer_html.py data/多層_血.json export/多層_血.html
再由 vision_html_screenshot 拍成 PNG。

規格格式：
{
  "標題": "同一個字，多層意思",
  "副標": "《靈樞》概念的多層結構　｜　縱向虛線＝同一個字　每一橫層＝一個語境",
  "組": [
    {"字": "血", "註": "…", "層": [{"語境":"生成","式":"…","出處":"決氣"}, …]}
  ],
  "腳註": ["…", "…"]
}
"""
import json, sys, html, os


def esc(s):
    return html.escape(str(s))


TEMPLATE = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>{title}</title>
<style>
  :root{{--ink:#1a1a1a;--mute:#8a8a8a;--line:#d8d4cc;--bg:#fbfaf7;--accent:#7a5c3e;}}
  *{{box-sizing:border-box;}}
  body{{margin:0;background:var(--bg);color:var(--ink);
       font-family:"Songti SC","PingFang SC","Noto Serif CJK TC",serif;
       padding:44px 52px 56px;}}
  h1{{font-size:26px;font-weight:600;margin:0 0 6px;letter-spacing:2px;}}
  .sub{{color:var(--mute);font-size:13px;margin-bottom:34px;letter-spacing:.5px;}}
  .panel{{margin-bottom:46px;}}
  .panel h2{{font-size:18px;margin:0 0 4px;font-weight:600;}}
  .panel .note{{font-size:12px;color:var(--mute);margin-bottom:16px;line-height:1.7;}}
  .row{{display:grid;grid-template-columns:160px 92px 1fr 200px;align-items:center;
       border-top:1px solid var(--line);min-height:54px;}}
  .row:last-child{{border-bottom:1px solid var(--line);}}
  .ctx{{font-size:13px;color:var(--mute);letter-spacing:1px;}}
  .word{{position:relative;font-size:22px;letter-spacing:4px;text-align:center;}}
  .word::before{{content:"";position:absolute;left:50%;top:-28px;bottom:-28px;
       border-left:1px dotted var(--accent);opacity:.45;}}
  .word span{{position:relative;background:var(--bg);padding:2px 6px;}}
  .eq{{font-size:15px;line-height:1.55;letter-spacing:.6px;padding-right:18px;}}
  .src{{font-size:12px;color:var(--mute);text-align:right;letter-spacing:.5px;}}
  .tag{{display:inline-block;font-size:11px;border:1px solid var(--line);border-radius:3px;
       padding:1px 5px;color:var(--mute);margin-left:8px;vertical-align:2px;}}
  .foot{{font-size:12px;color:var(--mute);line-height:1.9;border-top:1px solid var(--line);padding-top:14px;}}
  .ok{{color:var(--accent);}}
</style></head><body>
<h1>{title}</h1>
<div class="sub">{sub}</div>
{panels}
<div class="foot">{foot}</div>
</body></html>
"""


def main():
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    out = sys.argv[2]
    panels = []
    for g in spec['組']:
        rows = []
        for L in g['層']:
            rows.append(
                f'  <div class="row"><div class="ctx">{esc(L["語境"])}</div>'
                f'<div class="word"><span>{esc(g["字"])}</span></div>'
                f'<div class="eq">{esc(L["式"])}</div>'
                f'<div class="src">{esc(L["出處"])}</div></div>')
        panels.append(
            f'<div class="panel">\n  <h2>{esc(g["字"])} <span class="tag">{len(g["層"])} 層</span></h2>\n'
            f'  <div class="note">{esc(g.get("註",""))}</div>\n' + '\n'.join(rows) + '\n</div>')
    foot = '<br>\n'.join(f'<span class="ok">．</span> {esc(x)}' for x in spec.get('腳註', []))
    htmls = TEMPLATE.format(title=esc(spec.get('標題', '同一個字，多層意思')),
                            sub=esc(spec.get('副標', '')),
                            panels='\n'.join(panels), foot=foot)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'w', encoding='utf-8').write(htmls)
    total = sum(len(g['層']) for g in spec['組'])
    print(f'{out}：{len(spec["組"])} 組、{total} 層')


if __name__ == '__main__':
    main()
