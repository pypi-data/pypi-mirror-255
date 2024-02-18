#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : llm_test
# @Time         : 2023/12/8 15:56
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo: 渠道测试

from meutils.pipe import *

from openai import OpenAI

questions = [
    '树上9只鸟，打掉1只，还剩几只？',
    '鲁迅为什么暴打周树人',
]


def do_chat(
    q='鲁迅为什么暴打周树人',
    api_key: Optional[str] = None,
    base_url: Optional[str] = os.getenv('OPENAI_API_BASE'),
    model='chat2api'
) -> str:
    completions = OpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=3
    ).chat.completions

    _ = completions.create(
        messages=[{'role': 'user', 'content': q}],
        model=model,
        temperature=0,
    )

    logger.debug(_)

    return _.choices[0].message.content


if __name__ == '__main__':
    for q in questions:
        print(do_chat(q))
