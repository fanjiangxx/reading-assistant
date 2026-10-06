import os
import logging
import time

from openai import OpenAI


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def chat(user, system):
    try:
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url=os.environ.get('DEEPSEEK_BASE_URL'),
            max_retries=3,
        )
        logging.info("开始调用模型")
        started = time.perf_counter()
        response = client.chat.completions.create(
            model=os.environ.get('FINRAG_MODEL'),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
            stream_options={"include_usage": True},
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )

        def chunks():
            usage = None
            for chunk in response:
                if chunk.usage:
                    usage = chunk.usage
                yield chunk
            elapsed = time.perf_counter() - started
            logging.info("耗时 %.3f 秒 usage=%s", elapsed, usage)
        return chunks()
    except Exception as err:
        logging.warning("调用失败：%s", err)
        raise



