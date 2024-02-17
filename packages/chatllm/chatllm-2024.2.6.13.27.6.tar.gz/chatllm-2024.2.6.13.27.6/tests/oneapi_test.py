#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : oneapi_test
# @Time         : 2023/12/8 09:47
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *

from openai import OpenAI

completions = OpenAI(
    base_url=os.getenv('OPENAI_API_BASE'),
    max_retries=3
).chat.completions

_ = completions.create(
    messages=[{'role': 'user', 'content': '1+1'}],
    model='gpt-3.5-turbo',
    stream=False
)
print(_)


# "nohup python3 -m jupyterlab --ip 0.0.0.0 --port 39000 --no-browser --allow-root &"

# nohup huggingface-cli download --resume-download --local-dir-use-symlinks False infgrad/stella-large-zh-v2 --local-dir infgrad/stella-large-zh-v2 &


# nohup huggingface-cli download --resume-download --local-dir-use-symlinks False BAAI/bge-reranker-base --local-dir BAAI/bge-reranker-base &


# nohup huggingface-cli download --resume-download --local-dir-use-symlinks False deepseek-ai/deepseek-llm-7b-chat --local-dir deepseek-ai/deepseek-llm-7b-chat &


# export MODEL="01-ai/Yi-6B-200K"
# nohup huggingface-cli download --resume-download --local-dir-use-symlinks False $MODEL --local-dir $MODEL &
