"""把检索命中拼进提示，交给模型流式生成。"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from gateway import chat


def generate(hits: list[dict], problem: str) -> Iterator[Any]:
    """返回模型流。证据行格式为 [id p.页码] 正文。"""
    lines = []
    for hit in hits:
        lines.append(f"[{hit['id']} p.{hit['page']}] {hit['text']}")
    user = f"问题：{problem}\n\n证据：\n" + "\n".join(lines)
    system = (
        "你只能根据下面给出的证据回答。"
        "回答里写明出处（用证据里的 id 与页码）。"
        "证据不足以回答时，明确说不知道或无法从知识库得出，不要编造。"
    )
    return chat(user, system)
