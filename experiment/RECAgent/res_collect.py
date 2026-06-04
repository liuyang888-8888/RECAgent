# coding=utf-8
# -----道阻且长 行则将至-------
# -----   liuyangyang   -----
# ---  691255995@qq.com  ----
# 2025/5/25 15:29
import os
import json
from lib.lib import find_project_root


def default():
    # 收集RECAgent 的实验结果
    result_dir = os.path.join(find_project_root(),"experiment\RECAgent\diff+_second_all")
    print(result_dir)
    groups = {
        "base": os.path.join(result_dir, "base"),
        "regular": os.path.join(result_dir, "regular"),
        "clear": os.path.join(result_dir, "clear")
    }

    # 定义价格常量（元/千token）
    PRICE_INPUT = 0.004
    PRICE_OUTPUT = 0.012

    # 用于存储所有组的汇总数据
    all_results = {}
    metrics = []
    # 统计每个组的数据
    for group_name, group_dir in groups.items():
        total_time = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_success_count = 0
        total_interact_count = 0
        RCR = 0

        total_tasks = 0

        # 检查目录是否存在
        if not os.path.exists(group_dir):
            print(f"警告: 目录 {group_dir} 不存在")
            continue

        # 遍历目录中的所有任务+
        try:
            with open(os.path.join(group_dir, "result.json"), "r", encoding="utf-8") as f:
                rs = json.load(f)


        except Exception as e:
            print(f"错误: 读取文件 {group_dir + '/result.json'} 失败: {e}")
            continue
        for r in rs[:30]:
            total_tasks += 1

            # 处理成功和失败的任务
            if r.get("res", {}).get("task").get("run_status"):
                total_time += r["res"]["time"]["total_time"]
                total_prompt_tokens += r["res"]["tokens"]["total"]["prompt_tokens"]
                total_completion_tokens += r["res"]["tokens"]["total"]["completion_tokens"]
                total_interact_count += r["res"]["interaction_number"]

                total_success_count += 1
                if group_name == "base":
                    RCR += 5
                    metrics.append(r["res"]["task"]["metrics"])
                else:
                    RCR += r["res"]["task"]["RCR"]
            else:
                if group_name == "base":
                    metrics.append(-1)
                print(
                    f"失败任务id:{r['res']['task']['task_id']}, 组:{group_name}, 任务描述：{r['res'].get('task', '未知')}")

        # 计算各项指标
        if total_success_count > 0:
            avg_time = total_time / total_success_count
            avg_input_tokens = total_prompt_tokens / total_success_count
            avg_output_tokens = total_completion_tokens / total_success_count
            avg_cost = (avg_input_tokens * PRICE_INPUT + avg_output_tokens * PRICE_OUTPUT) / 1000
            avg_interact = total_interact_count / total_success_count
            RCR = RCR / total_success_count / 5.0
            success_rate = total_success_count / total_tasks if total_tasks > 0 else 0
        else:
            avg_time = 0
            avg_input_tokens = 0
            avg_output_tokens = 0
            avg_cost = 0
            avg_interact = 0
            success_rate = 0

        # 存储结果
        all_results[group_name] = {
            "success_rate": success_rate,
            "avg_time": avg_time,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_cost": avg_cost,
            "avg_interact": avg_interact,
            "ave_scaled_RCR": RCR,
            "total_success": total_success_count,
            "total_tasks": total_tasks
        }

        # 打印结果
        print(f"{group_name} :")
        print(f"  成功率: {success_rate:.3f} ({total_success_count}/{total_tasks})")
        print(f"  平均时间: {avg_time:.2f} s")
        print(f"  平均输入token: {avg_input_tokens:.2f}")
        print(f"  平均输出token: {avg_output_tokens:.2f}")
        print(f"  平均花费cost：{avg_cost:.6f} 元")
        print(f"  平均交互次数: {avg_interact:.3f}")
        print(f"  平均需求覆盖率: {RCR:.4f}")
        print("++" * 30)

    # 计算总体统计数据
    total_success_all = sum(data["total_success"] for data in all_results.values())
    total_tasks_all = sum(data["total_tasks"] for data in all_results.values())

    # 加权平均计算
    total_avg_time = sum(data["avg_time"] * data["total_success"] for data in
                         all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_input = sum(data["avg_input_tokens"] * data["total_success"] for data in
                          all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_output = sum(data["avg_output_tokens"] * data["total_success"] for data in
                           all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_scaled_RCR = sum(data["ave_scaled_RCR"] * data["total_success"] for data in
                               all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_interact = sum(data["avg_interact"] * data["total_success"] for data in
                             all_results.values()) / total_success_all if total_success_all > 0 else 0

    # 总成本计算
    total_avg_cost = (total_avg_input * PRICE_INPUT + total_avg_output * PRICE_OUTPUT) / 1000

    # 打印总体结果
    print(f"总体统计:")
    print(f"  成功率: {total_success_all / total_tasks_all:.3f} ({total_success_all}/{total_tasks_all})")
    print(f"  平均时间: {total_avg_time:.2f} s")
    print(f"  平均输入token: {total_avg_input:.2f}")
    print(f"  平均输出token: {total_avg_output:.2f}")
    print(f"  平均花费cost：{total_avg_cost:.6f} 元")
    print(f"  平均需求覆盖率: {total_avg_scaled_RCR:.4f}")
    print(f"  平均交互次数: {total_avg_interact:.3f}")

    print(metrics)
    print(len(metrics))

    print(
        "=================================================方法对比实验结果 131任务==============================================================")
    # 用于存储所有组的汇总数据
    all_results = {}
    # 统计每个组的数据
    for group_name, group_dir in groups.items():
        total_time = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_success_count = 0
        total_interact_count = 0
        RCR = 0

        total_tasks = 0

        # 检查目录是否存在
        if not os.path.exists(group_dir):
            print(f"警告: 目录 {group_dir} 不存在")
            continue

        # 遍历目录中的所有任务+
        try:
            with open(os.path.join(group_dir, "result.json"), "r", encoding="utf-8") as f:
                rs = json.load(f)


        except Exception as e:
            print(f"错误: 读取文件 {group_dir + '/result.json'} 失败: {e}")
            continue
        for r in rs:
            total_tasks += 1

            # 处理成功和失败的任务
            if r.get("res", {}).get("task").get("run_status"):
                total_time += r["res"]["time"]["total_time"]
                total_prompt_tokens += r["res"]["tokens"]["total"]["prompt_tokens"]
                total_completion_tokens += r["res"]["tokens"]["total"]["completion_tokens"]
                total_interact_count += r["res"]["interaction_number"]

                total_success_count += 1
                if group_name == "base":
                    RCR += 5

                else:
                    RCR += r["res"]["task"]["RCR"]
            else:
                print(
                    f"失败任务id:{r['res']['task']['task_id']}, 组:{group_name}, 任务描述：{r['res'].get('task', '未知')}")

        # 计算各项指标
        if total_success_count > 0:
            avg_time = total_time / total_success_count
            avg_input_tokens = total_prompt_tokens / total_success_count
            avg_output_tokens = total_completion_tokens / total_success_count
            avg_cost = (avg_input_tokens * PRICE_INPUT + avg_output_tokens * PRICE_OUTPUT) / 1000
            avg_interact = total_interact_count / total_success_count
            RCR = RCR / total_success_count / 5.0
            success_rate = total_success_count / total_tasks if total_tasks > 0 else 0
        else:
            avg_time = 0
            avg_input_tokens = 0
            avg_output_tokens = 0
            avg_cost = 0
            avg_interact = 0
            success_rate = 0

        # 存储结果
        all_results[group_name] = {
            "success_rate": success_rate,
            "avg_time": avg_time,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_cost": avg_cost,
            "avg_interact": avg_interact,
            "ave_scaled_RCR": RCR,
            "total_success": total_success_count,
            "total_tasks": total_tasks
        }

        # 打印结果
        print(f"{group_name} :")
        print(f"  成功率: {success_rate:.3f} ({total_success_count}/{total_tasks})")
        print(f"  平均时间: {avg_time:.2f} s")
        print(f"  平均输入token: {avg_input_tokens:.2f}")
        print(f"  平均输出token: {avg_output_tokens:.2f}")
        print(f"  平均花费cost：{avg_cost:.6f} 元")
        print(f"  平均交互次数: {avg_interact:.3f}")
        print(f"  平均需求覆盖率: {RCR:.4f}")
        print("++" * 30)

    # 计算总体统计数据
    total_success_all = sum(data["total_success"] for data in all_results.values())
    total_tasks_all = sum(data["total_tasks"] for data in all_results.values())

    # 加权平均计算
    total_avg_time = sum(data["avg_time"] * data["total_success"] for data in
                         all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_input = sum(data["avg_input_tokens"] * data["total_success"] for data in
                          all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_output = sum(data["avg_output_tokens"] * data["total_success"] for data in
                           all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_scaled_RCR = sum(data["ave_scaled_RCR"] * data["total_success"] for data in
                               all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_interact = sum(data["avg_interact"] * data["total_success"] for data in
                             all_results.values()) / total_success_all if total_success_all > 0 else 0

    # 总成本计算
    total_avg_cost = (total_avg_input * PRICE_INPUT + total_avg_output * PRICE_OUTPUT) / 1000

    # 打印总体结果
    print(f"总体统计:")
    print(f"  成功率: {total_success_all / total_tasks_all:.3f} ({total_success_all}/{total_tasks_all})")
    print(f"  平均时间: {total_avg_time:.2f} s")
    print(f"  平均输入token: {total_avg_input:.2f}")
    print(f"  平均输出token: {total_avg_output:.2f}")
    print(f"  平均花费cost：{total_avg_cost:.6f} 元")
    print(f"  平均需求覆盖率: {total_avg_scaled_RCR:.4f}")
    print(f"  平均交互次数: {total_avg_interact:.3f}")

def ablation_QWEN_14B():
    # 该函数用于模型参数消融实验的结果收集 使用的qwen2.5 14B
    result_dir = r"E:\Postgraduate\Code\SunnylnAgent\experiment\RECAgent\ablation_qwen2_5_14B"
    print(result_dir)
    groups = {
        "base": os.path.join(result_dir, "base"),
        "regular": os.path.join(result_dir, "regular"),
        "clear": os.path.join(result_dir, "clear")
    }

    # Qwen2.5 14B 定义价格常量（元/千token）
    PRICE_INPUT = 0.001
    PRICE_OUTPUT = 0.003


    print("=================================================ablation_qwen2_5_14B实验结果 131任务==============================================================")
    # 用于存储所有组的汇总数据
    all_results = {}
    # 统计每个组的数据
    for group_name, group_dir in groups.items():
        total_time = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_success_count = 0
        total_interact_count = 0
        RCR = 0

        total_tasks = 0

        # 检查目录是否存在
        if not os.path.exists(group_dir):
            print(f"警告: 目录 {group_dir} 不存在")
            continue

        # 遍历目录中的所有任务+
        try:
            with open(os.path.join(group_dir, "result.json"), "r", encoding="utf-8") as f:
                rs = json.load(f)


        except Exception as e:
            print(f"错误: 读取文件 {group_dir + '/result.json'} 失败: {e}")
            continue
        for r in rs:
            total_tasks += 1

            # 处理成功和失败的任务
            if r.get("res", {}).get("task").get("run_status"):
                total_time += r["res"]["time"]["total_time"]
                total_prompt_tokens += r["res"]["tokens"]["total"]["prompt_tokens"]
                total_completion_tokens += r["res"]["tokens"]["total"]["completion_tokens"]
                total_interact_count += r["res"]["interaction_number"]
                total_success_count += 1
                RCR += r["res"]["task"]["RCR"]
            else:
                print(
                    f"失败任务id:{r['res']['task']['task_id']}, 组:{group_name}, 任务描述：{r['res'].get('task', '未知')}")

        # 计算各项指标
        if total_success_count > 0:
            avg_time = total_time / total_success_count
            avg_input_tokens = total_prompt_tokens / total_success_count
            avg_output_tokens = total_completion_tokens / total_success_count
            avg_cost = (avg_input_tokens * PRICE_INPUT + avg_output_tokens * PRICE_OUTPUT) / 1000
            avg_interact = total_interact_count / total_success_count
            RCR = RCR / total_success_count / 5.0
            success_rate = total_success_count / total_tasks if total_tasks > 0 else 0
        else:
            avg_time = 0
            avg_input_tokens = 0
            avg_output_tokens = 0
            avg_cost = 0
            avg_interact = 0
            success_rate = 0

        # 存储结果
        all_results[group_name] = {
            "success_rate": success_rate,
            "avg_time": avg_time,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_cost": avg_cost,
            "avg_interact": avg_interact,
            "ave_scaled_RCR": RCR,
            "total_success": total_success_count,
            "total_tasks": total_tasks
        }

        # 打印结果
        print(f"{group_name} :")
        print(f"  成功率: {success_rate:.3f} ({total_success_count}/{total_tasks})")
        print(f"  平均时间: {avg_time:.2f} s")
        print(f"  平均输入token: {avg_input_tokens:.2f}")
        print(f"  平均输出token: {avg_output_tokens:.2f}")
        print(f"  平均花费cost：{avg_cost:.6f} 元")
        print(f"  平均交互次数: {avg_interact:.3f}")
        print(f"  平均需求覆盖率: {RCR:.4f}")
        print("++" * 30)

    # 计算总体统计数据
    total_success_all = sum(data["total_success"] for data in all_results.values())
    total_tasks_all = sum(data["total_tasks"] for data in all_results.values())

    # 加权平均计算
    total_avg_time = sum(data["avg_time"] * data["total_success"] for data in
                         all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_input = sum(data["avg_input_tokens"] * data["total_success"] for data in
                          all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_output = sum(data["avg_output_tokens"] * data["total_success"] for data in
                           all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_scaled_RCR = sum(data["ave_scaled_RCR"] * data["total_success"] for data in
                               all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_interact = sum(data["avg_interact"] * data["total_success"] for data in
                             all_results.values()) / total_success_all if total_success_all > 0 else 0

    # 总成本计算
    total_avg_cost = (total_avg_input * PRICE_INPUT + total_avg_output * PRICE_OUTPUT) / 1000

    # 打印总体结果
    print(f"总体统计:")
    print(f"  成功率: {total_success_all / total_tasks_all:.3f} ({total_success_all}/{total_tasks_all})")
    print(f"  平均时间: {total_avg_time:.2f} s")
    print(f"  平均输入token: {total_avg_input:.2f}")
    print(f"  平均输出token: {total_avg_output:.2f}")
    print(f"  平均花费cost：{total_avg_cost:.6f} 元")
    print(f"  平均需求覆盖率: {total_avg_scaled_RCR:.4f}")
    print(f"  平均交互次数: {total_avg_interact:.3f}")

def ablation_QWEN_32B():
    # 该函数用于模型参数消融实验的结果收集 使用的qwen2.5 32B
    result_dir = r"E:\Postgraduate\Code\SunnylnAgent\experiment\RECAgent\ablation_qwen2_5_32B"
    print(result_dir)
    groups = {
        "base": os.path.join(result_dir, "base"),
        "regular": os.path.join(result_dir, "regular"),
        "clear": os.path.join(result_dir, "clear")
    }

    # Qwen2.5 32B 定义价格常量（元/千token）
    PRICE_INPUT = 0.002
    PRICE_OUTPUT = 0.006


    print("=================================================ablation_qwen2_5_32B实验结果 131任务==============================================================")
    # 用于存储所有组的汇总数据
    all_results = {}
    # 统计每个组的数据
    for group_name, group_dir in groups.items():
        total_time = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_success_count = 0
        total_interact_count = 0
        RCR = 0

        total_tasks = 0

        # 检查目录是否存在
        if not os.path.exists(group_dir):
            print(f"警告: 目录 {group_dir} 不存在")
            continue

        # 遍历目录中的所有任务+
        try:
            with open(os.path.join(group_dir, "result.json"), "r", encoding="utf-8") as f:
                rs = json.load(f)


        except Exception as e:
            print(f"错误: 读取文件 {group_dir + '/result.json'} 失败: {e}")
            continue
        for r in rs:
            total_tasks += 1

            # 处理成功和失败的任务
            if r.get("res", {}).get("task").get("run_status"):
                total_time += r["res"]["time"]["total_time"]
                total_prompt_tokens += r["res"]["tokens"]["total"]["prompt_tokens"]
                total_completion_tokens += r["res"]["tokens"]["total"]["completion_tokens"]
                total_interact_count += r["res"]["interaction_number"]
                total_success_count += 1
                RCR += r["res"]["task"]["RCR"]
            else:
                print(
                    f"失败任务id:{r['res']['task']['task_id']}, 组:{group_name}, 任务描述：{r['res'].get('task', '未知')}")

        # 计算各项指标
        if total_success_count > 0:
            avg_time = total_time / total_success_count
            avg_input_tokens = total_prompt_tokens / total_success_count
            avg_output_tokens = total_completion_tokens / total_success_count
            avg_cost = (avg_input_tokens * PRICE_INPUT + avg_output_tokens * PRICE_OUTPUT) / 1000
            avg_interact = total_interact_count / total_success_count
            RCR = RCR / total_success_count / 5.0
            success_rate = total_success_count / total_tasks if total_tasks > 0 else 0
        else:
            avg_time = 0
            avg_input_tokens = 0
            avg_output_tokens = 0
            avg_cost = 0
            avg_interact = 0
            success_rate = 0

        # 存储结果
        all_results[group_name] = {
            "success_rate": success_rate,
            "avg_time": avg_time,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_cost": avg_cost,
            "avg_interact": avg_interact,
            "ave_scaled_RCR": RCR,
            "total_success": total_success_count,
            "total_tasks": total_tasks
        }

        # 打印结果
        print(f"{group_name} :")
        print(f"  成功率: {success_rate:.3f} ({total_success_count}/{total_tasks})")
        print(f"  平均时间: {avg_time:.2f} s")
        print(f"  平均输入token: {avg_input_tokens:.2f}")
        print(f"  平均输出token: {avg_output_tokens:.2f}")
        print(f"  平均花费cost：{avg_cost:.6f} 元")
        print(f"  平均交互次数: {avg_interact:.3f}")
        print(f"  平均需求覆盖率: {RCR:.4f}")
        print("++" * 30)

    # 计算总体统计数据
    total_success_all = sum(data["total_success"] for data in all_results.values())
    total_tasks_all = sum(data["total_tasks"] for data in all_results.values())

    # 加权平均计算
    total_avg_time = sum(data["avg_time"] * data["total_success"] for data in
                         all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_input = sum(data["avg_input_tokens"] * data["total_success"] for data in
                          all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_output = sum(data["avg_output_tokens"] * data["total_success"] for data in
                           all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_scaled_RCR = sum(data["ave_scaled_RCR"] * data["total_success"] for data in
                               all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_interact = sum(data["avg_interact"] * data["total_success"] for data in
                             all_results.values()) / total_success_all if total_success_all > 0 else 0

    # 总成本计算
    total_avg_cost = (total_avg_input * PRICE_INPUT + total_avg_output * PRICE_OUTPUT) / 1000

    # 打印总体结果
    print(f"总体统计:")
    print(f"  成功率: {total_success_all / total_tasks_all:.3f} ({total_success_all}/{total_tasks_all})")
    print(f"  平均时间: {total_avg_time:.2f} s")
    print(f"  平均输入token: {total_avg_input:.2f}")
    print(f"  平均输出token: {total_avg_output:.2f}")
    print(f"  平均花费cost：{total_avg_cost:.6f} 元")
    print(f"  平均需求覆盖率: {total_avg_scaled_RCR:.4f}")
    print(f"  平均交互次数: {total_avg_interact:.3f}")

def ablation_QWEN_one_extract():
    # 该函数用于层级规划消融实验的结果收集 使用的qwen2.5 72B

    result_dir = os.path.join(find_project_root(),r"experiment\RECAgent\ablation_qwen2_5_72B_one_extract")
    print(result_dir)
    groups = {
        "base": os.path.join(result_dir, "base"),
        "regular": os.path.join(result_dir, "regular"),
        "clear": os.path.join(result_dir, "clear")
    }

    # Qwen2.5 72B 定义价格常量（元/千token）
    PRICE_INPUT = 0.004
    PRICE_OUTPUT = 0.012


    print("=================================================ablation_one_extract_qwen2_5_72B实验结果 131任务==============================================================")
    # 用于存储所有组的汇总数据
    all_results = {}
    # 统计每个组的数据
    for group_name, group_dir in groups.items():
        total_time = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_success_count = 0
        total_interact_count = 0
        RCR = 0

        total_tasks = 0

        # 检查目录是否存在
        if not os.path.exists(group_dir):
            print(f"警告: 目录 {group_dir} 不存在")
            continue

        # 遍历目录中的所有任务+
        try:
            with open(os.path.join(group_dir, "result.json"), "r", encoding="utf-8") as f:
                rs = json.load(f)


        except Exception as e:
            print(f"错误: 读取文件 {group_dir + '/result.json'} 失败: {e}")
            continue
        for r in rs:
            total_tasks += 1

            # 处理成功和失败的任务
            if r.get("res", {}).get("task").get("run_status"):
                total_time += r["res"]["time"]["total_time"]
                total_prompt_tokens += r["res"]["tokens"]["total"]["prompt_tokens"]
                total_completion_tokens += r["res"]["tokens"]["total"]["completion_tokens"]
                total_interact_count += r["res"]["interaction_number"]
                total_success_count += 1
                RCR += r["res"]["task"]["RCR"]
            else:
                print(
                    f"失败任务id:{r['res']['task']['task_id']}, 组:{group_name}, 任务描述：{r['res'].get('task', '未知')}")

        # 计算各项指标
        if total_success_count > 0:
            avg_time = total_time / total_success_count
            avg_input_tokens = total_prompt_tokens / total_success_count
            avg_output_tokens = total_completion_tokens / total_success_count
            avg_cost = (avg_input_tokens * PRICE_INPUT + avg_output_tokens * PRICE_OUTPUT) / 1000
            avg_interact = total_interact_count / total_success_count
            RCR = RCR / total_success_count / 5.0
            success_rate = total_success_count / total_tasks if total_tasks > 0 else 0
        else:
            avg_time = 0
            avg_input_tokens = 0
            avg_output_tokens = 0
            avg_cost = 0
            avg_interact = 0
            success_rate = 0

        # 存储结果
        all_results[group_name] = {
            "success_rate": success_rate,
            "avg_time": avg_time,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_cost": avg_cost,
            "avg_interact": avg_interact,
            "ave_scaled_RCR": RCR,
            "total_success": total_success_count,
            "total_tasks": total_tasks
        }

        # 打印结果
        print(f"{group_name} :")
        print(f"  成功率: {success_rate:.3f} ({total_success_count}/{total_tasks})")
        print(f"  平均时间: {avg_time:.2f} s")
        print(f"  平均输入token: {avg_input_tokens:.2f}")
        print(f"  平均输出token: {avg_output_tokens:.2f}")
        print(f"  平均花费cost：{avg_cost:.6f} 元")
        print(f"  平均交互次数: {avg_interact:.3f}")
        print(f"  平均需求覆盖率: {RCR:.4f}")
        print("++" * 30)

    # 计算总体统计数据
    total_success_all = sum(data["total_success"] for data in all_results.values())
    total_tasks_all = sum(data["total_tasks"] for data in all_results.values())

    # 加权平均计算
    total_avg_time = sum(data["avg_time"] * data["total_success"] for data in
                         all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_input = sum(data["avg_input_tokens"] * data["total_success"] for data in
                          all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_output = sum(data["avg_output_tokens"] * data["total_success"] for data in
                           all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_scaled_RCR = sum(data["ave_scaled_RCR"] * data["total_success"] for data in
                               all_results.values()) / total_success_all if total_success_all > 0 else 0
    total_avg_interact = sum(data["avg_interact"] * data["total_success"] for data in
                             all_results.values()) / total_success_all if total_success_all > 0 else 0

    # 总成本计算
    total_avg_cost = (total_avg_input * PRICE_INPUT + total_avg_output * PRICE_OUTPUT) / 1000

    # 打印总体结果
    print(f"总体统计:")
    print(f"  成功率: {total_success_all / total_tasks_all:.3f} ({total_success_all}/{total_tasks_all})")
    print(f"  平均时间: {total_avg_time:.2f} s")
    print(f"  平均输入token: {total_avg_input:.2f}")
    print(f"  平均输出token: {total_avg_output:.2f}")
    print(f"  平均花费cost：{total_avg_cost:.6f} 元")
    print(f"  平均需求覆盖率: {total_avg_scaled_RCR:.4f}")
    print(f"  平均交互次数: {total_avg_interact:.3f}")

if __name__=="__main__":
    default()
    # ablation_QWEN_one_extract()