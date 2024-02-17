from airflow.providers.google.cloud.operators.dataform import DataformCreateCompilationResultOperator
from dataform_object_list import DataformObjectList

import os
import json


class DataformProjectVariables:
    def __init__(self, project_id, region, repository_id, git_commitish, location):
        self.project_id = project_id
        self.region = region
        self.repository_id = repository_id
        self.git_commitish = git_commitish
        self.location = location




class DataformParser:
    dataform_project_variables = None
    dataform_linage_path = ""
    dataform_compile_task = None
    dag = None
    dfo_list = None

    def __init__(self, linage_path, dag, project_id, repository_id, region, git_commitish, location):

        self.dataform_project_variables = DataformProjectVariables(project_id, region, repository_id, git_commitish,
                                                                   location)
        self.dataform_linage_path = linage_path
        self.dag = dag

        my_dir = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(my_dir, self.dataform_linage_path))
        dataform_json = json.load(f)
        f.close()

        self.dfo_list = DataformObjectList(dataform_json, self.dataform_project_variables)

    def create_dataform_compile_task(self, compile_variables={}):
        self.dataform_compile_task = DataformCreateCompilationResultOperator(
            task_id="create_dataform_compilation_result",
            project_id=self.dataform_project_variables.project_id,
            region=self.dataform_project_variables.region,
            repository_id=self.dataform_project_variables.repository_id,
            compilation_result={
                "code_compilation_config": {
                    "vars": compile_variables
                },
                "git_commitish": self.dataform_project_variables.git_commitish
            },
            dag=self.dag,
            priority_weight=10,
        )
        return self.dataform_compile_task

    def task_filter_by_tag(self, tag_name):
        self.dfo_list.filter_by_tag(tag_name)

    def parse(self):

        self.dfo_list.create_tasks(self.dag)

        for d in self.dfo_list.object_list.values():
            if d.action_task is not None:

                downstream = self.dfo_list.get_downstream_tasks(d.task_id)
                if len(downstream["action_tasks"]) > 0:
                    downstream["action_tasks"] >> d.action_task

                if d.task_type == "Table" and sum(1 for t in downstream["task_types"] if t == 'Table') == 0:
                    self.dataform_compile_task >> d.action_task
