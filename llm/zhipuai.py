# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  2024/9/13  10:07
from zhipuai import ZhipuAI
from config.config import log,zhipuai_config

class zhipuai:
    def __init__(self):
        pass
    def chat(self,messages):
        try:
            client = ZhipuAI (api_key=zhipuai_config["API_KEY"])  #
            response = client.chat.completions.create (
                model=zhipuai_config["MODEL"],
                temperature=0,
                messages=messages,
            )
            log.info(f"user:{messages[-1]['content']}")
            log.debug(f'{zhipuai_config["MODEL"]}respond:{response.choices [0].message.content}')
            return response.choices[0].message.content
        except Exception as e:
            log.error(f"chat error{e}")
            raise Exception(e)



if __name__=="__main__":
    pass