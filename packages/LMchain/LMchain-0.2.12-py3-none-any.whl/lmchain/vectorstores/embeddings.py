import warnings
warnings.filterwarnings("ignore")

import asyncio
from abc import ABC, abstractmethod
from typing import List


class Embeddings(ABC):
    """Interface for embedding models."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous Embed search docs."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_documents, texts
        )

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_query, text
        )

from zhipuai import ZhipuAI

class GLMEmbedding(Embeddings):
    def __init__(self,api_key = "",client = ZhipuAI(api_key="a8f63606c4dd11d501aa6ffee9be16d6.icUQlh0I0DFFaD7s"),model = "embedding-2"):
        if api_key == "":
            self.client = client  # 可以使用你自己key定义的chient
        else:
            self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def _costruct_inputs(self, texts):
        inputs = {
            "source_sentence": texts
        }

        return inputs

    aembeddings = []  # 这个是为了在并发获取embedding_value时候使用的存储embedding_list内容。
    atexts = []
    btexts = []
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        result_embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            result_embeddings.append(embedding)
        return result_embeddings

    def embed_query(self, text: str) -> List[float]:

        result_embeddings = self.client.embeddings.create(
            model="embedding-2",  # 填写需要调用的模型名称
            input=text,
        )
        return result_embeddings.data[0].embedding


    def aembed_query(self, text: str) -> List[float]:
        """Embed query text."""
        try:
            result_embeddings = self.client.embeddings.create(
                model=self.model,  # 填写需要调用的模型名称
                input=text,
            )

            aemb = result_embeddings.data[0].embedding

            self.aembeddings.append(aemb)
            self.atexts.append(text)
        except:
            #使用多线程的时候会报错，这里就把报错的重新存储并重新按顺序计算
            self.btexts.append(text)


    # 这里实现了并发embedding获取
    def aembed_documents(self, texts: List[str], thread_num=5, wait_sec=0.3) -> List[List[float]]:
        assert len(texts) > thread_num,print(f"文本序列长度{len(texts)}要大于线程数{thread_num}")
        import threading
        text_length = len(texts)
        thread_batch = text_length // thread_num

        for i in range(thread_batch):
            start = i * thread_num
            end = (i + 1) * thread_num

            # 创建线程列表
            threads = []
            # 创建并启动5个线程，每个线程调用一个模型
            for text in texts[start:end]:
                thread = threading.Thread(target=self.aembed_query, args=(text,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join(wait_sec)  # 设置超时时间为0.3秒

        if len(self.btexts) > 0:
            for btext in self.btexts:
                try:
                    bvector = self.embed_query(btext)
                    self.atexts.append(btext)
                    self.aembeddings.append(bvector)
                except:
                    pass
        return self.aembeddings, self.atexts


if __name__ == '__main__':
    import time

    embedding_tool = GLMEmbedding()
    texts = ["不可以，早晨喝牛奶不科学", "今天早晨喝牛奶不科学", "早晨喝牛奶不科学"] * 10

    start_time = time.time()

    aembeddings, atexts = (GLMEmbedding().embed_documents(texts))
    print(len(aembeddings))
    print(len(atexts))
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"函数执行时间: {execution_time} 秒")


