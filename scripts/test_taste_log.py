#!/usr/bin/env python3
"""Tests for the deterministic, network-bound parts of candidate-radar.py."""

import importlib.util
import pathlib
import unittest
from datetime import date
from unittest.mock import patch
from urllib.error import URLError


SCRIPT_PATH = pathlib.Path(__file__).with_name("candidate-radar.py")
SPEC = importlib.util.spec_from_file_location("candidate_radar", SCRIPT_PATH)
candidate_radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate_radar)


class CandidateRadarTests(unittest.TestCase):
    def test_select_featured_is_stable_and_uses_the_full_catalog(self):
        sites = [{"id": str(index)} for index in range(48)]

        first = candidate_radar.select_featured(sites, date(2026, 1, 1))
        second = candidate_radar.select_featured(sites, date(2026, 1, 1))

        self.assertEqual(first, second)
        self.assertIn(first, sites)

    def test_select_featured_rejects_an_empty_catalog(self):
        with self.assertRaisesRegex(ValueError, "没有可推荐的站点"):
            candidate_radar.select_featured([], date(2026, 1, 1))

    def test_select_featured_skips_recently_featured_sites(self):
        """回归测试：11-06~11-11 推过 Rive/Spline/Webflow/Cargo/Milanote/A24 之后，
        11-12 又推回 Rive（49 站取模轮转的死穴）。现在必须优先挑从没推过的。"""
        sites = [{"id": sid} for sid in ("rive", "spline", "webflow", "cargo", "fresh-a", "fresh-b")]
        records = [
            {"date": f"2026-11-0{i}", "site_id": sid}
            for i, sid in enumerate(("rive", "spline", "webflow", "cargo"), start=6)
        ]

        picked = candidate_radar.select_featured(sites, date(2026, 11, 12), records)

        self.assertIn(picked["id"], ("fresh-a", "fresh-b"))

    def test_select_featured_returns_oldest_when_pool_is_exhausted(self):
        sites = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        records = [
            {"date": "2026-11-01", "site_id": "a"},
            {"date": "2026-11-05", "site_id": "b"},
            {"date": "2026-11-09", "site_id": "c"},
        ]

        picked = candidate_radar.select_featured(sites, date(2026, 11, 12), records)

        self.assertEqual(picked["id"], "a")

    def test_select_featured_never_repeats_within_one_cycle(self):
        sites = [{"id": str(i)} for i in range(5)]
        records = []
        picked = []
        for day in range(1, 6):
            site = candidate_radar.select_featured(sites, date(2026, 11, day), records)
            picked.append(site["id"])
            records.append({"date": f"2026-11-{day:02d}", "site_id": site["id"]})

        self.assertEqual(len(set(picked)), 5)

    def test_append_daily_pick_is_idempotent_for_the_same_date(self):
        featured = {"id": "linear", "name": "Linear", "url": "https://linear.app/"}
        records = []

        records, changed = candidate_radar.append_daily_pick(records, featured, "产品与工具界面", "2026-08-11")
        records, changed_again = candidate_radar.append_daily_pick(records, featured, "产品与工具界面", "2026-08-11")

        self.assertTrue(changed)
        self.assertFalse(changed_again)
        self.assertEqual(len(records), 1)

    def test_issue_lookup_fails_closed_when_github_is_unreachable(self):
        with patch.object(candidate_radar.urllib.request, "urlopen", side_effect=URLError("offline")):
            with self.assertRaisesRegex(RuntimeError, "避免重复"):
                candidate_radar.issue_exists_today("token", "2026-08-11")


if __name__ == "__main__":
    unittest.main()
