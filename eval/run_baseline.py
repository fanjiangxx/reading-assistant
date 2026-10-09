import json
from pathlib import Path
from dotenv import load_dotenv

from pipeline import ask


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def collect_answer(problem: str) -> tuple[bool, str]:
    hit_ok = False
    parts = []
    for ok, _think, answer in ask(problem):
        hit_ok = ok
        if answer:
            parts.append(answer)
    return hit_ok, "".join(parts)

def numeric_match(gold: str, answer: str ) -> bool:
    g = gold.replace(" ", "").replace(",","")
    a = answer.replace(" ", "").replace(",","")
    return g in a

def main() -> None:
    path = Path(__file__).with_name("baseline_questions.json")
    items = json.loads(path.read_text(encoding="utf-8"))
    total = 0
    right = 0
    for item in items:
        if item.get("type") != "numeric":
            continue
        total += 1
        hit_ok, answer = collect_answer(item["question"])
        ok = hit_ok and numeric_match(item["gold"], answer)
        if ok:
            right += 1
        print(item["id"], "OK" if ok else "FAIL", answer[:80])
    print(f"{right}/{total} ")

if __name__ == "__main__":
    main()



