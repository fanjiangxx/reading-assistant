"""CLI 流式演示入口。

基线评测请用 eval/run_baseline.py，不要用手点本文件代替题集跑分。
用户可见的思考/回答走 print；错误与诊断走 logging。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from pipeline import ask

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
logger = logging.getLogger(__name__)


def run_cli() -> None:
    """读入一题，流式打印思考与回答。

    `ask` 每一圈交出三个值：
    - hit_ok (bool)：是否有过门槛的检索命中
    - think_piece (str)：深度思考增量；无则空串
    - answer_piece (str)：回答增量；无则空串
    """
    problem = input("请输入您的问题: ")
    shown_think_title = False
    shown_answer_title = False
    last_was_think = False

    for hit_ok, think_piece, answer_piece in ask(problem):
        if not hit_ok:
            print("知识库中没有足够证据，拒绝回答。")
            break

        if think_piece:
            if not shown_think_title:
                print("思考中:")
                shown_think_title = True
            # flush=True：立刻显示这一小块，不要等缓冲区攒满。
            print(think_piece, end="", flush=True)
            last_was_think = True

        if answer_piece:
            if not shown_answer_title:
                # 思考片段末尾常无换行；进回答前先断行，避免粘在同一行。
                if last_was_think:
                    print()
                print("回答:")
                shown_answer_title = True
            print(answer_piece, end="", flush=True)
            last_was_think = False


def main() -> None:
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
    except Exception:
        logger.exception("CLI 演示失败")
        print("出错了，详见上方日志。", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    main()
