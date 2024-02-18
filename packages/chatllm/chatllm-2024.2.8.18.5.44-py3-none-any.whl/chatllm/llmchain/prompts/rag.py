#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : quote
# @Time         : 2023/11/1 10:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

system = '''
你的背景知识:
"""
{context}
"""
对话要求：
1. 背景知识是最新的实时的信息，使用背景知识逐步思考、专业地回答问题。
2. 优先使用背景知识的内容回答我的问题，答案应与背景知识严格一致。
3. 背景知识无法回答我的问题时，可以忽略背景知识，根据你的知识来自由回答。
4. 使用对话的风格，自然的回答问题。
'''
strict_system = '''
你的背景知识:
"""
{context}
"""
对话要求：
1. 背景知识是最新的实时的信息，是你的唯一信息来源，使用背景知识回答问题。
2. 优先使用背景知识回答我的问题，答案与背景知识完全一致，无需做其他回答。
3. 背景知识与问题无关，或背景知识无法回答本次问题时，则拒绝回答本次问题：“亲，我不太清楚xxx”。
4. 使用对话的风格，自然的回答问题。
'''

# 我的问题是:"{question}"
template = ChatPromptTemplate.from_messages([
    ("system", system.strip()),
    # ("human", "Hello, how are you doing?"),
    # ("ai", "I'm doing well, thanks!"),
    ("human", "{question}"),
])

strict_template = ChatPromptTemplate.from_messages([
    ("system", strict_system.strip()),
    ("human", "{question}"),
])





if __name__ == '__main__':
#     from meutils.pipe import *
#     import langchain
#
#     langchain.debug = True
#     from langchain_community.chat_models import ChatOpenAI
#     from langchain.chains import LLMChain
#
#     llm = ChatOpenAI()
#
#     context = """
# 2022年的某一天，李明开着摩托车去给客户送货，路上遇到了一只小狗，他停下车去看了一下小狗，回去开车的时候货物不见了。李明在2023年进了一批货物，货物里面居然有一只小狗。
#     """
#     c = LLMChain(llm=llm, prompt=template)
#     # c = LLMChain(llm=llm, prompt=strict_template)
#     # print(c.run(context=context, question="李明开摩托车遇到了什么动物？"))
#     print(c.run(context=context, question="今天天气怎样"))
#     print(type(strict_template))
    print(strict_template.messages[0].prompt)
