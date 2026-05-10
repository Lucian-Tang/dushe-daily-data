#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode, urlparse

try:
    from docx import Document
    from bs4 import BeautifulSoup
except ImportError as e:
    print(json.dumps({"status": "error", "error": f"缺少依赖库: {str(e)}"}, ensure_ascii=False))
    sys.exit(1)

# 内容长度上限（字符数）
MAX_CONTENT_LENGTH = 3000

# 违禁词检测接口完整 URL（可通过环境变量覆盖，便于部署侧配置网关/代理）
_DEFAULT_SENSITIVE_API_URL = "https://onetotenvip.com/story/cozeSkill/sensitiveWordSearch"


def _sensitive_word_api_url():
    return os.environ.get("XHS_SENSITIVE_WORD_API_URL", _DEFAULT_SENSITIVE_API_URL).strip() or _DEFAULT_SENSITIVE_API_URL


def _url_opener(ssl_verify=True):
    """构建 urllib Opener：ssl_verify=False 时跳过证书校验（仅用于检测接口可选降级，网页抓取应始终为 True）。"""
    if not ssl_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener()


def _http_request(url, method="GET", json_body=None, query_params=None, timeout=30, max_retries=2, ssl_verify=True):
    """
    使用标准库 urllib 发起 HTTP/HTTPS 请求（TLS 默认校验服务端证书并发送 SNI）。
    POST 时使用 application/json 正文。对 5xx 及网络类错误按 max_retries 自动重试。

    Returns:
        dict: {"status_code": int, "body": str, "headers": dict}
    """
    method_u = method.upper()
    last_error = None
    opener = _url_opener(ssl_verify)

    for attempt in range(max_retries + 1):
        try:
            full_url = url
            if method_u == "GET" and query_params:
                qs = urlencode(query_params)
                full_url = f"{url}?{qs}" if qs else url

            payload = None
            headers = {
                "Accept": "application/json, text/html, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Encoding": "identity",
            }
            if method_u == "POST":
                payload = json.dumps(json_body or {}, ensure_ascii=False).encode("utf-8")
                headers["Content-Type"] = "application/json"

            req = urllib.request.Request(
                full_url,
                data=payload,
                headers=headers,
                method=method_u,
            )

            with opener.open(req, timeout=timeout) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8", errors="replace")
                headers_dict = {k.lower(): v for k, v in resp.headers.items()}

            if status_code >= 500 and attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue

            return {"status_code": status_code, "body": body, "headers": headers_dict}

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            headers_dict = {k.lower(): v.strip() for k, v in e.headers.items()}
            if e.code >= 500 and attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue
            return {"status_code": e.code, "body": body, "headers": headers_dict}

        except urllib.error.URLError as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue
            break

    if last_error is not None:
        msg = str(last_error.reason) if getattr(last_error, "reason", None) is not None else str(last_error)
        if "timed out" in msg.lower() or msg.lower().endswith("timeout"):
            raise Exception(f"连接超时，已重试{max_retries}次仍失败")
        raise Exception(f"网络异常: {msg}，已重试{max_retries}次仍失败")
    raise Exception(f"请求失败，已重试{max_retries}次仍失败")


def extract_from_file(file_path):
    """从文件中提取文本（支持DOC、DOCX、TXT等文本类型文件）"""
    if not os.path.exists(file_path):
        raise Exception(f"文件不存在: {file_path}")

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.pdf':
        raise Exception("不支持PDF文件，请上传图片、TXT等文本类型文件")
    elif file_ext in ['.doc', '.docx']:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().strip()
    elif file_ext in ['.csv', '.md', '.log', '.json', '.xml', '.html', '.htm']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().strip()
    else:
        raise Exception(f"不支持的文件类型: {file_ext}，仅支持图片、TXT、DOC、DOCX等文本类型文件")


def extract_from_web(url):
    """
    从网页中提取文本。优先使用 Playwright 无头浏览器渲染 JS 后提取（支持 SPA），
    若不可用则回退到 urllib 拉取静态 HTML 再解析。
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # 优先尝试Playwright（支持SPA/JS动态渲染页面）
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)  # 等待JS渲染

            # 优先提取文章正文区域（常见选择器）
            article_selectors = [
                'article', '.article-content', '.article-body', '.article-detail',
                '.post-content', '.post-body', '.content-body', '.entry-content',
                '.rich_media_content', '#js_content', '.detail-content',
                '.article-content', '.news-content', '.text-content',
            ]
            text = None
            for selector in article_selectors:
                try:
                    el = page.query_selector(selector)
                    if el:
                        extracted = el.inner_text().strip()
                        if len(extracted) > 100:  # 正文区域通常较长
                            text = extracted
                            break
                except Exception:
                    continue

            # 无匹配正文区域时回退到body
            if not text:
                text = page.inner_text('body')

            browser.close()
            return text.strip()
    except Exception:
        pass  # Playwright 不可用，回退到 urllib

    # 回退：urllib HTTPS/HTTP（仅能提取静态 HTML 中的文本）
    response = _http_request(url, method="GET", timeout=30)

    if response["status_code"] >= 400:
        raise Exception(f"网页请求失败: HTTP {response['status_code']}")

    soup = BeautifulSoup(response["body"], 'html.parser')

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator='\n', strip=True)
    return text.strip()


def check_sensitive_words(content):
    """
    调用小红书违禁词检测 API（POST，application/json 正文）。

    Args:
        content: 待检测的文案内容

    Returns:
        dict: 包含检测结果和格式化 HTML 的字典
    """

    # 内容长度校验
    if len(content) > MAX_CONTENT_LENGTH:
        return {
            "status": "error",
            "platform": "小红书",
            "original_content": content[:200] + "...",
            "error": f"文案内容过长（{len(content)}字符），上限为{MAX_CONTENT_LENGTH}字符，请缩减后重试"
        }

    api_url = _sensitive_word_api_url()
    payload = {
        "content": content,
        "platform": "小红书",
        "source": "小红书违禁词查询-ClawHub"
    }

    try:
        api_ssl_verify = os.environ.get("XHS_SENSITIVE_WORD_VERIFY_SSL", "1").strip().lower() not in ("0", "false", "no")
        response = _http_request(
            api_url,
            method="POST",
            json_body=payload,
            timeout=30,
            max_retries=2,
            ssl_verify=api_ssl_verify,
        )

        status_code = response["status_code"]
        resp_body = response["body"]

        if status_code >= 400:
            raise Exception(f"HTTP请求失败: {status_code}, {resp_body[:500]}")

        # 解析响应
        resp = json.loads(resp_body)

        # API返回格式: {"code": 2000, "data": {...}, "msg": "成功"}
        api_code = resp.get("code", 0)
        if api_code != 2000:
            raise Exception(f"API业务错误: code={api_code}, msg={resp.get('msg', '未知')}")

        api_data = resp.get("data") or {}

        # 从API返回的content中提取违禁词列表
        # API格式: content中用<span class="banned-word">或<span class="sensitive-word">标记违禁词
        api_content = api_data.get("content") or ""
        original_content = api_data.get("originalContent") or content
        prohibited_words_type = api_data.get("prohibitedWordsType") or []

        # 提取违禁词文本（兼容banned-word/sensitive-word/industry-banned-word三种类名，去重）
        sensitive_words = list(dict.fromkeys(
            re.findall(r'<span class="(?:banned-word|sensitive-word|industry-banned-word)">(.*?)</span>', api_content)
        ))

        # 将所有违禁词标签样式统一替换为color:red样式
        html_content = re.sub(
            r'<span class="(?:banned-word|sensitive-word|industry-banned-word)">',
            '<span style="color:red">',
            api_content
        )

        # 过滤英文误匹配：API会将英文单词内部子串误标为违禁词（如"Glasswing"中的"ass"）
        # 从原文提取所有英文单词，若违禁词是某个英文单词的子串则视为误匹配
        english_words = re.findall(r'[A-Za-z]+', original_content)
        false_positive_words = set()
        for ew in english_words:
            for sw in sensitive_words:
                if sw.isascii() and sw.isalpha() and sw.lower() in ew.lower() and sw.lower() != ew.lower():
                    false_positive_words.add(sw)

        # 从sensitive_words中移除误匹配项
        sensitive_words = [w for w in sensitive_words if w not in false_positive_words]

        # 从html_content中移除误匹配的span标签，还原为纯文本
        for fpw in false_positive_words:
            escaped = re.escape(fpw)
            html_content = re.sub(
                rf'<span style="color:red">{escaped}</span>',
                fpw,
                html_content
            )

        result = {
            "status": "success",
            "platform": "小红书",
            "original_content": original_content,
            "sensitive_words": sensitive_words,
            "prohibited_words_type": prohibited_words_type,
            "word_count": len(sensitive_words),
            "html_content": html_content
        }

        return result

    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "platform": "小红书",
            "original_content": content,
            "error": f"响应解析失败: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "platform": "小红书",
            "original_content": content,
            "error": f"处理失败: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="小红书违禁词检测工具")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--content", help="直接传入文案文本")
    group.add_argument("--file", help="文件路径（支持TXT、DOC、DOCX等文本类型文件）")
    group.add_argument("--url", help="网页地址")

    parser.add_argument("--extract-only", action="store_true", help="仅提取文本不检测，返回提取的文本内容和长度")

    args = parser.parse_args()

    # 获取文本内容
    try:
        if args.content:
            text = args.content
        elif args.file:
            text = extract_from_file(args.file)
        elif args.url:
            text = extract_from_web(args.url)
        else:
            print(json.dumps({"status": "error", "error": "请指定输入方式：--content、--file 或 --url"}, ensure_ascii=False))
            return
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"文本提取失败: {str(e)}"}, ensure_ascii=False))
        return

    if not text:
        print(json.dumps({"status": "error", "error": "未提取到文本内容"}, ensure_ascii=False))
        return

    # 仅提取模式：返回文本内容和长度，不调用检测API
    if args.extract_only:
        print(json.dumps({"status": "extracted", "content": text, "length": len(text)}, ensure_ascii=False))
        return

    # 调用违禁词检测
    result = check_sensitive_words(text)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
