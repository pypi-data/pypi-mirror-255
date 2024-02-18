#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : app
# @Time         : 2023/11/13 17:34
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 模型转发服务

from meutils.pipe import *

from fastapi import APIRouter, File, UploadFile, Query, Form
from sse_starlette import EventSourceResponse
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models.openai import acompletion_with_retry  # llm.completion_with_retry
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo
from chatllm.schemas.openai_api_protocol import ChatCompletionResponse, ChatCompletionStreamResponse

router = APIRouter()


# @app.post("/chat/completions", dependencies=[Depends(check_api_key)])
@router.post("/v1/chat/completions")
async def create_chat_completions(request: ChatCompletionRequest):
    """Creates a completion for the chat message"""

    if isinstance(request.messages, str):
        messages = [{'role': 'user', 'content': request.messages}]
    else:
        messages = request.messages

    return ChatCompletionResponse(**r)
