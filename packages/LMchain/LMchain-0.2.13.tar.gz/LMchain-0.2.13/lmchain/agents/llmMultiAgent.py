from zhipuai import ZhipuAI
from zhipuai.core._base_type import NotGiven, NOT_GIVEN

class AgentZhipuAI:
    def __init__(self, api_key = "", client =ZhipuAI(api_key="a8f63606c4dd11d501aa6ffee9be16d6.icUQlh0I0DFFaD7s"), system_info ="",
                 chat_model = "glm-4",image_model =  "cogview",embedding_model = "embedding-2",read_pic_model = "glm-4v"):
        if api_key == "":
            self.client = client  # 可以使用你自己key定义的chient
        else:
            self.client = ZhipuAI(api_key=api_key)

        if system_info == "":
            self.history = []
        else:
            self.history = [{"role": "system", "content": system_info}]

        self.model_name = chat_model
        self.image_model = image_model

        "下面是要处理embedding的集成"
        from lmchain.vectorstores import embeddings
        self.embedding_tool = embeddings.GLMEmbedding(client=self.client,model=embedding_model)
        "上面是要处理embedding的集成"

    def __call__(self, prompt="", role="user") -> str:
        """_call"""
        # construct query
        prompt_json = {
            "role": role,
            "content": prompt + "|以上是我请求的内容，请一步步进行推理并得出结论(Let’s think step by step, you must think more steps)。"
        }
        self.history.append(prompt_json)
        response = self.client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=self.history,
        )
        # 直接获取 message 字段，这里假设它是一个 CompletionMessage 实例
        choices = response.choices[0].message

        # 直接访问属性而不是作为字典键
        response_content = choices.content
        response_role = choices.role
        tool_calls = choices.tool_calls

        response_json = {
            "role": response_role,
            "content": response_content
        }
        self.history.append(response_json)

        return response_content

    "------------------------------------------下面是作图器部分--------------------------------------------------------------------"
    #显式图像
    def image_show(self,query):
        assert len(query) != 0, print("请输入作画要求")
        image = self.image_generator(query=query)
        image.show()

    #从做好的图像url地址将图像下载到本地
    def image_generator(self,query,return_np_image = False):
        assert  len(query) != 0,print("请输入作画要求")
        url = self.image_generator_get_url(query)

        import requests
        from PIL import Image
        from io import BytesIO

        # 发送HTTP请求获取图像数据
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        image = Image.open(BytesIO(response.content))

        if return_np_image:
            import  numpy as np
            import numpy as np
            _image = np.array(image)
            return image,_image #这里image的大小为[1024,1024],经过numpy则变为(1024, 1024, 3)
        return image

    #这力是使用作图器创作一个图像，并返回图像的URL地址
    def image_generator_get_url(self,query,
            quality = NOT_GIVEN,
            response_format  = NOT_GIVEN,
            size = NOT_GIVEN,
            style = NOT_GIVEN,
            user = NOT_GIVEN,
            extra_headers = None,
            disable_strict_validation = None):
        response = self.client.images.generations(
            model=self.image_model,  # 填写需要调用的模型名称
            prompt= query,
        )
        return (response.data[0].url)
    "------------------------------------------上面是作图器部分--------------------------------------------------------------------"

    "------------------------------------------下面是读图器，url输入可以为http://XXX.jpg--------------------------------------------------------------------"
    def read_pic_and_talk(self,query,url):
        response = self.client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[                {                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }                        }                    ]                }            ]        )
        return (response.choices[0].message.content)


if __name__ == '__main__':
    llm = AgentZhipuAI()

    response = llm("你好")
    print(response)

    response = llm("南京是哪里的省会")
    print(response)

    response = llm("那里有什么好玩的地方")
    print(response)

    "------------------------下面是作图的示例-----------------"
    image = llm.image_generator("一只可爱的小猫咪")   #返回一个图像image矩阵
    image.show()

    llm.image_show("鱼眼镜头里的小猫咪，背景是美丽的树林")    #直接展示image
    "------------------------上面是作图的示例-----------------"


    "--------------------下面是embedding的处理------------------"
    import time
    texts = ["不可以，早晨喝牛奶不科学", "今天早晨喝牛奶不科学", "早晨喝牛奶不科学"] * 10

    start_time = time.time()

    aembeddings, atexts = (llm.embedding_tool.aembed_documents(texts))
    print(len(aembeddings))
    print(len(atexts))
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"函数执行时间: {execution_time} 秒")
    "--------------------上面是embedding的处理------------------"

    response = llm.read_pic_and_talk("图里有什么",url="https://img1.baidu.com/it/u=1369931113,3388870256&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1703696400&t=f3028c7a1dca43a080aeb8239f09cc2f")
    print(response)