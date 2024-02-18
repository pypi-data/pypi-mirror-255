#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_embeddings
# @Time         : 2024/1/11 09:03
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo: 多线程

from meutils.pipe import *
from meutils.notice.feishu import send_message

from openai import OpenAI

send_message = partial(
    send_message,
    title="Embedding主备",
    url="https://open.feishu.cn/open-apis/bot/v2/hook/e2f5c8eb-4421-4a0b-88ea-e2d9441990f2"
)


@lru_cache()
class Embeddings(object):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        # 需要兜底的模型
        params = dict(
            api_key=api_key or 'sk-...',
            base_url=base_url or 'https://api.githubcopilot.com',
            default_headers={'Editor-Version': 'vscode/1.85.1'},
        )
        self.client = OpenAI(**params)  # todo: 异步

        self.backup_client = OpenAI(
            api_key=os.getenv("BACKUP_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.chatllm.vip/v1")
        )

    def create(self, **data) -> Any:
        # data = {key: data.get(key) for key in completion_keys if key in data}  # 去除多余key

        creates = [self.client.embeddings.create, self._backup_create, ]

        for i, _create in enumerate(creates):
            try:
                response = _create(**data)  # 尝试执行操作
                # break  # 如果操作成功，则跳出循环
                return response

            except Exception as e:  # 走兜底
                _ = f"EmbeddingsClient {i} failed: {e}"
                send_message(_)
                logging.error(_)

        return self._handle_error(data, "未知错误，请联系管理员")

    def _backup_create(self, **data):
        """恢复模型名"""
        backup_data = data.copy()
        backup_data['model'] = f"backup-{data['model']}"  # "backup-text-embedding-ada-002"
        backup_response = self.backup_client.embeddings.create(**backup_data)

        send_message(f"入参：{data}")  # 兜底监控

        return backup_response

    def _handle_error(self, data: Dict[str, Any], error: Union[str, Exception]) -> Any:
        """
        Handle errors and return an appropriate response.
        """
        return f"{data}: {error}"


if __name__ == '__main__':
    from chatllm.llmchain.completions.github_copilot import Completions

    input = ["To get started with PVC, there are resources available on the project's About and Getting Started pages.",
             'I learned Haskell in just 15 years', 'How I learned Haskell in just 15 years',
             'The author started learning Haskell around 15 years ago and initially struggled with grasping the language, despite exposure to resources and textbooks.',
             'The author made significant progress in learning Haskell after learning Elm, a language similar to Haskell, and then creating a static site builder with Shake, a Haskell library.',
             'The author applied principles learned from Haskell to improve the structure and logic of Python code, leading to successful outcomes in managing loan repayment schedules.',
             'After getting laid off and going freelance, the author was able to secure a client quickly due to their extensive experience and knowledge gained over the years.',
             "The author's journey in learning Haskell involved exposure to various resources, materials, and experiences, eventually leading to a deeper understanding and practical application of the language.",
             'How we got fine-tuning Mistral-7B to not suck',
             'How we got fine-tuning Mistral-7B to not suck: Helix Project Report, Feb 2024',
             'Helix v0.5 is announced with improvements in text fine-tuning and a new UI.',
             'The fine-tuned model initially struggled to answer basic questions consistently but was later improved by using a suite of different prompts to extract context from the document.',
             'The model was also taught about the IDs of individual documents, allowing it to refer back to the specific documents it was trained on.',
             'A framework for automatically evaluating and grading the fine-tuning process is being developed to improve the product.',
             'The decision to stick with fine-tuning instead of using RAG was based on its ability to memorize more information, better latency, style copying, understanding a large corpus of background knowledge, and easier deployment on edge devices.',
             'Apple to EU: "Go fuck yourself"',
             'Pluralistic: Apple to EU: “Go fuck yourself” (06 Feb 2024) – Pluralistic: Daily links from Cory Doctorow',
             'There is a contention that global gigacorporations are too big to fail or regulate, leading to rampant corruption and impunity.',
             'The GDPR initially impacted European data-brokerages and surveillance advertising companies, but US-based giants conducting illegal surveillance escaped enforcement.',
             "The reason for GDPR's differential impact was not compliance costs, but the Big Tech companies' ability to fly Irish flags of convenience.",
             'There is a global competition among tax-havens to provide regulatory impunity, leading to jurisdiction-shopping by corporations.',
             "The Digital Markets Act aims to regulate Big Tech monopolies, but Apple's response is seen as blatant disregard for the law and intended to circumvent it.",
             'China on cusp of next-generation chip production despite US curbs',
             'China on cusp of next-generation chip production despite US curbs',
             'Unlimited access for 4 weeks at HK$10, then HK$565 per month.', 'Cancel anytime during the trial period.',
             'Show HN: Geppetto, an open source AI companion for your Slack teams',
             "Deeptechia/geppetto: Geppetto: Advanced Slack bot integrating OpenAI's ChatGPT-4 and DALL-E-3 for interactive AI conversations and image generation. Enhances Slack communication with automated greetin",
             'Geppetto is an open source Slack App that allows users to use ChatGPT inside their workspace, written in Python and easy to tinker and fork.',
             'The project is available on GitHub at https://github.com/Deeptechia/geppetto and the first public release can be found at https://deeptechia.io/blog/geppetto-ai-companion-for-slack',
             'Sámi National Day', 'Sámi National Day',
             'The Sámi National Day is on February 6, commemorating the first Sámi congress held in 1917 in Trondheim, Norway, where Norwegian and Swedish Sámi came together to address common problems.']

    # api_key = Completions.get_access_token(None)
    # _ = Embeddings(api_key=api_key).create(input=input[:3], model='text-embedding-ada-002')

    print(len(input))
