#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chaturl
# @Time         : 2023/9/5 16:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
"""
"使用WebPilot"（触发开启WebPilot插件功）
"浏览这个URL：[URL]"（触发获取URL的网页内容功能）
"重写这个段落"（触发重写网页内容功）
"翻译这个网页到法语"（触发翻译网页内容功）
"我想要Steve Jobs的语气"（触发设置回答的语气功）
"Bonjour"（触发设置对话语言为法语功）
"提供这个网页的HTML元信息"（触发获取网页的HTML元信息功）
"提供这个网页的链接"（触发获取网页中的链接功）
"我想要一个简洁的摘要"（触发获取网页内容的简洁摘要功）
"我有一个问题：[问题]"（触发根据网页内容回答问题功）

"""

from meutils.pipe import *
from meutils.str_utils.regular_expression import parse_url
from meutils.decorators.retry import retrying

from openai import OpenAI, AsyncOpenAI
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo
from chatllm.schemas.openai_types import chat_completion_chunk, completion_keys


class Chat(object):

    def __init__(self, api_key=None, **kwargs):
        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.chatllm.vip/v1"),
            http_client=httpx.Client(follow_redirects=True)
        )

    @retrying
    def create(self, request: ChatCompletionRequest):
        # 提示词扩充
        prompt = """
        你是个网页问答助手，擅长根据网页内容回答问题，忽略url链接，我会给你具体的网页内容用```包裹.
        """.strip()

        if request.messages[0]['role'] == 'system':
            request.messages[0]['content'] += prompt
        else:
            request.messages = [{'role': 'system', 'content': prompt}] + request.messages

        for message in request.messages[1:]:
            message['content'] = self.content2url_content(message['content'])

        logger.debug(request.messages)

        # 通用化 to_openai_completion_params，多余的放在 extra_body 里
        data = request.model_dump()
        data = {key: data.get(key) for key in completion_keys if key in data}  # 去除多余key

        return self.client.chat.completions.create(**data)

    def create_sse(self, request: ChatCompletionRequest):
        response = self.create(request)
        if request.stream:
            from sse_starlette import EventSourceResponse
            generator = (chunk.model_dump_json() for chunk in response)
            return EventSourceResponse(generator, ping=10000)
        return response

    @lru_cache
    def content2url_content(self, content):
        urls = parse_url(content)

        for i, url in enumerate(urls):
            response = httpx.get(
                f"""{os.getenv("SPIDER_URL")}/preview/spider/playwright""",
                params={"url": url}
            ).json()
            url_content = response.get('content').strip()
            content = content.replace(url, f"```url\n{url_content}```")
            # content = content.replace(url, f"```\n{response}```")

        return content

    async def get_context(self, urls, params, **kwargs):
        async with httpx.AsyncClient() as client:
            responses = (await client.get(url, params=params, **kwargs) for url in urls)
            return [response.text for response in responses]


if __name__ == '__main__':
    url = "https://mp.weixin.qq.com/s/xxzNx6nPJTfovCzOBXTWKA"

    # print(Chat().url2content(url))

    data = {
        'model': 'gpt-3.5-turbo',
        # 'model': 'gpt-4-turbo',

        'messages': [
            {'role': 'user', 'content': f'有哪些名词  {url}'},
        ],
        'stream': False
    }

    print(Chat().create(ChatCompletionRequest(**data)))
