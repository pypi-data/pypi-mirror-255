#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : files
# @Time         : 2023/12/29 14:21
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo: 返回链接，参考kimi，接入文档解析，16c32g机器部署，不能通服务调用, minio_client通用化 id 映射

import shortuuid

from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials
from chatllm.utils.openai_utils import per_create

from enum import Enum
from minio import Minio
from redis import Redis
from openai import OpenAI
from openai._types import FileTypes
from openai.types.file_object import FileObject
from fastapi import APIRouter, File, UploadFile, Query, Form, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import Response, FileResponse

router = APIRouter()

file_map = {} or Redis(**os.getenv("REDIS_CLIENT_PARAMS", {}), decode_responses=True)  # redis_client_params


class Purpose(str, Enum):
    file_extract = "file-extract"
    assistants = "assistants"
    fine_tune = "fine-tune"


minio_client = Minio(
    endpoint=os.getenv('MINIO_ENDPOINT'),
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=False if ":" in os.getenv('MINIO_ENDPOINT') else True
)

OPENAI_BUCKET = os.getenv('OPENAI_BUCKET', 'openai')


@router.get("/files/{file_id}")
async def get_files(
    file_id: str,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),

):
    api_key = auth and auth.credentials or None
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败")

    try:
        file_name = file_map.get(file_id)
        response = minio_client.get_object(OPENAI_BUCKET, f"{api_key}/{file_name}")
        data = response.read()

        return FileObject(
            id=file_id,
            bytes=len(data),
            created_at=int(time.time()),
            filename=file_name,
            object='file',
            purpose='assistants',
            status='uploaded',
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File error: {e}")


@router.get("/files/{file_id}/content")
async def get_files_content(
    file_id: str,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),

):
    api_key = auth and auth.credentials or None
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败")
    try:
        file_name = file_map.get(file_id)
        response = minio_client.get_object(OPENAI_BUCKET, f"{api_key}/{file_name}")  # 获取链接
        data = response.data

        return Response(content=data, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File content error: {e}")


@router.post("/files")  # 同名文件会被覆盖
async def upload_files(
    file: UploadFile = File(...),
    purpose: Purpose = Form(...),
    # return_url=Form(...)
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),

):
    api_key = auth and auth.credentials or None
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败")

    if purpose == Purpose.fine_tune:
        # 对于微调，验证上传文件的格式
        content = await file.read()
        try:
            lines = content.decode().split("\n")
            for line in lines:
                record = json.loads(line)
                if "prompt" not in record or "completion" not in record:
                    raise ValueError("Invalid format")
        except:
            raise HTTPException(status_code=400, detail="Invalid file format for fine-tuning")
    elif purpose == Purpose.assistants:
        # 对于助手和消息，你可能需要进行不同的处理
        # todo: 直接解析到 es【后面支持队列】

        minio_client.put_object(OPENAI_BUCKET, f"{api_key}/{file.filename}", data=file.file, length=file.size)

        # fileid2filename
        file_id = f"file-{hash(file.filename)}"
        file_map[file_id] = file.filename  # shortuuid.uuid('a') "file-HASH"
        # logger.debug(file_map)

        # 按次计费
        try:
            _ = per_create(api_key=api_key)  # 无效key
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败")

        return FileObject(
            # id=f"file-{shortuuid.random()}",  # 新的模型名称
            id=file_id,

            bytes=file.size,
            created_at=int(time.time()),
            filename=file.filename,
            object='file',
            purpose='assistants',
            status='uploaded',  # Deprecated
        )


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    VERSION_PREFIX = '/v1'

    app = App()
    app.include_router(router, VERSION_PREFIX)
    app.run(port=9000)
