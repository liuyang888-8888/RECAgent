# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/9/26 
# 时 间：14:02
import unittest

class EnvTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_llm(self):
        try:
            from llm.LLM import LLM

            response = LLM.common_chat (messages=[{'role': 'system',
                                                   'content': '你是一个有用的助手'},
                                                   {'role': 'user',
                                                   'content': "你是谁？"}]
                                        )

            print (response)


            #print(common_chat(messages=[{'role': 'system', 'content': '你是一名有用的机器学习工作流的编排人员，你需要使用我给你的组件和可以调用的函数名称来编写代码构建工作流，代码中不可以使用我未提供函数，我会及时给你反馈工作流的状态。\n可以使用的函数如下：{\n add_node(widget_name,node_name):这个函数用来添加一个节点到工作流中，widget_name必须与我给出的组件信息一致，node_name可以自定义取名字，添加成功之后该函数会返回一个整数，是新添加的节点id。\n delete_node(node_id):这个函数用来删除一个节点，参数是node_id。\n add_edge(source_node_id,target_node_id):这个函数用来添加一个边到工作流中，参数是source_node_id和target_node_id，添加成功后会返回新添加的边的id。\n delete_edge(edge_id):这个函数用来删除一个边，参数是edge_id。\n update_node_params(node_id,node_params)：这个函数用来更新工作流当中的一个节点的参数，参数是需要更新的某节点的参数node_params和node_id，必须要与组件列表中的参数一致。\n 请严格按照如下格式：\n ```python \n    你所给出的代码\n ```\n 只需给出代码，不要回复无关内容。\n示例：\n问题：任务描述：使用XGboost模型，参数当中的学习率设置为0.1，学习器设置为DART。。组件名称：XGBoost，当前工作流信息：{\'edges\': [], \'nodes\': [{\'node_id\': \'31969\', \'widget_name\': \'File\', \'node_name\': \'文件输入\', \'node_params\': {\'type\': \'sample\', \'filename\': \'iris.csv\'}}]}\n回答：```python\nnode1_id=add_node(widget_name="XGBoost", node_name="XGBoost")\nupdate_node_params(node_id=node1_id, node_params={\'booster\': \'dart\',\'learning_rate\':0.1})\nadd_edge(31969,node1_id)\n```\n'}, {'role': 'user', 'content': "任务描述：使用SQL Table组件，数据集是鲍鱼数据集。组件名称：SQL Table，参数：{'table_name': 'abalone_train', 'attr_mapping': {'sex': {'key': 0, 'name': 'sex', 'type': 3, 'role': 0}, 'length': {'key': 1, 'name': 'length', 'type': 2, 'role': 0}, 'diameter': {'key': 2, 'name': 'diameter', 'type': 2, 'role': 0}, 'height': {'key': 3, 'name': 'height', 'type': 2, 'role': 0}, 'whole_weight': {'key': 4, 'name': 'whole_weight', 'type': 2, 'role': 0}, 'whole_weight1': {'key': 5, 'name': 'whole_weight1', 'type': 2, 'role': 0}, 'whole_weight2': {'key': 6, 'name': 'whole_weight2', 'type': 2, 'role': 0}, 'shell_weight': {'key': 7, 'name': 'shell_weight', 'type': 2, 'role': 0}, 'rings': {'key': 8, 'name': 'rings', 'type': 2, 'role': 0}}}当前工作流信息：{'edges': [], 'nodes': []}"}]))
        except Exception as e:
            print("LLM Error,Please check your api_key:", e)
            self.fail("test_llm failed.")


    def test_mysql(self):
        try:
            from tools.db import find_all_table_name, get_table_columns, fetch_data_from_table
            tables = find_all_table_name()
            self.assertTrue(len(tables)>0)

        except Exception as e:
            print("Error in Mysql Connecting:", e)
            self.fail("test_mysql failed.")
    def test_uniplore_token(self):
        try:
            from tools.actions import get_workflow
            workflow = get_workflow()
            self.assertTrue(workflow,"uniplore_AuthToken")

        except Exception as e:
            print("Error in Uniplore AuthToken:", e)
            self.fail("Uniplore_AuthToken")


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
    print("All tests passed!")

