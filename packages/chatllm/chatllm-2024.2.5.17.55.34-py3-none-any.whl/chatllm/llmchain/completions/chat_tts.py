#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : to_chat
# @Time         : 2024/1/22 12:09
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo: 聊天即画图

"""
chat-dall-e-3

"""
from meutils.pipe import *
from meutils.decorators.retry import retrying

from openai import OpenAI, AsyncOpenAI
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from chatllm.schemas.openai_types import ChatCompletionRequest, ImageRequest
from chatllm.schemas.openai_types import chat_completion_error, chat_completion_chunk_error, chat_completion_chunk


class Completions(object):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        # 需要兜底的模型
        params = dict(
            api_key=api_key,
            base_url=base_url or 'https://api.chatllm.vip/v1',
            http_client=httpx.Client(follow_redirects=True)
        )
        # 如果这一步就报错呢
        self.client = OpenAI(**params)  # todo: 异步

    def create(self, request: ChatCompletionRequest, **kwargs):
        prompt = request.messages[-1]['content']  # 仅支持单轮

        if request.model.startswith(('chat-dall-e', 'dall-e')):  # ToDo：触发词 prompt.startswith(('画',))
            image_request = ImageRequest(prompt=prompt)
            return self.openai_image_create(image_request)

        elif request.model.startswith(('chat-sd',)):

            return self.sd_image_create()
        elif request.model.startswith(('chat-mj',)):
            return self.mj_image_create()

        return self.client.completions.create(**request.model_dump())  # 聊天兜底

    # @retrying
    async def openai_image_create(self, image_request: ImageRequest):
        """
            class ImagesResponse(BaseModel):
                created: int

                data: List[Image]
        :param image_request:
        :return:
        """
        # 前置
        chunk = chat_completion_chunk.model_copy(deep=True)
        for i in self.progress_bar():
            chunk.choices[0].delta.content = i
            yield chunk

        response = await self.client.images.generate(**image_request.model_dump())
        # return response

        for i, image in enumerate(response.data):
            image_url = image.url
            # b64_json = image.b64_json
            revised_prompt = image.revised_prompt
            chunk.choices[0].delta.content = f"""
            ![{revised_prompt}]({image_url})
            """
            yield chunk

    def sd_image_create(self):
        """gpt增强提示词"""
        pass

    def mj_image_create(self):
        """gpt增强提示词"""
        pass



    def progress_bar(self, title="**🔥ChatfireProgress** task-id", interval=1):
        yield title

        for i in range(10, 100, 10):
            time.sleep(interval)
            # yield f"![Progress](https://progress-bar.dev/{i})"
            yield f"![Progress](https://api.chatllm.vip/minio/bar/{i}.svg)"
            # "[下载图片](https://ai-mj-images.oss-cn-hangzhou.aliyuncs.com/2024-01-24/rdojtqkahmdkgmqspyoykfczqsnkkrrr.png) "


if __name__ == '__main__':

    def main(self, image_request: ImageRequest):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.openai_image_create(image_request))


    r = Completions().create(
        ChatCompletionRequest(model='chat-dall-e-3', messages=[{'role': 'user', 'content': '画个猫'}])
    )

    for i in r:
        print(i)
