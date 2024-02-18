from lmchain.vectorstores import embeddings as emb
import math
from lmchain.vectorstores import laiss

import torch


class EmbeddingEngine:
    def __init__(self, embeddings, texts, embedding_services, embedding_dim=1024):
        """
        这里需要注意的使，EmbeddingIndex接受的是

        """
        super().__init__()

        self.embeddings = embeddings
        self.texts = texts
        self.embedding_services = embedding_services
        self.embedding_dim = embedding_dim

    def as_query_engine(self):
        return self

    def query(self, query_text, similarity_type="cosine_sim", top_k=3):
        query_embedding = self.embedding_services.embed_query(query_text)  # (1024,)
        sorted_indices = self.calculate_similarity_and_sort(query_embedding, self.embeddings, similarity_type)

        result_texts = []
        for i in (sorted_indices[:top_k]):
            result_texts.append(self.texts[i])
        return result_texts

    def calculate_similarity_and_sort(self, base_vector, comparison_vectors, similarity_type="cosine_sim"):
        base_vector = np.array(base_vector);
        base_vector = np.reshape(base_vector, [-1, self.embedding_dim])
        comparison_vectors = np.array(comparison_vectors);
        comparison_vectors = np.reshape(comparison_vectors, [-1, self.embedding_dim])

        # 这里统一返回一个similarity_list,这是一个包含相似度分数的 similarity_list = [0.1,0.2,0.35,0.17,0.55,0.61]
        if similarity_type == "cosine_sim":
            similarity_list = self.get_similarity_vector_indexs(base_vector, comparison_vectors)
            #print(similarity_list)
        else:
            "需要返回的是similarity_list"

        # 使用sorted函数和enumerate函数，根据值进行排序，并返回排序后的元素原始索引
        sorted_indices = sorted(enumerate(similarity_list), key=lambda x: x[1], reverse=True)
        # 提取排序后的索引
        sorted_indices_only = [index for index, value in sorted_indices]

        return sorted_indices_only

    def get_similarity_vector_indexs(self, query_vector, vectors):
        # 归一化向量
        def normalize(embeddings):
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            return embeddings / norms

        query_vector = normalize(query_vector)
        vectors = normalize(vectors)

        # 调用函数计算每个embedding与第一个embedding的cos距离
        cos_distances = self._cosine_distance(query_vector, vectors)
        # 转换为列表
        cos_distances_list = cos_distances.tolist()[0]
        # print("The list of cosine distances between the first embedding and each in the second array is:",cos_distances_list)
        return cos_distances_list

    def _cosine_distance(self, embedding1, embedding2):
        # 计算第一个embedding与所有其他embedding的点积
        dot_product = np.dot(embedding1, embedding2.T)
        # 计算余弦相似度
        dot_product = np.clip(dot_product, 0, 1)  # 裁剪相似度在[0, 1]范围内

        # 计算第一个embedding的范数
        norm1 = np.linalg.norm(embedding1, axis=1)
        # 计算第二个embedding数组中每个embedding的范数
        norm2 = np.linalg.norm(embedding2, axis=1)
        # 计算余弦相似度
        cos_similarity = dot_product / (norm1 * norm2)
        return cos_similarity


class VectorStoreIndex:
    def __init__(self, documents=None, embedding_services: emb.Embeddings = None, ):
        super().__init__()
        self.embedding_services = embedding_services
        self.documents = documents

    def from_documents(self):
        aembeddings, atexts = self.embedding_services.aembed_documents(self.documents)

        engine = EmbeddingEngine(aembeddings, atexts, embedding_services)

        return engine

    def __call__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    import numpy as np

    embedding_services = emb.GLMEmbedding()

    texts = ["好好学习天天向上", "我爱我的祖国", "今天晚上吃什么", "明天下雨吗", "你穿的红色的衣服","你去哪里玩去了","火红色的曹霞"] * 10
    aembeddings, atext = embedding_services.aembed_documents(texts)
    print(atext)
    print(len(atext), len(aembeddings))
    print("------------")

    q = "衣服是什么颜色的"
    enginer = EmbeddingEngine(aembeddings, atext, embedding_services)
    sorted_indices = enginer.query(q)
    print(sorted_indices)
