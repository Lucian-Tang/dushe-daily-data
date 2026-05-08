#!/usr/bin/env python3
"""
hf_papers_collector.py - HuggingFace Daily Papers Collector
Fetches papers from https://huggingface.co/api/daily_papers (public JSON API),
transforms to vibe-daily format, writes to local JSON + pushes to GitHub Pages.

Output: data/opportunities/huggingface/{date}.json
Also writes to dushe-daily-data/hf_daily_{date}.json (git-commit-push).

API response shape (per paper):
  paper.id, paper.title, paper.summary, paper.upvotes,
  paper.authors[*].name, paper.githubRepo, paper.ai_summary,
  publishedAt, submittedOnDailyAt
"""
import json, os, sys, subprocess
from datetime import datetime, timezone

OUT_DIR = os.path.expanduser("~/.openclaw/workspace/data/opportunities/huggingface")
DATA_REPO_DIR = os.path.expanduser("~/.openclaw/workspace/dushe-daily-data")
os.makedirs(OUT_DIR, exist_ok=True)

HF_API_URL = "https://huggingface.co/api/daily_papers"
HF_PAPERS_URL = "https://huggingface.co/papers"
MAX_PAPERS = 20  # cap to avoid oversized payloads


def log_jsonl(status, stage="full", duration_ms=0, error=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cron_name": "hf-papers",
        "stage": stage,
        "status": status,
        "duration_ms": duration_ms,
    }
    if error:
        entry["error"] = error
    print(json.dumps(entry))


def fetch_papers():
    """GET https://huggingface.co/api/daily_papers → list of paper dicts"""
    import urllib.request
    req = urllib.request.Request(
        HF_API_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; vibe-daily-bot/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def transform(paper_entry):
    """
    Map HF daily-paper entry → vibe-daily item format.
    Entry: { paper: {...}, publishedAt, title, summary, thumbnail, ... }
    """
    paper = paper_entry.get("paper", {})

    paper_id = paper.get("id", "")
    title = paper_entry.get("title") or paper.get("title", "")
    summary = paper_entry.get("summary") or paper.get("summary", "")
    ai_summary = paper.get("ai_summary") or ""
    upvotes = paper.get("upvotes", 0)
    github_repo = paper.get("githubRepo") or ""
    authors_raw = paper.get("authors", [])
    authors = [a["name"] for a in authors_raw if a.get("name")]

    # HF paper detail page
    paper_url = f"{HF_PAPERS_URL}/{paper_id}" if paper_id else HF_PAPERS_URL

    # Content: prefer ai_summary (often Chinese), fall back to English summary
    content = ai_summary if ai_summary else summary
    # Truncate to ~400 chars (小程序 text limit)
    if len(content) > 400:
        content = content[:400] + "…"

    # Compose a readable content block
    body_parts = [content]
    if github_repo:
        body_parts.append(f"\n🔗 GitHub: {github_repo}")
    body_parts.append(f"\n⬆️ 点赞: {upvotes}")
    body = "".join(body_parts).strip()

    # pubTime: normalize to YYYY-MM-DD or relative string
    published_at = paper.get("publishedAt", "")[:10]

    return {
        "title": title[:200],
        "url": paper_url,
        "source": "HuggingFace Daily Papers",
        "content": body,
        "authors": authors,
        "upvotes": upvotes,
        "github_repo": github_repo,
        "ai_summary": ai_summary,
        "published": published_at,
        # internal fields
        "hf_paper_id": paper_id,
        "hf_thumbnail": paper_entry.get("thumbnail", ""),
    }


def main():
    log_jsonl("started", "full", 0)
    start = datetime.now()

    try:
        entries = fetch_papers()
    except Exception as e:
        log_jsonl("failed", "fetch", 0, str(e))
        print(f"❌ HF API fetch failed: {e}")
        sys.exit(1)

    # Take up to MAX_PAPERS
    items = []
    for entry in entries[:MAX_PAPERS]:
        try:
            item = transform(entry)
            if item["title"]:
                items.append(item)
        except Exception as e:
            print(f"  ⚠️ transform skip: {e}")
            continue

    today = datetime.now().strftime("%Y-%m-%d")
    date_slug = datetime.now().strftime("%Y%m%d")

    # ── 1. Write to local opportunities dir ──────────────────────────────
    local_file = f"{OUT_DIR}/{today}.json"
    local_payload = {
        "date": today,
        "source": "huggingface",
        "count": len(items),
        "items": items,
    }
    with open(local_file, "w") as f:
        json.dump(local_payload, f, ensure_ascii=False, indent=2)
    print(f"✅ HF papers: {len(items)} items → {local_file}")

    # ── 2. Write to dushe-daily-data repo (git commit + push) ────────────
    out_filename = f"hf_daily_{date_slug}.json"
    repo_file = os.path.join(DATA_REPO_DIR, out_filename)

    # Ensure repo is checked out / pull latest
    if os.path.isdir(os.path.join(DATA_REPO_DIR, ".git")):
        subprocess.run(
            ["git", "-C", DATA_REPO_DIR, "fetch", "origin"],
            capture_output=True, timeout=30,
        )
        subprocess.run(
            ["git", "-C", DATA_REPO_DIR, "reset", "--hard", "origin/main"],
            capture_output=True, timeout=30,
        )
    else:
        print("⚠️  dushe-daily-data not a git repo, skipping push")
        repo_file = None

    if repo_file:
        with open(repo_file, "w") as f:
            json.dump(local_payload, f, ensure_ascii=False, indent=2)

        # Update index.json  (add/replace hf_daily entry)
        index_file = os.path.join(DATA_REPO_DIR, "index.json")
        if os.path.exists(index_file):
            with open(index_file) as f:
                index = json.load(f)
        else:
            index = {}

        # Read existing index to preserve structure
        index["hf_daily"] = out_filename

        with open(index_file, "w") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        subprocess.run(
            ["git", "-C", DATA_REPO_DIR, "add", "."],
            capture_output=True,
        )
        commit_msg = f"feat(hf-daily): add {today} papers ({len(items)} items)"
        subprocess.run(
            ["git", "-C", DATA_REPO_DIR, "commit", "-m", commit_msg],
            capture_output=True,
        )
        push = subprocess.run(
            ["git", "-C", DATA_REPO_DIR, "push", "origin", "main"],
            capture_output=True, timeout=60,
        )
        if push.returncode == 0:
            print(f"✅ Pushed hf_daily_{date_slug}.json to GitHub Pages")
        else:
            print(f"⚠️  git push failed: {push.stderr.decode()}")

    duration = int((datetime.now() - start).total_seconds() * 1000)
    log_jsonl("success", "full", duration)
    print(f"\n📋 Top 3 papers:")
    for item in items[:3]:
        print(f"  • {item['title'][:70]}…  ↑{item['upvotes']}")


if __name__ == "__main__":
    main()
