#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_embeddings
# @Time         : 2024/1/11 09:03
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

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
                response.usage.prompt_tokens = 10000
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

    api_key = Completions.get_access_token('xx')
    print(Embeddings(api_key=api_key).create(input=['傻逼'] * 5, model='text-embedding-ada-002'))
