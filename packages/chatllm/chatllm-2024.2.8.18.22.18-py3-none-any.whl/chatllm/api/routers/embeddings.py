#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : embeddings
# @Time         : 2024/1/11 09:22
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials

from chatllm.schemas.embedding import EmbeddingRequest
from chatllm.llmchain.embeddings.openai_embeddings import Embeddings
from chatllm.llmchain.completions.github_copilot import Completions

from fastapi import APIRouter, File, UploadFile, Query, Form, Depends, Request, HTTPException, status
from fastapi import Depends, FastAPI, APIRouter, Request, Response
from openai.types.create_embedding_response import CreateEmbeddingResponse, Embedding, Usage

router = APIRouter()


@router.post("/embeddings", summary="Embedding")  # request.model_dump(exclude={"user"})
async def create_embeddings(
    request: EmbeddingRequest,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> CreateEmbeddingResponse:
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

    texts = request.input
    model = request.model  # todo: 支持多模型

    if isinstance(texts, str):
        texts = [texts]

    embeddings = (
        Embeddings(api_key=Completions.get_access_token(api_key))
        .create(input=texts, model=model, user=request.user)
    )

    return embeddings


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/v1')

    app.run()
