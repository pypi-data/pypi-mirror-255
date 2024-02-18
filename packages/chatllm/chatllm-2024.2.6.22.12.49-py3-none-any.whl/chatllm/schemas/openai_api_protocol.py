#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_api_protocol
# @Time         : 2023/7/31 10:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import time
import uuid  # import ulid 毫秒级有序
from typing import Literal, Optional, List, Dict, Any, Union

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ModelPermission(BaseModel):
    id: str = Field(default_factory=lambda: f"modelperm-{uuid.uuid1()}")
    object: str = "model_permission"
    created: int = Field(default_factory=lambda: int(time.time()))
    allow_create_engine: bool = False
    allow_sampling: bool = True
    allow_logprobs: bool = True
    allow_search_indices: bool = True
    allow_view: bool = True
    allow_fine_tuning: bool = False
    organization: str = "*"
    group: Optional[str] = None
    is_blocking: str = False


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "chatllm"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: List[ModelPermission] = []


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: Optional[int] = 0
    total_tokens: int = 0


class CompletionUsage(BaseModel):
    completion_tokens: int
    """Number of tokens in the generated completion."""

    prompt_tokens: int
    """Number of tokens in the prompt."""

    total_tokens: int
    """Total number of tokens used in the request (prompt + completion)."""


class ChatCompletionRequest(BaseModel):
    """
    prompt_filter_result.content_filter_results
    choice.content_filter_results

    todo: ['messages', 'model', 'frequency_penalty', 'function_call', 'functions', 'logit_bias', 'logprobs', 'max_tokens', 'n', 'presence_penalty', 'response_format', 'seed', 'stop', 'stream', 'temperature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user']
    """
    model: str
    messages: Union[str, List[Dict[str, str]]] = [{'role': 'user', 'content': 'hi'}]
    temperature: Optional[float] = 0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    max_tokens: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

    # 1106
    response_format: Optional[Any] = None
    function_call: Optional[Any] = None

    # 拓展字段
    additional_kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    file_id: Optional[str] = None

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


class ChatMessage(BaseModel):
    role: str
    content: str
    #
    function_call: Optional[Any] = None
    tool_calls: Optional[Any] = None
    finish_details: List[Dict[str, str]] = {'type': 'stop', 'stop': '<|fim_suffix|>'}


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid1()}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo
    # system_fingerprint: Optional[str] = None


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid1()}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseStreamChoice]

    usage: UsageInfo = Field(default_factory=lambda: UsageInfo())  # add


class TokenCheckRequestItem(BaseModel):
    model: str
    prompt: str
    max_tokens: int


class TokenCheckRequest(BaseModel):
    prompts: List[TokenCheckRequestItem]


class TokenCheckResponseItem(BaseModel):
    fits: bool
    tokenCount: int
    contextLength: int


class TokenCheckResponse(BaseModel):
    prompts: List[TokenCheckResponseItem]


class EmbeddingsRequest(BaseModel):
    model: Optional[str] = None
    engine: Optional[str] = None
    input: Union[str, List[Any]]
    user: Optional[str] = None


class EmbeddingsResponse(BaseModel):
    object: str = "list"
    data: List[Dict[str, Any]]
    model: str
    usage: UsageInfo


class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[Any]]
    suffix: Optional[str] = None
    temperature: Optional[float] = 0.7
    n: Optional[int] = 1
    max_tokens: Optional[int] = 16
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    logprobs: Optional[int] = None
    echo: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class CompletionResponseChoice(BaseModel):
    index: int
    text: str
    logprobs: Optional[int] = None
    finish_reason: Optional[Literal["stop", "length"]]


class CompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{uuid.uuid1()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionResponseChoice]
    usage: UsageInfo


class CompletionResponseStreamChoice(BaseModel):
    index: int
    text: str
    logprobs: Optional[float] = None
    finish_reason: Optional[Literal["stop", "length"]] = None


class CompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{uuid.uuid1()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionResponseStreamChoice]


#
class Result(BaseModel):
    filtered: bool = False
    severity: str = 'safe'


class ContentFilterResult(BaseModel):
    hate: Result = Field(default_factory=Result)
    self_harm: Result = Field(default_factory=Result)
    sexual: Result = Field(default_factory=Result)
    violence: Result = Field(default_factory=Result)


class PromptFilterResults(BaseModel):
    prompt_index: int
    content_filter_results: List[ContentFilterResult]


# 4v
msg = {'id': 'chatcmpl-8KOSuwpEyGLa4JQOCe7KYPKApBJKt',
       'choices': [{'finish_reason': None,
                    'index': 0,
                    'message': {
                        'content': '这张图片显示的是一片开阔的绿色草地，中间有一条木制的步道延伸至画面的远方。步道左右两侧长着茂盛的草地，草地上方是一个晴朗的天空，蓝天中点缀着少许洁白的云朵。远处可以看到若干树木的轮廓，它们构成了天际线的一部分。光线明亮，色彩对比鲜明，呈现出一种宁静和自然之美的场景。整个画面传达出平静和放松的氛围。',
                        'role': 'assistant',
                        'function_call': None,
                        'tool_calls': None},
                    'finish_details': {'type': 'stop', 'stop': '<|fim_suffix|>'}
                    }],
       'created': 1699871296,
       'model': 'gpt-4-1106-vision-preview',
       'object': 'chat.completion',
       'system_fingerprint': None,
       'usage': {'completion_tokens': 188,
                 'prompt_tokens': 1115,
                 'total_tokens': 1303}}

if __name__ == '__main__':
    import openai
    import langchain
    # openai.types
