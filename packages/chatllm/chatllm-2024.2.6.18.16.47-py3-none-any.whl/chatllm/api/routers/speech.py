#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : speech
# @Time         : 2023/12/26 14:12
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials

from fastapi import APIRouter, File, UploadFile, Query, Form, Depends, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from chatllm.llmchain.audio.speech import Speech
from chatllm.schemas.openai_types import SpeechCreateRequest

router = APIRouter()


@router.post("/audio/speech")
async def create_speech(request: SpeechCreateRequest):
    logger.debug(request)

    try:
        data = request.model_dump()
        stream = await Speech().acreate(**data)
        return StreamingResponse(stream)

    except Exception as e:
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"message": f"{e}", "type": "api_error"}}
        )


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/v1')

    app.run()
