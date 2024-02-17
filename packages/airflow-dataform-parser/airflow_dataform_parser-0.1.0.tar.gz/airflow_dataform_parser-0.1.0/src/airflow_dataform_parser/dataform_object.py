import os
import json


class DataformObject:

    def __init__(self, dataform_object):
        self.task_id = self.target_to_task_id(dataform_object['target'])
        self.task_dataform_target = dataform_object['target']
        self.action_task = None
        self.task_group = None
        self.tags = dataform_object.get('tags', [])
        self.filtered = 'Default'  # default initial hali daha sonra eğer filtrelenirse true eğer kullanılmayacaksa false olur

    @staticmethod
    def target_to_task_id(target):
        return target['schema'] + '-' + target['name']

    def filter_by_tag(self, tag_name):
        if self.filtered == 'Default':
            self.filtered = 'False'

        if self.tags is not None:
            for t in self.tags:
                if t == tag_name:
                    self.filtered = 'True'

    def filter_control(self):
        return self.filtered == 'False' or self.action_task is not None

    def create_task(self, dataform_project_variables, dag):
        pass

