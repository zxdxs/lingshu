#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真瀏覽器冒煙測試：用 headless Chrome 跑閱讀器的每一條路由。

為什麼要有這一支：`scripts/check_reader.js` 用的是自製 DOM 樁，能抓 undefined／缺節點／
缺 class，但抓不到「樣式沒生效」「事件綁錯」「localStorage 沒寫進去」這類只有真瀏覽器
才會現形的問題。這一支把 Chrome 當使用者用：真的載入頁面、真的點按鈕、真的切路由。

用法：
  python3 scripts/smoke_browser.py            # 跑全部路由
  python3 scripts/smoke_browser.py --keep     # 留下暫存頁面以便手動開

需求：本機有 Chrome（預設找 /Applications/Google Chrome.app），或設 CHROME 環境變數。
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READER = os.path.join(ROOT, 'reader')
REL = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
STRIPE = REL['安全提醒短']

CHROME_CANDIDATES = [
    os.environ.get('CHROME', ''),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '',
    shutil.which('chromium') or '',
]

# 每一條路由至少要看到什麼（key 為元素選擇器計數，值為下限）
ROUTES = {
    'home': {'hero': 1, 'card': 5, 'grid': 1, 'alert': 1},
    'themes': {'card': 3, 'tiao': 5},
    'read': {'list': 1, 'tiao': 5},
    'read?seq=40': {'orig': 1},
    'items': {'card': 5},
    'items?seq=40': {'card': 3},
    'concept': {'card': 3},
    'suwen': {'card': 5, 'quote': 1},
    'law': {'card': 3, 'quote': 3},
    'binghou': {'card': 5, 'quote': 5},
    'search': {'row': 1},
    'variant': {'card': 6},
    'path': {'card': 3, 'table-wrap': 3},
    'module': {'fold': 8, 'table-wrap': 5},
    'govern': {'card': 4, 'law-item': 8, 'table-wrap': 3},
    'recite': {'card': 2, 'recite-line': 10, 'ruby': 10},
    'jizhu': {'card': 5, 'quote': 3, 'zj-note': 3, 'zj-case': 5},
    'jiugong': {'card': 4, 'quote': 3},
    'meridian': {'card': 5, 'mercard': 12},
    'meridian?tab=bie': {'card': 5, 'mercard': 6},
    'meridian?tab=jin': {'mercard': 12},
    'meridian?tab=luo': {'card': 1},
    'meridian?tab=shui': {'card': 2},
    'meridian?tab=shu': {'card': 12},
    'meridian?tab=yuan': {'card': 2, 'quote': 4},
    'meridian?tab=yw': {'card': 5, 'quote': 8},
    'prep': {'card': 2},
    'method': {},
    'collation': {},
    'limits': {'alert': 1},
    'mine': {},
    'about': {},
    'contact': {'card': 3},
}

HARNESS = '''<div id="smoke" style="display:none"></div>
<script>
window.__err = [];
window.addEventListener('error', function (e) { window.__err.push(String(e.message)); });
window.addEventListener('unhandledrejection', function (e) { window.__err.push('reject:' + e.reason); });
try { localStorage.setItem('lingshu.reader.v1', JSON.stringify({ agree: 1 })); } catch (e) {}
setTimeout(function () {
  var q = function (s) { return document.querySelectorAll(s).length; };
  var rep = { hash: location.hash, errors: window.__err,
    h1: (document.querySelector('#view h1') || {}).textContent || '',
    hero: q('.hero'), card: q('.card'), grid: q('.grid'), alert: q('.alert'),
    row: q('.row'), tiao: q('.tiao'), orig: q('.orig'), list: q('.list'), quote: q('.quote'),
    mercard: q('.mer-card'),
    'zj-note': q('.zj-note'), 'zj-case': q('.zj-case'), 'table-wrap': q('.table-wrap'), 'fold': q('details.fold'),
    'law-item': q('.law-item'), 'recite-line': q('.recite-line'), 'ruby': q('ruby'),
    stripe: (document.querySelector('#stripe') || {}).textContent || '',
    nav: q('#nav a'), foot: q('#footLinks a'),
    routes: window.__ROUTES || [],
    links: Array.prototype.map.call(document.querySelectorAll('a[href^="#/"]'), function (a) { return a.getAttribute('href'); }) };
  document.getElementById('smoke').textContent = 'SMOKE=' + JSON.stringify(rep);
}, 900);
</script>
'''

SHORTCUT = '''<div id="smoke" style="display:none"></div>
<script>
window.__err = [];
window.addEventListener('error', function (e) { window.__err.push(String(e.message)); });
try { localStorage.setItem('lingshu.reader.v1', JSON.stringify({ agree: 1 })); } catch (e) {}
setTimeout(function () {
  var ev = new KeyboardEvent('keydown', { key: '/', bubbles: true });
  document.body.dispatchEvent(ev);
  setTimeout(function () {
    var rep = { hash: location.hash, errors: window.__err,
                input: !!document.querySelector('input[type=search]') };
    document.getElementById('smoke').textContent = 'SMOKE=' + JSON.stringify(rep);
  }, 300);
}, 700);
</script>
'''

INTERACT = '''<div id="smoke" style="display:none"></div>
<script>
window.__err = [];
window.addEventListener('error', function (e) { window.__err.push(String(e.message)); });
try { localStorage.setItem('lingshu.reader.v1', JSON.stringify({ agree: 1 })); } catch (e) {}
setTimeout(function () {
  var rep = { steps: [], errors: window.__err };
  var cards = document.querySelectorAll('#view .card'), fill = null;
  for (var i = 0; i < cards.length && !fill; i++) {
    var bs = cards[i].querySelectorAll('button');
    for (var j = 0; j < bs.length; j++) if (bs[j].textContent === '顯示答案') { fill = { c: cards[i], b: bs[j] }; break; }
  }
  if (fill) {
    fill.b.click();
    var ans = fill.c.querySelector('.ans');
    rep.steps.push({ s: 'reveal', shown: !!(ans && ans.style.display !== 'none'),
                     len: ans ? ans.textContent.trim().length : 0 });
    var bs2 = fill.c.querySelectorAll('button');
    for (var k = 0; k < bs2.length; k++) if (bs2[k].textContent === '答對') { bs2[k].click(); rep.steps.push({ s: 'mark', btn: bs2[k].textContent }); }
  }
  var opt = document.querySelector('#view .opt');
  if (opt) {
    opt.click();
    rep.steps.push({ s: 'option', right: document.querySelectorAll('#view .opt.right').length,
                     wrong: document.querySelectorAll('#view .opt.wrong').length, disabled: opt.disabled });
  }
  try { rep.log = Object.keys((JSON.parse(localStorage.getItem('lingshu.reader.v1')) || {}).log || {}).length; }
  catch (e) { rep.log = -1; }
  location.hash = '#/limits';
  setTimeout(function () {
    rep.steps.push({ s: 'route', h1: (document.querySelector('#view h1') || {}).textContent || '',
                     alert: document.querySelectorAll('#view .alert').length });
    rep.errors = window.__err;
    document.getElementById('smoke').textContent = 'SMOKE=' + JSON.stringify(rep);
  }, 350);
}, 800);
</script>
'''


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return ''


def dump(chrome, url, profile, budget=5000):
    cmd = [chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
           f'--user-data-dir={profile}', f'--virtual-time-budget={budget}', '--dump-dom', url]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
    except subprocess.TimeoutExpired:
        return ''
    i = out.find('SMOKE=')
    if i < 0:
        return ''
    j = out.find('</div>', i)
    try:
        return json.loads(out[i + 6:j].strip())
    except Exception:
        return ''


def page(seed=True, interact=False, shortcut=False):
    src = open(os.path.join(READER, 'index.html'), encoding='utf-8').read()
    inject = SHORTCUT if shortcut else (INTERACT if interact else (HARNESS if seed else ''))
    if inject:
        src = src.replace('<script src="assets/data.js"></script>',
                          inject + '<script src="assets/data.js"></script>')
    name = ('_smoke_shortcut.html' if shortcut else
            '_smoke_interact.html' if interact else '_smoke_route.html')
    p = os.path.join(READER, name)
    open(p, 'w', encoding='utf-8').write(src)
    return os.path.basename(p)


def main():
    chrome = find_chrome()
    if not chrome:
        print('找不到 Chrome；設 CHROME=/path/to/chrome 後重跑'); return 2
    tmp = tempfile.mkdtemp(prefix='lingshu-smoke-')
    base = 'file://' + os.path.join(READER, '')
    route_page = page(seed=True)
    fails = []

    print(f'瀏覽器：{chrome.split("/")[-1]}　（{len(ROUTES)} 條路由 + 3 個情境）')
    seen, routes_known = {}, []
    for route, need in ROUTES.items():
        rep = dump(chrome, base + route_page + '#/' + route, os.path.join(tmp, 'p' + str(abs(hash(route)) % 99999)))
        if not rep:   # Chrome 偶爾起不來；給一次較長的機會，不讓偶發失敗冒充真錯
            rep = dump(chrome, base + route_page + '#/' + route,
                       os.path.join(tmp, 'r' + str(abs(hash(route)) % 99999)), 9000)
        if not rep:
            fails.append(f'{route}: 沒拿到 SMOKE 回報（頁面可能沒載入）'); continue
        for href in (rep.get('links') or []):
            seen.setdefault(href, route)
        routes_known = rep.get('routes') or routes_known
        bad = []
        if rep['errors']:
            bad.append('JS 錯誤 ' + '; '.join(rep['errors']))
        if not rep['h1']:
            bad.append('沒有 h1')
        if rep['stripe'] != STRIPE:
            bad.append(f'頂欄不是安全提醒（{rep["stripe"][:20]}）')
        if rep['nav'] != 24 or rep['foot'] != 5:
            bad.append(f'導覽 {rep["nav"]}／頁腳 {rep["foot"]}（應 24／5）')
        for k, v in need.items():
            if rep.get(k, 0) < v:
                bad.append(f'.{k}={rep.get(k, 0)}（至少 {v}）')
        if bad:
            fails.append(f'{route}: ' + '；'.join(bad))
        else:
            print(f'  ✓ {route:<14} h1={rep["h1"][:12]:<12} card={rep["card"]:<3} alert={rep["alert"]}')

    # 死連結：每個頁面的 #/... 連結都要指向存在的視圖（刪頁面時最容易漏掉的一步）
    dead = []
    for href, where in seen.items():
        name = href.split('?')[0].replace('#/', '').strip('/')
        if name and name not in routes_known:
            dead.append(f'{href}（出現在 {where}）')
    if dead:
        fails.append('死連結：' + '、'.join(dead))
    else:
        print(f'  ✓ links          {len(seen)} 個站內連結，全部指向存在的視圖')

    # 情境三：按 / 應跳到搜尋頁並聚焦輸入框
    sc = dump(chrome, base + page(shortcut=True) + '#/home', os.path.join(tmp, 'sc'), 4000)
    if sc and sc.get('hash', '').startswith('#/search') and sc.get('input'):
        print('  ✓ shortcut       按 / 跳到搜尋並聚焦輸入框')
    else:
        fails.append('shortcut: ' + json.dumps(sc, ensure_ascii=False)[:200])

    # 情境一：未同意 → 必須停在確認頁
    gate = dump(chrome, base + 'index.html#/home', os.path.join(tmp, 'gate'))
    gate_src = subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu',
                               '--user-data-dir=' + os.path.join(tmp, 'gate2'),
                               '--virtual-time-budget=3000', '--dump-dom', base + 'index.html#/home'],
                              capture_output=True, text=True, timeout=90).stdout
    if '使用前確認' in gate_src and STRIPE.replace('｜', '')[:8] in gate_src:
        print('  ✓ gate           未同意時停在確認頁，且看得到安全提醒')
    else:
        fails.append('gate: 未同意時沒有停在確認頁（或確認頁沒有安全提醒）')

    # 情境二：點按鈕、作答、切路由
    inter = dump(chrome, base + page(interact=True) + '#/items?seq=40', os.path.join(tmp, 'inter'), 7000)
    if not inter:
        fails.append('interact: 沒拿到回報')
    else:
        st = {x.get('s'): x for x in inter.get('steps', [])}
        ok = (st.get('reveal', {}).get('shown') and st.get('reveal', {}).get('len', 0) > 0
              and st.get('mark', {}).get('btn', '').startswith('答對')
              and (st.get('option', {}).get('right', 0) + st.get('option', {}).get('wrong', 0)) >= 1
              and st.get('route', {}).get('h1') == '已知限制'
              and not inter.get('errors') and inter.get('log', 0) >= 1)
        if ok:
            print(f'  ✓ interact       顯示答案／答對／選項判定／切路由都動作（紀錄 {inter.get("log")} 筆）')
        else:
            fails.append('interact: ' + json.dumps(inter, ensure_ascii=False)[:400])

    if '--keep' not in sys.argv:
        for n in (route_page, '_smoke_interact.html', '_smoke_shortcut.html'):
            try: os.remove(os.path.join(READER, n))
            except OSError: pass
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        for f in fails:
            print('  ✗ ' + f)
        print(f'結論：{len(fails)} 項失敗')
        return 1
    print(f'結論：{len(ROUTES)} 條路由與 3 個情境全部通過')
    return 0


if __name__ == '__main__':
    sys.exit(main())
