#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : dalle
# @Time         : 2023/11/6 16:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


import streamlit as st

from meutils.pipe import *

# Note: The openai-python library support for Azure OpenAI is in preview.


st.title("图片生成")

with st.form('11'):
    prompt = st.text_area(label='提示词', placeholder='一条鱼')

    if st.form_submit_button('开始生成') and prompt:


        with st.spinner("AI正在生成"):
            import openai

            openai.api_type = "azure"
            openai.api_base = "https://betterme.openai.azure.com/"
            openai.api_version = "2023-06-01-preview"
            openai.api_key = os.getenv("OPENAI_API_KEY", 'a5b4dddb389d4647b72814fe42cae643')

            response = openai.Image.create(
                prompt=prompt,
                size='1024x1024',
                n=1
            )

            image_url = response["data"][0]["url"]

            st.image(image_url)
