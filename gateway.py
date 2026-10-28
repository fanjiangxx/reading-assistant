"""唯一的模型出口。import 时不配置全局日志、不创建客户端。"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """进程内复用一个客户端。缺密钥立刻失败。"""
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL")
    if not api_key:
        raise RuntimeError("缺少环境变量 DEEPSEEK_API_KEY，请检查项目根目录 .env")
    if not base_url:
        raise RuntimeError("缺少环境变量 DEEPSEEK_BASE_URL，请检查项目根目录 .env")
    _client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=3,
    )
    return _client


def chat(user: str, system: str) -> Iterator[Any]:
    """流式调用当前 FINRAG_MODEL。深度思考开着（厂商参数，不是通用 OpenAI 必写项）。"""
    model = os.environ.get("FINRAG_MODEL")
    if not model:
        raise RuntimeError("缺少环境变量 FINRAG_MODEL，请检查项目根目录 .env")
    try:
        client = _get_client()
        logger.info("开始调用模型")
        started = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
            stream_options={"include_usage": True},
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )

        def chunks() -> Iterator[Any]:
            usage = None
            for chunk in response:
                if chunk.usage:
                    usage = chunk.usage
                yield chunk
            elapsed = time.perf_counter() - started
            logger.info("耗时 %.3f 秒 usage=%s", elapsed, usage)

        return chunks()
    except Exception as err:
        logger.warning("调用失败：%s", err)
        raise
