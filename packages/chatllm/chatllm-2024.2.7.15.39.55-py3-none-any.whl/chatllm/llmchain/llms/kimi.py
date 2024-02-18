#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : kimi
# @Time         : 2023/11/29 18:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from chatllm.llmchain.llms import BaseLLM
from chatllm.llmchain.completions.kimi import Completions

from pydantic import model_validator
from langchain.utils import get_from_dict_or_env


class Kimi(BaseLLM):
    client: Any  #: :meta private:
    model_name: str = Field(default="kimi", alias="model")
    openai_api_key: Optional[str] = Field(default=None, alias="kimi_api_key")

    class Config:
        """Configuration for this pydantic object."""

        allow_population_by_field_name = True

    @model_validator(mode='after')
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        # 覆盖 openai_api_key
        values["openai_api_key"] = get_from_dict_or_env(
            values, "kimi_api_key", "KIMI_API_KEY"
        )

        client_params = {
            "api_key": values["openai_api_key"],
            "organization": values["openai_organization"],
            "base_url": values["openai_api_base"],
            "timeout": values["request_timeout"],
            "max_retries": values["max_retries"],
            "default_headers": values["default_headers"],
            "default_query": values["default_query"],
            "http_client": values["http_client"],
        }

        values["client"] = Completions(**client_params)  # openai.OpenAI(**client_params).chat.completions

        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")
        return values


if __name__ == '__main__':
    from meutils.pipe import *
    from langchain.chains import LLMChain
    from langchain.prompts import ChatPromptTemplate

    from chatllm.llmchain.llms import Kimi

    first_prompt = ChatPromptTemplate.from_template("{q}")

    llm = Kimi(streaming=False)

    c = LLMChain(llm=llm, prompt=first_prompt)
    print(c.run('你是谁'))

    for i in c.run('你是谁'):
        print(i, end='')

    # from chatllm.llmchain.decorators import llm_stream
    #
    # for i in llm_stream(c.run)('你是谁'):
    #     print(i, end='')
