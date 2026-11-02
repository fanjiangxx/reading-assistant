"""网页入口：首页 + 流式问答。评测请用 eval/run_baseline.py。"""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import EventSourceResponse, FileResponse
from fastapi.sse import ServerSentEvent

from pipeline import begin_ask

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env", override=True)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/")
def home():
    """读书页：提问、回答、右侧原文。"""
    return FileResponse(_ROOT / "static" / "index.html")


@app.get("/ask", response_class=EventSourceResponse)
def ask_api(problem: str):
    """先发 event=sources（页码和原文），再发 event=token（回答增量）。"""
    text = (problem or "").strip()
    if not text:
        yield ServerSentEvent(raw_data="请先写一个问题。", event="token")
        yield ServerSentEvent(raw_data="ok", event="done")
        return

    shown_think_title = False
    shown_answer_title = False
    last_was_think = False
    try:
        hits, stream = begin_ask(text)
        yield ServerSentEvent(
            event="sources",
            data=[
                {
                    "id": hit.get("id"),
                    "page": hit.get("page"),
                    "text": hit.get("text") or "",
                }
                for hit in hits
            ],
        )
        for hit_ok, think_piece, answer_piece in stream:
            if not hit_ok:
                yield ServerSentEvent(
                    raw_data="知识库中没有足够证据，拒绝回答。",
                    event="token",
                )
                yield ServerSentEvent(raw_data="refused", event="done")
                return
            if think_piece:
                if not shown_think_title:
                    yield ServerSentEvent(raw_data="思考中:\n", event="token")
                    shown_think_title = True
                yield ServerSentEvent(raw_data=think_piece, event="token")
                last_was_think = True
            if answer_piece:
                if not shown_answer_title:
                    if last_was_think:
                        yield ServerSentEvent(raw_data="\n", event="token")
                    yield ServerSentEvent(raw_data="回答:\n", event="token")
                    shown_answer_title = True
                yield ServerSentEvent(raw_data=answer_piece, event="token")
                last_was_think = False
        yield ServerSentEvent(raw_data="ok", event="done")
    except Exception:
        logger.exception("网页问答失败")
        yield ServerSentEvent(raw_data="出错了，详见服务端日志。", event="token")
        yield ServerSentEvent(raw_data="error", event="done")


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    uvicorn.run(app, host="127.0.0.1", port=8000)
