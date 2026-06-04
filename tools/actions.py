import json
import os
import shutil
import time

import Levenshtein
from anyio import sleep

from config.config import Workflow_id, Accesstoken,log,MySQL_Config
# from tools.ids_tools import AI_Studio
from tools.ids_tools_loacl import AI_Studio
from lib.lib import find_project_root, print_dic


class Actions():

    def __init__(self):
        self.ai_studio = AI_Studio(Workflow_id,Accesstoken)
        self.project_root = find_project_root()
        
        self.widgets_path = os.path.join(self.project_root, r"tools/workflow_widgets.json")
        with open(self.widgets_path, encoding='utf-8') as  f:
            self.widgets = json.load(f)

        self.widgets_name = [widget['widget_name'] for widget in self.widgets]
        self.hpo_widgets_names=["KNN","XGBoost","Tree","Gradient Boosting Decision Tree","Random Forest","SVM","Stochastic Gradient Descent","LightGBM","Neural Network","Logistic Regression","AdaBoost","Naive Bayes"]
        self.relevant_widgets_names = self.widgets_name

        self.x = 30
        self.y = 300
        self.data_info = None
        self.total_tokens = 0
        # self.clear_workflow()
        self.attr_mapping = {}


    def find_most_similar(self,target):
        if len(self.relevant_widgets_names)==0:
            return None

        most_similar_string = None
        highest_similarity = -1

        for string in self.relevant_widgets_names:
            # Compute the similarity ratio using Levenshtein
            similarity = Levenshtein.ratio(target, string)

            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_string = string

        return most_similar_string
    def reset_XY(self):
        self.x = 30
        self.y = 300

    def execute_command(self, command_name, args):
        try:
            # Check if the method exists in the Workflow class
            if hasattr(self, command_name):
                method = getattr(self, command_name)
                result = method(args)
                return result
            else:
                return f'名为"{command_name}"的Action不存在！'

        except Exception as e:
            return f"Error: {e}"

    def add_node(self, args):
        workflows_info=self.get_workflow()
        for node in workflows_info["nodes"]:
            if args["widget_name"] == node["widget_name"]:
                self.y-=140


        if args["widget_name"] in self.relevant_widgets_names:

            w = self.widgets[self.widgets_name.index(args["widget_name"])]

            try:
                widgetParam = json.dumps(args["widget_params"])
            except:
                widgetParam = None

            node = {
                "pos_x": self.x,
                "pos_y": self.y,
                "abstractWidgetId": w["widget_id"],
                "abstractName": w["widget_name"],
                "name": args["node_name"],
                "image": w["image"],
                "package": w["package"],
                "widgetParam": widgetParam,
                "workflow_id": self.ai_studio.workflow_id
            }

            node = json.dumps(node)

            r = self.ai_studio.add_node(node)
            node_id = r["data"]["id"]

            self.x += 140
            self.y=300

            return node_id

        else:
            return f"WIDGETS LIBRARY中不存在组件{args['widget_name']}，添加的组件应该是{self.relevant_widgets_names}中的一个"

    def delete_node(self, args):
        res = self.ai_studio.delete_node(args)
        if res["message"] == "请求成功":
            return f"节点{args['node_id']}删除成功"
        else:
            return f"节点{args['node_id']}删除失败，错误原因为：{res['message']}"

    def update_node_params(self, args):
        if type(args["node_params"]).__name__ == 'dict':
            node_params = args["node_params"]
        else:
            node_params = json.loads(args["node_params"])
        if args["widget_name"] == "SQL Table":
            widget_params = {
                "type": "2",
                "server": MySQL_Config["host"],
                "database": MySQL_Config["db"],
                "schema": "public",
                "port": MySQL_Config["port"],
                "username": MySQL_Config["user"],
                "password": MySQL_Config["passwd"],
                "dbType": None,
                "load_type": "table",
                "getDatabaseFlag": False,
                "selectedDatasource": None,
                "selectedDatasourceUserId": -1,
                "isNewIDIS": True,
                "table_name": node_params["table_name"],
                "save2db": False,
                "sql_code": "",
                "dump_table": "my_table",
                "selectedDataset": "",
                "dataset_name": None,
                "dataset_sql": None,
                "field": None,
                "interact_type": 2,
                "attr_mapping": self.attr_mapping
            }

            data = {
                "workflow_id": self.ai_studio.workflow_id,
                "param_info": {str(args["node_id"]): widget_params},
            }


            data = json.dumps(data, ensure_ascii=False)

            result = self.ai_studio.update_node_params(data)
            return result
        else:
            index = self.widgets_name.index(args["widget_name"])

            new_node_params = {}
            for p in self.widgets[index]["params"]:
                if p["name"] in node_params:
                    new_node_params[p["name"]] = node_params[p["name"]]
                else:
                    new_node_params[p["name"]] = p["default"]
            if new_node_params == {}:
                new_node_params = node_params

            data = {
                "workflow_id": self.ai_studio.workflow_id,
                "param_info": {str(args["node_id"]): new_node_params},
            }

            data = json.dumps(data, ensure_ascii=False)

            result = self.ai_studio.update_node_params(data)

            if result["message"] == '更新控件参数失败：list index out of range':
                return f"节点{args['node_id']}参数更新失败！因为该节点不存在，请查看工作流信息检查节点ID是否正确！"
            if result["message"] == '请求成功':
                return f"节点{args['node_id']}参数更新成功！"
            else:
                log.debug(f"节点{args['node_id']}参数更新失败，错误原因为：{result['message']}")
                return f"节点{args['node_id']}参数更新失败，错误原因为：{result['message']}"

    def add_edge(self, args):

        source_node_endpoints = []
        target_node_endpoints = []
        source_endpoint_id = 0
        target_endpoint_id = 0
        source_node = ""
        target_node = ""

        workflow_info = self.ai_studio.get_workflow()
        for n in workflow_info["nodes"]:
            if n["node_id"] == str(args["source_node_id"]):
                source_node = n["widget_name"]
                for e in n["endpoints"]:
                    if e["type"] == "source":
                        source_node_endpoints.append(e)

            elif n["node_id"] == str(args["target_node_id"]):
                target_node = n["widget_name"]
                for e in n["endpoints"]:
                    if e["type"] == "target":
                        target_node_endpoints.append(e)


        if source_node == "Test & Score" and target_node == "Save Data":
            data = {
                "source_node_id": args["source_node_id"],
                "source_endpoint_id": source_node_endpoints[2]["id"],
                "target_node_id": args["target_node_id"],
                "target_endpoint_id": target_node_endpoints[0]["id"]
            }
            res=self.ai_studio.add_edge(data)
            if res["message"] == "添加连接！":
                return f"添加连接成功！"
            elif res["message"] == "控件间无法添加连接！":
                return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
            return res["message"]
        elif source_node == "Predictions" and target_node == "Save Data":
            data = {
                "source_node_id": args["source_node_id"],
                "source_endpoint_id": source_node_endpoints[1]["id"],
                "target_node_id": args["target_node_id"],
                "target_endpoint_id": target_node_endpoints[0]["id"]
            }
            res=self.ai_studio.add_edge(data)
            if res["message"] == "添加连接！":
                return f"添加连接成功！"
            elif res["message"] == "控件间无法添加连接！":
                return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
            return res["message"]
        elif source_node == "Select Columns" and  target_node == "Test & Score":

            if not args["default_end_point"]:
                if args["end_point"] == 0:
                    for tar in target_node_endpoints:
                        if tar["short_name"] == "tstdt":
                            target_endpoint_id = tar["id"]
                            break
                    data = {
                        "source_node_id": args["source_node_id"],
                        "source_endpoint_id": source_node_endpoints[0]["id"],
                        "target_node_id": args["target_node_id"],
                        "target_endpoint_id": target_endpoint_id
                    }
                    res = self.ai_studio.add_edge(data)
                    if res["message"] == "添加连接！":
                        return f"添加连接成功！"
                    elif res["message"] == "控件间无法添加连接！":
                        return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
                    return res["message"]
                elif args["end_point"] == 1:
                    for tar in target_node_endpoints:
                        if tar["short_name"] == "trndt":
                            target_endpoint_id = tar["id"]
                            break
                    data = {
                        "source_node_id": args["source_node_id"],
                        "source_endpoint_id": source_node_endpoints[0]["id"],
                        "target_node_id": args["target_node_id"],
                        "target_endpoint_id": target_endpoint_id
                    }
                    res = self.ai_studio.add_edge(data)
                    if res["message"] == "添加连接！":
                        return f"添加连接成功！"
                    elif res["message"] == "控件间无法添加连接！":
                        return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
                    return res["message"]


        elif source_node == "Interpolate" and  target_node == "Select Columns":
            data = {
                "source_node_id": args["source_node_id"],
                "source_endpoint_id": source_node_endpoints[0]["id"],
                "target_node_id": args["target_node_id"],
                "target_endpoint_id": target_node_endpoints[0]["id"]
            }
            res = self.ai_studio.add_edge(data)
            if res["message"] == "添加连接！":
                return f"添加连接成功！"
            elif res["message"] == "控件间无法添加连接！":
                return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
            return res["message"]

        elif source_node == "Data Sampler":
            if target_node == "Predictions":
                source_endpoint_id = source_node_endpoints[0]["id"]


            elif target_node == "Test & Score" and args["default_end_point"] == 0:
                if args["end_point"] == 0:
                    for tar in target_node_endpoints:
                        if tar["short_name"] == "tstdt":
                            target_endpoint_id = tar["id"]
                            break
                    data = {
                        "source_node_id": args["source_node_id"],
                        "source_endpoint_id": source_node_endpoints[0]["id"],
                        "target_node_id": args["target_node_id"],
                        "target_endpoint_id": target_endpoint_id
                    }
                    res = self.ai_studio.add_edge(data)
                    if res["message"] == "添加连接！":
                        return f"添加连接成功！"
                    elif res["message"] == "控件间无法添加连接！":
                        return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
                    return res["message"]

                elif args["end_point"] == 1:
                    for tar in target_node_endpoints:
                        if tar["short_name"] == "trndt":
                            target_endpoint_id = tar["id"]
                            break
                    data = {
                        "source_node_id": args["source_node_id"],
                        "source_endpoint_id": source_node_endpoints[1]["id"],
                        "target_node_id": args["target_node_id"],
                        "target_endpoint_id": target_endpoint_id
                    }
                    res = self.ai_studio.add_edge(data)
                    if res["message"] == "添加连接！":
                        return f"添加连接成功！"
                    elif res["message"] == "控件间无法添加连接！":
                        return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
                    return res["message"]

            else:
                for se in source_node_endpoints:
                    if se["short_name"] == "rmn":
                        source_endpoint_id = se["id"]
                        break
                source_endpoint_id = source_endpoint_id

            for te in target_node_endpoints:
                if te["short_name"] == "data":
                    target_endpoint_id = te["id"]
                    break
        elif source_node == "Predictions":
            if target_node_endpoints[0]["short_name"]== "evr":
                source_endpoint_id = source_node_endpoints[0]["id"]
            else:
                source_endpoint_id = source_node_endpoints[1]["id"]
            target_endpoint_id = target_node_endpoints[0]["id"]

        else:
            for se in source_node_endpoints:
                for te in target_node_endpoints:
                    if se["short_name"] == te["short_name"]:
                        source_endpoint_id = se["id"]
                        target_endpoint_id = te["id"]
                        # 不要break
                    elif  se["short_name"] == "data" and te["short_name"] == "tsd":
                        source_endpoint_id = se["id"]
                        target_endpoint_id = te["id"]
                    elif se["short_name"] == "tsd" and te["short_name"] == "data":
                        source_endpoint_id = se["id"]
                        target_endpoint_id = te["id"]
                    elif se["short_name"] in ["img","text","video","audio"] and te["short_name"] == "dpdata":
                        source_endpoint_id = se["id"]
                        target_endpoint_id = te["id"]
        data = {
            "source_node_id": args["source_node_id"],
            "source_endpoint_id": source_endpoint_id,
            "target_node_id": args["target_node_id"],
            "target_endpoint_id": target_endpoint_id
        }
        res = self.ai_studio.add_edge(data)

        if res["message"] == "添加连接！":
            return f"添加连接成功！"
        elif res["message"] == "控件间无法添加连接！":
            return f"无法添加从{data['begin_node_id']}到{data['end_node_id']}的边。"
        return  res["message"]

    def delete_edge(self, args):
        res = self.ai_studio.delete_edge(args)
        if res["message"]== "请求成功":
            return f"边{args['edge_id']}删除成功"
        return f"边{args['edge_id']}删除失败"

    def task_finish(self, args):

        return args["final_response"]

    def get_workflow(self):
        workflow_info = self.ai_studio.get_workflow()

        edges = []
        nodes = []
        for e in workflow_info["edges"]:
            is_exist = False
            for edge in edges:
                if edge["source_node_id"] == e["source_node_id"] and edge["target_node_id"] == e["target_node_id"]:
                    is_exist = True
                    break
            if not is_exist:
                edges.append({
                    "edge_id": e["edge_id"],
                    "source_node_id": e["source_node_id"],
                    "target_node_id": e["target_node_id"]
                })

        for n in  workflow_info["nodes"]:
            nodes.append({
                "node_id": n["node_id"],
                "widget_name": n["widget_name"],
                "node_name": n["node_name"],
                "node_params": n["node_params"]
            })
        return {"edges": edges, "nodes": nodes}

    def get_node_results(self, args):
        """
    运行状态说明
    FAILED = -1 运行出错
    NOSTATE = 0 无状态
    PENDING = 1 等待运行
    RUNNING = 2 运行中
    SUCCEED = 3 运行成功
        """
        import pandas as pd
        workflow_info = self.ai_studio.get_workflow()
        for node in workflow_info["nodes"]:
            if node["node_id"] == str(args["node_id"]):
                if node["widget_name"] == "Test & Score":
                    # 使用10折交叉验证
                    # data = {
                    #     "widget_id": str(args["node_id"]),
                    #     "interact_type": 1,
                    #     "resampling_type": 0,
                    #     "n_folds": 10,
                    #     "cv_stratified": True,
                    #     "fold_feature": None,
                    #     "n_repeats": 3,
                    #     "sample_size": 5,
                    #     "shuffle_stratified": True,
                    #     "target_idx": 0,
                    #     "workflow_id": Workflow_id
                    # }

                    #测试集中测试
                    data = {
                        "widget_id": str(args["node_id"]),
                        "interact_type": 1,
                        "resampling_type": 5,
                        "n_folds": 10,
                        "cv_stratified": True,
                        "fold_feature": None,
                        "n_repeats": 3,
                        "sample_size": 5,
                        "shuffle_stratified": True,
                        "target_idx": 0,
                        "workflow_id": Workflow_id
                    }
                    self.ai_studio.run_widget(json.dumps(data, ensure_ascii=False))
                    data = {
                        "widget_id": str(args["node_id"]),
                        "workflow_id": Workflow_id
                    }

                    while True:
                        run_info = self.ai_studio.get_run_widget_status(json.dumps(data, ensure_ascii=False))
                        if run_info["status"] == 3:
                            log.info(f"节点{args['node_id']}运行成功")

                            if "confusion_matrixes" in run_info["data"]:
                                d = {
                                    "confusion_matrixes": run_info["data"]["confusion_matrixes"],
                                    "colssum": run_info["data"]["colssum"],
                                    "rowssum": run_info["data"]["rowssum"],
                                    "headers": run_info["data"]["headers"],
                                    "total": run_info["data"]["total"],
                                    "model_params": run_info["data"]["model_params"],
                                }
                                return d
                            elif "score_table" in run_info["data"]:
                                return run_info["data"]["score_table"]
                            else:
                                return run_info["data"]
                        elif run_info["status"] == -1:
                            log.info(f"节点{args['node_id']}运行失败")
                            return {}
                        else:
                            log.info(f"节点{args['node_id']}运行中...")
                            log.info(json.dumps(run_info, ensure_ascii=False, indent=4))
                            time.sleep(3)
                if node["widget_name"] == "Data Table":
                    page = 1
                    page_size = 100
                    result = []
                    while True:
                        data = {
                            "widget_id": str(args["node_id"]),
                            "page": page,
                            "page_size": page_size,
                            "workflow_id": Workflow_id
                        }
                        page += 1
                        log.info(page)
                        self.ai_studio.run_widget(json.dumps(data, ensure_ascii=False))

                        data = {
                            "widget_id": str(args["node_id"]),
                            "workflow_id": Workflow_id
                        }

                        while True:
                            run_info = self.ai_studio.get_run_widget_status(json.dumps(data, ensure_ascii=False))
                            if run_info["status"] == 3:
                                result.extend(run_info["data"]["table_data"])
                                log.info(f"成功获取{len(result)}条数据")
                                if len(result) >= run_info["data"]["metadata"]["n_sample"]:
                                    return pd.DataFrame(result)
                                else:
                                    break
                            elif run_info["status"] == -1:
                                log.info(f"节点{args['node_id']}运行失败")
                                return {}
                            else:
                                log.info(f"节点{args['node_id']}运行中...")
                                log.info(json.dumps(run_info, ensure_ascii=False, indent=4))
                                time.sleep(3)
                if node["widget_name"] == "Save Data":
                    data = {
                      "filename": "mydata",
                      "ext": ".csv",
                      "widget_id": str(args["node_id"]),
                      "workflow_id": Workflow_id
                    }
                    self.ai_studio.run_widget(json.dumps(data, ensure_ascii=False))
                    data = {
                        "widget_id": str(args["node_id"]),
                        "workflow_id": Workflow_id
                    }

                    while True:
                        run_info = self.ai_studio.get_run_widget_status(json.dumps(data, ensure_ascii=False))
                        if run_info["status"] == 3:
                            log.info(f"节点{args['node_id']}运行成功")
                            return run_info["data"]["url"]

                        elif run_info["status"] == -1:
                            log.info(f"节点{args['node_id']}运行失败")
                            return {}
                        else:
                            log.info(f"节点{args['node_id']}运行中...")
                            log.info(json.dumps(run_info, ensure_ascii=False, indent=4))
                            time.sleep(3)
        return f"工作流中不存在节点{args['node_id']}"

    def get_preprocess_results(self, args):
        # self.run_workflow()
        datas=[]

        data=self.ai_studio.get_preprocess_data(args["final_node_ids"][0])
        print(data)


        max_try=0
        while len(data)==0 and max_try<15:
            time.sleep(3)
            max_try+=1
            data = self.ai_studio.get_preprocess_data(args["final_node_ids"][0])

        for i in args["final_node_ids"]:
            data=self.ai_studio.get_preprocess_data(i)

            datas.append(data)
        data_info=None
        workflow=get_workflow()
        for i in workflow["nodes"]:
            if i['widget_name'] in self.hpo_widgets_names:
                data_info = self.get_dataset_info({"node_id": i['node_id']})



        return datas,data_info
    def get_dataset_info(self, args):
        return self.ai_studio.get_data_info(args["node_id"])


    def clear_workflow(self):
        workflow_info = self.get_workflow()
        for n in workflow_info["nodes"]:
            self.delete_node({"node_id": n["node_id"]})



    def run_workflow(self):
        self.ai_studio.run_workflow()
        unstatus=0
        while True:
            time.sleep(1)
            unstatus += 1
            res = self.ai_studio.get_run_workflow_info()
            data = res["data"]
            flags=[]
            for d in data:
                flags.append(d["status"])



            if flags.count(3)==len(flags):
                log.info("工作流运行成功！")
                return True,""
            if -1 in flags:
                log.info(f"工作流运行失败！{flags}")

                return False,flags
            if unstatus > 100:
                self.ai_studio.stop_workflow()
                log.info("工作流运行失败！")
                return False,flags




action_agent = Actions()
"""
你是一名有用的python程序开发人员，你需要使用我给你的组件和可以调用的函数名称来编写代码构建工作流，代码中不可以使用我未提供函数，
可以使用的函数如下：{
 add_node(args):这个函数用来添加一个节点到工作流中，参数args是一个字典，包含了widget_name和node_name，widget_name必须与我给出的组件信息一致，node_name可以自定义取名字，添加成功之后该函数会返回一个整数，是新添加的节点id。参数示例：{"widget_name": "File","node_name": "加载文件"}，返回值示例：24556
 delete_node(args):这个函数用来删除一个节点，参数args是一个字典，包含了node_id，参数示例：{"node_id":24556}。
 add_edge(args):这个函数用来添加一个边到工作流中，参数args是一个字典，包含了source_node_id和target_node_id，添加成功后会返回新添加的边的id，参数示例：{"source_node_id": file_id, "target_node_id": data_sample_id},返回值示例：1566。
 delete_edge(args):这个函数用来删除一个边，参数args是一个字典，包含edge_id,参数示例：{"edge_id":1566}。
 update_node_params(args)：这个函数用来更新工作流当中的一个节点的参数，参数args是一个字典，其中的需要更新的某节点的参数node_params,widget_name,node_id，必须要与组件列表中的参数一致，参数示例：{{"node_params":{
                    "replicable": True
            },"widget_name":"Data Sampler","node_id":data_sample_id
        }}。
 get_workflow():这个函数用来获取当前工作流的信息。
 run_workflow():这个函数用来运行当前的工作流。}
 组件: %s"""

def add_node(widget_name,node_name):
    return action_agent.add_node({"widget_name":widget_name,"node_name":node_name})

def delete_node(node_id):
    return action_agent.delete_node({"node_id":node_id})

def add_edge(source_node_id,target_node_id,default_end_point=1,end_point=0):
    return action_agent.add_edge({"source_node_id": source_node_id, "target_node_id": target_node_id,"default_end_point":default_end_point,"end_point":end_point})

def delete_edge(edge_id):
    return action_agent.delete_edge({"edge_id":edge_id})

def update_node_params(node_id,node_params):
    widget_name =""
    workflow=action_agent.get_workflow()
    for node in workflow["nodes"]:
        if node["node_id"] == str(node_id):
            widget_name = node["widget_name"]
    if widget_name == "":
        raise Exception("error: can not find widget_name by node_id, please check node_id.")
    return action_agent.update_node_params({"node_id":node_id,"widget_name":widget_name,"node_params":node_params})









def get_workflow():
    return action_agent.get_workflow()

def clear_workflow():
    return action_agent.clear_workflow()

def save_data_to_loacl(datas=None,data_info=None,path=os.path.join(find_project_root(), r"data/current")):
    import pandas as pd
    TYPE_map = {
        "numeric": 'C',
        "categorical": 'D',
        "text": 'S',
        "date": 'T'
    }
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)
    if datas is None and data_info is None:
        SF_id = []
        workflow = action_agent.get_workflow()
        for node in workflow["nodes"]:
            if node["widget_name"] == "Select Columns":
                SF_id.append(node["node_id"])
        datas, data_info = action_agent.get_preprocess_results({"final_node_ids":SF_id})

    # 判断数据集个数
    if len(datas) == 2:
        train, test = datas[0], datas[1]
        if len(train['data']) <= len(test['data']):
            train, test = datas[1]["data"], datas[0]["data"]

    elif len(datas) == 1:
        from sklearn.model_selection import train_test_split

        # 可复现的8:2划分
        train_data, test_data = train_test_split(
            datas[0]["data"],
            test_size=0.2,
            random_state=42  # 固定随机种子以确保可复现性
        )

        train = {
            "data": train_data,
            "columns": datas[0]["columns"]
        }

        test = {
            "data": test_data,
            "columns": datas[0]["columns"]
        }

    df_train = pd.DataFrame(data=train['data'], columns=train['columns'])
    df_test = pd.DataFrame(data=test['data'], columns=test['columns'])
    # 提取类型和角色信息 实现属性列对齐
    cols = {col['name']: {"type": TYPE_map[col["data_type"]], "role": col['role'] if col['role'] !="target" else "class"} for col in
            data_info['columns_info']}
    types, roles = [], []

    for col_info in train['columns']:
        types.append(cols[col_info]["type"])
        roles.append(cols[col_info]["role"])

    # 将类型和角色信息添加到DataFrame的前两行
    df_train.loc[-2] = types  # 添加类型行
    df_test.loc[-2] = types  # 添加类型行
    df_train.loc[-1] = roles  # 添加角色行
    df_test.loc[-1] = roles  # 添加角色行
    df_train.index = df_train.index + 2  # 将索引后移
    df_test.index = df_test.index + 2  # 将索引后移
    df_train = df_train.sort_index()  # 重新排序索引
    df_test = df_test.sort_index()  # 重新排序索引

    # 保存到本地
    df_train.to_csv(os.path.join(path, r"train.csv"), index=False)
    df_test.to_csv(os.path.join(path, r"test.csv"), index=False)



if __name__=="__main__":
    dir_num=len(os.listdir(r"E:\Postgraduate\Code\SunnylnAgent\data\experiment_2"))
    save_data_to_loacl(path=os.path.join(r"E:\Postgraduate\Code\SunnylnAgent\data\experiment_2",str(dir_num)))

    # print_dic(action_agent.ai_studio.get_run_widget_status({"node_id": 826}))









