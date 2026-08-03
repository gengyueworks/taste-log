#!/usr/bin/env python3
"""
candidate-radar.py — 每日候选雷达

每天（由 .github/workflows/daily-candidates.yml 触发）去几个源头站抓「最新」，
抽出外链作为候选，去重后开一个 issue 给用户拍板。

设计原则：
- 全自动只负责「找候选」，绝不自动写进 sites.json（用户拍板才收）。
- 任何源头被反爬/超时挡住都静默跳过，绝不崩溃、绝不伪造数据。
- 一个候选都没找到时，不刷 issue（避免每天灌水）。

用法（本地调试）：
  python3 candidate-radar.py
需要环境变量 GITHUB_TOKEN（workflow 里自动注入）才能开 issue。
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

REPO = "gengyueworks/taste-log"
UA = "Mozilla/5.0 (compatible; taste-log-radar/1.0; +https://github.com/gengyueworks/taste-log)"

# 源头站「最新」页面。被 Cloudflare 挡住的会静默失败，属正常。
SOURCES = {
    "Land-book": "https://land-book.com/websites",
    "Awwwards": "https://www.awwwards.com/",
    "SiteInspire": "https://www.siteinspire.com/",
    "Godly": "https://godly.website/",
}

# 这些域不是作品站，过滤掉
NOISE_DOMAINS = {
    "twitter.com", "x.com", "instagram.com", "facebook.com", "linkedin.com",
    "youtube.com", "behance.net", "dribbble.com", "github.com", "pinterest.com",
    "t.me", "wa.me", "mailto", "javascript", "about:blank",
}


def load_existing_domains():
    """读 sites.json，拿到已收录的域名集合，用于去重。"""
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "data", "sites.json"), encoding="utf-8") as f:
            data = json.load(f)
        domains = set()
        for s in data.get("sites", []):
            try:
                from urllib.parse import urlparse
                domains.add(urlparse(s["url"]).netloc.lower().replace("www.", ""))
            except Exception:
                pass
        return domains
    except Exception:
        return set()


def fetch_links(url):
    """抓页面，抽出所有外链（不同域的 https 链接）。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", "ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as e:
        print(f"  [skip] {url} -> {type(e).__name__}", file=sys.stderr)
        return []
    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.I)
    from urllib.parse import urlparse
    out = []
    seen = set()
    for lnk in links:
        try:
            host = urlparse(lnk).netloc.lower().replace("www.", "")
        except Exception:
            continue
        if not host or host in NOISE_DOMAINS:
            continue
        # 只保留看起来像作品站的（有路径或就是根域，且不是巨型平台）
        if host in seen:
            continue
        seen.add(host)
        out.append((host, lnk))
    return out


def main():
    existing = load_existing_domains()
    candidates = []  # (source, host, url)
    for name, url in SOURCES.items():
        print(f"[scan] {name} …")
        for host, lnk in fetch_links(url):
            if host in existing:
                continue
            candidates.append((name, host, lnk))
        if len(candidates) >= 12:  # 每天最多 12 个候选，够看就行
            break

    if not candidates:
        print("[done] 今天没有新候选（源头可能被反爬挡住，或都已收录）。不刷 issue。")
        return 0

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[warn] 没有 GITHUB_TOKEN，候选只打印不开 issue：")
        for name, host, lnk in candidates:
            print(f"  - [{name}] {lnk}")
        return 0

    lines = [
        "每日候选雷达自动跑出来的，仅供参考，**不会自动入库**。",
        "看上哪个，按下面格式开 issue 或直接在评论里说一声，维护者收。",
        "",
        "| 源头 | 候选 |",
        "|------|------|",
    ]
    for name, host, lnk in candidates:
        lines.append(f"| {name} | {lnk} |")
    lines += [
        "",
        "**拍板格式**（开 issue 即可）：",
        "```",
        "站点：<url>",
        "分类：产品与工具界面",
        "喜欢哪一块：（一句话，要具体）",
        "```",
        "",
        "_由 `.github/workflows/daily-candidates.yml` 自动生成。_",
    ]
    body = "\n".join(lines)
    payload = {
        "title": f"候选雷达 · {len(candidates)} 个新站",
        "body": body,
        "labels": ["candidates"],
    }
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/issues",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "taste-log-radar",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rc = json.loads(resp.read())
        print(f"[issue] 已开候选 issue: {rc.get('html_url')}")
    except Exception as e:
        print(f"[error] 开 issue 失败: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
