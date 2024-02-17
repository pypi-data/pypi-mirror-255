#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : kimi
# @Time         : 2023/11/29 17:00
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 只要单轮对话

from meutils.pipe import *
from meutils.cache_utils import ttl_cache, diskcache
from meutils.decorators.retry import retrying
from meutils.notice.feishu import send_message
from meutils.str_utils.regular_expression import parse_url
from meutils.hash_utils import murmurhash

from chatllm.llmchain.utils import tiktoken_encoder
from chatllm.schemas.kimi.protocol import EventData
from chatllm.llmchain.completions import github_copilot

from openai.types.chat import chat_completion_chunk, chat_completion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from chatllm.schemas.openai_types import chat_completion_error, chat_completion_chunk_error
from chatllm.schemas.openai_types import chat_completion_chunk

send_message = partial(
    send_message,
    title="Kimi",
    url="https://open.feishu.cn/open-apis/bot/v2/hook/e2f5c8eb-4421-4a0b-88ea-e2d9441990f2"
)


class Completions(github_copilot.Completions):
    def __init__(self, **client_params):
        self.api_key = client_params.get('api_key')  # state_file
        self.access_token = self.get_access_token(self.api_key)

    def create(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        **kwargs,
    ):
        if isinstance(messages, str):
            messages = [{'role': 'user', 'content': messages}]

        logger.debug(f"messages：{messages}")

        ######################################################################################################
        data = {
            "model": 'gpt-4',
            "messages": messages[-1:],  # 系统提示词怎么自定义, # Check
            "conversation_name": f"{murmurhash(messages[:2], bins=100000)}: {messages[:2][-1]['content'][:10]}",
            **kwargs
        }  # 结构体

        # 额外参数
        if len(data.get('model')) > 20:  # 不联网
            refs = data.get('model', '').strip('kimi-').split('|')  # ['']
            refs = data.pop('refs', refs[0] and refs or [])
            logger.debug(refs)

            use_search = False if refs else data.pop('use_search', True)
            data["refs"] = refs
            data["use_search"] = use_search

        new_content = self._url2content(data["messages"][-1]["content"])
        if new_content:
            data['refs'] = []
            data['use_search'] = False
            data["messages"][-1]["content"] = new_content

        ######################################################################################################

        logger.debug(f"RequestData：{data}")

        if data.get('stream'):
            return self._stream_create(**data)
        else:
            return self._create(**data)

    def _create(self, **data):

        # todo
        # response = requests.post(url, json=json_str, headers=headers)
        # response.encoding = 'utf-8'
        # response.text.strip().split('\n\n')

        content = ''
        chunk_id = created = None
        model = data.get('model', 'kimi')
        for chunk in self._stream_create(**data):
            chunk_id = chunk.id
            created = chunk.created
            content += chunk.choices[0].delta.content

        message = chat_completion.ChatCompletionMessage(role='assistant', content=content)

        choice = chat_completion.Choice(
            index=0,
            message=message,
            finish_reason='stop',
            logprobs=None
        )

        prompt_tokens, completion_tokens = map(len, tiktoken_encoder.encode_batch([str(data.get('messages')), content]))
        total_tokens = prompt_tokens + completion_tokens

        usage = chat_completion.CompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )

        completion = chat_completion.ChatCompletion(
            id=chunk_id,
            choices=[choice],
            created=created,
            model=model,
            object="chat.completion",
            usage=usage

        )

        return completion

    def _url2content(self, content) -> Union[bool, str]:
        urls = parse_url(content)
        if not urls: return False

        for i, url in enumerate(urls):
            _url = f""" <url id="{i}" type="url" status="" title="" wc="">{url}</url> """
            content = content.replace(url, _url)

        return content

    def _search_plus(self, event_data: EventData):
        if event_data.msg.get("type") == "start":  # start_res
            chat_completion_chunk.choices[0].delta.content = "---\n🔎 开始搜索 🚀\n"
            yield chat_completion_chunk
        if event_data.msg.get("type") == "get_res":
            title = event_data.msg.get("title")
            url = event_data.msg.get("url")
            chat_completion_chunk.choices[0].delta.content = f"""- 🔗 [{title}]({url})\n"""
            yield chat_completion_chunk

        if event_data.msg.get("type") == "answer":
            chat_completion_chunk.choices[0].delta.content = f"""---\n\n"""
            yield chat_completion_chunk

    def _stream_create(self, **data):  # {'messages': messages, "refs": refs, "use_search": use_search}
        response = self._post(**data)
        if response is None or response.status_code != 200:
            chat_completion_chunk_error.choices[0].delta.content = hasattr(response, 'text') and response.text
            yield chat_completion_chunk_error
            return

        chunk_id = f"chatcmpl-{uuid.uuid1()}"
        created = int(time.time())
        model = data.get('model', 'kimi')
        finish_reason = None

        for chunk in response.iter_lines(chunk_size=1024):
            if chunk:
                # logger.debug(chunk.decode())
                chunk = chunk.strip(b"data: ")
                if chunk.startswith(b'{"error":'):
                    logger.debug(chunk.decode())
                event_data = EventData(**json.loads(chunk))

                if event_data.event == "all_done" or event_data.error_type:
                    finish_reason = 'stop'
                    logger.info(chunk.decode())
                    # {"error_type":"validation.error","message":"参数验证错误","detail":["Content is a required field"]}
                    # {"error":{"error_type":"openai.completion.stream","message":"Kimi 现在有点累了，晚一点再来问问我吧！","detail":"runtime error: invalid memory address or nil pointer dereference"},"event":"error"}

                    # if event_data.error_type == "chat.forbidden": # 敏感内容
                    #     event_data.text = "请稍后重试！"
                    #     data['conversation_name'] = f"「XchatNew：{time.ctime()}」"
                    #     return self._stream_create(**data)

                ##############################AGI#################################
                if event_data.event == 'debug':
                    logger.debug(event_data.message)
                if event_data.event == 'search_plus':
                    logger.debug(event_data.msg)
                    yield from self._search_plus(event_data)

                ##############################AGI#################################
                if event_data.text or finish_reason:
                    # chat_completion_chunk = chat_completion_chunk.model_copy(update={"model": "kimi"}, deep=True)
                    chat_completion_chunk.model = model
                    chat_completion_chunk.id = chunk_id
                    chat_completion_chunk.created = created

                    chat_completion_chunk.choices[0].delta.content = event_data.text

                    # logger.debug(chat_completion_chunk)

                    yield chat_completion_chunk

    @retrying(predicate=lambda r: isinstance(r, str) and ("auth.token.invalid" in r))
    def _post(self, **data):
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

        # {"error_type":"chat.not_found","message":"找不到指定的会话"}
        conversation_name = data.pop('conversation_name')
        chat_url = self._create_url(conversation_name=conversation_name, headers=headers)  #

        response = requests.post(
            chat_url,
            json=data,
            headers=headers,
            stream=data.get('stream'),
        )

        if response.status_code != 200:
            send_message(content=f"{response.text}\n\n{self.api_key}")
            return response.text

        return response

    @staticmethod
    def _create_url(conversation_name: Optional[str] = None, headers: Optional[dict] = None):
        headers = headers or {}
        url = "https://kimi.moonshot.cn/api/chat"
        payload = {"name": str(conversation_name), "is_example": False}
        response = requests.post(url, json=payload, headers=headers).json()
        # logger.debug(response)

        conversation_id = response.get('id')
        return f"{url}/{conversation_id}/completion/stream"

    @staticmethod
    @retrying
    def get_access_token(state_file):  # 从redis读取: 要跟会话名称一致吗【用户id区分】
        state_file = state_file or "/Users/betterme/PycharmProjects/AI/MeUtils/examples/爬虫/kimi_18198922940.json"

        cookies = json.loads(Path(state_file).read_text())
        storage = cookies.get('origins', [{}])[0].get('localStorage', [{}])

        access_token = refresh_token = None
        for name2value in storage:
            if name2value.get('name') == 'access_token':
                access_token = name2value.get('value')
            if name2value.get('name') == 'refresh_token':
                refresh_token = name2value.get('value')

        return access_token


if __name__ == '__main__':
    # {"error_type":"validation.error","message":"参数验证错误","detail":["Content is a required field"]}

    data = {
        'model': 'kimi', 'messages': [{'role': 'user', 'content': '今天南京天气怎么样'}], 'stream': True,
        'use_search': True
    }
    # data = {
    #     "messages":
    #         [
    #             {"role": "user",
    #              "content": "总结一下 https://waptianqi.2345.com/wea_history/58238.htm"}
    #         ],
    #     "refs": [],
    #     "use_search": False,
    #     'stream': True
    # }

    Completions.chat(data)

    # with timer('异步'):
    #     print([Completions().acreate(**data) for _ in range(10)] | xAsyncio)

    # state_file = "/Users/betterme/PycharmProjects/AI/MeUtils/examples/爬虫/kimi_cookies.json"
    # completion = Completions(api_key=state_file)
    #
    # data = {
    #     'model': 'kimi-clk4da83qff43om28p80|clk4da83qff43om28p80',
    #     'messages': [{'role': 'user', 'content': '总结一下'}],
    #     'stream': False,
    #     'use_search': False
    # }
    #
    # _ = completion.create(**data)
    #
    # if isinstance(_, Generator):
    #     for i in tqdm(_):
    #         content = i.choices[0].delta.content
    #         print(content, end='')
    # else:
    #     print(_)
