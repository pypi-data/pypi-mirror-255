#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : barkup
# @Time         : 2024/1/9 09:50
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/openai/openai-python
# todo: 设计更加通用的兜底方案【首先得有靠谱的渠道（多个兜底渠道，作双兜底）】

from meutils.pipe import *
from meutils.notice.feishu import send_message

from openai import OpenAI
from chatllm.schemas.openai_types import chat_completion_error, chat_completion_chunk_error, completion_keys
from chatllm.schemas.openai_api_protocol import ChatCompletionRequest, UsageInfo

send_message = partial(
    send_message,
    title="ChatCompletion主备",
    url="https://open.feishu.cn/open-apis/bot/v2/hook/e2f5c8eb-4421-4a0b-88ea-e2d9441990f2"
)


@lru_cache()
class Completions(object):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        # 需要兜底的模型
        params = dict(
            api_key=api_key or 'sk-...',
            base_url=base_url or 'https://api.githubcopilot.com',
            default_headers={'Editor-Version': 'vscode/1.85.1'},
        )
        # 如果这一步就报错呢
        self.client = OpenAI(**params)  # todo: 异步

        # todo: 一主多备
        self.backup_client = OpenAI(
            api_key=os.getenv("BACKUP_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.chatllm.vip/v1"),
            http_client=httpx.Client(follow_redirects=True)  # 重定向修复 307
        )

    def create(self, request: ChatCompletionRequest, **kwargs):
        data = request.model_dump()
        data = {key: data.get(key) for key in completion_keys if key in data}  # 去除多余key

        # 直接走官转
        if request.response_format or request.function_call:
            send_message(f"直接走官转：{data}")

            return self._backup_create(**data)

        creates = [self.client.chat.completions.create, self._backup_create, ]
        for i, _create in enumerate(creates):
            try:
                response = _create(**data)  # 尝试执行操作

                # break  # 如果操作成功，则跳出循环
                if i == 0 and data.get('stream'):
                    return self.post_process(response, data)

                if data.get('stream'):
                    return response
                else:
                    # n = 2 if datetime.datetime.today().hour < 6 else 1.2  # todo: 随机渠道
                    n = 1.2
                    response.usage.total_tokens = int(response.usage.total_tokens * n)
                    response.usage.prompt_tokens = int(response.usage.prompt_tokens * n)
                    response.usage.completion_tokens = int(response.usage.completion_tokens * n)
                    return response

            except Exception as e:  # 走兜底
                _ = f"CompletionsClient {i} failed: {e}"  # rate limit exceeded：阶段性跳过这样的请求，防止被封
                send_message(_)
                logging.error(_)
        return self._handle_error(data, "未知错误，请联系管理员")

    def post_process(self, response, data):  # copilot
        """兜底判断"""
        for chunk in response:
            if chunk.choices:
                if chunk.choices[0].finish_reason == 'content_filter':  # 走兜底
                    _ = f"ContentFilter：{chunk.model_dump_json()}"
                    logger.debug(_)
                    send_message(_)
                    yield from self._backup_create(**data)
                    break

                if chunk.choices[0].delta.content or chunk.choices[0].finish_reason:
                    # chunk.choices[0]###########
                    chunk.object = 'chat.completion.chunk'
                    # chunk.choices[0].delta.content = chunk.choices[0].delta.content or ''  # None替换为''
                    yield chunk

    def _backup_create(self, **data):
        """恢复模型名"""
        backup_data = data.copy()
        backup_data['model'] = "backup-gpt-4" if data['model'].startswith('gpt-4') else "backup-gpt"  # todo: 4v
        backup_response = self.backup_client.chat.completions.create(**backup_data)

        send_message(f"入参：{data}")  # 兜底监控

        if data.get('stream'):
            def gen():
                for chunk in backup_response:
                    chunk.model = data['model']
                    yield chunk

            return gen()
        else:
            backup_response.model = data['model']

        return backup_response

    def _handle_error(self, data: Dict[str, Any], error: Union[str, Exception]) -> Any:
        """
        Handle errors and return an appropriate response.
        """
        if data.get('stream'):
            # Assuming chat_completion_chunk_error is defined elsewhere
            chat_completion_chunk_error.choices[0].delta.content = str(error)
            return chat_completion_chunk_error
        else:
            # Assuming chat_completion_error is defined elsewhere
            chat_completion_error.choices[0].message.content = str(error)
            return chat_completion_error


if __name__ == '__main__':
    from chatllm.llmchain.completions import github_copilot

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': "你是gpt4, Let's think things through one step at a time."},
            {'role': 'user', 'content': 'hi'}
        ],
        'stream': False
    }

    # for i in range(3):
    #     print(Completions().create(ChatCompletionRequest(**data)))
    #     break

    data['stream'] = True

    api_key = github_copilot.Completions.get_access_token(None)
    for i in Completions(api_key=api_key).create(ChatCompletionRequest(**data)):
        print(i)
