# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  6/14/2024  3:19 PM
from openai import OpenAI, completions
from config.config import log,openai_config
# Set OpenAI's API key and API base to use vLLM's API server.

class OPENAI():
    def __init__(self):
        self.client = OpenAI(
            api_key=openai_config["API_KEY"],
            base_url=openai_config["BASE_URL"],
        )

    def chat(self,messages):
        response = self.client.chat.completions.create(
            model=openai_config["MODEL"],
            messages=messages,
            temperature=0,
            top_p=1
        )
        return response

    def chat_stream(self,messages):
        response = self.client.chat.completions.create(
            model=openai_config["MODEL"],
            messages=messages,
            temperature=0,
            top_p=1,
            stream=True,
        )
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, flush=True)
                full_response += chunk.choices[0].delta.content
                print(chunk)
        return full_response





if __name__=="__main__":
    pass
    # local_chat_stream(messages)




