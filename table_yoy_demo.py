"""切片 4 命令行验收：打印原材料同比计算是否对齐金标。

运行：
  .\\.venv\\Scripts\\python.exe table_yoy_demo.py
"""

from __future__ import annotations

from table_calc import GOLD_YOY_PERCENT, find_materials_row, yoy_percent


def main() -> None:
    file_page, a2025, a2024 = find_materials_row()
    computed = yoy_percent(a2025, a2024)
    rounded = round(computed, 2)
    ok = rounded == GOLD_YOY_PERCENT

    print(f"文件页码（pymupdf）: {file_page}")
    print(f"原材料 2025 金额: {a2025:,.0f}")
    print(f"原材料 2024 金额: {a2024:,.0f}")
    print(f"程序计算同比: {computed:.4f}%  → 四舍五入两位: {rounded}%")
    print(f"金标（验收）: {GOLD_YOY_PERCENT}%")
    print(f"是否对齐金标: {'是' if ok else '否'}")


if __name__ == "__main__":
    main()
