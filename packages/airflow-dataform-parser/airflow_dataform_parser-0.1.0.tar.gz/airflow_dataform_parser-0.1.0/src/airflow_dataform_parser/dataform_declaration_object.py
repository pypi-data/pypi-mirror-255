from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from dataform_object import DataformObject

import os
import json

class DataformDeclarationObject(DataformObject):
    def __init__(self, dataform_declaration):
        super().__init__(dataform_declaration)

        self.downstream_task_id_list = []
        self.task_type = "Declaration"
        my_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(my_dir, "pipeline_configs/" + self.task_id + ".json")

    def create_task(self, dataform_project_variables, dag):
        if super().filter_control() or not(os.path.exists(self.config_path)):
            return


        with open(self.config_path, 'r') as json_file:
            pipeline_config = json.load(json_file)
            body = pipeline_config["dataflow_config"]

        if self.task_group is not None:
            self.action_task = DataflowStartFlexTemplateOperator(
                task_id=self.task_id,
                project_id=dataform_project_variables.project_id,
                body=body,
                location=dataform_project_variables.region,
                #dag=dag,
                priority_weight=8,
                pool='dataflow_pool',
            )
            self.task_group.add(self.action_task)
        else:
            self.action_task = DataflowStartFlexTemplateOperator(
                task_id=self.task_id,
                project_id=dataform_project_variables.project_id,
                body=body,
                location=dataform_project_variables.region,
                dag=dag,
                priority_weight=8,
                pool='dataflow_pool',
            )
        return self.action_task
