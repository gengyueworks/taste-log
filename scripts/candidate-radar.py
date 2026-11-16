#!/usr/bin/env python3
"""
candidate-radar.py — 每日 GitHub 推荐 + 候选雷达

每天（由 .github/workflows/daily-candidates.yml 在 GitHub 服务器上触发）：

1. 【每日推荐 · 必有】从 data/sites.json 按「最久没被推荐过」挑一个站作为
   「今日推荐」：开一个 issue 推到 GitHub，同时把这条写进 data/daily-picks.json
   并 commit 回仓库。完全本地、零外部依赖，永远能跑——这就是「每天到 GitHub 上
   推荐一次」。池子转完一圈才会回头，不会隔几天推同一个站。
2. 【今日候选 · 附赠】从本地 data/candidates.json（scripts/discover-candidates.py
   每天扫源头站攒的）里取最新的几条当「今日候选」附在 issue 末尾，仅供拍板，
   绝不自动写进 sites.json；本地没跑过长扫描时才现场抓一遍兜底。

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
CAND_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "candidates.json")

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
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("sites"), list):
        raise ValueError("data/sites.json 必须包含 sites 数组")
    return data


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


def select_featured(sites, target_date, records=None):
    """挑今天推荐哪个站：最久没推过的优先，一圈转完才回头。

    只按「年内第几天取模」会让 49 个站 49 天转一圈、永不新增，还会在同一天
    重复落到同一批站上；改成看 daily-picks.json 里每个站上一次被推的日期，
    取最早的那个，就保证了「先补齐没推过的，再把老的轮到」，池子长多久都不会
    出现昨天推过的今天又推。
    """
    if not sites:
        raise ValueError("data/sites.json 没有可推荐的站点")
    last_seen = {}
    for r in records or []:
        sid = r.get("site_id")
        d = r.get("date") or ""
        if sid and d > last_seen.get(sid, ""):
            last_seen[sid] = d
    n = len(sites)
    offset = day_of_year(target_date) % n
    order = sorted(
        range(n),
        key=lambda i: (last_seen.get(sites[i].get("id", ""), ""), (offset + i) % n),
    )
    return sites[order[0]]


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
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("无法确认今日 issue 是否已存在，已停止发布以避免重复") from exc
    return any(today_str in (i.get("title") or "") for i in issues)


def load_candidate_pool(limit=3):
    """读本地候选池（scripts/discover-candidates.py 每天写），取最新几条待判断的。"""
    if not os.path.exists(CAND_PATH):
        return []
    try:
        with open(CAND_PATH, encoding="utf-8") as f:
            store = json.load(f)
    except (OSError, ValueError):
        return []
    items = [it for it in store.get("items", []) if it.get("status") == "new"]
    items.sort(key=lambda it: it.get("first_seen", ""), reverse=True)
    return items[:limit]


def main():
    data = load_sites()
    sites = data.get("sites", [])
    today = date.today()
    today_str = today.isoformat()
    records = load_daily_log()
    featured = select_featured(sites, today, records)
    czh = cat_zh(data, featured.get("category", ""))

    # 每日记录：写进 data/daily-picks.json（workflow 会把它 commit 回仓库）
    records, changed = append_daily_pick(records, featured, czh, today_str)
    if changed:
        write_daily_log(records)
        print(f"[record] 已写入 data/daily-picks.json（{today_str} · {featured['name']}）")
    else:
        print(f"[record] {today_str} 已在 daily-picks.json 中，无需重复写。")

    # 候选池：优先用本地 discover-candidates.py 每天扫出来的（带标题、已验活）；
    # 本地没跑过才现场扫一遍兜底（容易 403/429，只当垫底）。
    pool = load_candidate_pool(limit=3)
    candidates = []  # (source, url, title)
    if pool:
        print(f"[pool] 候选池里待判断 {len(pool)} 条")
        candidates = [(it.get("source", ""), it.get("url", ""), it.get("title", "")) for it in pool]
    else:
        existing = set()
        from urllib.parse import urlparse
        for s in sites:
            try:
                existing.add(urlparse(s["url"]).netloc.lower().replace("www.", ""))
            except Exception:
                pass
        for name, url in SOURCES.items():
            print(f"[scan] {name} …")
            for host, lnk in fetch_links(url):
                if host in existing:
                    continue
                candidates.append((name, lnk, ""))
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
        body += ["", "---", "", "### 今日候选（源头扫出来的新站，待判断，不会自动入库）", "",
                 "| 源头 | 候选 | 站名 |", "|------|------|------|"]
        for name, lnk, ttl in candidates:
            ttl = (ttl or "—").replace("|", "·")
            body.append(f"| {name} | {lnk} | {ttl} |")
        body.append("")
        body.append("按 `docs/criteria.md` 三条过一遍：第一屏有气质判断 / 结构成熟 / 有能拿走的东西。")
        body.append("通过的写进 `data/sites.json`（带 note），并补一张审美卡。")
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
