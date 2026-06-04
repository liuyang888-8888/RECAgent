# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/9/24 
# 时 间：14:10


search_space_pmt = """你是一名机器学习模型超参数优化工程师，我会给你任务的描述，模型名称及其相关参数信息以及数据集的特征信息。你需要做的任务是：根据我给出的该模型的一个搜索空间样例和数据集的描述信息，还有参数信息的具体含义信息，在我给你的搜索空间样例上进行范围调整，确定更为合适的搜索空间范围，用于使用NNI来进行参数优化。
示例问题1：{"task" : "您的工作是建立一个机器学习模型，根据客户以往的酒店预定相关数据，预测客户是否会取消预订。",
"model" : "Tree",
"params_des": [
            {
                "name": "limit_min_leaf",
                "type": "bool",
                "default": true,
                "description": "是否设置叶子节点中的最小实例数"
            },
            {
                "name": "min_leaf",
                "type": "int",
                "default": 2,
                "range": [1,21],
                "description": "叶子节点中的最小实例数"
            },
            {
                "name": "limit_min_internal",
                "type": "bool",
                "default": true,
                "description": "是否设置分割子集数"
            },
            {
                "name": "min_internal",
                "type": "int",
                "default": 5,
                "range": [2,21],
                "description": "分割子集数"
            },
            {
                "name": "limit_depth",
                "type": "bool",
                "default": true,
                "description": "是否设置最大数深度"
            },
            {
                "name": "max_depth",
                "type": "int",
                "default": 100,
                "range": [3,201],
                "description": "最大数深度"
            }
        ],
"dataset_info" :"数据集：reservation_cancellation_train 17个特征列：['no_of_adults', 'no_of_children', 'no_of_weekend_nights', 'no_of_week_nights', 'type_of_meal_plan', 'required_car_parking_space', 'room_type_reserved', 'lead_time', 'arrival_year', 'arrival_month', 'arrival_date', 'market_segment_type', 'repeated_guest', 'no_of_previous_cancellations', 'no_of_previous_bookings_not_canceled', 'avg_price_per_room', 'no_of_special_requests'] 1个目标列：['booking_status']。前五条数据如下：[{'id': 0, 'no_of_adults': 2.0, 'no_of_children': 0, 'no_of_weekend_nights': 0, 'no_of_week_nights': 2, 'type_of_meal_plan': 1, 'required_car_parking_space': 0, 'room_type_reserved': 0, 'lead_time': 9, 'arrival_year': 2018, 'arrival_month': 1, 'arrival_date': 14, 'market_segment_type': 1, 'repeated_guest': 1, 'no_of_previous_cancellations': 11, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 67.5, 'no_of_special_requests': 0, 'booking_status': 0}, {'id': 2, 'no_of_adults': 2.0, 'no_of_children': 0, 'no_of_weekend_nights': 0, 'no_of_week_nights': 1, 'type_of_meal_plan': 0, 'required_car_parking_space': 0, 'room_type_reserved': 0, 'lead_time': 315, 'arrival_year': 2018, 'arrival_month': 12, 'arrival_date': 2, 'market_segment_type': 0, 'repeated_guest': 0, 'no_of_previous_cancellations': 0, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 52.0, 'no_of_special_requests': 0, 'booking_status': 0}, {'id': 3, 'no_of_adults': 1.0, 'no_of_children': 0, 'no_of_weekend_nights': 0, 'no_of_week_nights': 2, 'type_of_meal_plan': 1, 'required_car_parking_space': 0, 'room_type_reserved': 0, 'lead_time': 32, 'arrival_year': 2018, 'arrival_month': 12, 'arrival_date': 1, 'market_segment_type': 1, 'repeated_guest': 0, 'no_of_previous_cancellations': 0, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 56.0, 'no_of_special_requests': 0, 'booking_status': 0}, {'id': 5, 'no_of_adults': 0.0, 'no_of_children': 2, 'no_of_weekend_nights': 2, 'no_of_week_nights': 5, 'type_of_meal_plan': 0, 'required_car_parking_space': 0, 'room_type_reserved': 2, 'lead_time': 215, 'arrival_year': 2018, 'arrival_month': 10, 'arrival_date': 6, 'market_segment_type': 1, 'repeated_guest': 0, 'no_of_previous_cancellations': 0, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 212.06, 'no_of_special_requests': 0, 'booking_status': 1}, {'id': 6, 'no_of_adults': 2.0, 'no_of_children': 0, 'no_of_weekend_nights': 0, 'no_of_week_nights': 1, 'type_of_meal_plan': 2, 'required_car_parking_space': 0, 'room_type_reserved': 0, 'lead_time': 320, 'arrival_year': 2018, 'arrival_month': 8, 'arrival_date': 18, 'market_segment_type': 0, 'repeated_guest': 0, 'no_of_previous_cancellations': 0, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 115.0, 'no_of_special_requests': 1, 'booking_status': 1}, {'id': 8, 'no_of_adults': 2.0, 'no_of_children': 0, 'no_of_weekend_nights': 2, 'no_of_week_nights': 3, 'type_of_meal_plan': 0, 'required_car_parking_space': 0, 'room_type_reserved': 0, 'lead_time': 189, 'arrival_year': 2018, 'arrival_month': 10, 'arrival_date': 8, 'market_segment_type': 0, 'repeated_guest': 0, 'no_of_previous_cancellations': 0, 'no_of_previous_bookings_not_canceled': 0, 'avg_price_per_room': 72.75, 'no_of_special_requests': 0, 'booking_status': 0}]",
"search_space_example":{
         "limit_min_leaf": {"_type": "choice", "_value": [true, false]},
         "min_leaf": {"_type": "randint", "_value": [1, 21],"_condition":{"limit_min_leaf":true}},
         "limit_min_internal": {"_type": "choice", "_value": [true, false]},
         "min_internal": {"_type": "randint", "_value": [2, 21],"_condition":{"limit_min_internal":true}},
         "limit_depth": {"_type": "choice", "_value": [true, false]},
         "max_depth": {"_type": "randint", "_value": [3, 201],"_condition":{"limit_depth":true}}
    }

}
示例回答1：```json
{
"task_type": "classification",
"search_space":{  
         "limit_min_leaf": {"_type": "choice", "_value": [true, false]},
         "min_leaf": {"_type": "randint", "_value": [3, 11],"_condition":{"limit_min_leaf":true}},
         "limit_min_internal": {"_type": "choice", "_value": [true, false]},
         "min_internal": {"_type": "randint", "_value": [2, 6],"_condition":{"limit_min_internal":true}},
         "limit_depth": {"_type": "choice", "_value": [true, false]},
         "max_depth": {"_type": "randint", "_value": [5, 30],"_condition":{"limit_depth":true}}
         }
}
```只需要返回json，不要回答无关内容。
"""