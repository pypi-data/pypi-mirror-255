#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : ppu_utils
# @Time         : 2024/1/8 16:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 按次计费

from openai import OpenAI

from meutils.pipe import *
from chatllm.schemas.openai_types import chat_completion_chunk, completion_keys
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest


def to_openai_completion_params(request: Union[dict, ChatCompletionRequest]):
    """
        print(to_openai_completion_params(ChatCompletionRequest(model='gpt')))
    :param request:
    :return:
    """
    data = copy.deepcopy(request)
    if isinstance(request, ChatCompletionRequest):
        data = request.model_dump()

    extra_body = {}
    for key in list(data):
        if key not in completion_keys:
            extra_body.setdefault(key, data.pop(key))

    data['extra_body'] = extra_body  # 拓展字段

    return data


# @background_task
def per_create(api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = 'per'):
    openai = OpenAI(
        api_key=api_key,
        base_url=base_url or "https://api.chatllm.vip/v1",
        http_client=httpx.Client(follow_redirects=True)
    )
    return openai.chat.completions.create(model=model, messages=[{"role": "user", "content": "hi"}])


def openai_stream2sse(stream_response):
    from sse_starlette import EventSourceResponse
    def gen():
        for chunk in stream_response:
            if chunk.choices[0].finish_reason == "stop":
                return chunk.model_dump_json()
            yield chunk.model_dump_json()

    return EventSourceResponse(gen(), ping=10000)  # sse_response


if __name__ == '__main__':
    print(per_create())
