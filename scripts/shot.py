#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""閱讀器長截圖：不靠視覺 API，也能證明「這張圖不是空白」。

用法：
  python3 scripts/shot.py <視圖> <輸出.png> [寬度]
  python3 scripts/shot.py jizhu export/reader_zhujia.png 1280

原理（兩趟，都是本機 Chrome）：
  1. 把頁面的 scrollHeight 寫進 document.title，用 --dump-dom 讀出來；
  2. 用該高度當視窗尺寸再截一張；
  3. 用 PIL 檢查「非底色像素比例」與「有內容的行數」，太低就失敗結束（不默默交空白圖）。

前提：reader/ 已由 http 服務供應（預設 127.0.0.1:8080），或設 BASE 環境變數。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READER = os.path.join(ROOT, 'reader')
CHROME_CANDIDATES = [
    os.environ.get('CHROME', ''),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '',
    shutil.which('chromium') or '',
]
MAX_H = 20000


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return ''


def wrapper(view, width):
    src = open(os.path.join(READER, 'index.html'), encoding='utf-8').read()
    inject = ("<script>try{localStorage.setItem('lingshu.reader.v1',"
              "JSON.stringify({agree:1}));}catch(e){}window.__PREVIEW__='" + view + "';</script>\n")
    src = src.replace('<script src="assets/data.js"></script>', inject + '<script src="assets/data.js"></script>')
    tail = ("<script>setTimeout(function(){document.title='H'+"
            "document.documentElement.scrollHeight;},1600);</script>\n</body>")
    src = src.replace('</body>', tail)
    name = '_shot_' + re.sub(r'[^a-z0-9]+', '_', view.lower()) + '.html'
    open(os.path.join(READER, name), 'w', encoding='utf-8').write(src)
    return name


def run(chrome, url, profile, extra, budget=6000):
    cmd = [chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
           '--disable-dev-shm-usage', f'--user-data-dir={profile}',
           f'--virtual-time-budget={budget}'] + extra + [url]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def measure(chrome, url, profile):
    r = run(chrome, url, profile, ['--dump-dom'])
    m = re.search(r'<title>H(\d+)</title>', r.stdout)
    return int(m.group(1)) if m else 0


def check_png(path):
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert('RGB')
    a = np.asarray(im)
    h, w, _ = a.shape
    # 底色取四角多數
    corners = np.concatenate([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]]).reshape(-1, 3)
    bg = np.median(corners, axis=0)
    diff = np.abs(a.astype(int) - bg.astype(int)).sum(axis=2) > 24
    ratio = float(diff.mean())
    rows = int((diff.mean(axis=1) > 0.01).sum())
    return w, h, ratio, rows


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    view, out = sys.argv[1], sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    chrome = find_chrome()
    if not chrome:
        print('找不到 Chrome；設 CHROME=/path/to/chrome'); return 2
    base = os.environ.get('BASE', 'http://127.0.0.1:8080')
    name = wrapper(view, width)
    url = f'{base}/{name}#/{view}'
    profile = tempfile.mkdtemp(prefix='shot-')
    try:
        h = measure(chrome, url, profile)
        if not h:
            print('✗ 量不到頁高（頁面可能沒渲染）'); return 1
        if h > MAX_H:
            print(f'！頁高 {h} 超過上限 {MAX_H}，只截上面 {MAX_H}')
            h = MAX_H
        r = run(chrome, url, profile,
                [f'--window-size={width},{h}', f'--screenshot={os.path.join(ROOT, out)}'])
        if not os.path.exists(os.path.join(ROOT, out)):
            print('✗ 沒有產出檔案'); print(r.stderr[-400:]); return 1
        w, hh, ratio, rows = check_png(os.path.join(ROOT, out))
        size = os.path.getsize(os.path.join(ROOT, out)) / 1024
        tag = '✓' if ratio > 0.01 and rows > 100 else '✗'
        print(f'{tag} {out}：{w}×{hh}px、{size:.0f} KB、非底色 {ratio*100:.1f}%、'
              f'有內容的行 {rows}')
        return 0 if tag == '✓' else 1
    finally:
        shutil.rmtree(profile, ignore_errors=True)
        try:
            os.remove(os.path.join(READER, name))
        except OSError:
            pass


if __name__ == '__main__':
    sys.exit(main())
