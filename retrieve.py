# import re
# import logging
# import json

from store import CHUNKS
from vector_store import ensure_indexed, search

# logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# logger = logging.getLogger(__name__)


def retrieve(problem):
    ensure_indexed(CHUNKS)
    hits = search(problem, k=5)
    return hits



    #旧的正则表达式写法
    # hits = []
    # for c in CHUNKS:
    #     # ensure_ascii=False：中文正常显示
    #     msg = json.dumps(c, ensure_ascii=False, indent=2)
    #     logger.info(msg)
#
    # terms = re.findall(r"[\u4e00-\u9fff]{2,}|[0-9A-Za-z.]+", problem)
    # for item in CHUNKS:
    #     for term in terms:
    #         if term in item["text"]:
    #             hits.append(item)
    #             break
    # return hits