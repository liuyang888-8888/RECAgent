# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  8/19/2024  4:05 PM
import os.path
import shutil

from .RCAgent import RCAgent
from .WBAgent import WBAgent
import concurrent.futures
from tools.actions import action_agent,save_data_to_loacl




import time
from llm.LLM import LLM
def ack_run(task,**kwargs):
    LLM.tokens=[]
    evaluate_res={}
    start_time=time.time()
    rc=RCAgent(task=task)
    rc.task_type_inference()
    infer_end_time=time.time()
    wb=WBAgent(requires=rc.requirement)
    wb.build_base_workflow()
    build_base_end_time=time.time()
    wb.param_fixed()
    wb.update_params()
    fixed_end_time=time.time()
    evaluate_res["time"]={}
    evaluate_res["time"]["infer_time"]=infer_end_time-start_time
    evaluate_res["time"]["build_base_workflow_time"]=build_base_end_time-infer_end_time
    evaluate_res["time"]["fixed_workflow_time"]=fixed_end_time-build_base_end_time
    evaluate_res["time"]["total_time"]=fixed_end_time-start_time
    prompt_tokens = 0
    completion_tokens = 0
    for t in LLM.tokens:
        prompt_tokens += (t["prompt_tokens"])
        completion_tokens += t["completion_tokens"]
    evaluate_res["tokens"] = {}
    evaluate_res["tokens"]["total"] = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,"total_tokens": prompt_tokens+completion_tokens}
    evaluate_res["tokens"]["detail"] = LLM.tokens
    return evaluate_res

# 自动构建工作流
def ack_run_mul(task,run_workflow=False,**kwargs):
    LLM.tokens = []
    evaluate_res = {}
    start_time = time.time()
    #此处传入任务类型使得check_valid方法可以返回正确的结果
    rc = RCAgent(task=task,real_task_info=kwargs.get("real_task_info"))
    rc.task_type_inference()
    infer_end_time = time.time()
    wb = WBAgent(requires=rc.requirement)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交 build_base_workflow 和 param_fixed 方法到线程池
        future_build = executor.submit(wb.build_base_workflow)
        future_fix = executor.submit(wb.param_fixed)

        # 等待两个任务都完成
        concurrent.futures.wait([future_build, future_fix])
    build_base_end_time = time.time()
    wb.update_params()
    update_end_time = time.time()
    if run_workflow:
        flag, message=action_agent.run_workflow()




    run_end_time = time.time()

    evaluate_res["time"] = {}
    evaluate_res["time"]["infer_time"] = infer_end_time - start_time
    evaluate_res["time"]["build_base_fixed_params_time"] = build_base_end_time - infer_end_time
    evaluate_res["time"]["update_params_time"] = update_end_time - build_base_end_time
    evaluate_res["time"]["run_workflow_time"] = run_end_time - update_end_time
    evaluate_res["time"]["total_time"] = run_end_time - start_time


    evaluate_res["task"] = {}
    evaluate_res["task"]["task_descript"]=task
    evaluate_res["task"]["task_type"]=kwargs.get("real_task_info")["task_type"]
    evaluate_res["task"]["task_id"]=kwargs.get("task_id")
    evaluate_res["task"]["workflow"]=action_agent.get_workflow()
    if len(evaluate_res["task"]["workflow"]["nodes"])>0:
        for node in evaluate_res["task"]["workflow"]["nodes"]:
            if node["widget_name"]=="Select Columns":
                for k,v in action_agent.attr_mapping.items():
                    if v['role']==0:
                        node["node_params"]["features"].append(k)
                    elif v['role']==2:
                        node["node_params"]["ignores"].append(k)
                    elif v['role']==1:
                        node["node_params"]["targets"]=k
    if run_workflow:
        evaluate_res["task"]["run_status"]=flag
        evaluate_res["task"]["run_message"]=message




    prompt_tokens = 0
    completion_tokens = 0
    for t in LLM.tokens:
        prompt_tokens += (t["prompt_tokens"])
        completion_tokens += t["completion_tokens"]
    evaluate_res["tokens"] = {}
    evaluate_res["tokens"]["total"] = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,"total_tokens": prompt_tokens+completion_tokens}
    evaluate_res["tokens"]["detail"] = LLM.tokens
    evaluate_res["interaction_number"]=len(LLM.tokens)

    return evaluate_res

# 层级任务识别模块消融
def ack_run_type_infer_ablation(task,run_workflow=False,**kwargs):
    LLM.tokens = []
    evaluate_res = {}
    start_time = time.time()
    #此处传入任务类型使得check_valid方法可以返回正确的结果
    rc = RCAgent(task=task,real_task_info=kwargs.get("real_task_info"))
    rc.task_type_inference_ablation()
    infer_end_time = time.time()
    wb = WBAgent(requires=rc.requirement)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交 build_base_workflow 和 param_fixed 方法到线程池
        future_build = executor.submit(wb.build_base_workflow)
        future_fix = executor.submit(wb.param_fixed)

        # 等待两个任务都完成
        concurrent.futures.wait([future_build, future_fix])
    build_base_end_time = time.time()
    wb.update_params()
    update_end_time = time.time()
    if run_workflow:
        flag, message=action_agent.run_workflow()




    run_end_time = time.time()

    evaluate_res["time"] = {}
    evaluate_res["time"]["infer_time"] = infer_end_time - start_time
    evaluate_res["time"]["build_base_fixed_params_time"] = build_base_end_time - infer_end_time
    evaluate_res["time"]["update_params_time"] = update_end_time - build_base_end_time
    evaluate_res["time"]["run_workflow_time"] = run_end_time - update_end_time
    evaluate_res["time"]["total_time"] = run_end_time - start_time


    evaluate_res["task"] = {}
    evaluate_res["task"]["task_descript"]=task
    evaluate_res["task"]["task_type"]=kwargs.get("real_task_info")["task_type"]
    evaluate_res["task"]["task_id"]=kwargs.get("task_id")
    evaluate_res["task"]["workflow"]=action_agent.get_workflow()
    if len(evaluate_res["task"]["workflow"]["nodes"])>0:
        for node in evaluate_res["task"]["workflow"]["nodes"]:
            if node["widget_name"]=="Select Columns":
                for k,v in action_agent.attr_mapping.items():
                    if v['role']==0:
                        node["node_params"]["features"].append(k)
                    elif v['role']==2:
                        node["node_params"]["ignores"].append(k)
                    elif v['role']==1:
                        node["node_params"]["targets"]=k
    if run_workflow:
        evaluate_res["task"]["run_status"]=flag
        evaluate_res["task"]["run_message"]=message




    prompt_tokens = 0
    completion_tokens = 0
    for t in LLM.tokens:
        prompt_tokens += (t["prompt_tokens"])
        completion_tokens += t["completion_tokens"]
    evaluate_res["tokens"] = {}
    evaluate_res["tokens"]["total"] = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,"total_tokens": prompt_tokens+completion_tokens}
    evaluate_res["tokens"]["detail"] = LLM.tokens
    evaluate_res["interaction_number"]=len(LLM.tokens)

    return evaluate_res


# 工作流优化
def wpo(task,run_workflow=True,**kwargs):
    # 基础工作流构建
    # rc = RCAgent(task=task,real_task_info=kwargs.get("real_task_info"))
    # rc.task_type_inference()
    # wb = WBAgent(requires=rc.requirement)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     # 提交 build_base_workflow 和 param_fixed 方法到线程池
    #     future_build = executor.submit(wb.build_base_workflow)
    #     future_fix = executor.submit(wb.param_fixed)
    #     # 等待两个任务都完成
    #     concurrent.futures.wait([future_build, future_fix])
    #
    # wb.update_params()
    #
    # flag,message=False,""
    # if run_workflow:
    #     flag, message=action_agent.run_workflow()

    # 1. 获取数据（包括特征和类型）
    # if not flag:
    #     return 0,message
    # 将工作流数据保存到本地
    # save_data_to_loacl()


    # 2. 分析数据信息
    from lib.lib import get_data_info
    data_description,data_vectors=get_data_info()


    # 3. 查找知识库，看是否有类似历史经验


    # 3.1 所有算法常用参数尝试 选取前三名的算法

    # 3.2 知识足够，直接使用知识库前三名算法

    # 4. 向量检索获取算法的相关信息

    # 5. 生成初始参数

    # 6. 运行初始参数获取结果

    # 7. 参数迭代（最大次数停止/已达最优）


    return None


