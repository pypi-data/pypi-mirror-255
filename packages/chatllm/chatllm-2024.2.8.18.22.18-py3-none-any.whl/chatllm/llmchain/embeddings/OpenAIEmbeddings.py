#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : OpenAIEmbeddings
# @Time         : 2023/7/11 18:40
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


from meutils.pipe import *
from meutils.np_utils import normalize
from openai import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings as _OpenAIEmbeddings


class OpenAIEmbeddings(_OpenAIEmbeddings):
    pre_fn: Optional[Callable[[str], str]] = None
    max_workers: Optional[int] = None

    def embed_documents(
        self,
        texts: List[str],
        chunk_size: Optional[int] = 0,
    ) -> List[List[float]]:
        # 文本前处理
        if self.pre_fn: texts = texts | xmap_(self.pre_fn)

        # 最大并发数
        max_workers = self.max_workers or np.clip(len(texts) // self.chunk_size + 1, 1, 16).astype(int)

        # logger.debug(max_workers)

        if max_workers == 1:  # 文本不多一次性请求最快
            return self._embed_documents(texts)

        return (
            texts | xgroup(self.chunk_size)
            | xThreadPoolExecutor(self._embed_documents, max_workers)
            | xchain_
        )

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = OpenAI(api_key=self.openai_api_key, base_url=self.openai_api_base).embeddings
        data = embeddings.create(input=texts, model=self.model).data
        e = [data[i].embedding for i in range(len(data))]

        return (e / np.linalg.norm(e, axis=-1, keepdims=True)).tolist()


if __name__ == '__main__':
    # model = "jina-embedding"
    #
    # texts = ['这是一条文本' * 200] * 1000
    # e1 = OpenAIEmbeddingsPlus(chunk_size=16, max_workers=4, model=model)
    # e2 = OpenAIEmbeddingsPlus(chunk_size=16, max_workers=16, model=model)
    #
    # with timer('4线程'):
    #     _ = e1.embed_documents(texts)
    #     print(len(_))
    #
    # with timer('16线程'):
    #     _ = e2.embed_documents(texts)
    #     print(len(_))

    # from chatllm.llmchain import init_cache
    #
    # init_cache()

    embeddings = OpenAIEmbeddings(chunk_size=16, model="jina-embedding")
    print((np.array(embeddings.embed_query('x')) ** 2).sum())
    print((np.array(embeddings.embed_query('x')) ** 2).sum())
