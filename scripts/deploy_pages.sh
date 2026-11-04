#!/usr/bin/env bash
# 把 site/ 發到 GitHub Pages（gh-pages 分支）。
#
# 用法：
#   scripts/deploy_pages.sh git@github.com:<user>/<repo>.git
#
# 前提：repo 已在 GitHub 建好（空 repo 即可）、本機 ssh key 已加到 GitHub。
# 這個腳本會：重建 site/ → 用暫存 worktree 建／更新 gh-pages → push → 收掉 worktree。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${1:-}"
BRANCH="gh-pages"
WT="$ROOT/.gh-pages-worktree"

if [ -z "$REMOTE" ]; then
  echo "用法：scripts/deploy_pages.sh git@github.com:<user>/<repo>.git" >&2
  exit 2
fi

cd "$ROOT"
python3 scripts/build_site.py

# 主分支要先有 commit 才能 worktree；沒有就提醒
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "主分支還沒有 commit，先 commit 再部署" >&2
  exit 2
fi

# 遠端若尚未設定，補上
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REMOTE"
else
  git remote set-url origin "$REMOTE"
fi

# 清掉舊 worktree（含 git 的登記；否則本地分支會被佔住而無法 checkout -B）
git worktree prune
if [ -d "$WT" ]; then
  git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  git worktree prune
fi

# 取遠端 gh-pages（有就接續，沒有就開 orphan）
if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git fetch origin "$BRANCH"
  git worktree add --detach "$WT" FETCH_HEAD
  git branch -D "$BRANCH" >/dev/null 2>&1 || true
  git -C "$WT" checkout -B "$BRANCH"
else
  git worktree add --detach "$WT" HEAD
  git -C "$WT" checkout --orphan "$BRANCH"
  git -C "$WT" rm -rf . >/dev/null 2>&1 || true
fi

# 只留 site/ 的內容
find "$WT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$ROOT/site/." "$WT/"

git -C "$WT" add -A
if git -C "$WT" diff --cached --quiet; then
  echo "gh-pages 內容沒有變，略過 commit"
else
  git -C "$WT" -c user.name="${GIT_AUTHOR_NAME:-lingshu}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-lingshu@localhost}" \
      commit -m "site: 發布 $(date +%Y-%m-%d\ %H:%M)（由 scripts/deploy_pages.sh 產生）"
fi

git -C "$WT" push origin "$BRANCH"
git worktree remove --force "$WT"

SLUG="${REMOTE#git@github.com:}"
SLUG="${SLUG%.git}"
OWNER="${SLUG%%/*}"
REPO="${SLUG#*/}"
URL="https://${OWNER}.github.io/${REPO}"
echo "已推送 ${BRANCH} 分支。"
echo "到 GitHub repo → Settings → Pages：Source 選「Deploy from a branch」，Branch 選 gh-pages / (root)，Save。"
echo "網址：${URL}/"
