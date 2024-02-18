#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_types
# @Time         : 2023/12/19 09:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

completion_keys = get_function_params()


class SpeechCreateRequest(BaseModel):
    input: str
    model: str = 'tts'
    voice: str = "alloy"
    response_format: Literal["mp3", "opus", "aac", "flac"] = "mp3"
    speed: float = 1


# todo: 结构体

chat_completion = {
    "id": "chatcmpl-id",
    "object": "chat.completion",
    "created": 0,
    "model": "LLM",
    "choices": [
        {
            "message": {"role": "assistant", "content": ''},
            "index": 0,
            "finish_reason": "stop",
            "logprobs": None
        }
    ],
    "usage": {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}

}

chat_completion_chunk = {
    "id": "chatcmpl-id",
    "object": "chat.completion.chunk",
    "created": 0,
    "model": "LLM",
    "choices": [
        {
            "delta": {"role": "assistant", "content": ''},
            "index": 0,
            "finish_reason": None,
            "logprobs": None
        }
    ]
}

# 通用
chat_completion = ChatCompletion.model_validate(chat_completion)
chat_completion_chunk = ChatCompletionChunk.model_validate(chat_completion_chunk)
chat_completion_chunk_stop = chat_completion_chunk.model_copy(deep=True)
chat_completion_chunk_stop.choices[0].finish_reason = "stop"

# ONEAPI_SLOGAN
ONEAPI_SLOGAN = os.getenv("ONEAPI_SLOGAN", "\n\n[永远相信美好的事情即将发生.](https://api.chatllm.vip/)\n\n")

chat_completion_slogan = chat_completion.model_copy(deep=True)
chat_completion_slogan.choices[0].message.content = ONEAPI_SLOGAN

chat_completion_chunk_slogan = chat_completion_chunk.model_copy(deep=True)
chat_completion_chunk_slogan.choices[0].delta.content = ONEAPI_SLOGAN

# ERROR
chat_completion_error = chat_completion.model_copy(deep=True)
chat_completion_chunk_error = chat_completion_chunk.model_copy(deep=True)

# PPU
chat_completion_per = chat_completion.model_copy(deep=True)
chat_completion_per.choices[0].message.content = "按次收费"
chat_completion_per.choices[0].finish_reason = "stop"
chat_completion_chunk_ppu = chat_completion_chunk.model_copy(deep=True)
chat_completion_chunk_ppu.choices[0].delta.content = "按次收费"


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]] = [{'role': 'user', 'content': 'hi'}]
    temperature: Optional[float] = 0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    max_tokens: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

    # extra
    # extra_headers: Headers | None = None,
    # extra_query: Query | None = None,
    extra_body: dict = None,
    # 拓展字段
    # additional_kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "hi"
                        }
                    ],
                    "stream": False
                },

                # url
                {
                    "model": "url-gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "总结一下https://mp.weixin.qq.com/s/Otl45GViytuAYPZw3m7q9w"
                        }
                    ],
                    "stream": False
                }
            ]
        }
    }


class ImageRequest(BaseModel):
    prompt: str
    model: str = 'dall-e-3'
    n: int = 1
    quality: str = 'standard'
    response_format: Literal["url", "b64_json"] = "url"
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = '1792x1024'  # 测试默认值
    style: Literal["vivid", "natural"] = "vivid"
    extra_body: dict = {}


model_config = {
    "json_schema_extra": {
        "examples": [
            {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": "hi"
                    }
                ],
                "stream": False
            },

            # url
            {
                "model": "url-gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": "总结一下https://mp.weixin.qq.com/s/Otl45GViytuAYPZw3m7q9w"
                    }
                ],
                "stream": False
            },

            {
                "model": "chat-dall-e-3",
                "messages": [
                    {
                        "role": "user",
                        "content": "总结一下https://mp.weixin.qq.com/s/Otl45GViytuAYPZw3m7q9w"
                    }
                ],
                "stream": False
            }
        ]
    }
}

if __name__ == '__main__':
    # data = {"stream": True, "model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "你好"}]}
    # print(ChatCompletionRequest(request=data).request)
    # print(chat_completion_error)
    # print(chat_completion_slogan)

    pass
