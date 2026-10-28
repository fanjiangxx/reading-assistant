"""问答编排：先检索，再生成。评测与命令行共用这一层。"""

from __future__ import annotations

from collections.abc import Iterator

from retrieve import retrieve
from generate import generate


def _iter_pieces(hits: list[dict], problem: str) -> Iterator[tuple[str, str]]:
    """从已取到的 hits 流式吐出 (think_piece, answer_piece)；保证与 generate 同源。"""
    response = generate(hits, problem)
    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        think_piece = delta.reasoning_content
        answer_piece = delta.content
        # if 变量: 会跳过 None 和空串 ''。is not None 时 '' 也会 yield 一次，入口白跑。
        if think_piece:
            yield think_piece, ""
        if answer_piece:
            yield "", answer_piece


def run_once(problem: str) -> dict:
    """一次问答：hit_ok / answer / hits 同源（同一轮 retrieve + generate）。

    评测归因用这个，不要先 ask 再另调一次 retrieve。
    hit_ok：检索后仍有通过相关度门槛的命中（不是「随便 top-k 非空」）。
    返回键：hit_ok (bool)、answer (str)、hits (list)。
    """
    hits = retrieve(problem)
    if not hits:
        return {"hit_ok": False, "answer": "", "hits": []}
    parts: list[str] = []
    for _think, answer_piece in _iter_pieces(hits, problem):
        if answer_piece:
            parts.append(answer_piece)
    return {"hit_ok": True, "answer": "".join(parts), "hits": hits}


def _stream(hits: list[dict], problem: str) -> Iterator[tuple[bool, str, str]]:
    if not hits:
        yield False, "", ""
        return
    for think_piece, answer_piece in _iter_pieces(hits, problem):
        if think_piece:
            yield True, think_piece, ""
        if answer_piece:
            yield True, "", answer_piece


def begin_ask(problem: str) -> tuple[list[dict], Iterator[tuple[bool, str, str]]]:
    """检索一次，返回命中和同一轮的流。网页要用命中画原文，不要再检索第二次。"""
    hits = retrieve(problem)
    return hits, _stream(hits, problem)


def ask(problem: str) -> Iterator[tuple[bool, str, str]]:
    """流式问答。每一圈是 (hit_ok, think_piece, answer_piece)。

    hit_ok 为假时只交出一圈空片段，调用方应拒答且不再调模型。
    """
    _hits, stream = begin_ask(problem)
    yield from stream
