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
    url="https://open.feishu.cn/open-apis/bot/v2/hook/f0475882-ad39-49d9-ad77-523c0e768e96"
)

hide_st_style()

init_cache(1)


@st.cache_resource(show_spinner=False)
def fn(file_path=None, file=None):
    chatfile = (
        ChatFiles(
            model="gpt-3.5-turbo",
            embedding_model="text-embedding-ada-002",
        )
        .load_file(file_path=file_path, file=file, chunk_size=500)
    )

    return chatfile


# chatfile = fn("附件1：东北证券股份有限公司员工合规手册（2023年12月）.docx")

if __name__ == '__main__':
    col1, col2, col3, *_ = st.columns(3)
    with col1:
        st.image('规丞相.png', width=64)
    with col2:
        st.markdown('##### ')
        st.markdown('##### ')
        st.markdown('##### 规丞相驾到')

    st.markdown('> ⚠️“规丞相”仅供东北证券内部测试使用，所做回答不得用于东北证券官方回复。')
    file_placeholder = st.empty()

    st_chat_message(ChatMessage(avatar="规丞相.png", generator="欢迎来找**规丞相**，您有什么要咨询的吗❓"))

    for message in st.session_state.messages:  # 设计his
        st_chat_message(message)

    print(st.session_state.messages)

    file = file_placeholder.file_uploader("文档问答")
    if file:
        with open(file.name, 'wb') as out:
            out.write(file.read())
        chatfile = fn(file.name)
    else:
        chatfile = fn("附件1：东北证券股份有限公司员工合规手册（2023年12月）.docx")

    prompt = st.chat_input("    🤔 你可以问我任何问题", key='xx')  # 最下面
    if prompt:
        send_message(prompt)
        with st.spinner('AI 🤔'):
            st_chat_message(ChatMessage(name="user", generator=prompt), is_history=False)

            # st_chat_message(
            #     ChatMessage(
            #         avatar="!.png",
            #         generator="`大模型根据公司相关法规及提问语义做答，不作为合规管理官方回复。`"
            #     )
            # )

            generator = chatfile.create(prompt, debug=True)
            nesc = "<font color='blue'>【大模型根据公司相关法规及提问语义做答，不作为合规管理官方回复。】</font>"


            def gen():
                yield nesc
                yield from generator


            st_chat_message(ChatMessage(avatar="规丞相.png", generator=gen()), is_history=False, unsafe_allow_html=True)
