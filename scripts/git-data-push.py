#!/usr/bin/env python3
"""
git-data-push.py — 用 Git Data API 把本地目录推到 GitHub（本机 git push 不通时的唯一方式）

用法：
  python3 scripts/git-data-push.py <local_dir> <repo> <branch> [YYYY-MM-DD]

- 自动建 blob → 递归建 tree（支持嵌套目录）→ 建 commit → 建/更新 ref
- 首次提交（仓库空）自动建分支；之后增量提交
- commit 日期可指定（默认今天）。真实内容才 backdate，素材历史年禁止。

依赖：gh CLI 已登录（用于取 token）。
"""
import base64
import io
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

SKIP_DIRS = {".git"}


def api(method, path, payload=None):
    url = "https://api.github.com/" + path
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "gengyueworks-agent")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 422 and attempt < 3:
                time.sleep(2)
                continue
            body = e.read().decode("utf-8", "ignore")[:300]
            raise RuntimeError(f"HTTP {e.code} {method} {path}: {body}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < 3:
                time.sleep(3)
                continue
            raise


def create_blob(repo, content_bytes):
    b64 = base64.b64encode(content_bytes).decode()
    blob = api("POST", f"repos/{repo}/git/blobs", {"content": b64, "encoding": "base64"})
    return blob["sha"]


def bootstrap_contents(repo, branch, path, content_bytes):
    """空仓库无法用 Git Data API 建 blob（409 Git Repository is empty）。
    先用 Contents API 建一个文件、自动建好分支，再走 Git Data 做完整提交。"""
    b64 = base64.b64encode(content_bytes).decode()
    api("PUT", f"repos/{repo}/contents/{path}",
        {"message": "chore: bootstrap branch", "content": b64, "branch": branch})
    ref = api("GET", f"repos/{repo}/git/refs/heads/{branch}")
    print(f"[bootstrap] 已用 Contents API 建首文件 {path}，分支 {branch} 就绪")
    return ref["object"]["sha"]


def build_tree(repo, path_map, base_tree_sha=None):
    """path_map: { 'data/sites.json': blob_sha, ... } -> 返回根 tree sha"""
    root = {}
    for path, sha in path_map.items():
        parts = path.split("/")
        node = root
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = sha

    def _create(node_dict, base=None):
        entries = []
        for name, val in node_dict.items():
            if isinstance(val, dict):
                sub_sha = _create(val)
                entries.append({"path": name, "mode": "040000", "type": "tree", "sha": sub_sha})
            else:
                entries.append({"path": name, "mode": "100644", "type": "blob", "sha": val})
        body = {"tree": entries}
        if base:
            body["base_tree"] = base
        return api("POST", f"repos/{repo}/git/trees", body)["sha"]

    return _create(root, base_tree_sha)


def main():
    local_dir, repo, branch = sys.argv[1], sys.argv[2], sys.argv[3]
    date_str = sys.argv[4] if len(sys.argv) > 4 else time.strftime("%Y-%m-%d")

    # 1. 收集本地文件字节（先不建 blob，空仓库要先 bootstrap 才能建 blob）
    files = []  # (rel, bytes)
    for dirpath, dirnames, filenames in os.walk(local_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, local_dir).replace(os.sep, "/")
            with io.open(full, "rb") as f:
                files.append((rel, f.read()))
    rels = [r for r, _ in files]
    print(f"[scan] 收集到 {len(files)} 个文件")

    # 2. 判断是首次提交还是增量
    initial = False
    head_sha = None
    base_tree_sha = None
    try:
        ref = api("GET", f"repos/{repo}/git/refs/heads/{branch}")
        head_sha = ref["object"]["sha"]
        head = api("GET", f"repos/{repo}/git/commits/{head_sha}")
        base_tree_sha = head["tree"]["sha"]
        print(f"[ref] 增量提交，基于 {head_sha[:8]}")
    except Exception:
        initial = True
        # 空仓库：先用 Contents API 建首文件，自动建好分支
        boot_path = "README.md" if "README.md" in rels else rels[0]
        boot_bytes = dict(files)[boot_path]
        head_sha = bootstrap_contents(repo, branch, boot_path, boot_bytes)
        head = api("GET", f"repos/{repo}/git/commits/{head_sha}")
        base_tree_sha = head["tree"]["sha"]
        print(f"[ref] 首次提交（已 bootstrap），将做完整提交")

    # 1.5 建 blob（bootstrap 之后仓库已非空，可建 blob）
    path_map = {}
    for rel, b in files:
        path_map[rel] = create_blob(repo, b)
    print(f"[blobs] {len(path_map)} 个文件已建 blob")

    # 3. 建 tree
    tree_sha = build_tree(repo, path_map, base_tree_sha)

    # 4. 建 commit
    dt = date_str + "T09:00:00+08:00"
    commit_body = {"message": "feat: init taste-log archive + don't-break-the-chain",
                   "tree": tree_sha,
                   "author": {"name": "GY", "email": "gengyueworks@users.noreply.github.com", "date": dt},
                   "committer": {"name": "GY", "email": "gengyueworks@users.noreply.github.com", "date": dt}}
    if head_sha is not None:
        commit_body["parents"] = [head_sha]
    commit = api("POST", f"repos/{repo}/git/commits", commit_body)
    commit_sha = commit["sha"]
    print(f"[commit] {date_str} -> {commit_sha[:8]}")

    # 5. ref
    if head_sha is None:
        api("POST", f"repos/{repo}/git/refs", {"ref": f"refs/heads/{branch}", "sha": commit_sha})
        print(f"[ref] 已创建分支 {branch}")
    else:
        api("PATCH", f"repos/{repo}/git/refs/heads/{branch}", {"sha": commit_sha, "force": False})
        print(f"[ref] 已更新分支 {branch}")

    # 6. 校验
    print("[verify] 列出远端文件：")
    contents = api("GET", f"repos/{repo}/contents/?ref={branch}")
    for c in sorted(contents, key=lambda x: x["path"]):
        print(f"  {c['type']:5} {c['path']}")


if __name__ == "__main__":
    main()
