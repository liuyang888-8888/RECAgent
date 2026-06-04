# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/8/29 
# 时 间：11:13
import json
import re

from pyexpat import features
from typing import Union

from pyexpat.errors import messages

from lib.lib import write_json_to_file
from prompts.CodeAgent_prompt import Prompt,CODE_TEMPLATE
from .RCAgent import ML_Requirements,DL_Requirements,PMA_Requirements
from config.config import log
from llm.LLM import LLM
from tools.actions import get_workflow, add_node, add_edge, update_node_params, action_agent, delete_node
from tools.widgets_info import ws


class WBAgent:
    def __init__(self,requires:Union[ML_Requirements, DL_Requirements, PMA_Requirements, None] = None):
        self.requires = requires
        self.need_update_params={}
        self.max_try = 3

    def build_base_workflow(self):
        if hasattr(self.requires,"task_type") and self.requires.task_type == "machine learning":
            if len(self.requires.data_source)==0:
                input_id=add_node(widget_name="File",node_name="上传本地文件")
            else:
                input_id=add_node(widget_name="SQL Table",node_name="加载数据库文件")
                #更新特征映射
                for key,value in action_agent.attr_mapping.items():
                    if key in self.requires.target:
                        action_agent.attr_mapping[key]["role"]=1
                    elif key in self.requires.feature:
                        action_agent.attr_mapping[key]["role"]=0
                    else:
                        action_agent.attr_mapping[key]["role"]=2

                update_node_params(node_id=input_id,node_params={"table_name":self.requires.data_source+"_train"})
            last_widget_id = input_id
            if len(self.requires.preprocess)!=0:
                for key in self.requires.preprocess:
                    if key == "Data Sampler":
                        # delete_node(input_id)
                        continue
                    preprocess_id=add_node(widget_name=key,node_name=key)
                    add_edge(source_node_id=last_widget_id,target_node_id=preprocess_id)
                    last_widget_id=preprocess_id
            # 用户特征工程节点
            if len(self.requires.feature)!=0:
                feature_id=add_node(widget_name="Select Columns",node_name="特征工程")
                add_edge(source_node_id=last_widget_id,target_node_id=feature_id)
                last_widget_id = feature_id
            if "Data Sampler" in self.requires.preprocess:
                data_sample_id=add_node(widget_name="Data Sampler",node_name="数据采样")
                add_edge(source_node_id=last_widget_id,target_node_id=data_sample_id)
                last_widget_id = data_sample_id



            # 模型节点
            if len(self.requires.model_widget_name)!=0:
                model_id=add_node(widget_name=self.requires.model_widget_name,node_name=self.requires.model_widget_name)
                add_edge(source_node_id=last_widget_id,target_node_id=model_id)
                last_widget_id=model_id
            if  self.requires.evaluate:
                # 加载验证集和数据处理 增加评估组件
                if "Data Sampler" not in self.requires.preprocess:
                    workflow = get_workflow()
                    model_widget_names = ws.get_models_widget_names()
                    preprocess = []

                    map = {}
                    for node in workflow["nodes"]:
                        if node["widget_name"] in model_widget_names:
                            model_id = node["node_id"]
                            continue
                        if node["widget_name"] == "SQL Table":
                            preprocess.append(node["node_id"])
                            id = add_node(widget_name=node["widget_name"], node_name="测试集加载")
                            test_sql_id = id

                            update_node_params(id, {"table_name": self.requires.data_source + "_test"})
                            map[node["node_id"]] = id
                        elif node["widget_name"] == "File":
                            preprocess.append(node["node_id"])

                            id = add_node(widget_name=node["widget_name"], node_name="上传测试集")
                            update_node_params(id, node["node_params"])
                            test_sql_id = id
                            map[node["node_id"]] = id
                        else:
                            preprocess.append(node["node_id"])
                            id = add_node(widget_name=node["widget_name"], node_name=node["node_name"])
                            update_node_params(id, node["node_params"])
                            map[node["node_id"]] = id
                    for edge in workflow["edges"]:
                        if edge["target_node_id"] == model_id:
                            train_final_node_id = edge["source_node_id"]
                            continue
                        add_edge(map[edge["source_node_id"]], map[edge["target_node_id"]])
                    visited_nodes = set()
                    final_node_ids = []

                    def get_final_node(edges, id):
                        visited_nodes.add(id)
                        flag = 1
                        for e in edges:
                            if e["source_node_id"] == id:
                                flag = 0
                        if flag == 1:
                            final_node_ids.append(id)
                            return 0
                        for e in edges:
                            if e["source_node_id"] == id and e["target_node_id"] not in visited_nodes:
                                get_final_node(edges, e["target_node_id"])

                    get_final_node(get_workflow()["edges"], test_sql_id)
                    if self.requires.ml_type == "timeseries":
                        e_id = add_node(widget_name="Model Evaluation", node_name="时序模型评估")
                        add_edge(final_node_ids[0], e_id)
                    else:
                        e_id = add_node(widget_name="Test & Score", node_name="模型评估")
                        add_edge(train_final_node_id, e_id, default_end_point=0, end_point=1)
                        add_edge(final_node_ids[0], e_id, default_end_point=0, end_point=0)
                    add_edge(model_id, e_id)
                else:
                    e_id = add_node(widget_name="Test & Score", node_name="模型评估")
                    add_edge(data_sample_id, e_id, default_end_point=0, end_point=0)
                    add_edge(data_sample_id, e_id, default_end_point=0, end_point=1)
                    add_edge(model_id, e_id)
                if self.requires.evaluate_result_save:
                    s_id = add_node(widget_name="Save Data", node_name="保存结果")
                    add_edge(e_id, s_id)

            if self.requires.predict and self.requires.ml_type!="timeseries":
                # 加载验证集和数据处理 增加预测组件
                if self.requires.evaluate:
                    workflow = get_workflow()
                    test_widget_id = -1
                    for node in workflow["nodes"]:
                        if node["widget_name"] == "Test & Score":
                            test_widget_id = node["node_id"]
                    if self.requires.predict_result_save and not self.requires.evaluate_result_save:
                        s_id = add_node(widget_name="Save Data", node_name="保存结果")
                        add_edge(test_widget_id, s_id)

                else:
                    if "Data Sampler" not in self.requires.preprocess:
                        workflow = get_workflow()
                        model_widget_names = ws.get_models_widget_names()
                        preprocess = []

                        map = {}
                        for node in workflow["nodes"]:
                            if node["widget_name"] in model_widget_names:
                                model_id = node["node_id"]
                                continue
                            if node["widget_name"] == "SQL Table":
                                preprocess.append(node["node_id"])
                                train_sql_id = node["node_id"]
                                id = add_node(widget_name=node["widget_name"], node_name="测试集加载")
                                test_sql_id = id
                                update_node_params(id, {"table_name": self.requires.data_source+"_test"})
                                map[node["node_id"]] = id
                            elif node["widget_name"] == "File":
                                preprocess.append(node["node_id"])

                                id = add_node(widget_name=node["widget_name"], node_name="上传测试集")
                                update_node_params(id, node["node_params"])
                                test_sql_id = id
                                map[node["node_id"]] = id
                            else:
                                preprocess.append(node["node_id"])
                                id = add_node(widget_name=node["widget_name"], node_name=node["node_name"])
                                update_node_params(id, node["node_params"])
                                map[node["node_id"]] = id
                        for edge in workflow["edges"]:
                            if edge["target_node_id"] == model_id:
                                continue
                            add_edge(map[edge["source_node_id"]], map[edge["target_node_id"]])
                        visited_nodes = set()
                        final_node_ids = []

                        def get_final_node(edges, id):
                            visited_nodes.add(id)
                            flag = 1
                            for e in edges:
                                if e["source_node_id"] == id:
                                    flag = 0
                            if flag == 1:
                                final_node_ids.append(id)
                                return 0
                            for e in edges:
                                if e["source_node_id"] == id and e["target_node_id"] not in visited_nodes:
                                    get_final_node(edges, e["target_node_id"])

                        get_final_node(get_workflow()["edges"], test_sql_id)
                        e_id = add_node(widget_name="Predictions", node_name="预测")
                        add_edge(final_node_ids[0], e_id)
                        add_edge(model_id, e_id)
                        if self.requires.predict_result_save:
                            # 保存预测结果
                            s_id = add_node(widget_name="Save Data", node_name="数据保存")
                            add_edge(e_id, s_id)
                    else:
                        e_id = add_node(widget_name="Predictions", node_name="预测")
                        add_edge(data_sample_id, e_id, default_end_point=0, end_point=0)
                        add_edge(model_id, e_id)
                        if self.requires.predict_result_save:
                            # 保存预测结果
                            s_id = add_node(widget_name="Save Data", node_name="数据保存")
                            add_edge(e_id, s_id)
            if self.requires.model_save and self.requires.ml_type!="timeseries":
                workflow = get_workflow()
                model_widget_id = -1
                model_widgets_names=ws.get_models_widget_names()
                for node in workflow["nodes"]:
                    if node["widget_name"] in model_widgets_names:
                        model_widget_id = node["node_id"]
                s_id = add_node(widget_name="Save Model", node_name="保存模型")
                add_edge(model_widget_id, s_id)

        if hasattr(self.requires, "task_type") and self.requires.task_type == "deep learning":
            last_widget_id = -1
            if self.requires.dl_type in ["audio","image","text","video"]:
                data_set_id=add_node(widget_name=self.requires.dl_type.capitalize(), node_name=self.requires.dl_type+"数据集上传")
                last_widget_id = data_set_id
            elif self.requires.dl_type == "graph":
                data_set_id=add_node(widget_name="Network File", node_name="Network数据集上传")
                last_widget_id = data_set_id
            model_id = add_node(widget_name=self.requires.model_widget_name, node_name=self.requires.model_widget_name)
            add_edge(last_widget_id, model_id)
            last_widget_id=model_id
            if self.requires.show_log:
                log_id=add_node(widget_name="Train Log", node_name="显示日志")
                add_edge(last_widget_id, log_id)
            if self.requires.predict:
                if self.requires.dl_type in ["audio", "image", "text", "video"]:
                    test_id = add_node(widget_name=self.requires.dl_type.capitalize(), node_name="测试数据集上传")
                elif self.requires.dl_type == "graph":
                    data_set_id = add_node(widget_name="Network File", node_name="测试Network数据集上传")
                    test_id = data_set_id
                infer_id=add_node(widget_name="Infer", node_name="训练")
                add_edge(last_widget_id, infer_id)
                add_edge(test_id, infer_id)
        if hasattr(self.requires, "task_type") and self.requires.task_type == "pretrained modeling application":
            last_widget_id = -1
            if self.requires.input_type in ["audio", "image", "text", "video"]:
                data_set_id = add_node(widget_name=self.requires.input_type.capitalize(),
                                       node_name=self.requires.input_type + "数据上传")
                last_widget_id = data_set_id
            elif self.requires.input_type == "graph":
                data_set_id = add_node(widget_name="Network File", node_name="Network数据上传")
                last_widget_id = data_set_id
            model_id = add_node(widget_name=self.requires.model_widget_name, node_name=self.requires.model_widget_name)
            add_edge(last_widget_id, model_id)
    def param_fixed(self):
        # 完善模型组件参数

        workflow = []
        if self.requires.task_type == "machine learning":
            workflow.extend(self.requires.preprocess)
            workflow.append(self.requires.model_widget_name)
        elif self.requires.task_type == "deep learning":
            workflow.append(self.requires.model_widget_name)
        elif self.requires.task_type == "pretrained modeling application":
            workflow.append(self.requires.model_widget_name)

        default_params=ws.get_default_params(workflow)
        if "One Hot Encoder" in workflow:
            workflow.remove("One Hot Encoder")
            default_params["One Hot Encoder"]={"encode_vars":[""]}


        sample_widget_params = ws.get_sample_params(workflow)

        messages = [{"role": "system", "content": """你是一个参数配置器，你需要做的是检查我的当前的参数配置是否满足要求，如果已经满足用户的特殊参数需求或者用户需求中没有对具体参数的要求，设置need_update为false,update_params为{},返回结果。如果不满足，你需要进行参数的更新。在update_params字段给出需要更新的组件名称和需要更新的参数，不需要更新的组件则不用管。
                组件参数配置参考手册：%s,回答严格按照以下json格式，不要回答无关内容：
                ```json
                {
                "need_update":true,
                "update_params":{'KNN': {'n_neighbors': 10, 'metric': 'euclidean'}}
                }```
                """ % str(sample_widget_params)}, {"role": "user", "content": "用户需求：" + str(
            self.requires.task) + "。当前组件和参数：" + str(default_params)}]
        res = LLM.common_chat(messages)
        ret = LLM.ExtractJson(res)
        if hasattr(self.requires,"one_hot_encode_vars") and len(self.requires.one_hot_encode_vars)!=0:
            ret["update_params"]["One Hot Encoder"] = {"encode_vars": self.requires.one_hot_encode_vars}
            ret["need_update"]=True

        if ret["need_update"]:
            self.need_update_params=ret["update_params"]

    def update_params(self):
        if len(self.need_update_params)!=0:
            for widget_name, params in self.need_update_params.items():
                workflow = get_workflow()
                for node in workflow["nodes"]:
                    if node["widget_name"] == widget_name:
                        node_id = node["node_id"]
                        res=update_node_params(node_id=node_id, node_params=params)




if __name__ == '__main__':
    pass