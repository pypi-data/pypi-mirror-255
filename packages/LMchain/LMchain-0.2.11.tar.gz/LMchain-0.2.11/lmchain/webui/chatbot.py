import gradio as gr
from lmchain.agents import llmMultiAgent

import time
import gradio as gr


from lmchain.agents import llmMultiAgent
llm = llmMultiAgent.AgentZhipuAI()

def slow_echo(message,history):
    response = llm(message)
    for i in range(len(response)):
        time.sleep(0.02)
        yield "AI Ans: " + response[: i+1]

app = gr.ChatInterface(slow_echo,autofocus=True).queue()

if __name__ == "__main__":
    app.launch(share=True)



