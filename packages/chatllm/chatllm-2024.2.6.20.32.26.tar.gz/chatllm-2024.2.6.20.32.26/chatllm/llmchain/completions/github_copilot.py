#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : copilot
# @Time         : 2023/12/6 13:14
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 不准白嫖 必须 star, todo: 兜底设计、gpt/图片
# https://github.com/CaoYunzhou/cocopilot-gpt/blob/main/main.py
# todo: chatfire sdk

import openai
from meutils.pipe import *
from meutils.cache_utils import ttl_cache
from meutils.decorators.retry import retrying
from meutils.queues.uniform_queue import UniformQueue

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from chatllm.llmchain.completions import openai_completions
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo


class Completions(object):
    def __init__(self, **client_params):
        self.api_key = client_params.get('api_key')
        self.access_token = self.get_access_token(api_key=self.api_key)
        self.completions = openai_completions.Completions(api_key=self.access_token)

    def create(self, request: ChatCompletionRequest, **kwargs):
        # logger.debug(request)

        request.model = request.model.startswith('gpt-4') and 'gpt-4' or 'gpt-3.5-turbo'

        if request.stream:
            stream = self.completions.create(request)
            # return stream

            interval = 0.05 if "gpt-4" in request.model else 0.01
            return UniformQueue(stream).consumer(interval=interval, break_fn=self.break_fn)

        else:
            return self.completions.create(request)

    def create_sse(self, request: ChatCompletionRequest):
        response = self.create(request)
        if request.stream:
            from sse_starlette import EventSourceResponse
            generator = (chunk.model_dump_json() for chunk in response)
            return EventSourceResponse(generator, ping=10000)
        return response

    @staticmethod
    def get_access_token(api_key):  # embedding 依赖于此
        token = Completions._get_access_token(api_key=api_key)
        # expires_at = int(token.split('exp=')[1][:10])  # tid=7fdaed051cf26939e7cc11e4aed37893;exp=1705749197
        if token and int(token.split('exp=')[1][:10]) < time.time():  # 过期刷新
            token = Completions._get_access_token(api_key, dynamic_param=time.time() // 180)  # 缓存3分钟
        return token

    @staticmethod
    @retrying
    @ttl_cache(ttl=1200)  # todo: 清除缓存
    def _get_access_token(api_key: Optional[str] = None, dynamic_param=None):

        api_key = api_key or os.getenv("GITHUB_COPILOT_TOKEN")
        assert api_key
        host = 'api.github.com'
        if api_key.startswith('ccu_'):  # api_key.startswith('ghu_')
            host = 'api.cocopilot.org'
        elif api_key.startswith('net|'):  # 新车
            host = 'api.cocopilot.net'
            api_key = api_key.strip('net|')

        headers = {
            'Host': host,
            # 'authorization': f'Bearer {api_key}',
            'authorization': f'token {api_key}',

            'Editor-Version': 'vscode/1.85.1',
            'Editor-Plugin-Version': 'copilot-chat/0.11.1',
            'User-Agent': 'GitHubCopilotChat/0.11.1',
            'Accept': '*/*',
            # "Accept-Encoding": "gzip, deflate, br"
        }

        url = f"https://{headers.get('Host')}/copilot_internal/v2/token"
        response = requests.get(url, headers=headers)  # todo: httpx
        resp = response.json()

        # resp['api_key'] = api_key
        # logger.debug(resp)

        return resp.get('token')

    @staticmethod
    def break_fn(line: ChatCompletionChunk):
        return line.choices and line.choices[0].finish_reason

    @classmethod
    def chat(cls, data: dict):  # TEST
        """
            Completions.chat(data)
        """

        # todo: 统一请求体
        with timer('聊天测试'):
            _ = cls().create(ChatCompletionRequest.model_validate(data))

            print(f'{"-" * 88}\n')
            if isinstance(_, Generator) or isinstance(_, openai.Stream):
                for i in _:
                    content = i.choices[0].delta.content
                    if content:
                        print(content, end='')
            else:
                print(_.choices[0].message.content)
            print(f'\n\n{"-" * 88}')


if __name__ == '__main__':
    # 触发风控
    s = """
    Question:已知节点类型只有六种：原因分析、排故方法、故障时间、故障现象、故障装备单位、训练地点，现在我给你一个问题，你需要根据这个句子来推理出这个问题的答案在哪个节点类型中，问题是”管道细长、阻力太大时的轴向柱塞泵故障如何解决？“,输出格式形为：["节点类型1"], ["节点类型2"], …。除了这个列表以外请不要输出别的多余的话。
['排故方法']

Question:已知节点类型只有六种：原因分析、排故方法、故障时间、故障现象、故障装备单位、训练地点，现在我给你一个问题，你需要根据这个句子来推理出这个问题的答案在哪个节点类型中，问题是”转向缸出现爬行现象，但是压力表却忽高忽低，相对应的解决方案是？“输出格式形为：["节点类型1"], ["节点类型2"], …。除了这个列表以外请不要输出别的多余的话。
['原因分析']、['排故方法']

Question:已知节点类型只有六种：原因分析、排故方法、故障时间、故障现象、故障装备单位、训练地点，现在我给你一个问题，你需要根据这个句子来推理出这个问题的答案在哪个节点类型中，问题是”在模拟训练场A，轴向柱塞马达出现过什么故障？“输出格式形为：["节点类型1"], ["节点类型2"], …。除了这个列表以外请不要输出别的多余的话。

['故障现象']

已知节点类型只有六种：原因分析、排故方法、故障时间、故障现象、故障装备单位、训练地点，现在我给你一个问题，你需要根据这个句子来推理出这个问题的答案在哪个节点类型中，问题是”密封圈挤出间隙的解决方法是什么？“。输出格式形为：["节点类型1"], ["节点类型2"], …。除了这个列表以外请不要输出别的多余的话。
    """

    # s = "1+1"
    # s = '树上9只鸟，打掉1只，还剩几只'
    # s = '讲个故事'

    data = {
        'model': 'gpt-4',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': s}
        ],
        'stream': True
    }

    Completions.chat(data)
    # data['stream'] = True
    # Completions.chat(data)

    # async def main():
    #     _ = await Completions().acreate(**data)
    #
    #     content = ''
    #     for i in _:
    #         content += i.choices[0].delta.content
    #     return content
    #
    #
    # print(arun(main()))

    # with timer('异步'):
    #     print([Completions().acreate(**data) for _ in range(10)] | xAsyncio)

    # data = {
    #     'model': 'gpt-xxx',
    #     'messages': [{'role': 'user', 'content': '讲个故事。 要足够长，这对我很重要。'}],
    #     'stream': False,
    #     # 'max_tokens': 16000
    # }
    # data = {
    #     'model': 'gpt-4',
    #     'messages': '树上9只鸟，打掉1只，还剩几只',  # [{'role': 'user', 'content': '树上9只鸟，打掉1只，还剩几只'}],
    #     'stream': False,
    #     'temperature': 0,
    #     # 'max_tokens': 32000
    # }
    #
    # for i in tqdm(range(1000)):
    #     _ = Completions().create(**data)
    #     print(_.choices[0].message.content)
    #     break
