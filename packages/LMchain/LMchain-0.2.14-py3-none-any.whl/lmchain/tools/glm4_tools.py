from lmchain.tools import tool_register
from typing import Annotated


class GLMTool:
    def __init__(self):
        super().__init__()
        self.tool_register = tool_register

    def add_tools(self, tool):
        self.tool_register.register_tool(tool)
        return True

    def get_tools_json(self):
        return (self.tool_register.get_tools())

    def get_tools(self):
        _tools = self.get_tools_json()
        tools = []

        for fun_name in _tools:

            value = (_tools[fun_name])

            params = value["params"]
            properties = {}
            for param in params:properties[param["name"]] = {"type": param["type"],"description": param["description"],}

            tool = {
                "type":"function",

                "function": {
                    "name": fun_name,

                    "description": value["description"],

                    "parameters":{"type": "object","properties":properties,"required":list(properties.keys())}
                },
            }
            tools.append(tool)
        return tools


if __name__ == '__main__':
    glm_tool = GLMTool()



    def rando_numbr(
            seed: Annotated[int, 'The random seed used by the generator'],
            range: Annotated[tuple[int, int], 'The range of the generated numbers'],
    ) -> int:
        """
        Generates a random number x, s.t. range[0] <= x < range[1]
        """
        import random
        return random.Random(seed).randint(*range)


    glm_tool.add_tools(rando_numbr)
    tools = glm_tool.get_tools()
    from zhipuai import ZhipuAI
    api_key = "a8f63606c4dd11d501aa6ffee9be16d6.icUQlh0I0DFFaD7s"
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey

    messages = [
        {
            "role": "user",
            "content": "帮我查一下上海的天气"
        }
    ]
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    print(response.choices[0].message)