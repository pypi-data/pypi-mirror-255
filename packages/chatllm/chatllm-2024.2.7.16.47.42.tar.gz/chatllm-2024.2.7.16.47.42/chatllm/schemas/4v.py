#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : 4v
# @Time         : 2023/11/15 17:49
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from pydantic import validator
from meutils.io.image import image_to_base64
from openai import OpenAI

client = OpenAI()
import langchain

class TextContent(BaseModel):
    type: str = "text"
    text: str


class ImageURL(BaseModel):
    url: str
    detail: Literal['low', 'high', 'auto'] = 'auto'

    @validator('url')
    def validate(cls, url):
        if not url.startswith('http') and Path(url).is_file():
            url = image_to_base64(url, for_image_url=True)
        return url


class ImageContent(BaseModel):
    type: str = "image_url"
    image_url: ImageURL


response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        "detail": "high"
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

# print(response.choices[0].message.content)
if __name__ == '__main__':
    # a = [TextContent(text="What’s in this image?"), ImageContent(image_url=ImageURL(url='http://xxx'))]
    # print(a)

    image_url = ImageURL(url='xxx')
    print(ImageContent(image_url=image_url))

    print(image_url)

