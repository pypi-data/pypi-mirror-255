#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : ppu_utils
# @Time         : 2024/1/8 16:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 按次计费

from meutils.pipe import *
from openai import OpenAI


# @background_task
def per_create(api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = 'per'):
    openai = OpenAI(
        api_key=api_key,
        base_url=base_url or "https://api.chatllm.vip/v1",
        http_client=httpx.Client(follow_redirects=True)
    )
    return openai.chat.completions.create(model=model, messages=[{"role": "user", "content": "hi"}])


if __name__ == '__main__':
    print(per_create())
