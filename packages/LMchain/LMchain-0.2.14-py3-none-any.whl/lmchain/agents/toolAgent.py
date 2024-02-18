from zhipuai import ZhipuAI
from lmchain.tools import glm4_tools

class GLMToolAgentZhipuAI:
    def __init__(self, api_key = "",client =ZhipuAI(api_key="a8f63606c4dd11d501aa6ffee9be16d6.icUQlh0I0DFFaD7s")):
        if api_key == "":
            self.client = client  # 可以使用你自己key定义的chient
        else:
            self.client = ZhipuAI(api_key=api_key)

        self.glm_tools = glm4_tools.GLMTool()

    def __call__(self, query):
        pass

    def run(self,query):
        try:
            query4tool = self.tool4query(query)
            # print(query4tool)
            # print(query4tool.tool_calls[0])
            # print(query4tool.tool_calls[0].function)
            # print(query4tool.tool_calls[0].function.name)
            # print(query4tool.tool_calls[0].function.arguments)
            tool_result = query4tool.tool_calls[0].function
            tool_name = tool_result.name    #这里是从工具库中找到的工具名称
            arguments = tool_result.arguments   #这里是从找到的参数
            tool_call = self.glm_tools.tool_register._TOOL_HOOKS[tool_name] #这里是根据工具名称找到的可调用的工具

            # 导入签名工具
            import json
            arguments_json = json.loads(arguments)
            args = [arguments_json[arg] for arg in (arguments_json)]

            return tool_call(*args)
        except:
            return "没有找到合适的工具，请确认工具是否提供或者您的要求是否合适."

    def dispatch_tool(self, tool_result) -> str:
        tool_name = tool_result.name
        tool_params = tool_result.arguments

        if tool_name not in self.glm_tools.tool_register._TOOL_HOOKS:
            return f"Tool `{tool_name}` not found. Please use a provided tool."
        tool_call = self.glm_tools.tool_register._TOOL_HOOKS[tool_name]

        try:
            ret = tool_call(**tool_params)
        except:
            import traceback
            ret = traceback.format_exc()
        return str(ret)


    def tool4query(self,query):
        tools = self.get_tools()
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        response = self.client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        return (response.choices[0].message)

    def get_tools(self):
        return self.glm_tools.get_tools()


    def add_tool(self,tool_fun:object):
        self.glm_tools.add_tools(tool_fun)

    def bind_tool(self,tool_fun:object):
        self.glm_tools.add_tools(tool_fun)

    def add_tools(self,tool_funs:list):
        for tool_fun in tool_funs:
            self.glm_tools.add_tools(tool_fun)


if __name__ == '__main__':
    from typing import Annotated
    #下面是一个自定义的乘法公式
    def math_multi_fun(
            a: Annotated[int, 'The random seed used by the generator'],
            b: Annotated[int, 'The range of the generated numbers'],
    ) -> float:
        """
        一个简单的乘法数学公式
        """
        return a * b + 1

    tool_agent = GLMToolAgentZhipuAI()

    query = "帮我查一下上海的天气"
    # query = "帮我定一下飞机"
    response = tool_agent.run(query)
    print(response)

    tool_agent.add_tool(math_multi_fun)
    print(tool_agent.get_tools())
    query = "帮我算一下3乘以5"
    response = tool_agent.run(query)
    print(response)



