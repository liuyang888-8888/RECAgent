# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  8/20/2024  5:36 PM

from config.config import log,model_conf
import json
import re


class llm():
    def __init__(self):
        self.tokens=[]
        self.client=None
        if model_conf == "openai":
            from llm.OPENAI import OPENAI
            self.client=OPENAI()
        elif model_conf == "dashscope":
            from llm.DashScope import Aliyun_Chat
            self.client=Aliyun_Chat()
        elif model_conf == "zhipuai":
            from llm.zhipuai import zhipuai
            self.client=zhipuai()
        else:
            raise Exception("model not support")

    def common_chat(self,messages):
        res=self.client.chat(messages)
        if hasattr(res.usage, "prompt_tokens"):
            self.tokens.append({
                "prompt_tokens": res.usage.prompt_tokens,
                "completion_tokens": res.usage.completion_tokens,
                "total_tokens": res.usage.total_tokens
            })
        elif hasattr(res.usage, "input_tokens"):
            self.tokens.append({
                "prompt_tokens": res.usage.input_tokens,
                "completion_tokens": res.usage.output_tokens,
                "total_tokens": res.usage.total_tokens
            })
        else:
            raise Exception("token consume attr not found")
        messages.append({"role": "assistant", "content": res.choices[0].message.content})
        # log.debug(json.dumps(messages, ensure_ascii=False, indent=4))
        log.info(
            f"token prompt_tokens:{int(res.usage.prompt_tokens) / 1000}k ,completion_tokens:{int(res.usage.completion_tokens) / 1000}k")
        print(res)
        return res.choices[0].message.content

    def ExtractJson(self, res: str, message=[], max_retries: int = 3):
        """
        从字符串中提取JSON对象，优先解析代码块中的内容，否则尝试整体解析。
        如果失败，会要求模型重新返回，并再次尝试解析，最多 max_retries 次。
        """

        def try_load(text):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None

        # 避免错误替换字符串内容，先简单替换布尔值
        res = res.replace("True", "true").replace("False", "false")

        # 1. 优先提取 ```json ... ```
        match = re.search(r"```json\s*([\s\S]*?)```", res, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            ret = try_load(candidate)
            if ret is not None:
                return ret

        # 2. 尝试整体解析
        ret = try_load(res)
        if ret is not None:
            return ret

        # 3. 如果失败，判断是否还能重试
        if max_retries <= 0:
            raise Exception(f"json extract error: 超过最大重试次数，最后返回内容:\n{res}")

        message.append({
            "role": "user",
            "content": "请检查你的回复，确保能够被json.loads()函数正常导入。"
        })
        new_res = self.common_chat(messages=message)

        # 递归调用，减少重试次数
        return self.ExtractJson(new_res, message, max_retries=max_retries - 1)

    def check_valid(self,ret: dict, messages: list,**kwargs):
        if "task_type" in ret:
            try_count = 0
            while ret["task_type"] == "unsure" or ret["task_type"] == "others":
                print(ret["rationale"])
                # supplemental_information = input("补充信息：")
                if kwargs.get("step",0)==1:
                    supplemental_information = f"这个任务是{kwargs.get('real_task_info')['task_type']}任务。"
                elif kwargs.get("step",0)==2:
                    if kwargs.get('real_task_info')['task_type']=="machine learning":
                        supplemental_information = f"这个任务是{kwargs.get('real_task_info')['machine_learning_type']}任务。"
                    elif kwargs.get('real_task_info')['task_type']=="deep learning":
                        supplemental_information = f"这个任务是{kwargs.get('real_task_info')['deep_learning_type']}任务。"
                # supplemental_information = "graph聚类分析应该属于deep learning,graph的其他分析任务应该属于pretrained modeling application"
                messages.append({'role': 'user', 'content': supplemental_information})
                res = self.common_chat(messages=messages)
                messages.append({'role': 'assistant', 'content': res})
                ret = self.ExtractJson(res)
                try_count += 1
                if try_count > 3:
                    print("多次无法判断，请检查输入")
                    raise Exception(f"多次无法判断，请检查输入:{messages}")

        return ret

LLM=llm()

if __name__ == '__main__':
    print(LLM.common_chat([{'role': 'user', 'content': "你好"}]))