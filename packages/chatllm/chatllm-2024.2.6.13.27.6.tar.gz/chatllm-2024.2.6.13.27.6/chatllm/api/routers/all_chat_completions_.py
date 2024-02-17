#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : completions
# @Time         : 2023/12/19 16:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.notice.feishu import send_message
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials

from sse_starlette import EventSourceResponse
from fastapi import APIRouter, File, UploadFile, Query, Form, Depends, Request, HTTPException, status

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from chatllm.llmchain.completions import github_copilot
from chatllm.llmchain.completions import moonshot_kimi
from chatllm.llmchain.completions import deepseek

from chatllm.schemas.openai_types import chat_completion_ppu
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo

router = APIRouter()

ChatCompletionResponse = Union[ChatCompletion, List[ChatCompletionChunk]]

send_message = lru_cache(send_message)


@router.post("/chat/completions")
def chat_completions(
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

    model = request.model.strip().lower()
    data = request.model_dump()

    # 空服务 按次计费 pay-per-use ppu
    if model.startswith(('pay-per-use', 'ppu')): return chat_completion_ppu

    ############################################################################ 写到外面去
    if request.file_id or model.__contains__('-file-'):  # 'gpt-3.5-turbo-file-d76e7a6b935373a797544628cbc89b76'
        from redis import Redis
        from minio import Minio
        from chatllm.llmchain.applications import ChatFiles

        minio_client = Minio(
            endpoint=os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=False)

        file_map = {} or Redis(**os.getenv("REDIS_CLIENT_PARAMS", {}), decode_responses=True)

        file_id = request.file_id or f"file-{model.split('-file-')[-1]}"
        file_name = file_map.get(file_id)

        logger.debug(file_id)
        logger.debug(file_name)

        file_data = minio_client.get_object('openai', f"{api_key}/{file_name}")
        file_data = io.BytesIO(file_data.read())  # todo: 为啥不支持file_data

        use_ann = request.rag.get('use_ann')
        chunk_size = request.rag.get('chunk_size', 1000)
        response = (
            ChatFiles(
                model=model.split('-file-')[0],
                embedding_model=request.embedding_model,
                openai_api_key=api_key,
                stream=data.get('stream'),
                use_ann=use_ann,
            )
            .load_file(file=file_data, chunk_size=chunk_size)
            .create_sse(query=data.get('messages')[-1].get('content')))  # todo:多轮对话

        return response

    ############################################################################

    if model.startswith(('kimi', 'moonshot')):
        if any(i in model for i in ('web', 'search', 'net')):
            data['use_search'] = True  # 联网模型

        completions = moonshot_kimi.Completions(api_key=api_key)

    elif model.startswith(('deepseek',)):
        completions = deepseek.Completions(api_key=api_key)

    else:
        completions = github_copilot.Completions(api_key=api_key)
        send_message(api_key, title="github_copilot", n=3)

    response: ChatCompletionResponse = completions.create_sse(**data)
    return response


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/v1')

    app.run()
    # for i in range(10):
    #     send_message(f"兜底模型", title="github_copilot")
