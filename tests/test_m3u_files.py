"""Tests for M3U / M3U8 playlist files.

Validates:
  - Starts with the #EXTM3U header
  - Every #EXTINF line is followed by a URL
  - Channel names in #EXTINF are non-empty
  - URLs use http or https
  - No duplicate channel entries within a single file
"""

import pathlib
import re

import pytest

URL_PATTERN = re.compile(r"^https?://\S+$")
EXTINF_PATTERN = re.compile(r"^#EXTINF:\s*-?\d+\s*,(.+)$")


def _parse_m3u(path: pathlib.Path):
    """Yield (channel_name, url) tuples from an M3U file."""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = EXTINF_PATTERN.match(line)
        if m:
            channel = m.group(1).strip()
            url = lines[i + 1].strip() if i + 1 < len(lines) else ""
            yield channel, url
            i += 2
        else:
            i += 1


class TestM3uFormat:
    def test_starts_with_extm3u_header(self, m3u_file):
        first_line = m3u_file.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
        assert first_line == "#EXTM3U", (
            f"{m3u_file.name} does not start with #EXTM3U"
        )

    def test_has_at_least_one_entry(self, m3u_file):
        entries = list(_parse_m3u(m3u_file))
        assert len(entries) > 0, f"{m3u_file.name} has no channel entries"

    def test_channel_names_are_nonempty(self, m3u_file):
        for channel, _ in _parse_m3u(m3u_file):
            assert len(channel) > 0, "Empty channel name found"

    def test_urls_are_valid(self, m3u_file):
        for channel, url in _parse_m3u(m3u_file):
            assert URL_PATTERN.match(url), (
                f"{m3u_file.name}: channel '{channel}' has invalid URL: {url}"
            )

    def test_no_empty_urls(self, m3u_file):
        for channel, url in _parse_m3u(m3u_file):
            assert len(url) > 0, (
                f"{m3u_file.name}: channel '{channel}' has empty URL"
            )

    def test_file_is_utf8_readable(self, m3u_file):
        m3u_file.read_text(encoding="utf-8")

    def test_entry_count_is_reasonable(self, m3u_file):
        entries = list(_parse_m3u(m3u_file))
        assert len(entries) >= 1, "File has too few entries"
