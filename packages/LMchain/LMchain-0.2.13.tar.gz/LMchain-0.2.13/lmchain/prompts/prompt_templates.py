from abc import ABC, abstractmethod


class MessagePromptTemplate(ABC):
    def __init__(self, role, message):
        self.role = role
        self.message = message

    @abstractmethod
    def format(self):
        # 这里可以添加自定义的格式化逻辑
        return f"[{self.role}]: {self.message}"

    @classmethod
    def from_template(cls, existing_template):
        # 假设existing_template是一个包含'role'和'message'属性的对象
        return cls(existing_template.role, existing_template.message)


class HumanMessagePromptTemplate(MessagePromptTemplate):
    def __init__(self, role = "Human", message = ""):
        self.role = role
        self.message = message

    def format(self):
        # 这里可以添加自定义的格式化逻辑
        return f"[{self.role}]: {self.message}"

    @classmethod
    def from_template(cls, existing_template):
        # 假设existing_template是一个包含'role'和'message'属性的对象
        return cls(existing_template.role, existing_template.message)



if __name__ == '__main__':

    # 使用示例
    ai_message = MessagePromptTemplate("AI", "Hello, how can I assist you?")
    formatted_ai_message = ai_message.format()
    print(formatted_ai_message)  # 输出: [AI]: Hello, how can I assist you?


