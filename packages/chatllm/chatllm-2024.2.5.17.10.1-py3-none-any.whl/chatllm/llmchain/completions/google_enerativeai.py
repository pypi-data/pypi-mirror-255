#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : generativeai
# @Time         : 2023/12/14 13:32
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb

from meutils.pipe import *
from meutils.cache_utils import ttl_cache
from meutils.decorators.retry import retrying

from chatllm.llmchain.utils import tiktoken_encoder
from chatllm.schemas.kimi.protocol import EventData
from chatllm.llmchain.completions import github_copilot

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

import google.generativeai as genai
from google.generativeai import GenerativeModel

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]


class Completions(github_copilot.Completions):

    def __init__(self, **client_params):
        self.client_params = client_params
        api_key = self.client_params.get('api_key')
        genai.configure(api_key=api_key or os.getenv('GOOGLE_API_KEY'))

    def create(self, messages: Union[str, List[Dict[str, Any]]], **kwargs):  # ChatCompletionRequest: 定义请求体

        data = {
            "model": 'gpt-4',
            "messages": messages if isinstance(messages, list) else [{"role": "user", "content": messages}],
            **kwargs
        }

        # logger.debug(data)

        if data.get('stream'):
            interval = 0.01
            return self.smooth_stream(interval=interval, **data)
        else:
            return self._create(**data)

    def _create(self, **data):
        response = self._post(**data)

        chunk_id = f"chatcmpl-{uuid.uuid1()}"
        created = int(time.time())
        model = data.get('model', 'kimi')  # "kimi-clk4da83qff43om28p80|clk4da83qff43om28p80"
        finish_reason = "stop"

        chunk = {
            'id': chunk_id,
            'choices': [
                {
                    'finish_reason': finish_reason,
                    'index': 0,
                    'message': {
                        'content': response.text,
                        'role': 'assistant',
                        'function_call': None,
                        'tool_calls': None},
                }
            ],
            'created': created,
            'model': model,
            'object': 'chat.completion',
            'system_fingerprint': None,
            'usage': {
                'completion_tokens': 188,
                'prompt_tokens': 1115,
                'total_tokens': 1303
            }
        }

        return ChatCompletion.model_validate(chunk)

    def _stream_create(self, **data):
        response = self._post(**data)

        chunk_id = f"chatcmpl-{uuid.uuid1()}"
        created = int(time.time())
        model = data.get('model', 'kimi')  # "kimi-clk4da83qff43om28p80|clk4da83qff43om28p80"
        finish_reason = None

        for chunk in response:
            chunk = {
                'id': chunk_id,
                'choices': [
                    {
                        'delta': {
                            'content': chunk.text,
                            'function_call': None,
                            'role': 'assistant',
                            'tool_calls': None
                        },
                        'finish_reason': finish_reason,
                        'index': 0
                    }
                ],
                'created': created,
                'model': model,
                'object': 'chat.completion.chunk',
                'system_fingerprint': None
            }
            chunk = ChatCompletionChunk.model_validate(chunk)
            # logger.debug(chunk)

            yield chunk
            # chunk.choices[0].finish_reason = 'stop' # 怎么判断
            # yield chunk

    def _post(self, **data):
        model_name = data.pop("model", "gemini-pro")
        messages = json.dumps(data.pop("messages"))  # 模拟多轮对话
        stream = data.pop("stream", False)

        generation_config = data
        # generation_config = {
        #     "temperature": 0.9,
        #     "top_p": 1,
        #     "top_k": 1,
        #     "max_output_tokens": 2048,
        # }
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # model.start
        return model.generate_content(messages, stream=stream)


if __name__ == '__main__':
    messages = [
        {'role': 'system', 'content': "你是个python专家"}, {'role': 'user', 'content': '你是谁'},
        {'role': 'assistant', 'content': '我是你的智能助手。'}, {'role': 'user', 'content': '我有点难过'},
        {'role': 'assistant', 'content': '你想让我帮你吗？'}, {'role': 'user', 'content': '帮我分担一下吧'}
    ]
