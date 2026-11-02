"""基线评测：对题集逐题调用 pipeline.run_once，按 type 判分并打印完整归因。

判分口径（本项目约定，不是 FlashRAG/RAGAS 全套）：
- numeric：去掉千分位/空格后，金标里的主数字须在回答里出现；
  允许 10% 与 10.00% 等价；金标带「近/约/接近」时，数字差 ≤1 也算对。
- text：金标按顿号/逗号拆成关键词，全部出现在回答里才算对
  （短金标无分隔符时，整段规范化后做子串包含）。
- refuse：检索未命中（hit_ok=False）算对；或回答里出现明确拒答用语算对。
  检索命中却瞎编库外公司数字 = 错。

每题打印：问题、gold、全文回答、送模证据（与回答同源）。
并写入 eval/runs/<时间戳>.jsonl。

从 finrag_min_hand 目录运行：
  python eval/run_baseline.py
  python eval/run_baseline.py --types numeric
  python eval/run_baseline.py --types text,refuse
  python eval/run_baseline.py --ids q007,q061,q062
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# 脚本在 eval/ 下；pipeline 等在上一级。终端直接跑本文件时，要把项目根放进搜索路径。
# （PyCharm 常自动加项目根，所以 IDE 里以前能 import，终端里会报 No module named 'pipeline'。）
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

from pipeline import run_once

load_dotenv(_ROOT / ".env", override=True)
logger = logging.getLogger(__name__)

_SOFT_PREFIXES = ("近", "约", "接近", "大约")
# 拒答比的是「明确不答」用意，不是背某一句固定台词。
_REFUSE_MARKERS = (
    "拒",
    "无法回答",
    "不能回答",
    "无法得知",
    "无法确定",
    "无法确认",
    "无法得出",
    "不知道",
    "没有足够",
    "知识库中无",
    "知识库中没有",
    "未找到",
    "找不到",
    "不足以",
    # 常见变体（中间夹字时，「无法得出」整串对不上）
    "无法从给定",
    "无法从提供",
    "无法根据",
    "现有知识库",
    "给定证据",
)
# 中间允许少量字：无法从…证据 / 无法根据…知识库 / 无法…知识库…回答
_REFUSE_REGEXES = (
    re.compile(r"无法从.{0,24}证据"),
    re.compile(r"无法根据.{0,24}知识库"),
    re.compile(r"无法.{0,12}知识库.{0,16}回答"),
)


def _norm_text(s: str) -> str:
    s = (
        s.replace(",", "")
        .replace("，", "")
        .replace(" ", "")
        .replace("\u3000", "")
        .replace("％", "%")
        .replace("“", "")
        .replace("”", "")
        .replace('"', "")
        .replace("'", "")
    )
    return s


def _numbers(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]


def numeric_match(gold: str, answer: str) -> bool:
    """数字题：比的是规范化后的主数字（及单位痕迹），不是整句一字不差。"""
    g_raw = _norm_text(gold)
    a = _norm_text(answer)
    soft = False
    g = g_raw
    for prefix in _SOFT_PREFIXES:
        if g.startswith(prefix):
            soft = True
            g = g[len(prefix) :]
            break

    if g and g in a:
        return True

    g_nums = _numbers(g)
    if not g_nums:
        return bool(g) and g in a

    target = g_nums[0]
    need_percent = "%" in g
    for n in _numbers(a):
        if need_percent and "%" not in a and "百分之" not in answer:
            continue
        if abs(n - target) < 1e-6:
            return True
        if abs(n - target) < 0.01:  # 10 vs 10.00
            return True
        if soft and abs(n - target) <= 1.0:  # 近50% ↔ 约49%/50%/51%
            return True
    return False


def text_match(gold: str, answer: str) -> bool:
    """文本题：关键词全覆盖；无分隔符时整段包含。"""
    a = _norm_text(answer)
    g = _norm_text(gold)
    parts = [p for p in re.split(r"[、，,；;]", gold) if p.strip()]
    if len(parts) <= 1:
        return bool(g) and g in a
    return all(_norm_text(p) in a for p in parts)


def refuse_match(hit_ok: bool, answer: str) -> bool:
    """拒答题：应拒答。检索没命中，或回答含明确拒答用意（词表或宽松模式）。"""
    if not hit_ok:
        return True
    if any(m in answer for m in _REFUSE_MARKERS):
        return True
    return any(rx.search(answer) for rx in _REFUSE_REGEXES)


def grade(item: dict, hit_ok: bool, answer: str) -> bool:
    t = item.get("type")
    if t == "numeric":
        return hit_ok and numeric_match(item["gold"], answer)
    if t == "text":
        return hit_ok and text_match(item["gold"], answer)
    if t == "refuse":
        return refuse_match(hit_ok, answer)
    raise ValueError(f"未知 type: {t!r}（题 {item.get('id')}）")


def _safe_print(text: str) -> None:
    """Windows 控制台常是 GBK，PDF 切块里偶发特殊字符会 UnicodeEncodeError。"""
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((text + "\n").encode(enc, errors="replace"))


def _print_case(item: dict, hit_ok: bool, answer: str, hits: list, ok: bool) -> None:
    sep = "=" * 72
    _safe_print(sep)
    _safe_print(
        f"{item['id']}\t{item.get('type')}\t"
        f"{'OK' if ok else 'FAIL'}\thit={hit_ok}"
    )
    _safe_print("--- 问题 ---")
    _safe_print(item["question"])
    _safe_print("--- gold ---")
    _safe_print(f"{item.get('gold')}")
    _safe_print(f"source_page: {item.get('source_page')}")
    _safe_print("--- 模型回答（全文） ---")
    _safe_print(answer if answer else "(空)")
    _safe_print("--- 证据（送入 generate 的 top-k，与回答同源） ---")
    if not hits:
        _safe_print("(无命中)")
    else:
        for i, hit in enumerate(hits, 1):
            _safe_print(f"[{i}] id={hit.get('id')}  page={hit.get('page')}")
            _safe_print(hit.get("text") or "")
            _safe_print("")


def main() -> None:
    parser = argparse.ArgumentParser(description="FinRAG 基线评测")
    parser.add_argument(
        "--types",
        default="numeric,text,refuse",
        help="逗号分隔，如 numeric 或 text,refuse",
    )
    parser.add_argument(
        "--ids",
        default="",
        help="只跑这些题号，逗号分隔；空=按 type 过滤后的全部",
    )
    args = parser.parse_args()
    want_types = {x.strip() for x in args.types.split(",") if x.strip()}
    want_ids = {x.strip() for x in args.ids.split(",") if x.strip()}

    path = Path(__file__).with_name("baseline_questions.json")
    items = json.loads(path.read_text(encoding="utf-8"))

    runs_dir = Path(__file__).with_name("runs")
    runs_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = runs_dir / f"{stamp}.jsonl"

    total = 0
    right = 0
    by_type: dict[str, list[int]] = {}

    with jsonl_path.open("w", encoding="utf-8") as out:
        for item in items:
            t = item.get("type")
            if t not in want_types:
                continue
            if want_ids and item["id"] not in want_ids:
                continue

            total += 1
            result = run_once(item["question"])
            hit_ok = result["hit_ok"]
            answer = result["answer"]
            hits = result["hits"]
            ok = grade(item, hit_ok, answer)
            if ok:
                right += 1

            bucket = by_type.setdefault(t, [0, 0])
            bucket[1] += 1
            if ok:
                bucket[0] += 1

            # 先写 jsonl，再打印：控制台编码炸了也不丢本题记录
            record = {
                "id": item["id"],
                "type": t,
                "ok": ok,
                "hit_ok": hit_ok,
                "question": item["question"],
                "gold": item.get("gold"),
                "source_page": item.get("source_page"),
                "answer": answer,
                "hits": [
                    {
                        "id": h.get("id"),
                        "page": h.get("page"),
                        "text": h.get("text") or "",
                    }
                    for h in hits
                ],
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

            _print_case(item, hit_ok, answer, hits, ok)

    _safe_print("=" * 72)
    _safe_print(f"合计 {right}/{total}")
    for t, (r, n) in sorted(by_type.items()):
        _safe_print(f"  {t}: {r}/{n}")
    _safe_print(f"jsonl: {jsonl_path}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
    except Exception:
        logger.exception("评测失败")
        print("出错了，详见上方日志。", file=sys.stderr)
        raise SystemExit(1) from None
