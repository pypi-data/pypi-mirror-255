import re,urllib.parse,urllib.request,urllib.error
from bs4 import BeautifulSoup as BS
import time


# 获取bing搜索的结果
def get_bing_results(word):
    baseUrl = 'http://cn.bing.com/search?'  # Bing搜索的基础URL
    data = {'q': word}  # 构造查询参数，其中'q'表示查询关键字，word为用户输入的搜索词
    data = urllib.parse.urlencode(data)  # 将查询参数编码为URL格式
    url = baseUrl + data  # 拼接成完整的搜索URL
    #print(url)  # 打印URL，用于调试

    try:
        html = urllib.request.urlopen(url)  # 尝试打开URL并获取响应内容
        soup = BS(html, "html.parser")  # 使用BeautifulSoup解析HTML内容，注意这里BS应该改为BeautifulSoup
        context = soup.findAll(class_="b_lineclamp4 b_algoSlug")  # 查找符合特定class属性的HTML元素，这里可能是搜索结果的容器
        results = ""  # 初始化一个空字符串用于存储处理后的搜索结果
        for i in range(len(context)):  # 遍历查找到的HTML元素
            if '\u2002·\u2002' not in str(context[i]):  # 如果元素中不包含特定字符（中间点·），则跳过
                continue
            results += (str(i) + '）')  # 将当前元素的索引添加到结果字符串中，并加上中文右括号
            # 分割字符串并移除HTML的</p>标签，这里假设搜索结果的标题和链接之间以中间点·分隔
            results += (str(context[i]).split('\u2002·\u2002')[1].replace('</p>', ''))
        return results, soup, context  # 返回处理后的搜索结果、soup对象以及原始的HTML元素，用于调试
    except urllib.error.HTTPError as e:  # 捕获HTTP错误
        print(e.code)  # 打印HTTP错误代码
        return None, None, None  # 在异常发生时返回None
    except urllib.error.URLError as e:  # 捕获URL错误
        print(e.reason)  # 打印URL错误原因
        return None, None, None  # 在异常发生时返回None


class WebSearchChain:
    def __init__(self, llm = ""):
        self.llm = llm

    def __call__(self, query = ""):

        flag = True
        counter = 0
        while flag:
            results, soup, context = self.get_bing_results(query)
            counter += 1
            if len(context) != 0 or counter >= 3:
                flag = False
            else:
                time.sleep(3)
        if len(context) == 0:
            return "未找到答案，请更换查询内容~"
        pattern = re.compile(r'<[^>]+>')
        context = [pattern.sub('', str(cont)) for cont in context]

        decomp_template = """
            用中文回答下面问题，下面有一些要求：
            
            你是一个很棒的网页搜索助手，现在你需要回答下面问题'{query}',而你现在有一些参考资料'{context}'。
            这些内容来自于网络，你需要根据给你的参考资料回答问题。
            Let’s think step by step, you must think more steps.

            如果你找到问题的答案，就直接回复问题。
            如果没有找到答案就回复'未找到对应答案，请重新运行~'

            """

        from lmchain.prompts import PromptTemplate
        prompt = PromptTemplate(
            input_variables=["query","context"],
            template=decomp_template,
        )

        # prompt = prompt.format(query=query, context=context)
        # response = self.llm(prompt)
        #
        from lmchain.chains import LLMChain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run({"query": query,"context":context})

        return response

    def get_bing_results(self,word):
        baseUrl = 'http://cn.bing.com/search?'  # Bing搜索的基础URL
        data = {'q': word}  # 构造查询参数，其中'q'表示查询关键字，word为用户输入的搜索词
        data = urllib.parse.urlencode(data)  # 将查询参数编码为URL格式
        url = baseUrl + data  # 拼接成完整的搜索URL
        # print(url)  # 打印URL，用于调试

        try:
            html = urllib.request.urlopen(url)  # 尝试打开URL并获取响应内容
            soup = BS(html, "html.parser")  # 使用BeautifulSoup解析HTML内容，注意这里BS应该改为BeautifulSoup
            context = soup.findAll(class_="b_lineclamp4 b_algoSlug")  # 查找符合特定class属性的HTML元素，这里可能是搜索结果的容器
            results = ""  # 初始化一个空字符串用于存储处理后的搜索结果
            for i in range(len(context)):  # 遍历查找到的HTML元素
                if '\u2002·\u2002' not in str(context[i]):  # 如果元素中不包含特定字符（中间点·），则跳过
                    continue
                results += (str(i) + '）')  # 将当前元素的索引添加到结果字符串中，并加上中文右括号
                # 分割字符串并移除HTML的</p>标签，这里假设搜索结果的标题和链接之间以中间点·分隔
                results += (str(context[i]).split('\u2002·\u2002')[1].replace('</p>', ''))
            return results, soup, context  # 返回处理后的搜索结果、soup对象以及原始的HTML元素，用于调试
        except urllib.error.HTTPError as e:  # 捕获HTTP错误
            print(e.code)  # 打印HTTP错误代码
            return None, None, None  # 在异常发生时返回None
        except urllib.error.URLError as e:  # 捕获URL错误
            print(e.reason)  # 打印URL错误原因
            return None, None, None  # 在异常发生时返回None


if __name__ == '__main__':

    from lmchain.agents import llmMultiAgent
    llm = llmMultiAgent.AgentZhipuAI()


    #搜索框中的搜索内容
    query = '酶切位点的作用是什么？'

    WebSearchChain(llm=llm)(query)




# from langchain.prompts import PromptTemplate
#
# template = """
# 你是一个网页搜索助手，现在有一个问题{query}你需要回答，而同时会提供你一份参考文献{context},你要根据这个参考文献，仔细思考后回答。
# 如果找不到对应的答案，请回答“没有找到对应内容，请重试。”
# """
# prompt = PromptTemplate(
#     input_variables=["query","context"],
#     template=template,
# )
#
# from lmchain.agents import llmMultiAgent
# llm = llmMultiAgent.AgentZhipuAI()
#
# from langchain.chains import LLMChain
# chain = LLMChain(llm=llm, prompt=prompt)
# print(chain.run({"query":query,"context":context}))
