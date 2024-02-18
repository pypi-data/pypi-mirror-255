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
from chatllm.llmchain.applications import ChatFile
from chatllm.llmchain.document_loaders import FileLoader
from chatllm.llmchain.embeddings import OpenAIEmbeddings
from meutils.serving.streamlit import hide_st_style, st_chat_message, ChatMessage

from chatllm.llmchain.prompts.rag import template

hide_st_style()

init_cache(1)


@st.cache_resource(show_spinner=False)
def fn(file):
    docs = FileLoader(file, file.name).load_and_split()
    print(file.name, len(docs))

    chatfile = ChatFile(embeddings=OpenAIEmbeddings(chunk_size=20), prompt_template=template)
    chatfile.create_index(docs)

    return chatfile


chatfile = fn(open("附件1：东北证券股份有限公司员工合规手册（2023年12月）.docx", 'rb'))

if __name__ == '__main__':
    col1, col2, col3, *_ = st.columns(3)
    with col1:
        st.image('规丞相.png', width=64)
    with col2:
        st.markdown('##### ')
        st.markdown('##### ')
        st.markdown('##### 规丞相驾到')

    st.markdown('> ⚠️“规丞相”仅供东北证券内部测试使用，所做回答不得用于东北证券官方回复。')

    st_chat_message(ChatMessage(avatar="规丞相.png", generator="欢迎来找**规丞相**，您有什么要咨询的吗❓"))

    for message in st.session_state.messages:  # 设计his
        st_chat_message(message)

    print(st.session_state.messages)

    prompt = st.chat_input("    🤔 你可以问我任何问题", key='xx')  # 最下面
    if prompt:
        with st.spinner('AI 🤔'):
            st_chat_message(ChatMessage(name="user", generator=prompt), is_history=True)

            st_chat_message(
                ChatMessage(
                    avatar="!.png",
                    generator="`大模型根据公司相关法规及提问语义做答，不作为合规管理官方回复。`"
                )
            )

            generator = chatfile.llm_qa(prompt, k=1)

            st_chat_message(ChatMessage(avatar="规丞相.png", generator=generator), is_history=True)
