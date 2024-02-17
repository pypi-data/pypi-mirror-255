#!/usr/bin/env python

'''
Picom script:

#!/usr/bin/env python

ex = PicomExecutor()
picom_task = ex.picom_task

sleep = picom_task.get_input('sleep')

if ex.context.step > 3:
    ex.stop()

for i in range(0, 5):
    task = ex.tasks.new(template='test task', name='task ' + str(i), submit=True)
    task.set_input('sleep', sleep)
    task.add_dependency(ex.tasks.last_tasks)


Available methods:
   TODO

'''
import logging

import time

from torii.executor.executor import Executor
from torii.executor.offline_task_service import OfflineTaskService
from torii.data import Struct, Task

import os
import sys
import json as jsonlib
import random


#
# Class Picom
#
class PicomExecutor(Executor):

    def __init__(self, step_dir=None, max_step=None, max_depth=None, max_errors=1, log_level=logging.DEBUG, debug=False):

        Executor.__init__(self, 'picom.log', log_level)

        try:
            if step_dir:
                self.step_dir = step_dir
            else :
                self.step_dir = sys.argv[1]

            # Load picom from disk
            with open('picom.json', 'r') as file:
                json = jsonlib.load(file)
                self.picom_task = Task(json, None)

            with open(os.path.join(self.step_dir, "context.json")) as file:
                json = jsonlib.load(file)
                self.picom_task.context = Struct(json)

            # Initiate he remote debugging if requested
            self.debug = debug or hasattr(self.picom_task.context, 'debug')
            if self.debug:
                try:
                    self._logger.info('Try to connect to the remote debugger')
                    import pydevd
                    pydevd.settrace(suspend=True, stdoutToServer=True, stderrToServer=True)
                except:
                    self._logger.warning('Failed to connect to remote debugger')

            # Step is written in the context by the picom itself
            if not hasattr(self.picom_task.context, 'step'):
                self.picom_task.context.step = 0

            # Set picom limits
            self.set_limits(max_step=max_step, max_depth=max_depth, max_errors=max_errors)

            # Some logs
            self._logger.info('step = %s' % self.step)
            self._logger.info('step_dir = %s' % self.step_dir)
            self._logger.info('curr_pwd = %s' % os.getcwd())
            self._logger.info('context = %s' % self.context)

            # Load informations
            templates = self.load_objects_from_dir('templates', Task)
            attic = self.load_objects_from_dir('attic', Task)
            last_tasks = self.load_objects_from_dir(os.path.join(self.step_dir, 'lastTasks'), Task)

            # Create the offline task service
            self.tasks = OfflineTaskService(self.picom_task, self.context, templates, last_tasks, attic)

            # Check if errors in last tasks
            last_tasks_failed = sum(1 for x in last_tasks if x.status in Task.FAILURE_STATUS)
            if self.context.max_errors > 0 and last_tasks_failed >= self.context.max_errors:
                self.picom_task.status = 'FAILED'
                self.picom_task.message = 'Picom has stopped (step={0}) because {1} tasks failed in last step'\
                    .format(self.step, last_tasks_failed)
                # self.exit()
            else:
                self.picom_task.status = 'RUNNING'
                self.picom_task.message = 'Picom is running (step={0})'.format(self.context.step)


        except:
            self._logger.error('Exception on init: %s' % str(sys.exc_info()))
            raise


    def dump(self):
        try:
            # Dump the next tasks on disk
            if hasattr(self, 'tasks'):
                for i, task in enumerate(self.tasks.next_tasks):

                    # we make a late check of the dependencies to avoid dependencies on templates
                    # in the case the tasks were not created in the proper order
                    self.tasks.update_dependencies(task)

                    task_file = os.path.join(self.step_dir, 'nextTasks', 'task_%03d.json' % i)
                    self._logger.info('dump {1} ({0})'.format(task, task_file))
                    jsonlib.dump(task.to_json(), open(task_file, 'w+'), indent=4, sort_keys=True)

                # Dump the context for the next round
                context_file = os.path.join(self.step_dir, 'context.json')
                self._logger.info('dump {0}'.format(context_file))
                jsonlib.dump(self.context.to_json(), open(context_file, 'w+'), indent=4, sort_keys=True)

                # Dump the status
                status_file = os.path.join(self.step_dir, 'status.json')
                self._logger.info('dump {0}'.format(status_file))
                status = {
                    'status': self.picom_task.status,
                    'message': self.picom_task.message,
                    'stepConditions': self.picom_task.stepConditions
                }

                # Dump the updated tasks
                for i, task in enumerate(self.tasks.updated_tasks):
                    diff = task.diff
                    if diff:
                        task_file = os.path.join(self.step_dir, 'updates', 'task_%03d.json' % i)
                        self._logger.info('dump {1} ({0})'.format(task, task_file))
                        jsonlib.dump(diff, open(task_file, 'w+'), indent=4, sort_keys=True)

                jsonlib.dump(status, open(status_file, 'w+'), indent=4, sort_keys=True)

            # Insert a blank in the log
            self._logger.info('')

        except:
            self._logger.info('Exception on dump: %s' % str(sys.exc_info()))
            raise

        return

    #
    # Public methods
    #

    @property
    def picom_task(self):
        return self.tasks.picom_task

    @property
    def last_tasks(self):
        return self.tasks.last_tasks

    @property
    def next_tasks(self):
        return self.tasks.next_tasks

    @property
    def templates(self):
        return self.tasks.templates

    @property
    def context(self):
        return self.picom_task.context

    @property
    def step(self):
        return self.context.step

    @property
    def step_conditions(self):
        return self.picom_task.step_conditions


    def set_limits(self, max_step=None, max_depth=None, max_retry=None, max_errors=None):
        if max_step is not None:
            self.context.max_step = max_step

        if max_depth is not None:
            self.context.max_depth = max_depth

        if max_retry is not None:
            self.context.max_retry = max_retry

        if max_errors is not None:
            self.context.max_errors = max_errors

        return


    def set_status(self, status='RUNNING', message='Picom is running', delay=None):
        self.picom_task.status = status
        self.picom_task.message = message

        if delay is not None:
            date = int(time.time() + delay)
            self.picom_task.stepConditions = [{'type': 'date', 'date': date}]

        return


    def stop(self, message='Picom is finished'):
        self.set_status(status='FINISHED', message=message)
        self.exit()
        return


    def pause(self, message='Picom is waiting'):
        self.set_status(status='WAITING', message=message)
        self.exit()
        return


    #
    # Test library method
    #
    def testlib(self):

        max_steps = 10
        current_step = self.get_step()
        sleep = self.get_value('sleep')
        my_age = self.get_context('my_previous_age')

        if current_step == 0:
            self.set_context('last_step_status', None)
            self.set_context('last_draw', None)

        if current_step >= max_steps:
            self.stop()

        templates = self.get_templates()
        last_tasks = self.get_last_tasks()

        random.seed()
        nb_task = random.randint(1, 5)
        # nb_task = (current_step + 1) % 3

        links = 'strong'
        if len(last_tasks) + nb_task > 5:
            links = 'weak'

        # Spawn myself for fun ...
        if nb_task == 1:
            self.add_task(self.get_picom(), links=links)
            pass


        for i in range(0, nb_task):
            idx = random.randint(0, len(templates)-1)
            template = templates[idx]
            self.add_task(template, links=links)


        self.set_context('my_previous_age', nb_task)

        if current_step == 1:
            # self.pause()
            pass

        return


