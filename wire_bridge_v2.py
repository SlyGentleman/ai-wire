#!/usr/bin/env python3
"""
Project: AI_WIRE_V2
Purpose: Canonical data ingestion for AI benchmarks & signals
Author: Slygentleman
Safe version: does NOT touch existing scripts
"""

import feedparser
import json
import os
import re
from datetime import datetime, timezone

# -----------------------------
# CONFIG
# -----------------------------

OUTPUT_FILE = os.path.expanduser("~/Desktop/ai_wire_v2/data.json")

FEEDS = {
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/technology-lab",
    "The Register": "https://www.theregister.com/headlines.rss",
    "Hackaday": "https://hackaday.com/blog/feed/",
}

KEYWORDS = [
    "ai", "artificial intelligence", "llm", "model",
    "benchmark", "compute", "gpu", "nvidia",
    "openai", "google", "anthropic", "deepseek"
]

KEYWORD_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in KEYWORDS) + r")\b",
    re.IGNORECASE
)

# -----------------------------
# DATA CONTAINER
# -----------------------------

data = {
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "entries": []
}

# -----------------------------
# INGESTION
# -----------------------------

for source, url in FEEDS.items():
    feed = feedparser.parse(url)

    for item in feed.entries:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        matches = sorted(set(KEYWORD_REGEX.findall(text)))

        if not matches:
            continue

        entry = {
            "title": item.get("title", "No title"),
            "source": source,
            "published": item.get("published", "unknown"),
            "link": item.get("link", ""),
            "matched_keywords": matches
        }

        data["entries"].append(entry)

# -----------------------------
# WRITE OUTPUT
# -----------------------------

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"[OK] Wrote {len(data['entries'])} entries to {OUTPUT_FILE}")
