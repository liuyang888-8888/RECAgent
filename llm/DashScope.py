# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  8/7/2024  6:33 PM

import time
from http import HTTPStatus
import dashscope
from config.config import log,aliyun_config

class Aliyun_Chat:
    def __init__(self):
        pass

    def chat(self,model=aliyun_config["MODEL"], messages:list=[]):
        if len(messages)==0:
            log.error("user message is empty!")

        dashscope.api_key=aliyun_config["API_KEY"]
        response = dashscope.Generation.call (
            model=model,
            messages=messages,
            temperature=0,
            top_k=1,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code==HTTPStatus.OK:
            return response
            # return response.output.choices[0].message.content
        elif response.status_code==HTTPStatus.TOO_MANY_REQUESTS:
            log.info("Too many requests, wait 3s")
            time.sleep(0.5)
            response = dashscope.Generation.call (
                model=model,
                messages=messages,
                result_format='message',  # set the result to be "message" format.
            )
            if response.status_code == HTTPStatus.OK:
                return response
            else:
                raise Exception ('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
        else:

            log.debug ('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            raise Exception ("Http request error")

if __name__ == '__main__':
    pass