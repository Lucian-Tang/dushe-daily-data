#!/usr/bin/env python3
"""
arxiv_signals.py - arXiv cs.AI/cs.LG Signals Collector
Fetches latest papers from arXiv API, filters by keywords in abstract,
writes to local JSON + Feishu Bitable.
"""
import json
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

APP_TOKEN = "S8mlbvHk6a4a6ss46klcw5CSnCY"
TABLE_ID = "tblIiWi9t04d0u5D"
DATA_DIR = "/root/.openclaw/workspace/data/opportunities/arxiv"

FILTER_KEYWORDS = ["LLM", "large language model", "agent", "autonomous", "multimodal",
                   "vision-language", "VLM", "GPT", "Claude", "Gemini", "generative AI",
                   "inference", "RAG", "retrieval", "embedding", "transformer", "attention"]
MAX_RESULTS = 15

def log_jsonl(status, stage="full", duration_ms=0, error=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cron_name": "arxiv-signals",
        "stage": stage,
        "status": status,
        "duration_ms": duration_ms
    }
    if error:
        entry["error"] = error
    print(json.dumps(entry))

def fetch_arxiv_papers():
    categories = ["cs.AI", "cs.LG", "cs.CL"]
    all_papers = []
    for cat in categories:
        url = (f"http://export.arxiv.org/api/query?"
               f"search_query=cat:{cat}&start=0&max_results={MAX_RESULTS//len(categories)}"
               f"&sortBy=submittedDate&sortOrder=descending")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                xml_data = r.read().decode("utf-8")
            all_papers.extend(parse_arxiv_xml(xml_data))
        except Exception as e:
            log_jsonl("failed", "fetch", 0, f"cat:{cat} {e}")
    return all_papers

def parse_arxiv_xml(xml_data):
    papers = []
    try:
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
           arxiv_id = entry.find("atom:id", ns)
            
            title_text = title.text.strip().replace("\n", " ") if title is not None else ""
            summary_text = summary.text.strip().replace("\n", " ") if summary is not None else ""
            pub_date = published.text[:10] if published is not None else ""
            paper_id = arxiv_id.text.split("/")[-1] if arxiv_id is not None else ""
            
            # Extract citation count if available (arxiv doesn't have it natively, use 0)
            papers.append({
                "title": title_text,
                "abstract": summary_text,
                "published": pub_date,
                "arxiv_id": paper_id,
                "url": f"https://arxiv.org/abs/{paper_id}",
                "citations": 0
            })
    except Exception as e:
        pass
    return papers

def score_paper(paper):
    score = 0
    abstract = paper.get("abstract", "").lower()
    title = paper.get("title", "").lower()
    text = abstract + " " + title
    
    # Dim1: Keyword density (max 4)
    kw_count = sum(1 for kw in FILTER_KEYWORDS if kw.lower() in text)
    score += min(4, kw_count)
    
    # Dim2: Abstract length (longer = more substantive, max 2)
    if len(abstract) > 500:
        score += 2
    elif len(abstract) > 200:
        score += 1
    
    # Dim3: Recentness (max 2) - papers from last 30 days get boost
    pub = paper.get("published", "")
    score += min(2, len(pub) // 5)  # placeholder heuristic
    
    # Dim4: LLM relevance (max 2)
    if any(x in text for x in ["llm", "large language", "gpt", "claude", "gemini"]):
        score += 2
    elif any(x in text for x in ["agent", "multimodal", "vision-language"]):
        score += 1
    
    return min(10, max(1, score))

def should_include(paper):
    abstract = paper.get("abstract", "").lower()
    title = paper.get("title", "").lower()
    text = abstract + " " + title
    for kw in FILTER_KEYWORDS:
        if kw.lower() in text:
            return True
    return False

def infer_signal_type(paper):
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    text = title + " " + abstract
    if any(x in text for x in ["benchmark", "evaluation", "dataset", "survey"]):
        return "技术突破"
    elif any(x in text for x in ["agent", "autonomous", "planning", "reasoning"]):
        return "技术突破"
    elif any(x in text for x in ["model", "architecture", "novel", "approach"]):
        return "技术突破"
    return "技术突破"

def infer_tags(paper):
    tags = []
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
    if any(x in text for x in ["llm", "large language model", "gpt", "claude", "gemini"]):
        tags.append("LLM")
    if any(x in text for x in ["agent", "autonomous", "planning"]):
        tags.append("Agent")
    if any(x in text for x in ["multimodal", "vision-language", "VLM", "image"]):
        tags.append("AI")
    if any(x in text for x in ["open source", "code", "github"]):
        tags.append("开源")
    if any(x in text for x in ["developer", "api", "tool"]):
        tags.append("开发者工具")
    if not tags:
        tags = ["AI"]
    return tags

def main():
    log_jsonl("started", "full", 0)
    start = datetime.now()
    today = datetime.now().strftime("%Y-%m-%d")
    
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    
    papers = fetch_arxiv_papers()
    
    signals = []
    for paper in papers:
        if should_include(paper):
            abstract_short = paper["abstract"][:150] + "..." if len(paper["abstract"]) > 150 else paper["abstract"]
            signal = {
                "title": paper["title"][:200],
                "source": "arXiv",
                "signal_type": infer_signal_type(paper),
                "url": paper["url"],
                "raw_summary": f"{abstract_short} | Published:{paper['published']} | Citations:{paper['citations']}",
                "rough_score": score_paper(paper),
                "status": "raw",
                "discovered_at": today,
                "tags": infer_tags(paper)
            }
            signals.append(signal)
    
    total = len(papers)
    passed = len(signals)
    
    month = datetime.now().strftime("%Y-%m")
    json_file = f"{DATA_DIR}/{month}.json"
    existing = []
    if os.path.exists(json_file):
        with open(json_file) as f:
            existing = json.load(f)
    existing.append({
        "date": today,
        "source": "arXiv",
        "total_fetched": total,
        "passed_filter": passed,
        "signals": signals
    })
    with open(json_file, "w") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Write to Feishu
    for sig in signals:
        tags = sig.pop("tags", [])
        fields = {
            "Opportunity Signals": sig["title"],
            "信源": sig["source"],
            "信号类型": sig["signal_type"],
            "原始链接": {"text": sig["title"], "link": sig["url"]},
            "原始摘要": sig["raw_summary"],
            "粗筛评分": sig["rough_score"],
            "状态": sig["status"],
            "发现时间": int(datetime.now().timestamp() * 1000),
            "标签": tags
        }
        import subprocess
        subprocess.run(["python3", "-c",
            f"from feishu_bitable_client import create_record; print(create_record('{APP_TOKEN}', '{TABLE_ID}', {json.dumps(fields)}))"],
            capture_output=True)
    
    duration = int((datetime.now() - start).total_seconds() * 1000)
    log_jsonl("success", "full", duration)
    print(f"arxiv-signals: fetched={total}, passed={passed}")

if __name__ == "__main__":
    main()