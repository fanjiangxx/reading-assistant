import re
import logging
import json

from store import CHUNKS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def retrieve(problem):
    """
    将输入的问题通过正则与chunks里面的正文对比,若命中便保存下来
    :param problem: 输入的问题
    :return: 命中的chunks的id page text
    """
    hits = []
    for c in CHUNKS:
        # ensure_ascii=False：中文正常显示
        msg = json.dumps(c, ensure_ascii=False, indent=2)
        logger.info(msg)

    terms = re.findall(r"[\u4e00-\u9fff]{2,}|[0-9A-Za-z.]+", problem)
    for item in CHUNKS:
        for term in terms:
            if term in item["text"]:
                hits.append(item)
                break
    return hits