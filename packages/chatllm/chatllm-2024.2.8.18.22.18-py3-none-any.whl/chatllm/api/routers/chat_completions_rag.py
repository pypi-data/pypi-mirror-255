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

from chatllm.utils.openai_utils import to_openai_completion_params, openai_response2sse

from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo

router = APIRouter()

ChatCompletionResponse = Union[ChatCompletion, List[ChatCompletionChunk]]

send_message = lru_cache(send_message)


@router.post("/chat/completions")
async def create_chat_completions_for_rag(
    request: ChatCompletionRequest,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    logger.debug(request)

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

    request.model = request.model[4:]  # rag-gpt-4、rag-gpt-4-file-id
    if '-file-' in request.model:  # gpt-4-file-id
        request.model, *request.file_ids = request.model.split('-file-')

    client = OpenAI(
        api_key=api_key,
        base_url='https://api.chatllm.vip/v1',
        http_client=httpx.Client(follow_redirects=True)
    )
    if request.file_ids:
        file_content = request.file_ids | xThreadPoolExecutor(
            lambda file_id: client.files.content(file_id).text) | xjoin('\n')

        request.messages = [
                               {
                                   "role": "system",
                                   "content": "你是 ChatfireBot，由 Chatfire AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一些涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Chatfire AI 为专有名词，不可翻译成其他语言。",
                               },
                               {
                                   "role": "system",
                                   "content": file_content,
                               }
                           ] + request.messages

    data = to_openai_completion_params(request)
    response = client.chat.completions.create(**data)

    return openai_response2sse(response)


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/v1')

    app.run()
