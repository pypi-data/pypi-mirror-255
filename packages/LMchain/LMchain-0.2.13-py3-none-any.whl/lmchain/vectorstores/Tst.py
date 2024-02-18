from zhipuai import ZhipuAI
api_key="a8f63606c4dd11d501aa6ffee9be16d6.icUQlh0I0DFFaD7s"
client = ZhipuAI(api_key=api_key)
result_embeddings = client.embeddings.create(
    model="embedding-2",  # 填写需要调用的模型名称
    input="晚上吃什么",
)
vector1 = result_embeddings.data[0].embedding

result_embeddings = client.embeddings.create(
    model="embedding-2",  # 填写需要调用的模型名称
    input="明天下雨吗",
)
vector2 = result_embeddings.data[0].embedding

import numpy as np
vector1 = np.reshape(vector1,(1,1024))
vector2 = np.reshape(vector2,(1,1024))
# 计算两个向量的余弦相似度
cosine_similarity = np.dot(vector1, vector2.T) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

print("The cosine similarity between the two vectors is:", cosine_similarity)


from lmchain.vectorstores import embeddings as emb
import math
from lmchain.vectorstores import laiss

import torch
class EmbeddingEngine:
    def __init__(self,embeddings, texts,embedding_services,embedding_dim = 1024):
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

    def query(self,query_text,similarity_type = "cosine_sim"):
        query_embedding = self.embedding_services.embed_query(query_text)   #(1024,)
        index = self.calculate_similarity_and_sort(query_embedding,self.embeddings,similarity_type)
        return index

    def calculate_similarity_and_sort(self,base_vector, comparison_vectors,similarity_type = "cosine_sim"):
        base_vector = np.array(base_vector);        base_vector = np.reshape(base_vector, [-1, self.embedding_dim])
        comparison_vectors = np.array(comparison_vectors);        comparison_vectors = np.reshape(comparison_vectors, [-1, self.embedding_dim])

        if similarity_type == "cosine_sim":
            self.get_similarity_vector_indexs(base_vector,comparison_vectors)

        return base_vector, comparison_vectors

    def get_similarity_vector_indexs(self, query_vector ,vectors, k: int = 3):
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
        print("The list of cosine distances between the first embedding and each in the second array is:",
              cos_distances_list)

    def _cosine_distance(self,embedding1, embedding2):
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
        # 计算余弦距离
        cos_distance = 1- cos_similarity
        return cos_distance

class VectorStoreIndex:
    def __init__(self,documents = None,embedding_services:emb.Embeddings = None,):
        super().__init__()
        self.embedding_services = embedding_services
        self.documents = documents


    def from_documents(self):
        aembeddings, atexts = self.embedding_services.aembed_documents(self.documents)

        engine = EmbeddingEngine(aembeddings, atexts,embedding_services)

        return engine


    def __call__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    import numpy as np

    embedding_services = emb.GLMEmbedding()

    texts = ["今天早晨喝牛奶不科学", "早晨喝牛奶不科学","今天晚上吃什么","明天下雨吗","你穿的红色的衣服"]
    query = "晚上下雨吗"

    embeddings = embedding_services.embed_documents(texts)
    query_embeding = embedding_services.embed_query(query)

    embeddings = np.reshape((embeddings),(-1,1024))
    query_embeding = np.reshape((query_embeding),(1,1024))

    for em in embeddings:
        # 计算两个向量的余弦相似度
        cosine_similarity = np.dot(query_embeding, em.T) / (np.linalg.norm(query_embeding) * np.linalg.norm(em))

        print("The cosine similarity between the two vectors is:", cosine_similarity)


