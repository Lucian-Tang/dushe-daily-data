#!/usr/bin/env python3
"""
generate_daily_json.py - 统一 JSON 生成脚本 (Phase 2)
读取 raw + MD 报告，生成标准 6 字段 JSON → *_daily_YYYYMMDD.json
"""

import os, re, json, logging, argparse, hashlib
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"
OUT_DIR = WORKSPACE
REPORTS_DIR = WORKSPACE.parent / "reports"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
SECTIONS = ["dev", "ai", "design", "startup", "industry", "github", "clawhub"]
TODAY = datetime.now().strftime("%Y%m%d")

# ===== ClawHub 毒舌点评模板 (15-30字) =====
CLAWHUB_QUOTES = [
    "又一个试图让 AI 干所有活的工具包",
    "听起来很美，装上了可能翻车翻得彻底",
    "名字取得不错，能不能用就另说了",
    "卷王的新玩具，普通人观望就好了",
    "开源精神值得表扬，稳定性打个问号",
    "技能市场的长尾产物，有用就算赚了",
    "社区贡献喜+1，实际价值等时间验证",
    "装完发现原来自己也能手写，何必呢",
    "给 Agent 加技能包，跟装浏览器插件一样",
    "又一个'让工作流自动化'的尝试，祝好运",
    "看起来花里胡哨，核心代码就几百行",
    "低代码梦还在继续，这次是 Agent 版",
    "宣称很好用，实际全看运气和网络",
    "技能生态的一块砖，搭起来才算数",
    "小众但确实有用，可惜多数人用不上",
    "工具链又胖了一圈，项目依赖+1",
    "先 star 收藏再说，反正不一定会用",
    "卷王的又一个新玩具，普通人观望就行",
]

# ===== Clean helper =====
def clean_source(s):
    """Clean source string: strip ** markers, leading/trailing whitespace."""
    s = s.strip()
    s = re.sub(r'^\*+', '', s)  # leading asterisks
    s = re.sub(r'\*+$', '', s)  # trailing asterisks
    return s.strip()

def clean_url(s):
    """Clean URL string: strip ** markers, leading/trailing whitespace."""
    return s.strip().strip('*').strip()

def _clean_raw_content(raw_content, source):
    """清洗 raw content：剥离HN/NL等平台的元数据格式，提取有效文本"""
    if not raw_content:
        return ''
    c = raw_content.strip()
    # 剥离 HN/NL 格式化行（Article URL / Comments URL / Points / # Comments）
    c = re.sub(r'\n(?:Article\s+)?URL:\s*https?://\S+', '', c)
    c = re.sub(r'\nComments URL:\s*https?://\S+', '', c)
    c = re.sub(r'\nPoints:\s*\d+', '', c)
    c = re.sub(r'\n# Comments:\s*\d+.*', '', c)
    c = re.sub(r'\nhttps?://\S+', '', c)
    c = re.sub(r'^Hey HN,?\s*', '', c)
    c = re.sub(r'^Hi HN,?\s*', '', c)
    c = re.sub(r'^RT\s+', '', c)
    # 移除孤立的缩略链接
    c = re.sub(r'\nComments URL:.*$', '', c)
    c = re.sub(r'^Article URL:.*$\n?', '', c, flags=re.MULTILINE)
    # 移除 archive.ph 链接行
    c = re.sub(r'\nhttps?://archive\.ph/\S+', '', c)
    # 压缩多余空白
    c = re.sub(r'\n{3,}', '\n\n', c)
    c = c.strip()
    return c[:300] if len(c) > 300 else c


def clean_title(t):
    """清洗标题中的 Unicode 修饰符和残留学符"""
    if not t:
        return t
    t = t.replace('\u20E3', '')   # Combining Enclosing Keycap
    t = t.replace('\uFE0F', '')   # Variation Selector-16
    t = t.replace('\U0001F51F', '')  # KEYCAP TEN emoji
    # 移除 keycap 删除后残留的开头数字
    t = re.sub(r'^\d+\s*', '', t)
    return t.strip()

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
    解析AI日报MD，支持两种格式:
    1. 新格式（emoji blockquote）:
       ## N. Title
       > 📅 YYYY-MM-DD | 📰 Source Name
       > 💬 毒舌评论
       Content paragraph(s)...
       [🔗 原文](url)
    2. 旧格式（**来源：**/**链接：**/**毒舌：** 标签）
    """
    items = []
    for part in re.split(r'\n#{2,3}\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title: continue
        src = url = quote = ''
        content_lines = []

        # Detect format: scan for emoji blockquote markers
        is_new_format = any(
            l.strip().startswith('> 📅') or l.strip().startswith('> 💬')
            for l in lines[1:] if l.strip()
        )

        if is_new_format:
            # --- New format: emoji blockquotes ---
            for l in lines[1:]:
                s = l.strip()
                if not s or s == '---':
                    continue

                # Source line: > 📅 YYYY-MM-DD | 📰 SourceName
                if s.startswith('> 📅'):
                    parts_src = s.split('|')
                    if len(parts_src) >= 2:
                        src_part = parts_src[1].strip()
                        src_part = re.sub(r'📰\s*', '', src_part).strip()
                        if src_part:
                            src = clean_source(src_part)
                    continue

                # Quote line: > 💬 Quote text
                m = re.match(r'> 💬\s*(.+)', s)
                if m:
                    quote = m.group(1).strip()
                    continue

                # URL: [🔗 原文](url) or any [text](url)
                m = re.search(r'\[🔗\s*原文\]\((.+)\)', s)
                if m:
                    url = clean_url(m.group(1))
                    continue
                m = re.search(r'\[.*?\]\((.+)\)', s)
                if m and not url:
                    url = clean_url(m.group(1))
                    continue

                # Skip other blockquote lines
                if s.startswith('>'):
                    continue

                # Remaining lines are content
                content_lines.append(s)

        else:
            # --- Old format: **来源：** / **毒舌：** markdown tags ---
            re_source = re.compile(r'[- ]*\*\*来源[：:]*\*{0,2}\s*(.+)')
            re_xinyuan = re.compile(r'[- ]*\*\*信源[：:]*\*{0,2}\s*(.+)')
            re_link = re.compile(r'[- ]*\*\*链接[：:]*\*{0,2}\s*(.+)')
            re_douche_pd = re.compile(r'[- ]*\*\*毒舌点评[：:]*\*{0,2}\s*(.+)')
            re_douche = re.compile(r'[- ]*\*\*毒舌[：:]*\*{0,2}\s*(.+)')

            for l in lines[1:]:
                s = l.strip()
                if not s or s == '---':
                    continue

                m = re_source.match(s) or re_xinyuan.match(s)
                if m:
                    val = m.group(1).strip()
                    if not src: src = val
                    continue

                m = re_link.match(s)
                if m:
                    val = m.group(1).strip()
                    url_m = re.search(r'(https?://[^\s\)\]]+)', val)
                    if url_m and not url: url = clean_url(url_m.group(1))
                    continue

                m = re_douche_pd.match(s) or re_douche.match(s)
                if m:
                    quote = m.group(1).strip()
                    continue

                content_lines.append(s)

        content = ' '.join(content_lines).strip()
        items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_design(text):
    """Parse design MD with format: ### N. Title | **来源：** | 🔗 [阅读原文](url) | > 💬 quote
    
    Handles section headers (H2 with emoji like 🔥📱🏗️🧩📊) by skipping them.
    Extracts source/url/quote from structured MD lines.
    """
    items = []
    for part in re.split(r'\n###\s+\d+\.\s+', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title:
            continue

        # 🔴 Skip section headers (H2 with emoji markers — not real articles)
        # Strip leading non-word/non-CJK characters (emojis, symbols, spaces)
        title_stripped = re.sub(r'^[^\w\u4e00-\u9fff]+', '', title).strip()
        if title_stripped in ['设计大师与空间', '移动端 UX 与 AI', '设计工具与平台',
                               '空间与建筑', '设计系统', '本期覆盖', '今日数据',
                               '移动端UX与AI', '移动端UX', '移动端']:
            continue
        # Short Chinese-only titles (1-6 chars) are likely section headers
        if re.match(r'^[\u4e00-\u9fff]{1,6}$', title_stripped) and len(title_stripped) <= 6:
            continue

        src = url = quote = ''
        content_lines = []

        for l in lines[1:]:
            s = l.strip()
            if not s or s == '---':
                continue

            # Skip nested section headers
            if s.startswith('## ') or s.startswith('### '):
                if re.search(r'[🔥📱🏗️🧩📊🎨📐🖌️💡🎯🏛️🪑]', s[:10]):
                    continue
                if re.match(r'#{2,3}\s+\d+\b', s):
                    continue

            # Source line: **来源：Source | Date** (may have trailing **)
            m = re.match(r'\*\*来源[：:]\s*(.+?)\*{0,2}$', s)
            if m:
                src = clean_source(m.group(1))
                continue

            # Date-only line: **日期：...** (skip)
            if re.match(r'\*\*日期[：:]', s):
                continue

            # URL: 🔗 [阅读原文](url) or [阅读原文](url) or bare 🔗 url
            m = re.search(r'\[🔗?\s*(?:阅读原文|原文|原文链接)?\]\((.+?)\)', s)
            if m:
                url = clean_url(m.group(1))
                continue
            m = re.match(r'🔗\s*(https?://\S+)', s)
            if m:
                url = clean_url(m.group(1))
                continue
            # Generic markdown link [text](url)
            m = re.search(r'\[.*?\]\((.+?)\)', s)
            if m and not url:
                url = clean_url(m.group(1))
                continue

            # Quote: > 💬 text — goes to quote, NOT content
            if s.startswith('> '):
                inner = s[2:].strip()
                inner = re.sub(r'^💬\s*', '', inner)
                inner = re.sub(r'^\*\*Lucia\s*毒舌[：:]*\*{0,2}\s*', '', inner)
                inner = re.sub(r'^毒舌[^：:]*[：:]\s*', '', inner)
                if inner:
                    quote = inner if not quote else quote + ' ' + inner
                continue

            # Quote: **Lucia毒舌：text** or **Lucia 毒舌：text**
            m = re.match(r'.*毒舌[^：:]*[：:]\s*(.+)', s)
            if m:
                val = m.group(1).strip().rstrip('*')
                if val:
                    quote = val if not quote else quote + ' ' + val
                continue

            # General content (skip metadata and table rows)
            if len(s) > 5 and not s.startswith('**') and not s.startswith('|') and not s.startswith('*'):
                content_lines.append(s)

        content = ' '.join(content_lines).strip()
        items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_startup(text):
    """Parse startup MD with format: ### N. Title | **来源：** | 🔗 url | > 💬 quote
    
    Handles section headers (H2 with emoji like 🔥📡🛠️📊) by skipping them.
    Extracts source/url/quote from structured MD lines.
    """
    items = []
    # Split on ### N. or ## N. item headers
    for part in re.split(r'\n#{2,3}\s+\d*\.?\s*', text)[1:]:
        lines = part.strip().split('\n')
        title = lines[0].strip() if lines else ''
        if not title:
            continue

        # 🔴 Skip section headers (H2 with emoji markers — not real articles)
        # Strip leading non-word/non-CJK characters (emojis, symbols, spaces)
        title_stripped = re.sub(r'^[^\w\u4e00-\u9fff]+', '', title).strip()
        if title_stripped in ['今日头条', '行业风向', '创业 & 开源', '今日数据', '热点关键词',
                               '本期覆盖', '亮点一览', '数据回看', '深度分析', '快讯',
                               '创业与开源', '创业和开源', '创业·开源', '创业&开源']:
            continue
        # Short Chinese-only titles (1-6 chars) without URL-like content are section headers
        if re.match(r'^[\u4e00-\u9fff]{1,6}$', title_stripped) and len(title_stripped) <= 6:
            continue

        src = url = quote = ''
        content_lines = []

        for l in lines[1:]:
            s = l.strip()
            if not s or s == '---':
                continue

            # Skip nested section headers (## or ### within content)
            if s.startswith('## ') or s.startswith('### '):
                if re.search(r'[🔥📡🛠️📊📈🎯💡🔬🏗️📱🧩📦🎨💼🌟⚡📰💰🎬🔧🧪]', s[:10]):
                    continue
                # Also skip numbered headers like "## 10."
                if re.match(r'#{2,3}\s+\d+\b', s):
                    continue

            # Source line: **来源：Source | Date** (may have trailing **)
            m = re.match(r'\*\*来源[：:]\s*(.+?)\*{0,2}$', s)
            if not m:
                m = re.match(r'\*\*信源[：:]\s*(.+?)\*{0,2}$', s)
            if m:
                src = clean_source(m.group(1))
                continue

            # Date-only line: **日期：...** or **日期**: ... (skip, date is in published)
            if re.match(r'\*\*日期[：:]', s):
                continue

            # URL: 🔗 url or 🔗 [text](url) or bare URL
            m = re.search(r'\[🔗?\s*(?:原文|阅读原文|原文链接)?\]\((.+?)\)', s)
            if m:
                url = clean_url(m.group(1))
                continue
            # 🔗 followed by URL
            m = re.match(r'🔗\s*(https?://\S+)', s)
            if m:
                url = clean_url(m.group(1))
                continue
            # **链接**：url or **原文**：url
            m = re.search(r'\*\*(?:链接|原文)\*{0,2}[：:]\s*(https?://\S+)', s)
            if m:
                url = clean_url(m.group(1))
                continue
            # Bare URL on its own line
            m = re.match(r'^(https?://[^\s]+)$', s)
            if m and not url:
                url = clean_url(m.group(1))
                continue

            # Quote: > 💬 quote text | > 毒舌：text | > quote
            if s.startswith('> '):
                inner = s[2:].strip()
                # Strip leading emoji/prefix like 💬 or **毒舌：**
                inner = re.sub(r'^💬\s*', '', inner)
                inner = re.sub(r'^\*\*毒舌[^：:]*[：:]\*{0,2}\s*', '', inner)
                inner = re.sub(r'^毒舌[^：:]*[：:]\s*', '', inner)
                if inner:
                    quote = inner if not quote else quote + ' ' + inner
                continue

            # Quote: **毒舌：text** or **Lucia毒舌：text**
            m = re.match(r'.*毒舌[^：:]*[：:]\s*(.+)', s)
            if m:
                val = m.group(1).strip().rstrip('*')
                if val:
                    quote = val if not quote else quote + ' ' + val
                continue

            # General content (not metadata, not headers)
            if len(s) > 5 and not s.startswith('**') and not s.startswith('|'):
                content_lines.append(s)

        content = ' '.join(content_lines).strip()
        items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_industry(text):
    items = []
    lines = text.split('\n')[:30]

    # Format detection (priority order):
    # 1. New format: ### N. emoji Title with emoji blockquotes
    # 2. Old format: ## N. Title with **信源** / **原文** / **Lucia毒舌**
    # 3. Plain format: N. emoji **Title** with **来源** / **日期** / --- separators

    is_new_format = any(
        l.strip().startswith('> 💬') or l.strip().startswith('> 📅')
        for l in lines
    )
    is_old_format = bool(re.search(r'\n##\s+\d+\.\s+', text[:500]))
    is_plain_format = bool(re.search(r'\n\d+\.\s+[\U0001F300-\U0001FAFF]', text[:500]) \
                          or re.search(r'\n\d+\.\s+[\U0001F900-\U0001F9FF]', text[:500]) \
                          or re.search(r'\n\d+\.\s+[\U00010000-\U000EFFFF]', text[:500])) \
                     if not is_new_format and not is_old_format else False
    # Also detect plain format by checking for `---` separated numbered items
    if not is_new_format and not is_old_format:
        plain_matches = re.findall(r'\n(\d+)\.\s+', text[:1000])
        if len(plain_matches) >= 3 and re.search(r'\*\*来源\*\*', text[:1000]):
            is_plain_format = True

    if is_new_format:
        # New format: ### N. emoji Title with emoji blockquotes (same as AI new format)
        for part in re.split(r'\n###\s+\d+\.\s+', text)[1:]:
            plines = part.strip().split('\n')
            title = plines[0].strip() if plines else ''
            if not title: continue
            src = url = quote = ''
            content_lines = []
            for l in plines[1:]:
                s = l.strip()
                if not s or s == '---': continue
                # Source line: **来源**: Source | **日期**:
                m = re.match(r'\*\*来源\*{0,2}[：:]\s*(.+?)(?:\s*\|\s*\*\*日期)', s)
                if m:
                    src = clean_source(m.group(1))
                    continue
                # Source line: **来源**: Source alone
                m = re.match(r'\*\*来源\*{0,2}[：:]\s*(.+)', s)
                if m and not src:
                    src = clean_source(m.group(1))
                    continue
                # Quote line: > 💬 Quote text
                if s.startswith('> 💬'):
                    quote = s[4:].strip()
                    continue
                # URL: [🔗 原文链接](url)
                m = re.search(r'\[🔗\s*原文链接\]\((.+)\)', s)
                if m:
                    url = clean_url(m.group(1))
                    continue
                m = re.search(r'\[.*?\]\((.+)\)', s)
                if m and not url:
                    url = clean_url(m.group(1))
                    continue
                # Skip other blockquotes
                if s.startswith('>'):
                    continue
                # Content lines
                content_lines.append(s)
            content = ' '.join(content_lines).strip()
            items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    elif is_old_format:
        # Old format: ## N. Title with **信源** / **原文** / **Lucia毒舌**
        for part in re.split(r'\n##\s+\d+\.\s+', text)[1:]:
            plines = part.strip().split('\n')
            title = plines[0].strip() if plines else ''
            if not title: continue
            src = url = quote = ''
            for l in plines[1:]:
                s = l.strip()
                if s == '---': continue
                m = re.match(r'\*\*信源\*\*[：:]\s*(.+)', s)
                if m: src = clean_source(m.group(1)); continue
                m = re.search(r'\*\*原文\*\*[：:]\s*\[?([^\]]*)\]?\s*[\(]?\s*(https?://\S+)', s)
                if m: url = m.group(2).strip().rstrip(')'); continue
                if not url:
                    m = re.search(r'(https?://[^\s\)]+)', s)
                    if m: url = m.group(1).strip().rstrip(')'); continue
                m = re.search(r'\*\*Lucia毒舌\*\*[：:]\s*(.+)', s)
                if m: quote = m.group(1).strip(); continue
            items.append(dict(title=title, content='', quote=quote, source=src, url=url))
    elif is_plain_format:
        # Plain format: N. emoji **Title** separated by ---
        # Each item block is separated by ---
        blocks = re.split(r'\n---\s*\n', text)
        for block in blocks:
            block = block.strip()
            if not block or block.startswith('# '):
                continue
            # Skip header line / summary line
            if block.startswith('*日报生成'):
                continue
            # First line should be "N. emoji **Title**"
            blines = block.split('\n')
            first = blines[0].strip()
            m = re.match(r'(\d+)\.\s+(.*)', first)
            if not m:
                continue
            title = m.group(2).strip()
            # Strip ** markers and emoji
            title = re.sub(r'\*\*', '', title).strip()
            # Strip leading emoji (any single Unicode emoji character)
            title = re.sub(r'^[\U0001F300-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\u2600-\u27BF\uFE00-\uFE0F]\s*', '', title).strip()
            if not title:
                continue
            src = url = quote = ''
            content_lines = []
            for l in blines[1:]:
                s = l.strip()
                if not s:
                    continue
                # Source line: **来源**: Source | **日期**:
                m_src = re.match(r'\*\*来源\*{0,2}[：:]\s*(.+?)(?:\s*\|\s*\*\*日期)', s)
                if m_src:
                    src = clean_source(m_src.group(1))
                    continue
                # **来源**: Source alone
                m_src = re.match(r'\*\*来源\*{0,2}[：:]\s*(.+)', s)
                if m_src and not src:
                    src = clean_source(m_src.group(1))
                    continue
                # Quote line: > quote text
                if s.startswith('>'):
                    quote = s.lstrip('>').strip()
                    continue
                # URL: [🔗 原文链接](url)
                m_url = re.search(r'\[🔗\s*原文链接\]\((.+)\)', s)
                if m_url:
                    url = clean_url(m_url.group(1))
                    continue
                m_url = re.search(r'\[🔗\s*原文\]\((.+)\)', s)
                if m_url:
                    url = clean_url(m_url.group(1))
                    continue
                m_url = re.search(r'\[.*?\]\((.+)\)', s)
                if m_url and not url:
                    url = clean_url(m_url.group(1))
                    continue
                # Content lines
                content_lines.append(s)
            content = ' '.join(content_lines).strip()
            items.append(dict(title=title, content=content, quote=quote, source=src, url=url))
    return items

def parse_clawhub(raw_path, date_str):
    """从 raw_clawhub JSON 生成标准化条目（中文内容 + 毒舌点评）"""
    if not raw_path.exists():
        return []
    try:
        with open(raw_path) as f:
            skills = json.load(f)
    except Exception as e:
        logger.warning(f"[clawhub] 读取失败: {e}")
        return []

    if not isinstance(skills, list):
        skills = skills.get("items", [])
    if not skills:
        logger.warning("[clawhub] 技能列表为空")
        return []

    # 取 5~8 条，按 downloads + stars 加权排序
    def score(s):
        st = s.get("stats", {}) or {}
        downloads = st.get("downloads", 0) or 0
        stars = st.get("stars", 0) or 0
        return downloads * 1 + stars * 10

    skills_sorted = sorted(skills, key=score, reverse=True)
    # 去重（按 slug）
    seen = set()
    unique = []
    for s in skills_sorted:
        slug = s.get("slug", "")
        if slug and slug not in seen:
            seen.add(slug)
            unique.append(s)

    take = min(max(5, len(unique)), 8)
    selected = unique[:take]

    import random
    items = []
    for i, s in enumerate(selected):
        slug = s.get("slug", "")
        display_name = s.get("displayName", slug)
        summary = s.get("summary", "")
        tags = s.get("tags", {}) or {}
        version = tags.get("latest", "")
        stats = s.get("stats", {}) or {}
        downloads = stats.get("downloads", 0) or 0
        stars = stats.get("stars", 0) or 0

        # 中文标题：优先用 displayName，必要时做简单转译
        title = display_name.strip() if display_name else slug.replace("-", " ").title()

        # 中文摘要 (~80字)：从英文 summary 提取关键信息
        # 基础描述
        summary_short = summary[:200] if summary else f"ClawHub 技能市场收录的 {slug} 技能包"
        content = f"ClawHub 技能市场收录的开源技能包「{display_name}」"
        if version:
            content += f"（v{version}）"
        content += f"，可安装至 OpenClaw Agent 使用。"
        # 追加 summary 核心描述
        if summary:
            # 简单截取前几个描述句
            sentences = re.split(r'[.,;!?]\s*', summary)
            desc_part = ". ".join(sentences[:2]).strip()
            if len(desc_part) < len(content):
                desc_part = summary[:120].strip()
            content += f"功能要点：{desc_part}。"
        if downloads or stars:
            content += f"已累计 {downloads} 次下载"
            if stars:
                content += f"、{stars} 个 Star"
            content += "。"
        content = content[:200]
        if len(content) < 50:
            content += "可作为日常开发效率工具，按需安装体验。"

        # 毒舌点评 (15-30字)
        quote = random.choice(CLAWHUB_QUOTES)

        # uid
        key = f"{title}|ClawHub"
        uid = f"dev_{hashlib.md5(key.encode()).hexdigest()[:8]}"

        items.append({
            "title": title,
            "source": "ClawHub",
            "content": content,
            "quote": quote,
            "url": f"https://clawhub.ai/skills/{slug}",
            "published": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
            "uid": uid,
        })

    logger.info(f"[clawhub] 生成 {len(items)} 条")
    return items

PARSERS = dict(dev=parse_dev, ai=parse_ai, design=parse_design, startup=parse_startup, industry=parse_industry)

# github 和 clawhub 是直通板块：从 source JSON 读取，不做格式转换
PASSTHROUGH_SECTIONS = ["github", "clawhub"]

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

        # ── 直通板块：直接从 source JSON 读取（不解析 MD）──
        if sec in PASSTHROUGH_SECTIONS:
            source_map = {
                "github": DATA_DIR / f"github_trending_{d_short}.json",
                "clawhub": DATA_DIR / f"clawhub_trending_{d_short}.json",
            }
            src_path = source_map.get(sec)
            if src_path and src_path.exists():
                with open(src_path) as f:
                    parsed = json.load(f)
                logger.info(f"[{sec}] 直通: {len(parsed)}条")
            else:
                logger.warning(f"[{sec}] 无源数据({src_path.name if src_path else 'N/A'}), skip")
                continue
            # 直通板块直接写入最终文件，跳过 parse/enrich 逻辑
            op = OUT_DIR / f'{sec}_daily_{d_short}.json'
            with open(op, 'w') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            logger.info(f'[{sec}] {len(parsed)}条 → {op.name}')
            continue

        # ── 传统板块：raw + MD 解析 ──
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
            parsed = []
            # 🔴 修复：无MD报告时从raw数据生成更干净的条目，不直接复制raw的垃圾content
            for r in raw[:25]:
                title = r.get('title', '')
                if not title:
                    continue
                source = r.get('source', '')
                url = r.get('url', '')
                raw_content = r.get('content', '')
                # 清洗raw content：剥离HN/NL等平台的元数据格式
                cleaned = _clean_raw_content(raw_content, source)
                parsed.append(dict(
                    title=title,
                    content=cleaned if cleaned else '',
                    quote='',
                    source=source,
                    url=url
                ))
            logger.info(f"[{sec}] 无MD, 从raw取(已清洗): {len(parsed)}条")
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
                if not item.get('content'):
                    item['content'] = _clean_raw_content(r.get('content') or '', r.get('source',''))
            for f in ('title','content','quote','source','url'):
                item.setdefault(f, '')
            # 🔴 问题2: published 日期归一化（截断至10字符 YYYY-MM-DD）
            published = item.get('published', d_long)
            if len(published) > 10:
                published = published[:10]
            item['published'] = published
            # 🔴 问题3: 标题 Unicode 清洗
            item['title'] = clean_title(item.get('title', ''))



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
