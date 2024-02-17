
class SubQuestChain:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, query=""):
        if query == "":
            raise "query需要填入查询问题"

        decomp_template = """
            用中文回答下面问题，下面有一些要求：
            You are a domain expert. Your task is to break down a complex question into simpler sub-parts.
            选择你认可的最合适的分解步骤，在回答之前要仔细想清楚再回复，不要额外添加不需要的内容。
            并且你需要尝试使用你的答案验证是否可以解决问题，如果确定可以解决就坚定的回答问题。
            回答的时候只需要按ANSWER FORMAT格式，不要回答其他内容也不要进行解释。
            Let’s think step by step, you must think more steps.
            
            USER QUESTION
            {user_question}

            ANSWER FORMAT
            ["sub-questions_1","sub-questions_2","sub-questions_3","sub-questions_4",...]
            
            """

        from lmchain.prompts import PromptTemplate
        prompt = PromptTemplate(
            input_variables=["user_question"],
            template=decomp_template,
        )

        from lmchain.chains import LLMChain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run({"user_question": query})

        return response

    def run(self, query):
        sub_list = self.__call__(query)
        return sub_list


if __name__ == '__main__':
    from lmchain.agents import llmMultiAgent

    llm = llmMultiAgent.AgentZhipuAI()
    subQC = SubQuestChain(llm)
    response = subQC.run(query="工商银行财报中，2024财年Q1与Q2 之间，利润增长了多少？")
    print(response)