#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包發布：dist/lingshu-vX.Y.zip + manifest（含計數與 sha256）。

用法：python3 scripts/package_release.py [版本號]
"""
import hashlib, json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else '1.0.0'
OUT = os.path.join(ROOT, 'dist')
INCLUDE = ['README.md', 'CHANGELOG.md', '底本', 'data', 'docs', 'scripts', 'export', 'reader', 'vendor/README.md']
SKIP_DIRS = {'__pycache__', 'pylib', 'anki模板'.replace('anki模板', '__none__')}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def files():
    for item in INCLUDE:
        p = os.path.join(ROOT, item)
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for dirpath, dirnames, names in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for n in names:
                    if n.endswith(('.pyc',)) or n.startswith('.'):
                        continue
                    yield os.path.join(dirpath, n)


def main():
    os.makedirs(OUT, exist_ok=True)
    items = json.load(open(os.path.join(ROOT, 'data', '題庫_示例.json'), encoding='utf-8'))
    rel = json.load(open(os.path.join(ROOT, 'data', '發布資訊.json'), encoding='utf-8'))
    undecided = [k for k in rel.get('必要', []) if rel.get(k) in ('', None, '待定', '待補', '未測')]
    entries, total = [], 0
    zp = os.path.join(OUT, f'lingshu-v{VERSION}.zip')
    lic = os.path.join(ROOT, 'LICENSE.txt')
    lic_ok = os.path.exists(lic) and rel.get('授權') not in ('', None, '待定')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files():
            rel_p = os.path.relpath(p, ROOT)
            z.write(p, rel_p)
            entries.append({'path': rel_p, 'sha256': sha(p), 'bytes': os.path.getsize(p)})
            total += os.path.getsize(p)
        if lic_ok:
            z.write(lic, 'LICENSE.txt')
            entries.append({'path': 'LICENSE.txt', 'sha256': sha(lic), 'bytes': os.path.getsize(lic)})
            total += os.path.getsize(lic)
    manifest = {
        '版本': VERSION,
        '站名': rel['站名'],
        '授權': rel['授權'],
        '聯絡': rel['聯絡'],
        '發布待決': undecided,
        '題數': items['題數'],
        '題型分布': items['題型分布'],
        '檔案數': len(entries),
        '原始大小': total,
        '打包大小': os.path.getsize(zp),
        'zip_sha256': sha(zp),
        '檔案': entries,
    }
    json.dump(manifest, open(os.path.join(OUT, f'manifest-v{VERSION}.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'打包 {zp}：{len(entries)} 檔、{total/1e6:.1f} MB → {manifest["打包大小"]/1e6:.1f} MB')
    print(f'  LICENSE.txt：{"已收錄（授權 " + str(rel.get("授權")) + "）" if lic_ok else "未收錄（授權未定或檔案不存在）"}')
    if undecided:
        print(f'  ⚠ 發布待決 {len(undecided)} 項：{"、".join(undecided)}　→ 目前僅可作審閱稿')
    return 0


if __name__ == '__main__':
    sys.exit(main())
