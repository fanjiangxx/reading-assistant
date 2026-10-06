# 用 PyCharm 打开本文件。第一步已过关：名单里是带 id/page/text 的假库。
# 三个键为什么存在：项目/FinRAG/目标梯子：每一步为了什么.md
from dotenv import load_dotenv

from pipeline import ask


load_dotenv()
problem = input("请输入您的问题: ")
shown_think_title = False
shown_answer_title = False
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
    if answer_piece:
        if not shown_answer_title:
            print("\n回答:")
            shown_answer_title = True
        print(answer_piece, end="", flush=True)

# --- 原写法（对照，不要取消注释和上面一起跑）---
# problem = input("请输入您的问题")
# think_first = True
# answer_first = True
# for hit_ok, think, answer in ask(problem):
#     if hit_ok:
#         if think != "":
#             if think_first:
#                 print("思考中:\n")
#                 think_first = False
#             print(think, end="")  # 没有 flush=True 时，字可能攒一会儿才出现。
#         if answer != "":
#             if answer_first:
#                 print("\n回答:\n")
#                 answer_first = False
#             print(answer, end="")
#     else:
#         print("文档中没有找到相关的证据,无法做出回答")
