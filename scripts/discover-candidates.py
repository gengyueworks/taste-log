#!/usr/bin/env python3
"""
discover-candidates.py — 每天扫一遍源头站，把「主库里还没有的新站」攒进候选池。

这个脚本只负责「发现」，不负责「判断」——判断（哪一块好、能拿走什么）必须有人看，
见 docs/criteria.md。它的产出是 data/candidates.json，供人工或 agent 每天挑一个。

每天（本地 launchd 或手动）：
  1. 抓 SOURCES 里每个源头页面的站外链接；
  2. 去掉社媒 / CDN / 源头站自己 / 主库已有的域名；
  3. 对没见过的新链接做一次存活探测：必须 200、不能跳去停放页/验证页，顺便抓 <title>；
  4. 合并进 data/candidates.json（保留 first_seen / last_seen，不会丢历史，也不会重复堆）。

用法：
    python3 scripts/discover-candidates.py            # 正常跑，写盘
    python3 scripts/discover-candidates.py --dry-run  # 只看结果不写盘
    python3 scripts/discover-candidates.py --limit 40 # 单次最多探测多少个新站（默认 30）
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from urllib.parse import urlparse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES_PATH = os.path.join(ROOT, "data", "sites.json")
CAND_PATH = os.path.join(ROOT, "data", "candidates.json")

# 源头：只留实测能抓的。抓失败不影响其他源头（best-effort）。
SOURCES = [
    ("Awwwards · 每日精选", "https://www.awwwards.com/websites/sites_of_the_day/"),
    ("Awwwards · 本周", "https://www.awwwards.com/websites/"),
    ("Awwwards · 提名", "https://www.awwwards.com/websites/nominees/"),
    ("SaaS Landing Page", "https://saaslandingpage.com/"),
    ("Minimal Gallery", "https://minimal.gallery/"),
]

# 来源站自己 + 社媒 + CDN + 统计，一律不算候选
NOISE_HOSTS = {
    "awwwards.com", "assets.awwwards.com", "www.awwwards.com",
    "saaslandingpage.com", "minimal.gallery", "godly.website", "recent.design",
    "cdn.recent.design", "land-book.com", "siteinspire.com",
    "twitter.com", "x.com", "instagram.com", "facebook.com", "linkedin.com",
    "youtube.com", "behance.net", "dribbble.com", "github.com", "pinterest.com",
    "tiktok.com", "threads.net", "t.me", "wa.me", "discord.gg", "medium.com",
    "google.com", "gstatic.com", "cloudflare.com", "cloudfront.net",
    "typekit.net", "fonts.googleapis.com", "gmpg.org", "schema.org",
    "apple.com", "microsoft.com", "adobe.com", "figma.com", "spotify.com",
}
# 探测到这些最终落地页 = 停放页 / 验证页 / 反爬，不算候选
PARKING_MARKERS = (
    "security-checkpoint", "sedoparking", "parkingcrew", "domain-for-sale",
    "godaddy.com/domainsearch", "hugedomains.com", "afternic.com",
    "captcha", "cloudflare.com/cdn-cgi", "verify.",
)

MAX_KEEP = 400          # candidates.json 最多保留多少条
PROBE_TIMEOUT = 10
PROBE_SLEEP = 0.6       # 探测间隔，别把人家站打死


def opener():
    """显式绕开环境变量里的代理：代理挂了脚本不能跟着挂。"""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    return opener().open(req, timeout=timeout)


def norm_host(netloc):
    h = netloc.lower().strip()
    return h[4:] if h.startswith("www.") else h


def extract_links(html):
    out = []
    for u in re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.I):
        u = u.strip()
        host = norm_host(urlparse(u).netloc)
        if not host:
            continue
        out.append((host, u))
    return out


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def probe(url):
    """返回 (ok, final_url, title)。ok=False 表示死了 / 停放 / 反爬。"""
    try:
        resp = fetch(url, timeout=PROBE_TIMEOUT)
        status = getattr(resp, "status", 200)
        final = resp.geturl()
        html = resp.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return False, url, f"HTTP {e.code}"
    except Exception as e:
        return False, url, type(e).__name__
    low = final.lower()
    if any(m in low for m in PARKING_MARKERS):
        return False, final, "parking/checkpoint"
    if status >= 400:
        return False, final, f"HTTP {status}"
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    return True, final, title[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    sites = load_json(SITES_PATH, {}).get("sites", [])
    known_hosts = set()
    for s in sites:
        try:
            known_hosts.add(norm_host(urlparse(s["url"]).netloc))
        except Exception:
            pass

    store = load_json(CAND_PATH, {"updated": "", "items": []})
    items = {it["host"]: it for it in store.get("items", [])}
    seen_hosts = set(items) | known_hosts

    today = date.today().isoformat()
    fresh = []
    for name, src in SOURCES:
        try:
            html = fetch(src).read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"[skip ] {name}: {type(e).__name__}")
            continue
        picked = 0
        for host, url in extract_links(html):
            if host in NOISE_HOSTS or host in seen_hosts:
                continue
            if len(host) < 4 or "." not in host:
                continue
            seen_hosts.add(host)
            fresh.append((name, host, url))
            picked += 1
        print(f"[scan ] {name}: 新链接 +{picked}")

    # 同一域名只留第一条
    dedup, used = [], set()
    for name, host, url in fresh:
        if host in used:
            continue
        used.add(host)
        dedup.append((name, host, url))

    todo = dedup[:args.limit]
    print(f"[probe] 待探测 {len(todo)} 个（今日新链接共 {len(dedup)} 个）")
    added = 0
    for i, (name, host, url) in enumerate(todo, 1):
        ok, final, info = probe(url)
        if ok:
            items[host] = {
                "host": host, "url": url, "title": info, "source": name,
                "first_seen": today, "last_seen": today, "status": "new",
            }
            added += 1
            print(f"  ✓ {i:02d}/{len(todo)} {host}  · {info[:60]}")
        else:
            items[host] = {
                "host": host, "url": url, "title": "", "source": name,
                "first_seen": today, "last_seen": today, "status": "dead",
                "reason": info,
            }
            print(f"  ✗ {i:02d}/{len(todo)} {host}  ({info})")
        time.sleep(PROBE_SLEEP)

    # 清掉过老的死链，别让文件无限涨
    alive = [it for it in items.values() if it.get("status") != "dead"]
    dead = [it for it in items.values() if it.get("status") == "dead"]
    keep_dead = sorted(dead, key=lambda x: x.get("last_seen", ""), reverse=True)[:40]
    merged = sorted(alive + keep_dead, key=lambda x: x.get("first_seen", ""), reverse=True)[:MAX_KEEP]

    new_total = sum(1 for it in merged if it.get("status") == "new")
    print(f"[done ] 今日新增可用候选 {added} 个；池内待判断 {new_total} 个")
    for it in merged[:12]:
        if it.get("status") == "new":
            print(f"   · {it['host']:<28} {it.get('title', '')[:50]}  « {it['source']}")

    if args.dry_run:
        print("[dry-run] 未写盘")
        return 0

    with open(CAND_PATH, "w", encoding="utf-8") as f:
        json.dump({"updated": today, "items": merged}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[write ] {CAND_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
