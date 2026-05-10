#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import socket
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse

try:
    from docx import Document
    from bs4 import BeautifulSoup
except ImportError as e:
    print(json.dumps({"status": "error", "error": f"缺少依赖库: {str(e)}"}, ensure_ascii=False))
    sys.exit(1)

# API单次查询最大字符数
MAX_CONTENT_LENGTH = 3000

# 内容总字数上限（超过此值直接提示用户手动分批，不执行检测）
MAX_TOTAL_LENGTH = 10000

# 违禁词检测 HTTPS API：不在仓库中内置第三方域名，由部署方通过环境变量或本地 JSON 配置（见 _resolve_sensitive_word_api_config）
DEFAULT_API_PATH = "/story/cozeSkill/sensitiveWordSearch"
DEFAULT_API_PORT = 443
API_CONFIG_FILENAME = "gzh_sensitive_word_api.json"
API_CONFIG_EXAMPLE_FILENAME = "gzh_sensitive_word_api.example.json"


def _load_api_config_dict(data):
    """从 dict 解析 API 配置；失败返回 (None, error_message)。"""
    if not isinstance(data, dict):
        return None, "API 配置必须是 JSON 对象"
    host = str(data.get("host", "")).strip()
    if not host:
        return None, '配置中缺少非空 "host" 字段'
    try:
        port = int(data.get("port", DEFAULT_API_PORT) or DEFAULT_API_PORT)
    except (TypeError, ValueError):
        return None, '"port" 必须是整数'
    path = str(data.get("path") or DEFAULT_API_PATH).strip() or DEFAULT_API_PATH
    host_header = str(data.get("host_header") or host).strip() or host
    return {"host": host, "port": port, "path": path, "host_header": host_header}, None


def _resolve_sensitive_word_api_config():
    """
    解析检测 API 接入点（Host / Path 等），优先级：
    1) 环境变量 GZH_SENSITIVE_WORD_API_HOST（及可选 PORT、PATH、HOST_HEADER）
    2) 环境变量 GZH_SENSITIVE_WORD_API_CONFIG 指向的 JSON 文件路径
    3) 与本脚本同目录下的 gzh_sensitive_word_api.json

    不在代码或仓库中写死第三方域名，便于 Skill 开源分发与合规审计。
    """
    env_host = os.environ.get("GZH_SENSITIVE_WORD_API_HOST", "").strip()
    if env_host:
        try:
            port = int(os.environ.get("GZH_SENSITIVE_WORD_API_PORT", str(DEFAULT_API_PORT)) or DEFAULT_API_PORT)
        except ValueError:
            return None, "环境变量 GZH_SENSITIVE_WORD_API_PORT 必须是整数"
        path = (os.environ.get("GZH_SENSITIVE_WORD_API_PATH") or DEFAULT_API_PATH).strip() or DEFAULT_API_PATH
        host_header = os.environ.get("GZH_SENSITIVE_WORD_API_HOST_HEADER", "").strip() or env_host
        return {"host": env_host, "port": port, "path": path, "host_header": host_header}, None

    script_dir = Path(__file__).resolve().parent
    config_path = None
    env_config = os.environ.get("GZH_SENSITIVE_WORD_API_CONFIG", "").strip()
    if env_config:
        config_path = Path(env_config).expanduser()
    else:
        config_path = script_dir / API_CONFIG_FILENAME

    if config_path.is_file():
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            return None, f"读取 API 配置文件失败 ({config_path}): {e}"
        cfg, err = _load_api_config_dict(data)
        if err:
            return None, f"{config_path.name}: {err}"
        return cfg, None

    example_name = API_CONFIG_EXAMPLE_FILENAME
    return None, (
        "未配置违禁词检测 API：本脚本不在仓库中内置第三方服务器域名。"
        "请设置环境变量 GZH_SENSITIVE_WORD_API_HOST，"
        f"或设置 GZH_SENSITIVE_WORD_API_CONFIG 指向 JSON 配置文件，"
        f"或将 {API_CONFIG_FILENAME} 放在脚本同目录（可参考 {example_name}）。"
    )


def _https_get_no_sni(host, port, path, params_dict, host_header, timeout=30, max_retries=2):
    """
    使用原生 socket + ssl 手动发送 HTTPS GET 请求，不发送 SNI（wrap_socket 不传 server_hostname）。
    通过 Host 头指定目标站点，绕过 CDN/ICP 基于 SNI 的拦截。
    支持自动重试：5xx、超时、连接重置等场景自动重试。

    Args:
        host: 目标服务器IP或域名
        port: 端口号
        path: 请求路径
        params_dict: Query参数字典
        host_header: HTTP Host头的值
        timeout: 超时秒数
        max_retries: 最大重试次数（不含首次请求）

    Returns:
        dict: {"status_code": int, "body": str, "headers": dict}
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            result = _do_https_get(host, port, path, params_dict, host_header, timeout)

            # 5xx 自动重试
            if result["status_code"] >= 500 and attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue

            return result

        except (socket.timeout, ConnectionResetError, ConnectionRefusedError, OSError) as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue
            break

    # 所有重试耗尽，抛出最后一次异常
    if last_error:
        if isinstance(last_error, socket.timeout):
            raise Exception(f"连接超时，已重试{max_retries}次仍失败")
        elif isinstance(last_error, ConnectionResetError):
            raise Exception(f"连接被重置，已重试{max_retries}次仍失败")
        elif isinstance(last_error, ConnectionRefusedError):
            raise Exception(f"连接被拒绝，已重试{max_retries}次仍失败")
        else:
            raise Exception(f"网络异常: {str(last_error)}，已重试{max_retries}次仍失败")


def _do_https_get(host, port, path, params_dict, host_header, timeout):
    """单次HTTPS GET请求执行"""
    query_string = urlencode(params_dict)
    full_path = f"{path}?{query_string}" if query_string else path

    # 构建原始HTTP请求
    raw_request = (
        f"GET {full_path} HTTP/1.1\r\n"
        f"Host: {host_header}\r\n"
        f"Connection: close\r\n"
        f"Accept: application/json, */*\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        f"\r\n"
    ).encode("utf-8")

    # 创建socket连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))

        # wrap_socket 不传 server_hostname → 不发送 SNI
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ssl_sock = context.wrap_socket(sock)  # 故意不传 server_hostname

        # 发送请求
        ssl_sock.sendall(raw_request)

        # 接收响应
        response_data = b""
        while True:
            try:
                chunk = ssl_sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            except socket.timeout:
                break

        ssl_sock.close()

        # 解析响应
        response_text = response_data.decode("utf-8", errors="replace")

        # 分离头部和正文
        header_end = response_text.find("\r\n\r\n")
        if header_end == -1:
            return {"status_code": 0, "body": response_text, "headers": {}}

        header_section = response_text[:header_end]
        body = response_text[header_end + 4:]

        # 解析状态行
        status_line = header_section.split("\r\n")[0]
        status_code = int(status_line.split(" ")[1]) if len(status_line.split(" ")) >= 2 else 0

        # 解析响应头
        headers_dict = {}
        for line in header_section.split("\r\n")[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers_dict[key.strip().lower()] = value.strip()

        # 处理Transfer-Encoding: chunked
        if headers_dict.get("transfer-encoding", "").lower() == "chunked":
            body = _decode_chunked(body)

        # 处理Content-Encoding: gzip
        if headers_dict.get("content-encoding", "").lower() == "gzip":
            import gzip
            try:
                body = gzip.decompress(body.encode("latin-1")).decode("utf-8", errors="replace")
            except Exception:
                pass

        return {"status_code": status_code, "body": body, "headers": headers_dict}

    except socket.gaierror as e:
        raise Exception(f"DNS解析失败: {str(e)}")
    except socket.timeout as e:
        raise e
    except ConnectionResetError as e:
        raise e
    except ConnectionRefusedError as e:
        raise e
    except Exception as e:
        raise Exception(f"请求异常: {str(e)}")
    finally:
        sock.close()


def _decode_chunked(body):
    """解码chunked传输编码"""
    decoded = ""
    remaining = body
    while remaining:
        chunk_end = remaining.find("\r\n")
        if chunk_end == -1:
            break
        size_str = remaining[:chunk_end].strip()
        if not size_str:
            break
        try:
            chunk_size = int(size_str, 16)
        except ValueError:
            break
        if chunk_size == 0:
            break
        remaining = remaining[chunk_end + 2:]
        decoded += remaining[:chunk_size]
        remaining = remaining[chunk_size + 2:]
    return decoded


def _do_https_post(host, port, path, body_data, content_type, host_header, timeout):
    """单次HTTPS POST请求执行"""
    body_bytes = body_data.encode("utf-8")

    # 构建原始HTTP请求
    raw_request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host_header}\r\n"
        f"Connection: close\r\n"
        f"Accept: application/json, */*\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    # 创建socket连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))

        # wrap_socket 不传 server_hostname → 不发送 SNI
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ssl_sock = context.wrap_socket(sock)  # 故意不传 server_hostname

        # 发送请求
        ssl_sock.sendall(raw_request)

        # 接收响应
        response_data = b""
        while True:
            try:
                chunk = ssl_sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            except socket.timeout:
                break

        ssl_sock.close()

        # 解析响应
        response_text = response_data.decode("utf-8", errors="replace")

        # 分离头部和正文
        header_end = response_text.find("\r\n\r\n")
        if header_end == -1:
            return {"status_code": 0, "body": response_text, "headers": {}}

        header_section = response_text[:header_end]
        body = response_text[header_end + 4:]

        # 解析状态行
        status_line = header_section.split("\r\n")[0]
        status_code = int(status_line.split(" ", 2)[1]) if len(status_line.split(" ", 2)) >= 2 else 0

        # 解析响应头
        headers_dict = {}
        for line in header_section.split("\r\n")[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers_dict[key.strip().lower()] = value.strip()

        # 处理分块传输
        if headers_dict.get("transfer-encoding", "").lower() == "chunked":
            body = _decode_chunked(body)

        # 处理Content-Encoding: gzip
        if headers_dict.get("content-encoding", "").lower() == "gzip":
            import gzip
            try:
                body = gzip.decompress(body.encode("latin-1")).decode("utf-8", errors="replace")
            except Exception:
                pass

        return {"status_code": status_code, "body": body, "headers": headers_dict}

    except socket.gaierror as e:
        raise Exception(f"DNS解析失败: {str(e)}")
    except socket.timeout as e:
        raise e
    except ConnectionResetError as e:
        raise e
    except ConnectionRefusedError as e:
        raise e
    except Exception as e:
        raise Exception(f"请求异常: {str(e)}")
    finally:
        sock.close()


def _https_post_no_sni(host, port, path, body_data, content_type, host_header, timeout=30, max_retries=2):
    """
    使用原生 socket + ssl 手动发送 HTTPS POST 请求，不发送 SNI（wrap_socket 不传 server_hostname）。
    通过 Host 头指定目标站点，绕过 CDN/ICP 基于 SNI 的拦截。
    自动重试：遇到5xx、超时、连接重置等场景最多重试max_retries次。
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            result = _do_https_post(host, port, path, body_data, content_type, host_header, timeout)

            # 5xx错误自动重试
            if result["status_code"] >= 500 and attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue

            return result

        except (socket.timeout, ConnectionResetError, ConnectionRefusedError, OSError) as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))
                continue
            break

    # 所有重试耗尽，抛出最后一次异常
    if last_error:
        if isinstance(last_error, socket.timeout):
            raise Exception(f"连接超时，已重试{max_retries}次仍失败")
        elif isinstance(last_error, ConnectionResetError):
            raise Exception(f"连接被重置，已重试{max_retries}次仍失败")
        elif isinstance(last_error, ConnectionRefusedError):
            raise Exception(f"连接被拒绝，已重试{max_retries}次仍失败")
        else:
            raise Exception(f"网络异常: {str(last_error)}，已重试{max_retries}次仍失败")


def extract_from_file(file_path):
    """从文件中提取文本（支持DOC、DOCX、TXT等文本类型文件）"""
    if not os.path.exists(file_path):
        raise Exception(f"文件不存在: {file_path}")

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in ['.doc', '.docx']:
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
    从网页中提取文本。优先使用Playwright无头浏览器渲染JS后提取（支持SPA页面），
    若Playwright不可用则回退到socket+ssl方式。
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
        pass  # Playwright不可用，回退到socket方式

    # 回退：socket+ssl无SNI方式（仅能提取静态HTML中的文本）
    parsed = urlparse(url)
    host = parsed.netloc
    port = 443 if parsed.scheme == 'https' else 80
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query

    response = _https_get_no_sni(
        host=host,
        port=port,
        path=path,
        params_dict={},
        host_header=host,
        timeout=30
    )

    if response["status_code"] >= 400:
        raise Exception(f"网页请求失败: HTTP {response['status_code']}")

    soup = BeautifulSoup(response["body"], 'html.parser')

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator='\n', strip=True)
    return text.strip()


def check_sensitive_words(content):
    """
    调用公众号违禁词检测API（POST方式，参数通过请求体传递）

    Args:
        content: 待检测的文案内容

    Returns:
        dict: 包含检测结果和格式化HTML的字典
    """
    api_cfg, api_err = _resolve_sensitive_word_api_config()
    if api_err:
        return {
            "status": "error",
            "platform": "公众号",
            "original_content": content,
            "error": api_err,
        }

    # 内容长度校验
    if len(content) > MAX_CONTENT_LENGTH:
        return {
            "status": "error",
            "platform": "公众号",
            "original_content": content[:200] + "...",
            "error": f"文案内容过长（{len(content)}字符），单次上限为{MAX_CONTENT_LENGTH}字符，请缩减后重试"
        }

    # POST请求参数（JSON格式）
    params = {
        "content": content,
        "platform": "公众号",
        "source": "公众号违禁词查询-ClawHub"
    }
    body_data = json.dumps(params, ensure_ascii=False)

    try:
        # 发起HTTPS POST请求（不发送SNI，参数通过请求体传递，自动重试）
        response = _https_post_no_sni(
            host=api_cfg["host"],
            port=api_cfg["port"],
            path=api_cfg["path"],
            body_data=body_data,
            content_type="application/json; charset=utf-8",
            host_header=api_cfg["host_header"],
            timeout=30,
            max_retries=2
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
            "platform": "公众号",
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
            "platform": "公众号",
            "original_content": content,
            "error": f"响应解析失败: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "platform": "公众号",
            "original_content": content,
            "error": f"处理失败: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="公众号违禁词检测工具")

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
