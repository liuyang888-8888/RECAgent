# coding=utf-8
# -----道阻且长 行则将至-------
# -----   liuyangyang   -----
# ---  691255995@qq.com  ----
# 日 期：2025/4/11 
# 时 间：23:47

import os.path


import pandas as pd
import json



import Agent
from lib.lib import find_project_root
from tools.actions import clear_workflow,get_workflow,action_agent







def evaluate_in_compare_dataset(exp_name):

    #读入数据
    # with open(os.path.join(find_project_root(), r"data/BenchMark/compare_data.json"), "r",encoding='utf-8') as f:
    #     data = json.load(f)


    #判断实验是否运行过
    if os.path.exists(os.path.join(r"/experiment\RECAgent", exp_name)):
        print(f"实验 {exp_name} 已经运行过，继续运行")
    else:
        os.makedirs(os.path.join(r"/experiment\RECAgent", exp_name))
        print(f"实验 {exp_name} 启动")




def evaluate_in_new_dataset(tasks,result_path,method="default"):


    #判断实验是否运行过
    if os.path.exists(result_path):
        print(f"实验 {result_path} 已经运行过，继续运行")

    else:
        os.makedirs(result_path)
        print(f"实验 {result_path} 启动")


    res = []
    res_path=os.path.join(result_path ,"result.json")

    if os.path.exists(res_path):
        with open(res_path, "r", encoding='utf-8') as f:
            res = json.load(f)

    executed_task_id=[]
    for r in res:
        executed_task_id.append(r["res"]["task"]["task_id"])

    for task in tasks:
        if task['id'] in executed_task_id:
            print(f"{task['id']}已执行过 跳过~")
            continue


        print(f"开始运行第 {task['id']} 个任务")
        clear_workflow()
        try:
            if method=="default":
                ev = Agent.ack_run_mul(task['task_description'],real_task_info=task,task_id=task['id'],run_workflow=False)
            elif method=="one_extract":
                ev = Agent.ack_run_type_infer_ablation(task['task_description'], real_task_info=task, task_id=task['id'],
                                       run_workflow=False)
            res.append({"index":task['id']-1,"res":ev})

            #保存结果
            res.sort(key=lambda x: x["index"])

            with open(res_path, 'w',
                      encoding='utf-8') as file:
                json.dump(res, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(e)

            res.append({"index":task['id']-1,"res":{"task": {"task_id":task['id'],"task_descript": task["task_description"],
                "task_type": task["task_type"],},"error": str(e)}})
            res.sort(key=lambda x:x["index"])
            # 保存结果
            with open(res_path, 'w',
                      encoding='utf-8') as file:
                json.dump(res, file, ensure_ascii=False, indent=4)

    print(f"数据已成功保存到 {res_path}")


def evaluate(data_path,res_dir,method="default"):
    # 每个RI CI BI 需要分别运行 这个是default：层级规划  one_extract： 层级的消融 单次提取需求
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)
    evaluate_in_new_dataset(data,res_dir,method=method)




if __name__ == '__main__':
    evaluate(method="default",data_path=r"E:\Postgraduate\Code\SunnylnAgent\data\BenchMark\regular.json"
             ,res_dir=os.path.join(r"E:\Postgraduate\Code\SunnylnAgent\experiment\RECAgent", "ablation_qwen2_5_14B", "regular"))

    

