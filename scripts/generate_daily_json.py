#!/usr/bin/env python3
"""
generate_daily_json.py - 统一 JSON 生成脚本 (Phase 2)
读取 raw + MD 报告，生成标准 6 字段 JSON → *_daily_YYYYMMDD.json
"""

import os, re, json, logging, argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"
OUT_DIR = WORKSPACE
REPORTS_DIR = WORKSPACE.parent / "reports"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
SECTIONS = ["dev", "ai", "design", "startup", "industry"]
TODAY = datetime.now().strftime("%Y%m%d")

# ===== Clean helper =====
def clean_source(s):
    return s.lstrip('*').lstrip(' ').strip()

def clean_url(s):
    return s.lstrip('*').lstrip(' ').strip()

# ===== PARSERS =====

def parse_dev(text):
    items = []
    for part in re.split(r'\n#{2,3}\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = content = ''
        for l in lines[1:]:
            s = l.strip()
            if s == '---' or not s: continue
            m = re.match(r'[- ]*\*\*来源[：:]\s*(.+)', s)
            if m: src = clean_source(m.group(1)); continue
            m = re.match(r'[- ]*\*\*链接[：:]\s*(.+)', s)
            if m: url = clean_url(m.group(1)); continue
            m = re.match(r'[- ]*\*\*毒舌[^：:]*[：:]\s*(.+)', s)
            if m: quote = m.group(1).strip(); continue
            m = re.match(r'[- ]*\*\*内容[：:]\s*(.+)', s)
            if m: content = m.group(1).strip(); continue
            m = re.match(r'[- ]*\*\*标题[：:]\s*(.+)', s)
            if m: title = m.group(1).strip(); continue
        items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_ai(text):
    """
    解析AI日报MD,同时支持晨报(## N. Title)和晚间(### N. Title)两种格式。
    晨报字段: **来源：**、**链接：**、**毒舌点评：**、**详情**
    晚间字段: **信源：**、**链接：**、**毒舌：**、无**详情**,content在标题和毒舌之间
    """
    items = []
    for part in re.split(r'\n#{2,3}\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = content = ''
        content_lines = []

        # Regex for metadata fields (support both **Field：** and - **Field**：)
        re_source = re.compile(r'[- ]*\*\*来源[：:]*\*{0,2}\s*(.+)')
        re_xinyuan = re.compile(r'[- ]*\*\*信源[：:]*\*{0,2}\s*(.+)')
        re_link = re.compile(r'[- ]*\*\*链接[：:]*\*{0,2}\s*(.+)')
        re_douche_pd = re.compile(r'[- ]*\*\*毒舌点评[：:]*\*{0,2}\s*(.+)')
        re_douche = re.compile(r'[- ]*\*\*毒舌[：:]*\*{0,2}\s*(.+)')

        for l in lines[1:]:
            s = l.strip()
            if not s or s == '---':
                continue

            # Source matching (morning: **来源：**, evening: **信源：**)
            m = re_source.match(s) or re_xinyuan.match(s)
            if m:
                val = m.group(1).strip()
                if not src: src = val
                continue

            # Link matching
            m = re_link.match(s)
            if m:
                val = m.group(1).strip()
                url_m = re.search(r'(https?://[^\s\)\]]+)', val)
                if url_m and not url: url = clean_url(url_m.group(1))
                continue

            # Douche matching (morning: **毒舌点评：**, evening: **毒舌：**)
            m = re_douche_pd.match(s) or re_douche.match(s)
            if m:
                quote = m.group(1).strip()
                continue

            # Not metadata → this is content
            content_lines.append(s)

        content = ' '.join(content_lines).strip()
        items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_design(text):
    items = []
    for part in re.split(r'\n###\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = ''
        content = []
        for l in lines[1:]:
            s = l.strip()
            if not s or s == '---': continue
            m = re.match(r'\*\*来源[：:]\s*(.+)', s)
            if m: src = clean_source(m.group(1)); continue
            m = re.match(r'\*\*链接[：:]\s*(.+)', s)
            if m: url = clean_url(m.group(1)); continue
            m = re.match(r'\*\*Lucia 毒舌[：:]\s*(.+)', s)
            if m: quote = m.group(1).strip(); continue
            if s.startswith('> '):
                content.append(s[2:].strip())
        items.append(dict(title=title, content=' '.join(content).strip(), quote=quote, source=src, url=url))
    return items

def parse_startup(text):
    """Parse startup MD with format: ### Title | **来源：** | **链接：** | > *毒舌点评：*"""
    items = []
    for part in re.split(r'\n###\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = content = ''
        for l in lines[1:]:
            s = l.strip()
            if not s or s.startswith('---') or s.startswith('##'): continue
            m = re.match(r'\*\*来源[：:]\s*(.+)', s)
            if m: src = clean_source(m.group(1)); continue
            m = re.search(r'\*\*链接[\w]*[：:]\s*(.+)', s)
            if m:
                val = m.group(1).strip()
                url_m = re.search(r'(https?://[^\s\)\]]+)', val)
                if url_m: url = clean_url(url_m.group(1))
                if not url: url = clean_url(val)
                continue
            if s.startswith('> '):
                content += s[2:].strip() + ' '
                continue
            m = re.match(r'.*毒舌[^：:]*[：:]\s*(.+)', s)
            if m: quote = m.group(1).strip(); continue
            # General content (not metadata)
            if len(s) > 10 and not s.startswith('**'):
                content += s + ' '
        items.append(dict(title=title, content=content.strip(), quote=quote, source=src, url=url))
    return items

def parse_industry(text):
    items = []
    for part in re.split(r'\n##\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = ''
        for l in lines[1:]:
            s = l.strip()
            if s == '---': continue
            m = re.match(r'\*\*信源\*\*[：:]\s*(.+)', s)
            if m: src = clean_source(m.group(1)); continue
            m = re.search(r'\*\*原文\*\*[：:]\s*\[?([^\]]*)\]?\s*[\(]?\s*(https?://\S+)', s)
            if m: url = m.group(2).strip().rstrip(')'); continue
            # Also handle just URL in the line
            if not url:
                m = re.search(r'(https?://[^\s\)]+)', s)
                if m: url = m.group(1).strip().rstrip(')'); continue
            m = re.search(r'\*\*Lucia毒舌\*\*[：:]\s*(.+)', s)
            if m: quote = m.group(1).strip(); continue
        items.append(dict(title=title, content='', quote=quote, source=src, url=url))
    return items

PARSERS = dict(dev=parse_dev, ai=parse_ai, design=parse_design, startup=parse_startup, industry=parse_industry)

# ===== MAIN =====

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--section', '-s', choices=SECTIONS)
    ap.add_argument('--date', '-d', default=TODAY)
    ap.add_argument('--dry-run', '-n', action='store_true')
    args = ap.parse_args()
    sections = [args.section] if args.section else SECTIONS

    for sec in sections:
        d_short = args.date
        d_long = f"{d_short[:4]}-{d_short[4:6]}-{d_short[6:8]}"

        raw_path = DATA_DIR / f"raw_{sec}_{d_short}.json"
        raw = []
        if raw_path.exists():
            with open(raw_path) as f: raw = json.load(f)
            logger.info(f"[{sec}] raw: {len(raw)}条")

        md_path = REPORTS_DIR / f"{sec}-daily" / f"{d_long}.md"
        md_content = md_path.read_text(encoding='utf-8') if md_path.exists() else ''

        if md_content:
            parsed = PARSERS[sec](md_content)
            logger.info(f"[{sec}] MD解析: {len(parsed)}条")
        elif raw:
            parsed = [dict(title=r.get('title',''), content='', quote='',
                           source=r.get('source',''), url=r.get('url','')) for r in raw[:10]]
            logger.info(f"[{sec}] 无MD, 从raw取: {len(parsed)}条")
        else:
            logger.warning(f"[{sec}] 无数据, skip")
            continue

        # Enrich from raw (by url match)
        raw_by_url = {}
        for r in raw:
            k = r.get('url','').split('?')[0].rstrip('/')
            if k:
                raw_by_url[k] = r

        for item in parsed:
            k = item.get('url','').split('?')[0].rstrip('/')
            r = raw_by_url.get(k) if k else None
            if r:
                if not item.get('source'): item['source'] = r.get('source','')
                if not item.get('url'): item['url'] = r.get('url','')
                if not item.get('content'): item['content'] = (r.get('content') or '')[:300]
            for f in ('title','content','quote','source','url'):
                item.setdefault(f, '')
            item['published'] = d_long

        if args.dry_run:
            print(f'\n[{sec}] {len(parsed)}条 (md={"✅" if md_content else "❌"} raw={len(raw)})')
            for item in parsed[:2]:
                print(f'  title={item["title"][:30]} src={item["source"]!r:20s} c={len(item["content"])} q={len(item["quote"])} url={item["url"][:20]}')
            if len(parsed) > 2:
                print(f'  ... +{len(parsed)-2}')
        else:
            op = OUT_DIR / f'{sec}_daily_{d_short}.json'
            with open(op, 'w') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            logger.info(f'[{sec}] {len(parsed)}条 → {op.name}')

if __name__ == '__main__':
    main()
