# -*- coding: utf-8 -*-
#  道阻且长，行则将至
# -----Sunnyln---
#  7/16/2024  3:50 PM
import json
import os

import Levenshtein

from lib.lib import find_project_root


class Widgets:
    def __init__(self):
        with open(os.path.join(find_project_root(), 'tools/workflow_widgets.json'), 'r', encoding='utf-8') as f:
            self.widgets= json.load(f)
        self.widget_names=[]
        for widget in self.widgets:
            self.widget_names.append(widget['widget_name'])

    # widgetAgent tools
    def widgets_info(self):

        widgets_by_type = {"ml_IO": [],"dl_IO": [], "Preprocess": [], "FeatureEngineering": [], "image": [], "text": [],
                           "timeseries": [], "clustering": [], "regression": [], "classification": [], "dl_evaluate": [],"ml_evaluate": [],
                           "visualize": []}
        for widget in self.widgets:
            if widget["type"] == "IO":
                if "classification" in widget["fit_task_type"]:
                    widgets_by_type["ml_IO"].append(widget)
                if "text" in widget["fit_task_type"] or "image" in widget["fit_task_type"]:
                    widgets_by_type["dl_IO"].append(widget)
            elif widget["type"] == "Preprocess":
                widgets_by_type["Preprocess"].append(widget)
            elif widget["type"] == "FeatureEngineering":
                widgets_by_type["FeatureEngineering"].append(widget)
            elif widget["type"] == "model":
                if "classification" in widget["fit_task_type"]:
                    widgets_by_type["classification"].append(widget)
                if "regression" in widget["fit_task_type"]:
                    widgets_by_type["regression"].append(widget)
                if "clustering" in widget["fit_task_type"]:
                    widgets_by_type["clustering"].append(widget)
                if "timeseries" in widget["fit_task_type"]:
                    widgets_by_type["timeseries"].append(widget)
                if "text" in widget["fit_task_type"]:
                    widgets_by_type["text"].append(widget)
                if "image" in widget["fit_task_type"]:
                    widgets_by_type["image"].append(widget)

            elif widget["type"] == "evaluate":
                if "classification" in widget["fit_task_type"]:
                    widgets_by_type["ml_evaluate"].append(widget)
                elif "text" in widget["fit_task_type"]:
                    widgets_by_type["dl_evaluate"].append(widget)
            elif widget["type"] == "visualize":
                widgets_by_type["visualize"].append(widget)
        return widgets_by_type

    #PlanAgent tools
    def get_ml_type_models_name(self):
        models = {"classification":[],"regression":[],"clustering":[],"timeseries":[]}
        for widget in self.widgets:
            if widget["type"] == "model":
                if "classification" in widget["fit_task_type"]:
                    models["classification"].append(widget["widget_name"])
                if "regression" in widget["fit_task_type"]:
                    models["regression"].append(widget["widget_name"])
                if "clustering" in widget["fit_task_type"]:
                    models["clustering"].append(widget["widget_name"])
                if "timeseries" in widget["fit_task_type"]:
                    models["timeseries"].append(widget["widget_name"])
        return models

    def get_dl_type_models_name(self):
        models = {"image":[],"audio":[],"text":[],"video":[],"graph":[]}
        for widget in self.widgets:
            if widget["type"] == "model":
                if "image" in widget["fit_task_type"]:
                    models["image"].append(widget["widget_name"])
                if "audio" in widget["fit_task_type"]:
                    models["audio"].append(widget["widget_name"])
                if "text" in widget["fit_task_type"]:
                    models["text"].append(widget["widget_name"])
                if "video" in widget["fit_task_type"]:
                    models["video"].append(widget["widget_name"])
                if "graph" in widget["fit_task_type"]:
                    models["graph"].append(widget["widget_name"])
        return models
    def get_PMA_type_models_name(self):
        models = []
        for widget in self.widgets:
            if widget["type"] == "model" and "pretrained modeling application" in widget["fit_task_type"]:
                models.append(widget["widget_name"])

        return models
    def get_all_models_name(self):
        models = []
        for widget in self.widgets:
            if widget["type"] == "model":
                models.append(widget["widget_name"])
        return models
    def get_preprocess(self):
        support_operations = ["Impute","Interpolate","Data Sampler","Outliers","Select Rows","Unique","Randomize","One Hot Encoder"]
        res={}
        for widget in self.widgets:
            if widget["widget_name"] in support_operations:
                res[widget["widget_name"]]={"description":widget["description"]}
        return res
    def get_sample_params(self, widget_names):
        res={}
        for widget in self.widgets:
            if widget["widget_name"] in widget_names:
                res[widget["widget_name"]]=widget["params"]
        return res

    def get_models_widget_names(self):
        res=[]
        for widget in self.widgets:
            if widget["type"] == "model":
                res.append(widget["widget_name"])
        return res

    def get_default_params(self, widget_names:list):
        res={}
        for widget in self.widgets:
            if widget["widget_name"] in widget_names:
                params={}
                for param in widget["params"]:
                    params[param["name"]]=param["default"]
                res[widget["widget_name"]]=params
        return res
    def find_most_similar(self,target):

        most_similar_string = None
        highest_similarity = -1

        for string in self.widget_names:
            # Compute the similarity ratio using Levenshtein
            similarity = Levenshtein.ratio(target, string)

            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_string = string
        return most_similar_string


ws=Widgets()










if __name__=="__main__":
    print(ws.get_PMA_type_models_name())

