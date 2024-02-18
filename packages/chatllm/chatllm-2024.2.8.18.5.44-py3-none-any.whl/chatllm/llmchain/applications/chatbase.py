#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : base
# @Time         : 2023/8/9 15:04
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
from langchain.chains.question_answering import load_qa_chain

from meutils.pipe import *

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, ChatPromptValue
from langchain.schema.language_model import BaseLanguageModel

from chatllm.llmchain.decorators import llm_stream, llm_astream
from chatllm.llmchain.prompts.rag import template, strict_template


class ChatBase(object):

    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        get_api_key: Optional[Callable[[int], List[str]]] = None,  # 队列
        **kwargs
    ):
        self.llm = llm or ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0, streaming=True)

        if get_api_key:
            self.llm.openai_api_key = get_api_key(1)[0]

    def chat(self, prompt, **kwargs):
        if isinstance(prompt, ChatPromptValue):
            prompt = prompt.to_string().strip()

        self.switch_model_hook(prompt)

        yield from llm_stream(self.llm.predict)(prompt)

    def achat(self, prompt, **kwargs):
        close_event_loop()
        yield from async2sync_generator(llm_astream(self.llm.apredict)(prompt))

    async def _achat(self, prompt, **kwargs):
        await llm_astream(self.llm.apredict)(prompt)

    def switch_model_hook(self, prompt):  # todo: 可以更丰富些
        """根据tokens切换模型"""
        logger.debug(prompt)
        num_tokens = self.llm.get_num_tokens(prompt)
        if num_tokens < 3600:  # 切换阈值
            self.llm.model_name = 'gpt-3.5-turbo-0613'
        else:
            self.llm.model_name = 'gpt-3.5-turbo-16k-0613'


if __name__ == '__main__':
    cb = ChatBase()
    print(cb.llm.model_name)

    # cb.chat('p') | xprint(end='\n')
    # cb.chat('p' * 100) | xprint(end='\n')

    # ChatBase().chat('1+1') | xprint(end='\n')
    # ChatBase().achat('周杰伦是谁') | xprint(end='\n')

    p = strict_template.format_prompt(context='小明在南京', question='介绍小明')


    # p.to_string()
    # ChatBase().chat(p.to_string()) | xprint(end='\n')

    for i in cb.chat(p):
        print(i, end='')
