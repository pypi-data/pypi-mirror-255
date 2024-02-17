#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat_copilot
# @Time         : 2023/12/14 10:06
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


import streamlit as st
# st.set_page_config('🔥ChatLLM', layout='wide', initial_sidebar_state='collapsed')


from chatllm.llmchain.completions.github_copilot import Completions

from meutils.serving.streamlit import hide_st_style, st_chat_message, ChatMessage
from meutils.notice.feishu import send_message

hide_st_style()

st.markdown('### Cocopilot 打字机测试')
st.sidebar.markdown('#### [国内大模型API](https://vip.chatllm.vip/)')

info = {}
with st.form(key='my_form'):
    token = st.text_input('CocopilotToken', placeholder='ghu_...').strip()
    info['token'] = token
    if st.form_submit_button(label='确定') or token.startswith('ghu_'):
        try:
            completions = Completions(api_key=token)
            info["completions"] = completions
            st.success('token验证成功')
            send_message(title='Cocopilot', content=token)
        except Exception:
            st.error('token验证失败')
    else:
        st.markdown('> [如果没有token，请点击获取token, 也可以联系wx313303303拼车](https://cocopilot.org/copilot/token)')

prompt = st.chat_input("    🤔 你可以问我任何问题", key='xx')  # 最下面
if prompt and info:
    st_chat_message(ChatMessage(name="user", generator=prompt))

    with st.spinner('AI 🤔'):
        generator = info["completions"].create(messages=[{'role': 'user', 'content': prompt}], stream=True)

        st_chat_message(
            ChatMessage(
                generator=(_.choices[0].delta.content for _ in generator if _)
            ),
            is_history=True)
