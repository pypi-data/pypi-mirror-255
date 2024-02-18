#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : VectorRecordManager
# @Time         : 2023/9/12 13:40
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://python.langchain.com/docs/modules/data_connection/indexing#using-with-loaders

from langchain.indexes import SQLRecordManager, index
from langchain.schema import Document
from langchain_community.vectorstores import Chroma, VectorStore
from langchain_community.document_loaders.base import BaseLoader
from langchain.retrievers.elastic_search_bm25 import ElasticSearchBM25Retriever

from meutils.pipe import *
from chatllm.llmchain.vectorstores import ElasticsearchStore
from chatllm.llmchain.embeddings import OpenAIEmbeddings  # 多线程


# 混合检索 https://zhuanlan.zhihu.com/p/665097446
class VectorRecordManager(object):
    """
    增量更新向量
        manager.vectorstore.similarity_search(
        'doc',
        filter=[{'term': {'metadata.source': 'unknown'}}]
    )
    """

    def __init__(
        self, collection_name="test_index",
        vectorstore: Optional[VectorStore] = None,
        db_url: Optional[str] = None,
    ):
        """

        :param collection_name:
        :param vectorstore:
            # 本地
            vectorstore = Chroma(collection_name=collection_name, embedding_function=embedding)

        :param db_url:
            # 默认在 HOME_CACHE
            f"sqlite:///{HOME_CACHE}/chatllm/vector_record_manager.sql"

            "sqlite:///chatllm_vector_record_manager_cache.sql"

        """
        self.collection_name = collection_name
        self.vectorstore = vectorstore or ElasticsearchStore(
            embedding=OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")),
            index_name=self.collection_name,  # 同一模型的embedding
            es_url=os.getenv('ES_URL'),
            es_user=os.getenv('ES_USER'),
            es_password=os.getenv('ES_PASSWORD'),
        )

        # ElasticSearchBM25Retriever(client=self.vectorstore.client, index_name=collection_name).get_relevant_documents()
        # self.vectorstore.strategy.hybrid = True  # 检索策略

        namespace = f"{self.vectorstore.__class__.__name__}/{collection_name}"
        db_url = db_url or f"sqlite:///{HOME_CACHE / 'chatllm/vector_record_manager.sql'}"

        self.record_manager = SQLRecordManager(namespace, db_url=db_url)
        self.record_manager.create_schema()

    def update(
        self,
        docs_source: Union[List[str], BaseLoader, Iterable[Document]],
        cleanup: Literal["incremental", "full", None] = "incremental",
        source_id_key: Union[str, Callable[[Document], str], None] = "source",
    ):
        """

        :param docs_source:
        :param cleanup:        :param source_id_key: 根据 metadata 信息去重

        :return:
        """
        if isinstance(docs_source, List) and isinstance(docs_source[0], str):
            docs_source = [Document(page_content=text, metadata={"source": 'unknown'}) for text in docs_source]

        return index(docs_source, self.record_manager, self.vectorstore, cleanup=cleanup, source_id_key=source_id_key)

    def clear(self):
        return index([], self.record_manager, self.vectorstore, cleanup="full", source_id_key="source")


if __name__ == '__main__':
    doc1 = Document(page_content="kitty", metadata={"source": "kitty.txt"})
    doc2 = Document(page_content="doggy", metadata={"source": "doggy.txt"})
    with timer():
        manager = VectorRecordManager()
    print(manager.clear())
    print(manager.update([doc1, doc2] * 30))

    # 检索
    # filter_term = [{"term": {"metadata.source": "kitty.txt"}}]
    # print(manager.vectorstore.similarity_search(query='总结下', filter=filter_term, threshold=0.5))

    # filter_term = [{"match": {"metadata.source.keyword": "同程商旅Q&A.pdf"}}]

    # filter_term = [{"match": {"metadata.source.keyword": "zhihe18_10365805170e4b00919c4eb8994.docx"}}]
    # filter_term = None
    # manager = VectorRecordManager(collection_name='zhihe_test')
    # print(manager.vectorstore.similarity_search(query='总结下', filter=filter_term, threshold=0.5))
    # with timer('client'):
    #     client = VectorRecordManager(collection_name='zhihe_test').vectorstore
    # with timer('search'):
    #     _ = (
    #         client.similarity_search(
    #             query='总结下',
    #             filter=filter_term,
    #             threshold=0.8
    #         )
    #     )
    #     print(_)
