#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : demo
# @Time         : 2023/11/6 17:18
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
import openai

# openai.api_type = "azure"
# openai.api_base = "https://betterme.openai.azure.com/"
# openai.api_version = "2023-06-01-preview"

response = openai.Image.create(
    prompt='一条鱼',
    size='1024x1024',
    n=1
)

image_url = response["data"][0]["url"]

print(image_url)
