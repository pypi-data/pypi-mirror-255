import contextlib

import logging

import sys

import io

from torii.data import ToriiObject, Task
from torii.exception import ToriiException

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class OfflineTaskService(object):

    def __init__(self, picom_task, current_context, templates, last_tasks, attic):
        """
        Create the task service
        """

        self._logger = logging.Logger('Torii')
        self.picom_task = picom_task
        self.current_context = current_context
        self.templates = templates
        self.last_tasks = last_tasks
        self.attic = attic
        self.next_tasks = []
        self.updated_tasks = []

        for task in self.last_tasks:
            task._service = self

        for task in self.attic:
            task._service = self

    def refresh(self, task):
        self._logger.debug('In Executor task service, \'refresh\' operation has no effect.')

        return task


    def new(self, template=None, submit=True, automap=False, **kwargs):
        try:

            # find the template in the template list
            if isinstance(template, str):
                tpl_name = template
                template = next(task for task in self.templates if task.name == tpl_name)

                # If we are here, this mean we did not find the template based on the name
                if template is None:
                    raise ToriiException('Cannot create task, no template \'{0}\''.format(tpl_name))

            # Copy the template in new task object
            if isinstance(template, Task):
                task = Task(template)
                task.cloneOf = template.ref
            else:
                raise ToriiException('Cannot create task, missing template arg')

            # set other fields
            if kwargs:
                for key, value in kwargs.items():
                    if isinstance(value, ToriiObject):
                        setattr(task, key, value.ref)
                    else:
                        setattr(task, key, value)

            # update the dependencies
            self.update_dependencies(task)

            # map the input tasks to the picom
            if automap and not task.get_dependencies():
                for input in task.inputs:
                    picom_input = next((x for x in self.picom_task.inputs if x.name == input.name), None)
                    if picom_input:
                        input.mapping = '{}:{}'.format(self.picom_task.id, input.name)

            # ask for the task submission
            if submit:
                delattr(task, 'status')
            else:
                task.status = 'REGISTERED'

            # init the task condition according to the condition pattern
            self.next_tasks.append(task)

            self._logger.info('add {0} (cloned from template {0})'.format(task, template))

            return task

        except BaseException as e:
            raise ToriiException('Failed to add task from {0}\n{1}'
                                 .format(template, e)).with_traceback(sys.exc_info()[2])


    def update_dependencies(self, task):
        """
        Replace the dependencies of templates with dependencies on the actual tasks
        """

        try:
            # Build the map of task ids matching the template ids with the ids on the actual task
            id_map = {}
            for template in self.templates:
                # ... first we try to find one in the last created task
                ref_task = next((task for task in reversed(self.next_tasks) if template.match(task.cloneOf)), None)

                # ... or the task of the previous step
                if not ref_task:
                    ref_task = next((task for task in reversed(self.last_tasks) if template.match(task.cloneOf)), None)

                # ... or even the tasks from the attic
                if not ref_task:
                    ref_task = next((task for task in reversed(self.attic) if template.match(task.cloneOf)), None)

                if ref_task:
                    id_map[template.id] = ref_task.id

            # we look for the dependencies that must be updated
            for dependency in task.get_dependencies():
                if dependency.taskReference.id in id_map:
                    dependency.taskReference.id = id_map[dependency.taskReference.id]

            # update the mapping
            for input in task.inputs:
                if not hasattr(input, 'mapping'):
                    continue

                for template_id, task_id in id_map.items():
                    input.mapping = input.mapping.replace(template_id, task_id)

        except BaseException as e:
            raise ToriiException('Failed to update dependencies for {0}\n{1}'
                                 .format(task, e)).with_traceback(sys.exc_info()[2])


    def validate(self, task):
        """
        Validate a task

        :param task: the task to be validated
        :return:
        """

        if task.validationScript:
            try:
                # execute the validation script in the context of the picom
                with stdoutIO() as json:
                    exec(task.validationScript)

                # update the task with the outcome of the validation script
                task.from_json(json)

            except BaseException as e:
                raise ToriiException('Failed to validate {0}\n{1}'.format(task, e)).with_traceback(sys.exc_info()[2])

        return task


    def create(self, task):
        self._logger.debug('In Executor task service, \'create\' operation has no effect.')
        return task

    def submit(self, task):
        setattr(task, 'status', 'SUBMITTING')
        return task


    def command(self, task, commandId, commandOption=None):
        raise ToriiException('Command \'{0}\' is not implemented in Executor task service'.format(commandId))

    def kill(self, task):
        return self.command(task, 'kill')

    def pause(self, task):
        return self.command(task, 'pause')

    def resume(self, task):
        return self.command(task, 'resume')

    def update(self, task):
        return self.updated_tasks.append(task)

    def check_status(self, task=None, parent=None, root=None, status=None):
        """
        Check if a task or the children or the descendants are active

        by default, if no argument is provided the service will check the children of the current container

        :param task: the task to check (id or Task)
        :param parent: the parent of the tasks to check (id or Task)
        :param root: the root of the tasks to check (id or Task)
        :param status: the status against which the task(s) is checked
        :return: True or False
        """
        if isinstance(task, Task):
            return task.is_status(status)
        else:
            raise ToriiException('Bad parameter, \'check_status\' requires task being Task')


    def check_active(self, task=None, parent=None, root=None, status=None):
        """
        Check if a task or a group of tasks are active
        """
        return self.check_status(task, parent, root, Task.ACTIVE_STATUS)

    def check_complete(self, task=None, parent=None, root=None, status=None):
        """
        Check if a task or a group of tasks are complete
        """
        return self.check_status(task, parent, root, Task.COMPLETE_STATUS)

    def wait(self, task=None, parent=None, root=None, period=None, timeout=None, status=Task.COMPLETE_STATUS):
        raise ToriiException('\'Wait\' is not implemented in Executor task service')

    def get_records(self, task, max_records=100, increment=True):
        raise ToriiException('\'get_records\' is not implemented in Executor task service')
