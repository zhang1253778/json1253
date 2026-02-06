#!/usr/bin/env python3
"""JSON parser with repair, formatting and minifying support."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


_COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE | re.DOTALL)
_UNQUOTED_KEY_RE = re.compile(r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)')
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def strip_comments(text: str) -> str:
    """Remove // and /* */ comments."""
    return _COMMENT_RE.sub("", text)


def quote_unquoted_keys(text: str) -> str:
    """Wrap unquoted object keys with double quotes."""

    def repl(match: re.Match[str]) -> str:
        prefix, key, suffix = match.groups()
        return f'{prefix}"{key}"{suffix}'

    return _UNQUOTED_KEY_RE.sub(repl, text)


def remove_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ]."""
    return _TRAILING_COMMA_RE.sub(r"\1", text)


def convert_single_quotes(text: str) -> str:
    """Convert single-quoted strings to valid JSON double-quoted strings."""
    result: list[str] = []
    i = 0
    n = len(text)
    in_double = False
    escape = False

    while i < n:
        ch = text[i]
        if in_double:
            result.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_double = False
            i += 1
            continue

        if ch == '"':
            in_double = True
            result.append(ch)
            i += 1
            continue

        if ch == "'":
            i += 1
            converted: list[str] = ['"']
            escaped = False
            while i < n:
                c = text[i]
                if escaped:
                    converted.append(c)
                    escaped = False
                elif c == "\\":
                    converted.append("\\")
                    escaped = True
                elif c == "'":
                    converted.append('"')
                    i += 1
                    break
                elif c == '"':
                    converted.append('\\"')
                else:
                    converted.append(c)
                i += 1
            result.extend(converted)
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def repair_json_text(text: str) -> str:
    """Apply common fixes to non-strict JSON text."""
    text = text.lstrip("\ufeff")
    text = strip_comments(text)
    text = convert_single_quotes(text)
    text = quote_unquoted_keys(text)
    text = remove_trailing_commas(text)
    return text


def parse_json_with_repair(text: str) -> Any:
    """Parse JSON, trying repair rules when strict parsing fails."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = repair_json_text(text)
        return json.loads(repaired)


def format_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent) + "\n"


def minify_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="解析 JSON 并尝试修复常见格式问题，支持格式化和压缩输出。"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="输入文件路径，不传则从标准输入读取",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=("format", "minify"),
        default="format",
        help="输出模式：format(格式化) 或 minify(压缩)",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        default=2,
        help="格式化缩进空格数（仅 format 模式生效）",
    )
    return parser


def read_input(path: str | None) -> str:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        raw = read_input(args.input)
        data = parse_json_with_repair(raw)
        if args.mode == "minify":
            sys.stdout.write(minify_json(data))
        else:
            sys.stdout.write(format_json(data, indent=args.indent))
        return 0
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"JSON 解析失败，修复后仍无效: {exc}\n")
        return 1
    except OSError as exc:
        sys.stderr.write(f"文件读取失败: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
