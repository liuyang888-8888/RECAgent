# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/8/27 
# 时 间：10:03
import json
import math
import os
import re

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity


def find_project_root():
    #根据当前文件的目录获取root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#格式化打印字符串
def print_dic(dic):
    """
    格式化输出json
    :param dic:
    :return:
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(dic)

def get_params_des(widget_name):
    with open(os.path.join(find_project_root(),'tools/workflow_widgets.json'),'r',encoding='utf-8') as f:
        data=json.load(f)
    for widget in data:
        if widget['widget_name']==widget_name:
            return widget['params']

#清空文件夹
def clear_folder(folder_path):
    """
    清空指定的文件夹。

    :param folder_path: 文件夹路径
    """
    import os
    import shutil
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径 {folder_path} 不是一个有效的文件夹路径")

    # 遍历文件夹中的所有文件和子文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 如果是文件，则删除
        if os.path.isfile(item_path):
            os.remove(item_path)
        # 如果是文件夹，则递归调用清空函数并删除文件夹
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

def write_json_to_file(new_json_data, file_name):
    """
    将新的 JSON 数据追加到文件中。如果文件不存在，则创建新文件。

    :param new_json_data: 新的 JSON 数据（列表形式）
    :param file_name: 文件名（不带扩展名）
    """
    from config.config import save_chat_log
    if not save_chat_log:
        return
    file_path = os.path.join(find_project_root(), f'data/chats/{file_name}.json')

    # 如果文件存在，读取原有数据
    if os.path.exists(file_path):
        with open(file_path, 'r',encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    raise ValueError("文件中的数据不是一个列表，无法追加。")
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # 将新的数据追加到原有数据
    if isinstance(new_json_data, list):
        existing_data.append(new_json_data)
    else:
        raise ValueError("新的 JSON 数据应为列表形式。")

    # 写回文件
    with open(file_path, 'w',encoding='utf-8') as file:
        json.dump(existing_data, file,ensure_ascii=False, indent=4)
def write_csv_to_file(data, filename,table_name=""):
    column_names = data["data"]["columns"]
    # column_types = [col["type"] for col in data["data_info"]["columns_info"]]
    column_roles = ["class" if col["role"]=="target" else col["role"] for col in data["data_info"]["columns_info"]]
    import pandas as pd
    # 提取数据部分
    data_df = pd.DataFrame(data=data["data"]["data"], columns=column_names)

    # 写入 CSV 文件
    with open(os.path.join(find_project_root(), f"data/current/{filename}.csv"), "w", encoding="utf-8",
              newline="") as f:
        # 写入列名
        f.write(",".join(column_names) + "\n")
        # 写入列类型
        # f.write(",".join(column_types) + "\n")
        # 写入列角色
        f.write(",".join(column_roles) + "\n")
        # 写入数据
        data_df.to_csv(f, index=False, header=False)
    if table_name !="":
        import shutil
        # 定义原始文件路径和目标文件路径
        source_file = os.path.join(find_project_root(), f"data/current/{filename}.csv")
        destination_folder = os.path.join(find_project_root(), f"data/MLBench")
        new_file_name = table_name + filename + ".csv"

        # 构建完整的目标文件路径
        destination_file = os.path.join(destination_folder, new_file_name)
        # 拷贝并重命名文件
        try:
            shutil.copy(source_file, destination_file)
            print(f"文件已从 {source_file} 拷贝并重命名为 {destination_file}")
        except IOError as e:
            print(f"无法拷贝文件. {e}")


def update_json_record(key: str, value: dict, filepath: str):
    """
    更新JSON文件中的指定字段

    Args:
        key: 要更新的键名
        value: 新的键值
        filepath: JSON文件路径
    """
    with open(filepath, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

def get_data_info(path=r"E:\Postgraduate\Code\SunnylnAgent\data\current\train.csv"):
    import pandas as pd

    description_template = "数据集特征信息：数据共有{sample_size}条，{num_features}个特征属性，其中{num_categorical_features}个类别特征，{num_numeric_features}个数值特征，空值比例为{missing_ratio}%。"
    df = pd.read_csv(path)
    roles = df.iloc[1].tolist()
    types = df.iloc[0].tolist()

    # 删除第一行和第二行
    df.drop([0, 1], inplace=True)

    # 数据集信息搜集
    sample_size = len(df)
    num_features = 0
    num_categorical_features = 0
    num_numeric_features = 0
    target_type_code = 0
    num_target_classes_or_range = [0, 0, 0]
    missing_ratio = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
    meta = 0

    for i in range(len(types)):
        if roles[i] == "target":
            if types[i] == "C":
                target_type_code = 0  # 分类
                num_target_classes_or_range = [len(df.iloc[:, i].unique()), 0, 0]
            elif types[i] == "D":
                target_type_code = 1  # 回归
                # 进行数值转换 转换成数值类型 遇到无法转换置为NaN
                df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors='coerce')
                num_target_classes_or_range = [len(df.iloc[:, i].unique()), df.iloc[:, i].min(), df.iloc[:, i].max()]


        elif roles[i] == "feature":
            if types[i] == "C":
                num_numeric_features += 1
            elif types[i] == "D":
                num_categorical_features += 1
            num_features += 1

        elif roles[i] == "meta":
            meta += 1

    data_des = description_template.format(sample_size=sample_size, num_features=num_features,
                                         num_categorical_features=num_categorical_features,
                                         num_numeric_features=num_numeric_features, missing_ratio=missing_ratio)
    data_des_vector=[math.log(sample_size),num_features,num_categorical_features,num_numeric_features,missing_ratio*100%100,target_type_code,math.log(1 + num_target_classes_or_range[0]),math.log(1+num_target_classes_or_range[2]-num_target_classes_or_range[1])]

    if target_type_code == 0:
        data_des += "数据集目标变量为分类变量，共有{}个类别。".format(num_target_classes_or_range[0])
    elif target_type_code == 1:
        data_des += "数据集目标变量为连续变量，取值范围在{}到{}之间。".format(num_target_classes_or_range[1],
                                                                          num_target_classes_or_range[2])
    return data_des,data_des_vector






if __name__ == '__main__':
    des,vec=get_data_info()
    print(cosine_similarity(np.array([3.191231489926741, 6, 1, 5, 0.0, 0, 0.0, 0.0]).reshape(1, -1) ,np.array(vec).reshape(1, -1) ))