from lmchain.prompts.prompt_template import PromptTemplate


class LLMChain:
    def __init__(self,llm,prompt:PromptTemplate):
        super().__init__()
        self.llm = llm
        self.prompt = prompt

    def run(self,query):

        new_prompt = self.prompt.format(params = query)
        response = self.llm(new_prompt)

        return response


if __name__ == '__main__':
    decomp_template = """
        GENERAL INSTRUCTIONS
        You are a domain expert. Your task is to break down a complex question into simpler sub-parts.

        USER QUESTION
        {user_question}

        ANSWER FORMAT
        ["sub-questions_1","sub-questions_2","sub-questions_3",...]
        """

    from lmchain.prompts import PromptTemplate

    prompt = PromptTemplate(
        input_variables=["user_question"],
        template=decomp_template,
    )

    from lmchain.agents import AgentZhipuAI
    llm = AgentZhipuAI()

    chain = LLMChain(llm,prompt)
    query = "工商银行财报中，2024财年Q1与Q2 之间，利润增长了多少？"
    print(chain.run({"user_question": query}))

