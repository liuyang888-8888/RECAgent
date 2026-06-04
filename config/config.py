# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/6/9 
# 时 间：20:19
import logging.config
import os
from lib.lib import find_project_root
from datetime import datetime
import colorlog

###########################################################
###                  Uniplore AuthToken                 ###
###########################################################
# Accesstoken = r"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NDQzODI3OTMsImlhdCI6MTc0NDM3MTk5MywiaXNzIjoidW5pcGxvcmUiLCJkYXRhIjp7ImlkIjo3MywibmFtZSI6IjEyMzQ1NiIsImVtYWlsIjoiMTIzQHFxLmNvbSIsInRlbmFudF9pZCI6MTAwMDAwfX0.4bzlJ2c3HVm5ZDUH9ZzI0kgglXxWeOiNIEB4qJ9ey3E"
# Workflow_id = 6
Accesstoken = r"xxx-xxxxxxxxxxxxxxxxxxx"
Workflow_id = 41





###########################################################
###                      LLM API KEY                    ###
###########################################################

model_conf = "openai"
# model_conf = "dashscope"
# model_conf="zhipuai"



openai_config={
    "BASE_URL":"https://dashscope.aliyuncs.com/compatible-mode/v1",
    "API_KEY":"xxx",
    "MODEL":"qwen2.5-72b-instruct"

}


zhipuai_config={
    "API_KEY":"7fd10a17f7ed02e7b1bc4c4bd40f94d1.Y1QhGU8hDgszoLfx",
    "MODEL":"glm-4-flash"
}

aliyun_config={
    "API_KEY":os.environ.get("ALIYUN_KEY"),
    "MODEL":"qwen2.5-72b-instruct"
}

###########################################################
###                      MYSQL Config                   ###
###########################################################
MySQL_Config = {
    "host": "",
    "port": 23309,
    "user": "deploy",
    "passwd": "xxx",
    "db": "MLBench"
}


###########################################################
###                      Other Config                   ###
###########################################################
save_chat_log=False




###########################################################
###                      LOG Config                    ###
###########################################################
now = datetime.now()
formatted_time = now.strftime('%Y-%m-%d')
debug_log=os.path.join(find_project_root(),f'WPO_Experiment/logs\\{formatted_time}.log')
#日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s %(module)s : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',

        },
        'simple': {
            'format': '%(log_color)s%(module)s: %(message_log_color)s%(message)s%(reset)s',
            '()': 'colorlog.ColoredFormatter',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            'secondary_log_colors': {
                'message': {
                    'DEBUG': 'white',
                    'INFO': 'bold_white',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red'
                }
            }
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': debug_log,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'dev': {  # 自定义logger名称
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    # 'root': {  # 根logger配置
    #     'handlers': ['console'],
    #     'level': 'INFO',
    # },
}
logger = logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('dev')