#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : smooth
# @Time         : 2023/12/21 09:40
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 加广告 去广告 平滑

from meutils.pipe import *
from meutils.queues.uniform_queue import UniformQueue

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from chatllm.schemas.openai_types import chat_completion, chat_completion_chunk, completion_keys

from meutils.decorators.retry import retrying


class Completions(object):

    def __init__(self, **client_params):
        api_key = client_params.get('api_key')
        base_url = client_params.get('base_url')
        self.completions = OpenAI(api_key=api_key, base_url=base_url).chat.completions
        self.interval = client_params.get('interval', 0.015)

        self.slogan = client_params.get('slogan', '')  # 加广告
        self.sub_pattern = client_params.get('sub_pattern')  # 去广告

    def create(self, **data):
        data = {key: data.get(key) for key in completion_keys if key in data}

        completions_create = retrying(self.completions.create, max_retries=5)
        # {
        #     "error": {
        #         "message": "bad response status code 400 (request id: 20240102085642292168498oeV9Ip0w)",
        #         "type": "upstream_error",
        #         "param": "400",
        #         "code": "bad_response_status_code"
        #     }
        # }

        # response = self.completions.create(**data)
        response = completions_create(**data)
        if data.get('stream'):
            def generator():
                for chunk in response:
                    raw_content = chunk.choices[0].delta.content or ""

                    if self.sub_pattern:
                        raw_content = re.sub(self.sub_pattern, "", raw_content)

                    for content in raw_content:
                        _chunk = chunk.model_copy(deep=True)
                        _chunk.choices[0].delta.content = content
                        yield _chunk

                if len(data.get('messages')) < 16:
                    yield self.chat_completion_chunk_slogan
                else:
                    yield chat_completion_chunk

            return UniformQueue(generator()).consumer(interval=self.interval, break_fn=self.break_fn)

        else:
            response.choices[0].message.content = response.choices[0].message.content + self.slogan
            return response

    def create_sse(self, **data):
        response = self.create(**data)
        if data.get('stream'):
            from sse_starlette import EventSourceResponse
            generator = (chunk.model_dump_json() for chunk in response)
            return EventSourceResponse(generator, ping=10000)
        return response

    @staticmethod
    def break_fn(line: ChatCompletionChunk):
        return line.choices[0].finish_reason

    # @property
    # def chat_completion_slogan(self):
    #     from chatllm.schemas.openai_types import chat_completion, chat_completion_chunk
    #
    #     chat_completion = chat_completion.model_copy(deep=True)
    #     chat_completion.choices[0].message.content = self.slogan
    #     return chat_completion

    @cached_property
    def chat_completion_chunk_slogan(self):
        from chatllm.schemas.openai_types import chat_completion, chat_completion_chunk
        chat_completion_chunk = chat_completion_chunk.model_copy(deep=True)
        chat_completion_chunk.choices[0].delta.content = self.slogan

        return chat_completion_chunk


if __name__ == '__main__':

    data = {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': '1+1'}], 'stream': True}

    completions = Completions(
        api_key='sk-s7uphlJIyJJN9isi9aE17b57Eb604c6a8b957fEf2c8f0e54',
        base_url='https://vip.zzapi.life/v1',
        slogan='\n\n#### [Xchat永远相信美好的事情即将发生](https://api.chatllm.vip/) ',
    )
    # print(completions.create(**data))
    for idx, i in enumerate(completions.create(**data)):
        # print(idx)
        print(i.choices[0].delta.content, end='')
