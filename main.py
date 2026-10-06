from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import EventSourceResponse

from pipeline import ask


load_dotenv()
app = FastAPI()


@app.get("/ask", response_class=EventSourceResponse)
def ask_api(problem: str):
    shown_think_title = False
    shown_answer_title = False
    for hit_ok, think_piece, answer_piece in ask(problem):
        if not hit_ok:
            yield {"text": "知识库中没有足够证据，拒绝回答。"}
            return
        if think_piece:
            if not shown_think_title:
                yield {"text": "思考中:"}
                shown_think_title = True
            yield {"text": think_piece}
        if answer_piece:
            if not shown_answer_title:
                yield {"text": "回答:"}
                shown_answer_title = True
            yield {"text": answer_piece}

# --- 原写法（对照，不要取消注释和上面一起跑）---
# @app.get("/ask")
# def ask_api(problem: str):
#     shown_think_title = False
#     shown_answer_title = False
#     for hit_ok, think_piece, answer_piece in ask(problem):
#         if not hit_ok:
#             # 花括号里没有 键:值，这是集合，不是 JSON 对象。
#             # 函数里已有 yield，这里的 return 也不是普通 JSON 响应。
#             return {"知识库中没有足够证据，拒绝回答。"}
#         if think_piece:
#             if not shown_think_title:
#                 yield {"思考中:"}  # 集合，不是字典
#                 shown_think_title = True
#             # flush 只属于 print，yield 没有这个参数。
#             yield {think_piece}
#         if answer_piece:
#             if not shown_answer_title:
#                 yield {"\n回答:"}
#                 shown_answer_title = True
#             yield {answer_piece}
