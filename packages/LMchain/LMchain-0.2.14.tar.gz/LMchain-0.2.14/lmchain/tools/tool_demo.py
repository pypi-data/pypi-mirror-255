#这里我的思路是，分别对于不同的问询情况，判定该使用哪种时间计算处理的函数

def fun(ztime, data):
    min_time = min(item['time'] for item in data)
    if ztime < min_time:
        return 0.

    dp = [[0 for _ in range(ztime + 1)] for _ in range(len(data) + 1)]

    for i in range(1, len(data) + 1):
        for j in range(1, ztime + 1):
            if j >= data[i - 1]['time']:
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - data[i - 1]['time']] + data[i - 1]['view'])
            else:
                dp[i][j] = dp[i - 1][j]

    max_experience = dp[-1][ztime]

    # step9: 反推选择的项目
    chosen_projects = []
    i, j = len(data), ztime
    while i > 0:
        if dp[i][j] != dp[i - 1][j]:
            chosen_projects.append(data[i - 1]['name'])
            j -= data[i - 1]['time']
        i -= 1

    chosen_projects.reverse()  # 反转列表，以得到正确的顺序
    return chosen_projects, max_experience


from typing import Annotated
def max_view_experience_hours(
        data: Annotated[list, '一份数据，包含:“游乐项目名称name”、“用时time”、“体验指数（视觉指数view、刺激指数thrill）'],
        ztime: Annotated[int, '按小时来计数，游玩项目消耗的总时长,用小时来计数']
):
    """
        在给定的时间内，处理景点游玩时间方面的最优规划，这个时间情景问题
    """
    data = data["Items"]

    response = fun(ztime*60, data)

    return response

def max_view_experience_minutes(
        data: Annotated[list, '一份数据，包含:“游乐项目名称name”、“用时time”、“体验指数（视觉指数view、刺激指数thrill）'],
        ztime: Annotated[int, '按分钟来计数，游玩项目消耗的总时长,用分钟来计数']
):
    """
        在给定的时间内，处理景点游玩时间方面的最优规划，这个时间情景问题
    """
    data = data["Items"]

    response = fun(ztime, data)

    return response


data = [
    {"name": "喷气背包飞行器", "time": 60, "view": 3, "thrill": 9},
    {"name": "创极速光轮-雪佛兰呈现", "time": 50, "view": 7, "thrill": 10},
    {'name': '抱抱龙冲天赛车', 'time': 100, 'view': 3, 'thrill': 8},
    {'name': '小熊维尼历险记', 'time': 50, 'view': 7, 'thrill': 4},
    {'name': '疯狂动物城', 'time': 220, 'view': 9, 'thrill': 6},
    {'name': '加勒比海盗-沉落宝藏之战', 'time': 45, 'view': 10, 'thrill': 4},
    {'name': '翱翔-飞跃地平线', 'time': 130, 'view': 10, 'thrill': 8},
    {'name': '雷鸣山漂流', 'time': 130, 'view': 4, 'thrill': 9},
    {'name': '小飞象', 'time': 40, 'view': 6, 'thrill': 5},
    {'name': '城堡迎宾阁', 'time': 60, 'view': 7, 'thrill': 1},
    {'name': '小矮人矿山车', 'time': 145, 'view': 3, 'thrill': 8}
]

from lmchain.agents import toolAgent

tool_agent = toolAgent.GLMToolAgentZhipuAI(api_key="1656d1ee48a05ddb91dc6c7366c2eeb8.UuWXdmwv8iDS2VTG")
tool_agent.add_tool(max_view_experience_hours)
tool_agent.add_tool(max_view_experience_minutes)

query = "只有120分钟，怎么玩才能视觉体验最大化"
prompt = f"""
    你现在作为一个人工智能算法助手，根据提供给你的DATA，调用函数帮助游客解答query查询问题。
    你的函数工具箱中分别有以下几个函数：
        1、在给定的时间内，处理景点游玩时间方面的最优规划，这个时间情景问题；


    <DATA>
    {data}

    <USER QUESTION>
    {query}

    请严格按照上述算法和输出要求，运算出结果并输出。让我们一步一步来思考！
"""
response = tool_agent.run(prompt)
print(response)



query = "只有3个小时，怎么玩才能视觉体验最大化"
prompt = f"""
    你现在作为一个人工智能算法助手，根据提供给你的DATA，调用函数帮助游客解答query查询问题。
    你的函数工具箱中分别有以下几个函数：
        1、在给定的时间内，处理景点游玩时间方面的最优规划，这个时间情景问题；


    <DATA>
    {data}

    <USER QUESTION>
    {query}

    请严格按照上述算法和输出要求，运算出结果并输出。让我们一步一步来思考！
"""
response = tool_agent.run(prompt)
print(response)

"-----------------------------下面是一个生成函数的demo----------------------------------"
# query = "游玩300分钟，玩哪些项目刺激最大"
#
# from lmchain.agents import AgentZhipuAI
#
# llm = AgentZhipuAI(api_key="1656d1ee48a05ddb91dc6c7366c2eeb8.UuWXdmwv8iDS2VTG")
#
# prompt = f"""
# 你现在作为一个人工智能算法助手，
# 根据下面提供的算法逻辑和【0-1背包问题】解题思路来处理景点游玩最优规划这个情景问题。
# 【代码算法逻辑及步骤】：
# step1:分析问题,获得可用总时长$ztime（分钟）;
# step2:加载以下全部11组$data数据
# $data = {data}；
# 其中“游乐项目名称name”、“用时time”、“体验指数（视觉指数view、刺激指数thrill）”。
# step3:分析问题,设置对应要计算的指数（刺激指数:thrill;视觉指数:view）;
# step4:判断总耗时是否小于$data中的time最小值，如果小于则直接结束运算，说明不会存在最优解。如果大于等于则进行下一步;
# step5：定义状态 dp[i][j]，表示前 i 个物品在容量为 j 的背包下的最大值。
# step6：初始化 dp 状态，dp[0][j] = 0，表示背包没有容量时的最大价值也就是 0。
# step7：状态转移方程为 dp[i][j] = max(dp[i-1][j], dp[i-1][j - data[i].time] + data[i].thrill) if j > data[i].time else dp[i-1][j] 。表示在有足够容量的情况下，可以选择放入或者不放入当前的物品。
# step8：求出 dp[len(data)][$ztime]，该值就是最大的体验指数。
# step9：通过 dp 状态表，反推出$data.name(项目名称)。
#
# query = {query}
#
# 请严格按照上述算法和输出要求，运算出结果并输出。让我们一步一步来思考！
# """
#
# print(prompt)
#
# response = llm(prompt)
# print(response)