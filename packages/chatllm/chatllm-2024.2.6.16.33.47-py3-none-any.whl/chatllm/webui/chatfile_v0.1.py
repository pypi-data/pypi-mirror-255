#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : st_chat
# @Time         : 2023/8/11 14:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import streamlit as st
# st.set_page_config('🔥ChatLLM', layout='wide', initial_sidebar_state='collapsed')

from chatllm.llmchain import init_cache
from chatllm.llmchain.applications import ChatFiles

from meutils.pipe import *
from meutils.notice.feishu import send_message
from meutils.serving.streamlit import hide_st_style, st_chat_message, ChatMessage

send_message = partial(
    send_message,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/d9c14c9b-7572-42a5-9318-463bc10768a0"
)

hide_st_style()

init_cache(1)

st.sidebar.markdown("##### [必填](https://api.chatfire.cn/)")

openai_api_key = st.sidebar.text_input("api_key", placeholder="sk-...").strip()
openai_api_base = st.sidebar.text_input("base_url", placeholder="https://api.chatfire.cn/v1")

if openai_api_key and len(openai_api_key) != 51:
    st.sidebar.error("请填写正确的api_key")


@st.cache_resource(show_spinner=False)
def fn(file_path=None, file=None):
    chatfile = (
        ChatFiles(
            model="gpt-3.5-turbo",
            embedding_model="text-embedding-ada-002",
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base
        )
        .load_file(file_path=file_path, file=file, chunk_size=500)
    )

    return chatfile


if __name__ == '__main__':
    col1, col2, col3, *_ = st.columns(3)

    st.markdown('##### 🔥Chatfire RAG')
    file_placeholder = st.empty()

    st_chat_message(ChatMessage(avatar='fire.png', generator="我是文件问答助手，请问有什么可以帮助你❓"))

    for message in st.session_state.messages:  # 设计his
        st_chat_message(message)

    file = file_placeholder.file_uploader("📃请上传文件")
    chatfile = None
    if file:
        with open(file.name, 'wb') as out:
            out.write(file.read())
        chatfile = fn(file.name)

    prompt = st.chat_input("    🤔 你可以问我任何问题", key='xx')  # 最下面
    if prompt:
        send_message(prompt)
        with st.spinner('AI 🤔'):
            st_chat_message(ChatMessage(name="user", generator=prompt), is_history=False)

            if chatfile:
                generator = chatfile.create(prompt, debug=True)

                st_chat_message(ChatMessage(avatar='fire.png', generator=generator), is_history=False,
                                unsafe_allow_html=True)

            else:

                st_chat_message(ChatMessage(avatar='fire.png', generator="**请先上传文件**"), is_history=False,
                                unsafe_allow_html=True)
