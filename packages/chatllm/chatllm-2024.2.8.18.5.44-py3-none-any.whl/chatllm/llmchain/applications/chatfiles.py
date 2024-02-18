#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chatdoc
# @Time         : 2023/7/15 20:53
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo:多轮对话

from chatllm.llmchain.decorators import llm_stream
from chatllm.llmchain.vectorstores import FAISS
from chatllm.llmchain.embeddings import OpenAIEmbeddings
from chatllm.llmchain.prompts import rag
from chatllm.llmchain.utils import tiktoken_encoder
from chatllm.schemas.openai_types import chat_completion, chat_completion_chunk

from langchain.text_splitter import *
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import UnstructuredFileLoader
from chatllm.llmchain.document_loaders import FileLoader

from meutils.pipe import *
from meutils.notice.feishu import send_message
from typing import IO


class ChatFiles(object):

    def __init__(
        self,
        model="gpt-3.5-turbo",
        # embedding_model="text-embedding-ada-002",
        embedding_model="jina-embedding",
        openai_api_key: Optional[str] = None,
        openai_api_base: Optional[str] = None,
        stream: bool = True,
        temperature: float = 0,
        use_ann: Optional[bool] = None,
        max_tokens: Optional[int] = 10000,
        prompt_template: Optional[ChatPromptTemplate] = None,
        **kwargs
    ):
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        openai_api_base = openai_api_base or os.getenv("OPENAI_API_BASE", "https://api.chatllm.vip/v1")

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=stream,
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base
        )
        self.embeddings = OpenAIEmbeddings(
            chunk_size=5,  # 小一点
            model=embedding_model,
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base
        )
        self.prompt_template = prompt_template or rag.template

        self.stream = stream

        self.docs = None
        self.use_ann = use_ann
        self.max_tokens = max_tokens
        self.vectorstore = None

        self.chain = load_qa_chain(self.llm, prompt=prompt_template)  # todo: 增加信源

    def create(self, query: str, top_k: int = 5, threshold: float = 0.666, debug=False, **kwargs: Any):
        if self.vectorstore:
            self.docs = self.vectorstore.similarity_search(query, k=top_k, threshold=threshold, **kwargs)  # 优化加速

            if debug:
                # logger.debug(query)
                # self.docs | xmap_(logger.debug)
                send_message(title=query)
                self.docs | xmap(lambda doc: doc.page_content) | xmap_(send_message)

            if not self.docs:
                logger.warning(f"DocsNull: {query} -> {self.docs}")

        if self.stream:
            return llm_stream(self.chain.run)({"input_documents": self.docs, "question": query})
        else:
            return self.chain.run({"input_documents": self.docs, "question": query})

    def create_sse(self, query):
        response = self.create(query)
        if self.stream:
            def generator():
                for chunk in response:
                    chat_completion_chunk.choices[0].delta.content = chunk
                    yield chat_completion_chunk.model_dump_json()

            from sse_starlette import EventSourceResponse
            return EventSourceResponse(generator(), ping=10000)

        chat_completion.choices[0].message.content = response
        return chat_completion

    def load_file(
        self,
        file_path: Optional[str] = None,
        file: Optional[IO[bytes]] = None,
        chunk_size=1000,
        chunk_overlap=50,
        separators: Optional[List[str]] = None,
        **kwargs
    ):

        """todo: 支持多文件"""
        self.docs = UnstructuredFileLoader(
            file_path=file_path,
            file=file,
            metadata_filename=file_path and Path(file_path).name or (hasattr(file, 'name') and file.name),
            strategy="fast",
        ).load()

        if self.use_ann or len(tiktoken_encoder.encode(self.docs[0].page_content)) > self.max_tokens:
            separators = separators or ['\n\n', '\r', '\n', '\r\n', '。', '!', '！', '\\?', '？', '……', '…']
            textsplitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                add_start_index=True,
                separators=separators
            )
            self.docs = textsplitter.split_documents(self.docs)
            self.vectorstore = FAISS.from_documents(self.docs, self.embeddings)  # ann 索引
            return self

        logger.debug('不走ANN')

        return self


if __name__ == '__main__':
    from chatllm.llmchain import init_cache

    # init_cache()
    model: str = "text-embedding-ada-002"
    model = "jina-embedding"

    q = '已出票成功的机票，发现姓名/证件号码写错了，要如何操作？'
    # q = 'Q:为什么有的订单要收取消费？ A:不同服务商针对乘客取消订单行为可能会收取相应取消费，为避免造成额外损失，请合理安排出行计划合理下单。如遇特殊情况，请及时联系 同程商旅客服协助处理。'
    _ = (
        ChatFiles(use_ann=False, embedding_model=model)
        .load_file(
            file=open(
                '/Users/betterme/PycharmProjects/AI/ChatWecom/chatwecom/data/同程商旅Q&A通用版（机、酒、火、用车）1.1 (1)(1).pdf',
                'rb'),
            chunk_size=300,
        )
        .create(q)
    )

    for i in _:
        print(i, end='')
