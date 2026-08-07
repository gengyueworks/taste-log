#!/usr/bin/env python3
"""
candidate-radar.py — 每日 GitHub 推荐 + 候选雷达

每天（由 .github/workflows/daily-candidates.yml 在 GitHub 服务器上触发）：

1. 【每日推荐 · 必有】从 data/sites.json 按「当天是这一年第几天」挑一个站作为
   「今日推荐」：开一个 issue 推到 GitHub，同时把这条写进 data/daily-picks.json
   并 commit 回仓库。完全本地、零外部依赖，永远能跑——这就是「每天到 GitHub 上
   推荐一次」。最长能连着推 47 天不重样，收录变多后更久。
2. 【候选雷达 · 附赠】顺手去几个源头站扫一遍外链，当作「新候选」附在 issue 末尾，
   仅供拍板，绝不自动写进 sites.json。

需要环境变量 GITHUB_TOKEN（workflow 自动注入）；本地调试没有 token 时会打印不开 issue。
同一天重复跑不会刷重复 issue、不会重复写记录（按日期去重）。
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import date

REPO = "gengyueworks/taste-log"
UA = "Mozilla/5.0 (compatible; taste-log-radar/1.0; +https://github.com/gengyueworks/taste-log)"
PAGES_URL = "https://gengyueworks.github.io/taste-log/"
DAILY_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "daily-picks.json")

SOURCES = {
    "Land-book": "https://land-book.com/websites",
    "Awwwards": "https://www.awwwards.com/",
    "SiteInspire": "https://www.siteinspire.com/",
    "Godly": "https://godly.website/",
}
NOISE_DOMAINS = {
    "twitter.com", "x.com", "instagram.com", "facebook.com", "linkedin.com",
    "youtube.com", "behance.net", "dribbble.com", "github.com", "pinterest.com",
    "t.me", "wa.me", "mailto", "javascript", "about:blank",
}


def day_of_year(d):
    return (d - date(d.year, 1, 1)).days + 1


def load_sites():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sites.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cat_zh(data, key):
    for c in data.get("categories", []):
        if c.get("key") == key:
            return c.get("zh", key)
    return key


def load_daily_log():
    if os.path.exists(DAILY_LOG_PATH):
        with open(DAILY_LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def append_daily_pick(records, featured, czh, today_str):
    """把今日推荐追加进 daily-picks.json，按日期去重，返回 (records, changed)。"""
    if any(r.get("date") == today_str for r in records):
        return records, False
    records.append({
        "date": today_str,
        "site_id": featured.get("id", ""),
        "name": featured.get("name", ""),
        "url": featured.get("url", ""),
        "category": czh,
    })
    return records, True


def write_daily_log(records):
    with open(DAILY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_links(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"  [skip] {url} -> {type(e).__name__}", file=sys.stderr)
        return []
    from urllib.parse import urlparse
    out, seen = [], set()
    for lnk in re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.I):
        host = urlparse(lnk).netloc.lower().replace("www.", "")
        if not host or host in NOISE_DOMAINS or host in seen:
            continue
        seen.add(host)
        out.append((host, lnk))
    return out


def post_issue(token, title, body, labels):
    payload = {"title": title, "body": body, "labels": labels}
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def issue_exists_today(token, today_str):
    """查今天是否已经发过 daily-pick，避免手动重跑刷重复。"""
    url = f"https://api.github.com/repos/{REPO}/issues?labels=daily-pick&state=all&per_page=50"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "taste-log-radar",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            issues = json.loads(resp.read())
    except Exception:
        return False
    return any(today_str in (i.get("title") or "") for i in issues)


def main():
    data = load_sites()
    sites = data.get("sites", [])
    today = date.today()
    today_str = today.isoformat()
    doy = day_of_year(today)
    featured = sites[doy % len(sites)]
    czh = cat_zh(data, featured.get("category", ""))

    # 每日记录：写进 data/daily-picks.json（workflow 会把它 commit 回仓库）
    records, changed = append_daily_pick(load_daily_log(), featured, czh, today_str)
    if changed:
        write_daily_log(records)
        print(f"[record] 已写入 data/daily-picks.json（{today_str} · {featured['name']}）")
    else:
        print(f"[record] {today_str} 已在 daily-picks.json 中，无需重复写。")

    # 附赠：外部候选扫描（best-effort，被挡就跳过）
    existing = set()
    from urllib.parse import urlparse
    for s in sites:
        try:
            existing.add(urlparse(s["url"]).netloc.lower().replace("www.", ""))
        except Exception:
            pass
    candidates = []
    for name, url in SOURCES.items():
        print(f"[scan] {name} …")
        for host, lnk in fetch_links(url):
            if host in existing:
                continue
            candidates.append((name, host, lnk))
            if len(candidates) >= 12:
                break
        if len(candidates) >= 12:
            break

    # 组装 issue
    note = featured.get("note") or "（这个站还没写判断，打开看完补一句它好在哪，这条就成立了。）"
    body = [
        f"## 今日推荐 · {today_str}",
        "",
        f"> 每天从档案里挑一个站推到这里，逼自己真的去看一眼。",
        "",
        f"**{featured['name']}** · {czh}",
        "",
        f"{note}",
        "",
        f"🔗 {featured['url']}",
        "",
        f"看完顺手点亮打卡链 → {PAGES_URL}#chain",
    ]
    labels = ["daily-pick"]
    if candidates:
        body += ["", "---", "", "### 新候选（自动扫描，待你拍板，不会自动入库）", "",
                 "| 源头 | 候选 |", "|------|------|"]
        for name, host, lnk in candidates:
            body.append(f"| {name} | {lnk} |")
        body.append("")
        body.append("看上哪个，开 issue 按 `docs/criteria.md` 的格式补一句判断，维护者收进档案。")
        labels.append("candidates")

    title = f"今日推荐 · {today_str} · {featured['name']}"
    full = "\n".join(body)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[warn] 没有 GITHUB_TOKEN，仅打印：\n")
        print(full)
        return 0

    if issue_exists_today(token, today_str):
        print(f"[skip] 今天（{today_str}）已经发过推荐，不重复开 issue。")
        return 0

    try:
        rc = post_issue(token, title, full, labels)
        print(f"[issue] 已开今日推荐 issue: {rc.get('html_url')}")
    except Exception as e:
        print(f"[error] 开 issue 失败: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
