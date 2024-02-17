#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : MultiPrompt
# @Time         : 2023/10/25 14:26
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://www.langchain.com.cn/modules/chains/examples/multi_prompt_router

from meutils.pipe import *

from langchain.chains.router import MultiPromptChain


class PromptBase(BaseModel):
    """
    prompt_infos = [
    {
        "name": "physics",
        "description": "Good for answering questions about physics",
        "prompt_template": You are a very good mathematician. Here is a question: {input}
    }
]

    """
    name: str
    description: str
    prompt_template: str




from langchain.chains import APIChain
