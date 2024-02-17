from airflow.providers.google.cloud.operators.dataform import DataformCreateWorkflowInvocationOperator
from dataform_object import DataformObject


class DataformTableObject(DataformObject):
    def __init__(self, dataform_table):
        super().__init__(dataform_table)

        self.downstream_task_id_list = [self.target_to_task_id(d) for d in
                                        dataform_table.get('dependencyTargets', [])]

        if dataform_table.get('type', '') == 'view':
            self.task_type = 'View'
            self.filtered = 'False'
        else:
            self.task_type = 'Table'

    def create_task(self, dataform_project_variables, dag):
        if super().filter_control():
            return

        if self.task_group is not None:
            self.action_task = DataformCreateWorkflowInvocationOperator(
                task_id=self.task_id,
                project_id=dataform_project_variables.project_id,
                region=dataform_project_variables.region,
                repository_id=dataform_project_variables.repository_id,
                workflow_invocation={
                    "compilation_result": "{{ task_instance.xcom_pull('create_dataform_compilation_result')['name'] }}",
                    'invocation_config': {"included_targets": [self.task_dataform_target]}
                },
                # dag=dag,
                priority_weight=5,
                pool='dataform_pool',
            )
            self.task_group.add(self.action_task)
        else:
            self.action_task = DataformCreateWorkflowInvocationOperator(
                task_id=self.task_id,
                project_id=dataform_project_variables.project_id,
                region=dataform_project_variables.region,
                repository_id=dataform_project_variables.repository_id,
                workflow_invocation={
                    "compilation_result": "{{ task_instance.xcom_pull('create_dataform_compilation_result')['name'] }}",
                    'invocation_config': {"included_targets": [self.task_dataform_target]}
                },
                dag=dag,
                priority_weight=5,
                pool='dataform_pool',
            )
        return self.action_task
