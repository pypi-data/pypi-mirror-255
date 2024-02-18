#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : speech
# @Time         : 2023/12/26 13:05
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.ai_audio.tts import EdgeTTS


class Speech(object):

    def __init__(self, **client_params):
        self.api_key = client_params.get('api_key')

    async def acreate(
        self,
        input: str,
        model: Union[str, Literal["tts-1", "tts-1-hd"]] = 'tts',
        voice: Union[str, Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = '云希',  # 男声 女声
        speed: float = 1,
        **kwargs
    ):
        data = {
            "text": input,
            "voice": voice,
            # "rate": speed - 1
        }
        return EdgeTTS().stream_acreate(**data)


if __name__ == '__main__':
    from meutils.async_utils import async2sync_generator

    text = """
    陕西省，简称“陕”或“秦”，中华人民共和国省级行政区，省会西安，位于中国内陆腹地，黄河中游，东邻山西、河南，西连宁夏、甘肃，南抵四川、重庆、湖北，北接内蒙古，介于东经105°29′—111°15′，北纬31°42′—39°35′之间，总面积205624.3平方千米。 [1] [5]截至2022年11月，陕西省下辖10个地级市（其中省会西安为副省级市）、31个市辖区、7个县级市、69个县。 [121]截至2022年末，陕西省常住人口3956万人。
    """

    # print(cls.find_voices(Locale="zh-CN"))
    for i in async2sync_generator(Speech().acreate(text)):
        print(i)
