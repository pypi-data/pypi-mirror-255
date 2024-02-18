from typing import Optional, List, Any
import re


class ChineseTextSplitter:
    def __init__(
            self,
            chunk_vocab_size = 12,    #这里指的是每个chunk中包含的字符个数
            chunk_overlap = 0,
            customer_clean_fun = None
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__()

        print("\033[0;31;40m", "注意chunk_size定义为每个chunk中包含的字符个数，而不是chunk的数目", "\033[0m")
        # 确保chunk_size大于chunk_overlap
        assert chunk_vocab_size > chunk_overlap, "Chunk size must be greater than overlap."

        self._separators = [
            "\n\n",
            "\n",
            "[。！？]",  # 使用字符类来匹配中文字符的句号、感叹号和问号
            "\.\s|\!\s|\?\s",
            "[；;]\s",  # 同时匹配中文分号和英文分号
            "[，,]\s"  # 同时匹配中文逗号和英文逗号
        ]

        self.chunk_size = chunk_vocab_size
        self.chunk_overlap = chunk_overlap
        self.customer_clean_fun = customer_clean_fun

    def customer_clean(self,text):
        return self.customer_clean_fun(text)

    def load_txt(self,txt_file_path,need_clean_text = True):

        file_content = "".join(open(txt_file_path, "r", encoding="UTF-8").readlines())
        if need_clean_text:
            file_content = self.clean_text(file_content)

        if self.customer_clean_fun != None:
            file_content = self.customer_clean(file_content)


        chunk_size = self.chunk_size
        chunk_overlap = self.chunk_overlap

        # 初始化结果列表
        text_num = len(file_content)
        chunk_step = chunk_size - chunk_overlap
        chunks_num = text_num//chunk_step + 1
        print(f"您预期划分的每个段落块中有{chunk_size}个字符，预期划分的块数chunks_num为{chunks_num}个。总字数为{text_num}")

        return file_content


    def recursive_split_text(self, text: str,need_clean_text = True) -> List[str]:
        if need_clean_text:
            text = self.clean_text(text)

        if self.customer_clean_fun != None:
            text = self.customer_clean(text)

        chunk_size = self.chunk_size
        chunk_overlap = self.chunk_overlap

        # 初始化结果列表
        chunks = []
        text_num = len(text)
        chunk_step = chunk_size - chunk_overlap
        chunks_num = text_num//chunk_step + 1
        print(f"您预期划分的每个段落块中有{chunk_size}个字符，预期划分的块数chunks_num为{chunks_num}个。总字数为{text_num}")
        for i in range(chunks_num):
            start = i * chunk_step
            end = (i+1) * chunk_size
            chunks.append(text[start:end])

            # 返回结果列表
        return chunks

    def clean_text(self, text):
        separators = self._separators
        # 将包含管道符的模式字符串修正为正则表达式
        regex_patterns = [
                             re.escape(sep.replace('|', '')) for sep in separators if '|' not in sep
                         ] + [
                             sep.replace('|', '') for sep in separators if '|' in sep
                         ]
        # 合并所有的模式为一个大的正则表达式，使用管道符连接
        regex_combined = '|'.join(regex_patterns)
        # 使用正则表达式替换所有的匹配项为空字符串
        cleaned_text = re.sub(regex_combined, ' ', text)
        # 额外的步骤：将多个连续空格替换为单个空格，并去除文本开头和结尾的空格
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text

if __name__ == "__main__":
    text_splitter = ChineseTextSplitter(
        chunk_vocab_size=1280,
        chunk_overlap=5
    )

    file_content = "本来我抽了几天晚上和周末时间，刚开始提交是17名左右，在上周末被更多分数冲下来了，卷得飞起，主要是还在开发项目，时间确实有限，本来以为自己很拼了，我粗略估计，别人花的时间是我的十倍以上，让我想起了那句话：别拿自己的爱好挑战别人吃饭的技能，虽然我的AI能力很强， 但是金融知识确实欠缺，我有个梦想，就是AI可以逐步理解行业的思考逻辑，或者叫行业knowhow，以后做行业相关的还得打牢基础，目前还有点远。之，感谢举办方、感谢小打小闹，感谢小姐姐，加我微信指导我，挺负责的。以上仅是我的理解，有不妥之处还望指出，我来修正。"

    chunks = text_splitter.recursive_split_text(file_content)
    print(chunks)


