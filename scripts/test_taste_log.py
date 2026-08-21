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
