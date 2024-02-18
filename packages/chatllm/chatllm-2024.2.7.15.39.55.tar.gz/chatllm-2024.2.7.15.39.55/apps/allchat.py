#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : apps
# @Time         : 2023/12/14 19:30
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


from meutils.serving.fastapi import App
from chatllm.llmchain import init_cache
from chatllm.api.routers import all_chat_completions, embeddings

init_cache()

app = App()

app.include_router(embeddings.router, '/v1')
app.include_router(all_chat_completions.router, '/v1')

if __name__ == '__main__':
    app.run(port=39999)
