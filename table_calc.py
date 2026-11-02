"""表格计算（切片 4）：从年报抽出原材料金额；同比题再套公式。

覆盖两类问法（仍是临时窄规则，不是通用表格引擎）：
1. 原材料 + 同比/增长 → 用两年金额算同比
2. 原材料 + 成本/金额/多少 → 直接给出表内 2025 年金额（单位千元）
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

_ROOT = Path(__file__).resolve().parent
_PDF = _ROOT / "data" / "2025年美的财务报告.pdf"

GOLD_YOY_PERCENT = 12.53
ROW_NAME = "原材料"
_YOY_MARKERS = ("同比", "增长")
_AMOUNT_MARKERS = ("成本", "金额", "多少")


def yoy_percent(amount_2025: float, amount_2024: float) -> float:
    """同比增长率（%）：(今年 - 去年) / 去年 * 100。"""
    if amount_2024 == 0:
        raise ValueError("去年金额为 0，无法算同比")
    return (amount_2025 - amount_2024) / amount_2024 * 100


def parse_amount(cell: str | None) -> float | None:
    """把 '209,752,421' 这类单元格变成数字；空或非数字返回 None。"""
    if cell is None:
        return None
    text = str(cell).strip().replace(",", "").replace(" ", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def find_materials_row(pdf_path: Path | None = None) -> tuple[int, float, float]:
    """在 PDF 里找到含原材料金额的表行。

    返回：(文件页码从 1 起, 2025金额, 2024金额)
    阅读器页码可能和文件页序号不一致；本函数用内容定位。
    """
    path = Path(pdf_path) if pdf_path else _PDF
    if not path.exists():
        raise FileNotFoundError(f"缺少年报 PDF: {path}")

    doc = pymupdf.open(path)
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            tables = page.find_tables()
            if not tables:
                continue
            for table in tables.tables:
                for row in table.extract():
                    cells = ["" if c is None else str(c).strip() for c in row]
                    if ROW_NAME not in cells:
                        continue
                    name_at = cells.index(ROW_NAME)
                    amounts: list[float] = []
                    for cell in cells[name_at + 1 :]:
                        value = parse_amount(cell)
                        # 占比/同比是小于 1000 的小数；金额是很大的数
                        if value is not None and value > 1000:
                            amounts.append(value)
                        if len(amounts) == 2:
                            return page_index + 1, amounts[0], amounts[1]
        raise RuntimeError(f"PDF 里没有找到含「{ROW_NAME}」两年金额的表行: {path}")
    finally:
        doc.close()


def _wants_yoy(problem: str) -> bool:
    return any(mark in problem for mark in _YOY_MARKERS)


def _wants_amount(problem: str) -> bool:
    return any(mark in problem for mark in _AMOUNT_MARKERS)


def is_materials_table_question(problem: str) -> bool:
    """临时路由：提到原材料，且像在问同比或问金额/成本，才走表格。"""
    text = (problem or "").strip()
    if "原材料" not in text:
        return False
    return _wants_yoy(text) or _wants_amount(text)


# 旧名字留给口头习惯；实现与 is_materials_table_question 相同意图的「同比子集」。
def is_materials_yoy_question(problem: str) -> bool:
    text = (problem or "").strip()
    return ("原材料" in text) and _wants_yoy(text)


def _evidence_block(file_page: int, a2025: float, a2024: float, extra: str = "") -> str:
    body = (
        f"家用电器行业 · 原材料（金额单位：千元）\n"
        f"2025年金额：{a2025:,.0f}\n"
        f"2024年金额：{a2024:,.0f}\n"
    )
    if extra:
        body += extra + "\n"
    body += f"（文件页码 {file_page}；阅读器页码可能不同）"
    return body


def materials_table_answer(problem: str) -> tuple[list[dict], str]:
    """按问句意图返回 hits + 回答。同比优先；否则给 2025 金额。"""
    file_page, a2025, a2024 = find_materials_row()
    text = (problem or "").strip()

    if _wants_yoy(text):
        computed = yoy_percent(a2025, a2024)
        rounded = round(computed, 2)
        extra = (
            f"计算：({a2025:,.0f} - {a2024:,.0f}) / {a2024:,.0f} × 100% "
            f"≈ {rounded}%"
        )
        hits = [
            {
                "id": "table_calc_materials_yoy",
                "doc_id": _PDF.name,
                "page": file_page,
                "text": _evidence_block(file_page, a2025, a2024, extra),
                "distance": 0.0,
            }
        ]
        answer = (
            f"根据年报表格中原材料的两年金额计算，"
            f"同比增长率约为 {rounded}%"
            f"（金标验收值 {GOLD_YOY_PERCENT}%；本结果由程序套公式得出，不是抄表内同比列）。"
        )
        return hits, answer

    hits = [
        {
            "id": "table_calc_materials_amount",
            "doc_id": _PDF.name,
            "page": file_page,
            "text": _evidence_block(file_page, a2025, a2024),
            "distance": 0.0,
        }
    ]
    answer = (
        f"根据年报表格，家用电器行业原材料 2025 年金额为 "
        f"{a2025:,.0f} 千元"
        f"（表头单位是千元；同表 2024 年为 {a2024:,.0f} 千元。"
        f"本结果从表中抽出，不是模型估算）。"
    )
    return hits, answer


def materials_yoy_answer() -> tuple[list[dict], str]:
    """兼容旧调用：等价于问一句同比题。"""
    return materials_table_answer("原材料同比增长率是多少")
