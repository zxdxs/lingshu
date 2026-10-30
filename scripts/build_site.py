#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""組出可發布的靜態站：site/（給 GitHub Pages 用的內容）。

做法：把 reader/ 的 index.html 與 assets 複製到 site/，另附授權、交付清單、.nojekyll。
不重新編譯、不改任何檔案——site/ 是產物，內容與 reader/ 相同，方便比對。

用法：python3 scripts/build_site.py
之後：cd site && python3 -m http.server 8081 --bind 127.0.0.1   # 本機預覽
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(os.path.join(SITE, 'assets'))
    shutil.copy2(os.path.join(ROOT, 'reader', 'index.html'), os.path.join(SITE, 'index.html'))
    src_assets = os.path.join(ROOT, 'reader', 'assets')
    for name in sorted(os.listdir(src_assets)):
        p = os.path.join(src_assets, name)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(SITE, 'assets', name))
    for extra in ('LICENSE.txt',):
        p = os.path.join(ROOT, extra)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(SITE, extra))
    # GitHub 會用 Jekyll 處理，這裡不需要；.nojekyll 讓底線開頭的檔案也照原樣送出
    open(os.path.join(SITE, '.nojekyll'), 'w').close()

    # 交付清單：放在站上，讀者直接看得到
    p = os.path.join(ROOT, 'export', '交付清單.md')
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SITE, '交付清單.md'))

    # 404 一律回首頁（本站用 hash 路由，深層路徑不該存在）
    open(os.path.join(SITE, '404.html'), 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0; url=./">'
        '<title>回首頁</title><p>這個路徑不存在，正在回首頁……</p>')

    rel = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fs in os.walk(SITE) for f in fs)
    files = sum(len(fs) for _dp, _d, fs in os.walk(SITE))
    print(f'站台：{SITE}')
    print(f'  檔案 {files} 個、{total/1e6:.2f} MB')
    print(f'  站名：{rel["站名"]}　v{rel["版本"]}　授權：{rel["授權"]}')
    print('  入口：site/index.html（開起來就是首頁）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
