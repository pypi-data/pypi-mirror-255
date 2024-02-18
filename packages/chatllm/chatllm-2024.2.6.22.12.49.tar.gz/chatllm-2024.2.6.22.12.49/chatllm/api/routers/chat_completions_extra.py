#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : completions
# @Time         : 2023/12/19 16:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 逆向工程

from meutils.pipe import *
from meutils.notice.feishu import send_message
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials

from sse_starlette import EventSourceResponse
from fastapi import APIRouter, File, UploadFile, Query, Form, Depends, Request, HTTPException, status

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from chatllm.utils.openai_utils import to_openai_completion_params, openai_stream2sse
from chatllm.llmchain.completions import moonshot_kimi
from chatllm.llmchain.completions import deepseek
from chatllm.llmchain.applications import chaturl

from chatllm.schemas.openai_types import chat_completion_per, chat_completion_slogan, chat_completion_chunk_slogan
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo

router = APIRouter()

ChatCompletionResponse = Union[ChatCompletion, List[ChatCompletionChunk]]

send_message = lru_cache(send_message)


@router.post("/chat/completions")
async def create_chat_completions_with_ad(
    request: ChatCompletionRequest,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    api_key = auth and auth.credentials or None
    if api_key is None:
        detail = {
            "error": {
                "message": "",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_api_key",
            }
        }
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    # 空服务 按次计费 per
    if request.model.startswith(("per", "file-extract", "ocr")): return chat_completion_per

    # todo
    # if request.model.startswith(('url-',)):
    #     request.model = request.model.strip('url-')
    #     response = chaturl.Chat(api_key=api_key).create(request)  # todo: 优化
    #     return completions

    data = to_openai_completion_params(request)
    response = OpenAI(
        api_key=api_key,
        base_url='https://api.chatllm.vip/v1',
        http_client=httpx.Client(follow_redirects=True)
    ).chat.completions.create(**data)

    if request.stream:
        _ = itertools.chain((chat_completion_chunk_slogan,), response)
        return openai_stream2sse(_)

    return response


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/v1')

    app.run()
    # for i in range(10):
    #     send_message(f"兜底模型", title="github_copilot")
