#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : prompt_maker
# @Time         : 2023/11/10 17:09
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *

from langchain import hub
obj = hub.pull("hardkothari/prompt-maker")

from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI

llm = LLMChain(llm=ChatOpenAI(), prompt=obj)
llm.run(lazy_prompt='拖把', task='小红书写文章, 用中文回答')

