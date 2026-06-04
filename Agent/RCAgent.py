# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  8/7/2024  6:20 PM
import json

from llm.LLM import LLM
from lib.lib import write_json_to_file, print_dic
from tools.widgets_info import ws
from prompts.PlanAgent_prompt import task_type_inference_Prompt, task_type_inference_ablation_Prompt,requirements_check
from prompts.DataAgent_prompt import table_choose_Prompt, table_choose_ablation_Prompt

import random
from tools.db import find_all_table_name,fetch_data_from_table,get_table_columns
from config.config import log
from tools.actions import action_agent

class ML_Requirements():
    def __init__(self, task: str):
        self.task = task
        self.task_type = "machine learning"
        self.ml_type = ""
        self.data_description=""
        self.data_source = {}
        self.preprocess = []
        self.one_hot_encode_vars=[]
        self.feature = []
        self.target = []
        self.model_widget_name = ""
        self.evaluate = False
        self.evaluate_result_save = False
        self.predict = False
        self.predict_result_save = False
        self.model_save = False
    def __str__(self):
        result = f"任务: {self.task}\n"
        result += f"任务类型: {self.task_type}\n"
        result += f"机器学习类型: {self.ml_type}\n"
        result += f"数据描述: {self.data_description}\n"
        result += f"数据源: {self.data_source}\n"
        result += f"预处理操作: {self.preprocess}\n"
        result += f"独热编码变量: {self.one_hot_encode_vars}\n"
        result += f"特征: {self.feature}\n"
        result += f"目标变量: {self.target}\n"
        result += f"模型组件名称: {self.model_widget_name}\n"
        result += f"是否评估: {self.evaluate}\n"
        result += f"是否预测: {self.predict}\n"
        result += f"是否保存预测结果: {self.predict_result_save}\n"
        result += f"是否保存模型: {self.model_save}\n"
        return result
    def prompt(self):
        Prompt = """你是一个有用的助手，你的任务是根据我给你的机器学习任务描述和数据集信息,进行以下判断：
        1. 判断机器学习任务类型，将其划分为['classification','regression','clustering','timeseries','others']中的一种，并在rationale当中给出你的理由。如果给出的信息不足以判断，可以归类为others,并在rationale给出推断，向我确认。
        2. 判断任务描述中是否特殊要求进行以下的处理组件如下：%s，请按照["<处理1>"，"<处理2>"...]格式回复，如果没有特别指明，将process设置为[],注意，如果使用了One Hot Encoder,你需要在one_hot_encode_vars字段给出需要编码的变量名。
        3. 根据机器学习任务类型，从数据的属性列中选出特征列(可以忽略一些无关的属性列)和目标列，除非是聚类任务，目标列为[]，其他类型任务必须要有一个属性为目标列,同一个属性不能同时属于特征列和目标列。
        4. 判断任务描述中是否指明具体使用的模型（算法）或及参数，目前支持的算法如下：%s,如果没有特别指明或者是该算法不被支持，根据数据集信息和任务类型从以上算法中进行选择。
        5. 判断任务描述中是否明确要求在测试集或者验证集上进行评估,在evaluate_in_test和evaluate_result_save给出判断结果。
        6. 判断任务描述中是否明确要求在测试集或者验证集上进行预测和保存预测结果，在predict_in_test和predict_result_save给出判断结果。
        7. 判断任务描述中是否明确要求对模型进行保存操作。
        数据按照json格式返回给我。
        回答示例：
        ```json
        {
        "rationale":"根据这个任务描述和数据集信息的推断，该任务应该是一个分类任务。",
        "task_type":"classification",
        "process":["Impute"],
        "one_hot_encode_vars":[],
        "feature":["width","length","color"],
        "target":["class_label"],
        "algorithm":"Random Forest",
        "evaluate_in_test":false,
        "evaluate_result_save":false,
        "predict_in_test":false,
        "predict_result_save":false,
        "model_save":false
        }
        ```
        回答严格按照这个JSON格式，不要回答无关内容。"""
        return Prompt % (str(ws.get_preprocess()), str(ws.get_ml_type_models_name()))

    def data_sets_info(self):
        messages = [{'role': 'system', 'content': table_choose_Prompt}, {'role': 'user',
                                                                         'content': "任务：" + self.task + "，数据库当中的表有：" + str(
                                                                             find_all_table_name())}]
        try:
            response_content = LLM.common_chat(messages=messages)
            json_data=LLM.ExtractJson(response_content)
            if len(json_data['table']) == 0:
                self.data_source = ""
                log.info("数据库中没有匹配的数据，默认只构建工作流。")
                return
            else:
                log.info(f'选中的表：{json_data}')
                self.data_source = json_data['table'][0]

        except Exception as e:
            log.error("choose_table error")
            raise Exception(f"choose_table error{e}")
        import pandas as pd


        tuple_data = fetch_data_from_table(table_name=self.data_source+"_train",limit=5000)
        cols_info = get_table_columns(self.data_source+"_train")
        attr = {}
        key = 0
        """
        "id": {
            "key": 0,
            "name": "id",
            "type": 2,
            "role": 0
        }"""
        for c in cols_info:
            #文本类型归类，不能直接忽略，直接忽略的默认做法会导致工作流无法正常运行
            type=-1
            role=-1
            if c[1]=="double" or "int" in c[1]:
                type=2
                role=0
            elif "varchar" in c[1] or "text" in c[1]:
                type=1
                role=0
            elif "date" in c[1]:
                type=4
                role=0
            attr[c[0]] = {
                "key": key,
                "name": c[0],
                "type": type,
                "role": role
            }
            key += 1

        action_agent.attr_mapping=attr
        columns = [col[0] for col in cols_info]
        df_data = pd.DataFrame(tuple_data, columns=columns)
        num_rows_with_na = df_data.isnull().any(axis=1).sum()
        # 计算总行数
        total_rows = len(df_data)
        null_columns = df_data.columns[df_data.isnull().any()].tolist()
        # 1. 检查是否存在重复行
        has_duplicates = df_data.duplicated().any()
        # 2. 计算重复行的数量
        num_duplicates = 0
        if has_duplicates:
            num_duplicates = df_data.duplicated().sum()
        random.seed(42)
        des=""
        des += f"数据一共有{total_rows}行"
        if num_rows_with_na > 0:
            des+= f"，以下列{null_columns}含有空值,含有空值的行数：{num_rows_with_na}，"
        else:
            des += "，数据无空值"
        if has_duplicates:
            des += f",重复数据的行数：{num_duplicates}"
        else:
            des += ",数据无重复行"
        des += f",属性列如下：{str(columns)}，随机2行数据样例如下：{random.sample(tuple_data, 2)}"
        self.data_description=des
        log.debug(f"数据描述：{des}")


class DL_Requirements():
    def __init__(self, task: str):
        self.task = task
        self.task_type = "deep learning"
        self.dl_type = ""
        self.model_widget_name = ""
        self.show_log = False
        self.predict = False
    def prompt(self):
        Prompt="""
        你是一个有用的助手，你的任务是根据我给你的深度学习任务描述进行以下判断。。
        1. 判断深度学习任务类型，将其划分为['text','image','audio','video','graph','others']中的一种。如果给出的信息不足以判断，可以归类为others,并在confirmation给出推断，向我确认,如果信息足够，confirmation应当为""。
        2. 判断任务描述中是否指明具体使用的模型（算法）或及参数，目前支持的算法如下：%s,如果没有特别指明或者是该算法不被支持，根据任务描述和任务类型从以上算法中进行选择。
        3. 判断任务描述中是否要求在测试集或者验证集上进行预测，在predict_in_test给出判断结果。
        4. 判断任务描述中是否要求展示训练日志或训练记录，在show_log给出判断结果。
        数据按照json格式返回给我。
        回答示例：
        ```json
        {
        "confirmation":"",
        "task_type":"text",
        "algorithm":"Text Classification",
        "predict_in_test":false,
        "show_log":false
        }
        ```
        回答严格按照这个JSON格式，不要回答无关内容。
        """
        return Prompt%(str(ws.get_dl_type_models_name()))

    def __str__(self):
        return f"""
        任务类型：{self.task_type}
        深度学习任务类型：{self.dl_type}
        模型widget_name：{self.model_widget_name}
        展示训练日志：{self.show_log}
        在测试集上进行预测：{self.predict}
        """

class PMA_Requirements():
    def __init__(self, task: str):
        self.task = task
        self.task_type = "pretrained modeling application"
        self.input_type=""
        self.model_widget_name = ""

    def prompt(self):
        Prompt= """
        你是一个有用的助手，你的任务是根据我给你的任务描述进行以下判断。
        1. 判断任务的输入类型，将其划分为['text','image','audio','video','graph','others']中的一种。如果给出的信息不足以判断，可以归类为others,并在confirmation给出推断，向我确认。
        2. 判断任务描述中是否指明具体使用的组件（算法）或及参数，目前支持的算法如下：%s,如果没有特别指明或者是该算法不被支持，根据任务描述和任务类型从以上算法中进行选择，算法参数则返回default，等待后续确认。
        数据按照json格式返回给我。
        回答示例：
        ```json
        {
        "confirmation":"",
        "input_type":"text",
        "widget_name":"audio synthesis"
        }
        ```
        回答严格按照这个JSON格式，不要回答无关内容。
        """
        return Prompt%(str(ws.get_PMA_type_models_name()))

    def __str__(self):
        return f"""
        任务类型：{self.task_type}
        深度学习任务类型：{self.input_type}
        模型widget_name：{self.model_widget_name}
        """


class RCAgent():
    def __init__(self,task:str,**kwargs):

        self.task=task
        self.task_type=""
        self.max_try = 3
        self.requirement=None
        self.real_task_info=kwargs.get("real_task_info")
    def task_type_inference(self):
        msgs = [{'role': 'system', 'content': task_type_inference_Prompt}]
        msgs.append({'role': 'user', 'content': "任务：" + self.task})
        res = LLM.common_chat(messages=msgs)
        ret=LLM.ExtractJson(res)
        ret=LLM.check_valid(ret,msgs,real_task_info=self.real_task_info,step=1)
        self.task_type = ret["task_type"]
        log.info(f'推断任务类型：{self.task_type}')
        if self.task_type == "machine learning":
            self.requirement=ML_Requirements(task=self.task)
            self.requirement.data_sets_info()
            self.machine_learn_rc(requires=self.requirement)


        elif self.task_type == "deep learning":
            self.requirement=DL_Requirements(task=self.task)
            self.deep_learn_rc(requires=self.requirement)
        elif self.task_type == "pretrained modeling applications":
            self.requirement=PMA_Requirements(task=self.task)
            self.pretrained_modeling_applications_rc(requires=self.requirement)

    def task_type_inference_ablation(self):
        def data_info():
            messages = [{'role': 'system', 'content': table_choose_ablation_Prompt}, {'role': 'user',
                                                                             'content': "任务：" + self.task + "，数据库当中的表有：" + str(
                                                                                 find_all_table_name())}]
            try:
                response_content = LLM.common_chat(messages=messages)
                json_data = LLM.ExtractJson(response_content)
                if len(json_data['table']) == 0:
                    log.info("数据库中没有匹配的数据，默认只构建工作流。")
                    return "",""
                else:
                    log.info(f'选中的表：{json_data}')
                    data_source = json_data['table'][0]

            except Exception as e:
                log.error("choose_table error")
                raise Exception(f"choose_table error{e}")
            import pandas as pd

            tuple_data = fetch_data_from_table(table_name=data_source + "_train", limit=5000)
            cols_info = get_table_columns(data_source + "_train")
            attr = {}
            key = 0
            """
            "id": {
                "key": 0,
                "name": "id",
                "type": 2,
                "role": 0
            }"""
            for c in cols_info:
                # 文本类型归类，不能直接忽略，直接忽略的默认做法会导致工作流无法正常运行
                type = -1
                role = -1
                if c[1] == "double" or "int" in c[1]:
                    type = 2
                    role = 0
                elif "varchar" in c[1] or "text" in c[1]:
                    type = 1
                    role = 0
                elif "date" in c[1]:
                    type = 4
                    role = 0
                attr[c[0]] = {
                    "key": key,
                    "name": c[0],
                    "type": type,
                    "role": role
                }
                key += 1

            action_agent.attr_mapping = attr
            columns = [col[0] for col in cols_info]
            df_data = pd.DataFrame(tuple_data, columns=columns)
            num_rows_with_na = df_data.isnull().any(axis=1).sum()
            # 计算总行数
            total_rows = len(df_data)
            null_columns = df_data.columns[df_data.isnull().any()].tolist()
            # 1. 检查是否存在重复行
            has_duplicates = df_data.duplicated().any()
            # 2. 计算重复行的数量
            num_duplicates = 0
            if has_duplicates:
                num_duplicates = df_data.duplicated().sum()
            random.seed(42)
            des = "数据集信息如下："
            des += f"数据一共有{total_rows}行"
            if num_rows_with_na > 0:
                des += f"，以下列{null_columns}含有空值,含有空值的行数：{num_rows_with_na}，"
            else:
                des += "，数据无空值"
            if has_duplicates:
                des += f",重复数据的行数：{num_duplicates}"
            else:
                des += ",数据无重复行"
            des += f",属性列如下：{str(columns)}，随机2行数据样例如下：{random.sample(tuple_data, 2)}"
            return data_source,des
        msgs = [{'role': 'system', 'content': task_type_inference_ablation_Prompt}]
        data_source,des=data_info()
        user_prompt="任务：" + self.task
        if len(des)>0:
            user_prompt+=des

        msgs.append({'role': 'user', 'content': user_prompt})
        res = LLM.common_chat(messages=msgs)
        ret=LLM.ExtractJson(res)

        # self.task_type = ret["task_type"]
        log.info(f'推断任务类型：{json.dumps(ret,ensure_ascii=False,indent=4)}')
        if ret["input_type"]=="tabular":
            self.task_type = "machine learning"
            self.requirement=ML_Requirements(task=self.task)
            self.requirement.data_source=data_source
            if "process" in ret.keys():
                self.requirement.preprocess = ret["process"]
            if "task_type" in ret.keys():
                if ret["task_type"] in ['classification','regression','clustering','timeseries']:
                    self.requirement.ml_type = ret["task_type"]
                else:
                    self.requirement.ml_type = ret["input_type"]
                self.requirement.ml_type = ret["task_type"]
            if "one_hot_encode_vars" in ret.keys():
                self.requirement.one_hot_encode_vars = ret["one_hot_encode_vars"]

            if "algorithm" in ret.keys():
                self.requirement.model_widget_name = ret["algorithm"]
            if "feature" in ret.keys():
                self.requirement.feature = ret["feature"]
            if "target" in ret.keys():
                self.requirement.target = ret["target"]
            if "evaluate_in_test" in ret.keys():
                self.requirement.evaluate = ret["evaluate_in_test"]
            if "evaluate_result_save" in ret.keys():
                self.requirement.evaluate_result_save = ret["evaluate_result_save"]
            if "predict_in_test" in ret.keys():
                self.requirement.predict = ret["predict_in_test"]
            if "predict_result_save" in ret.keys():
                self.requirement.predict_result_save = ret["predict_result_save"]
            if "model_save" in ret.keys():
                self.requirement.model_save = ret["model_save"]


        elif ret["input_type"] in ['text','image','audio','video','graph'] and ret["need_train_model"]:
            self.requirement=DL_Requirements(task=self.task)
            self.task_type = "deep learning"
            if "task_type" in ret.keys():
                if ret["task_type"] in ['text','image','audio','video','graph']:
                    self.requirement.dl_type = ret["task_type"]
                else:
                    self.requirement.dl_type = ret["input_type"]
            if "algorithm" in ret.keys():
                self.requirement.model_widget_name = ret["algorithm"]
            if "predict_in_test" in ret.keys():
                self.requirement.predict = ret["predict_in_test"]
            if "show_log" in ret.keys():
                self.requirement.show_log = ret["show_log"]
        elif ret["input_type"] in ['text','image','audio','video','graph'] and not ret["need_train_model"]:
            self.requirement=PMA_Requirements(task=self.task)
            self.task_type = "pretrained modeling application"
            if "algorithm" in ret.keys():
                self.requirement.model_widget_name = ret["algorithm"]
            if "input_type" in ret.keys():
                self.requirement.input_type = ret["input_type"]


    def machine_learn_rc(self,requires:ML_Requirements):
        msgs = [{'role': 'system', 'content': requires.prompt()}]
        msgs.append({'role': 'user', 'content': "任务：" + self.task+"数据集描述："+str(requires.data_description)})
        res = LLM.common_chat(messages=msgs)

        ret=LLM.ExtractJson(res)
        ret = LLM.check_valid(ret, msgs, real_task_info=self.real_task_info, step=2)
        # flag,feedback=True,""
        # try_count=1
        # while not flag:
        #     msgs.append({'role': 'user', 'content': "当前提取的需求存在如下问题："+feedback+"请检查你的结果。修改后再次返回给我。"})
        #     res = LLM.common_chat(messages=msgs)
        #
        #     ret=LLM.ExtractJson(res)
        #     try_count+=1
        #     if flag or try_count>self.max_try:
        #         break
        if "process" in ret.keys():
            requires.preprocess=ret["process"]
        if "task_type" in ret.keys():
            requires.ml_type=ret["task_type"]
        if "one_hot_encode_vars" in ret.keys():
            requires.one_hot_encode_vars=ret["one_hot_encode_vars"]

        if "algorithm" in ret.keys():
            requires.model_widget_name=ret["algorithm"]
        if "feature" in ret.keys():
            requires.feature=ret["feature"]
        if "target" in ret.keys():
            requires.target=ret["target"]
        if "evaluate_in_test"  in ret.keys():
            requires.evaluate=ret["evaluate_in_test"]
        if "evaluate_result_save" in ret.keys():
            requires.evaluate_result_save=ret["evaluate_result_save"]
        if "predict_in_test"  in ret.keys():
            requires.predict=ret["predict_in_test"]
        if "predict_result_save"  in ret.keys():
            requires.predict_result_save=ret["predict_result_save"]
        if "model_save"  in ret.keys():
            requires.model_save=ret["model_save"]



    def deep_learn_rc(self,requires:DL_Requirements):
        msgs = [{'role': 'system', 'content': requires.prompt()}]
        msgs.append({'role': 'user', 'content': "任务：" + self.task})
        res = LLM.common_chat(messages=msgs)

        ret = LLM.ExtractJson(res)

        flag, feedback = True, ""
        try_count = 1
        while not flag:
            msgs.append({'role': 'user',
                         'content': "当前提取的需求存在如下问题：" + feedback + "请检查你的结果。修改后再次返回给我。"})
            res = LLM.common_chat(messages=msgs)

            ret = LLM.ExtractJson(res)
            ret = LLM.check_valid(ret, msgs, real_task_info=self.real_task_info, step=2)
            # flag,feedback=self.check_requirements(requirements=ret,stage="type_infer")
            try_count += 1
            if flag or try_count > self.max_try:
                break

        if "task_type" in ret.keys():
            requires.dl_type = ret["task_type"]
        if "algorithm" in ret.keys():
            requires.model_widget_name = ret["algorithm"]
        if "predict_in_test" in ret.keys():
            requires.predict = ret["predict_in_test"]
        if "show_log" in ret.keys():
            requires.show_log = ret["show_log"]

    def pretrained_modeling_applications_rc(self,requires:PMA_Requirements):
        msgs = [{'role': 'system', 'content': requires.prompt()}]
        msgs.append({'role': 'user', 'content': "任务：" + self.task})
        res = LLM.common_chat(messages=msgs)
        msgs.append({'role': 'assistant', 'content': res})
        ret = LLM.ExtractJson(res)

        flag, feedback = True, ""
        try_count = 1
        while not flag:
            msgs.append({'role': 'user',
                         'content': "当前提取的需求存在如下问题：" + feedback + "请检查你的结果。修改后再次返回给我。"})
            res = LLM.common_chat(messages=msgs)

            ret = LLM.ExtractJson(res)
            # flag,feedback=self.check_requirements(requirements=ret,stage="type_infer")
            try_count += 1
            if flag or try_count > self.max_try:
                break
        if "widget_name" in ret.keys():
            requires.model_widget_name = ret["widget_name"]
        if "input_type" in ret.keys():
            requires.input_type = ret["input_type"]

    def check_requirements(self,requirement_type:str,requirements:str,**kwargs):
        #暂时未启用
        if requirement_type == "machine learning":
            msgs = [{"role": "system", "content": requirements_check}, {"role": "user",
                                                                        "content": "任务描述：" + self.task + "。需求提取：" +requirements}]
            responses_data = LLM.ExtractJson(LLM.common_chat(messages=msgs))
            write_json_to_file(msgs, "check_requirements")
            if responses_data["judge"] == "satisfactory":
                return True, ""
            else:
                return False, responses_data["rationale"]
        return True, ""
if __name__ == '__main__':
    task = "根据员工的个人相关数据并使用一个决策树算法，目的是来找出哪些员工可能要流失，最后对测试集进行预测，然后保存预测结果"
    RCAgent(task=task).task_type_inference()




