from retrieve import retrieve
from generate import generate


def ask(problem):
    hits = retrieve(problem)
    if not hits:
        # 生成器里要用 yield 把「没命中」交出去。
        # 只有 return 时，外面的 for 一圈都不会跑，拒答句印不出来。
        yield False, "", ""
        return

    response = generate(hits, problem)
    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        think_piece = delta.reasoning_content
        answer_piece = delta.content
        # if 变量: 会跳过 None 和空串 ''。is not None 时 '' 也会 yield 一次，入口白跑。
        if think_piece:
            yield True, think_piece, ""
        if answer_piece:
            yield True, "", answer_piece

    # --- 原写法（对照，不要取消注释和上面一起跑）---
    # hits = retrieve(problem)
    # think = ""
    # answer = ""
    # hit_ok = False
    # if hits:
    #     hit_ok = True
    #     response = generate(hits, problem)
    #     for chunk in response:
    #         think = ""
    #         answer = ""
    #         # 每圈先把 think/answer 清空，再分别 yield，容易一次交出空串。
    #         if chunk.choices[0].delta.reasoning_content is not None:
    #             yield hit_ok, chunk.choices[0].delta.reasoning_content, answer
    #         if chunk.choices[0].delta.content is not None:
    #             yield hit_ok, think, chunk.choices[0].delta.content
    # # 带 yield 的函数里，这个 return 不会变成 for 循环多出来的一圈，
    # # 没命中时上面 if hits 不进，这里又从不 yield，外面 for 直接结束。
    # return hit_ok, think, answer
