from dataform_table_object import DataformTableObject
from dataform_declaration_object import DataformDeclarationObject

class DataformObjectList:
    object_list = {}

    def __init__(self, dataform_json, dataform_project_variables):
        for table in dataform_json['tables']:
            self.object_list[DataformTableObject.target_to_task_id(table['target'])] = DataformTableObject(table)
        for declaration in dataform_json['declarations']:
            self.object_list[DataformTableObject.target_to_task_id(declaration['target'])] = DataformDeclarationObject(declaration)

        self.dataform_project_variables = dataform_project_variables

    def create_tasks(self, dag):
        for o in self.object_list.values():
            o.create_task(self.dataform_project_variables, dag)

    def filter_by_tag(self, tag_name):
        for o in self.object_list.values():
            o.filter_by_tag(tag_name)

    def get_downstream_tasks(self, task_id):

        downstream_tasks = []
        task_types = []

        for d in self.object_list[task_id].downstream_task_id_list:
            if self.object_list.get(d) is not None and self.object_list[d].action_task is not None:
                downstream_tasks.append(self.object_list[d].action_task)
                task_types.append(self.object_list[d].task_type)

        return {"action_tasks": downstream_tasks, "task_types": task_types}