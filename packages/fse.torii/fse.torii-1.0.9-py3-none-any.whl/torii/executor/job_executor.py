#!/usr/bin/env python

import json
import logging
import os
import random
import socket
from threading import Thread
from multiprocessing import Process
import time
import bson

import requests
from flask import Flask, request, make_response, jsonify

from torii import Task, BusinessObject
from torii.data import json_to_struct
from .notification_manager import NotificationManager


class JobExecutor(object):
    """
    Client for the batch_relay mediator
    Used by the utilities or the jobs to send task notifications back to the cluster agent
    ex: outputs, message, runinfos, monitoring records...
    """

    def __init__(self, logger=None):
        """
        Constructor
        """
        pwd = os.getcwd()
        self.runlog = os.getenv('HPCG_RUN_LOG', pwd)
        self.log = os.getenv('HPCG_LOGS')
        self.job_id = os.getenv('HPCG_BATCH_ID_SHORT', 'unknown')

        # init the job executor dir
        self.dir = os.path.join(self.runlog, 'executor', str(self.job_id))
        os.makedirs(self.dir, exist_ok=True)

        # init the logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('JobExecutor')
            hdlr = logging.FileHandler(os.path.join(self.dir, 'executor.log'))
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.INFO)

        # read the recorder context or initialize it
        self.context_file = os.path.join(self.dir, 'context')
        if os.path.isfile(self.context_file):
            self.logger.info('Loading context from ' + self.context_file)
            with open(self.context_file) as f:
                self.context = json.load(f)
        else:
            self.init_context()

        # Error count
        self.notif_manager = NotificationManager(self.logger, self.context)
        self.error = 0


    def parse_runlog(self):

        # parse the task object
        with open(self.runlog + '/task.json') as f:
            self.task = Task(json=json.load(f))

        # get the bo inputs
        for input in self.task.inputs:
            if input.type == 'bos' and os.path.isfile(os.path.join(self.runlog, 'inputs', input.name)):
                try:
                    with open(os.path.join(self.runlog, 'inputs', input.name)) as f:
                        jsons = json_to_struct(json.load(f))

                    input.value = [BusinessObject(json=x) for x in jsons]
                except Exception as e:
                    input.value = None
                    self.logger.warn("Failed to parse input {} from {}"
                                     .format(input.name, os.path.join(self.runlog, 'inputs', input.name)))

            if input.type == 'bo' and os.path.isfile(os.path.join(self.runlog, 'inputs', input.name)):
                try:
                    with open(os.path.join(self.runlog, 'inputs', input.name)) as f:
                        input.value = BusinessObject(json=json.load(f))
                except Exception as e:
                    input.value = None
                    self.logger.warn("Failed to parse input {} from {}"
                                     .format(input.name, os.path.join(self.runlog, 'inputs', input.name)))

    def start_lowla_server(self, callback, callback_kwargs={}, blocking=False):
        self.lowla_app = Flask(__name__)
        self.lowla_app.debug = False
        self.lowla_app.use_reloader = False
        self.lowla_callback = callback
        self.lowla_callback_kargs = callback_kargs
        self.lowla_app.route('/lowla/', methods=['POST'])(self.run_lowla)
        self.lowla_app.route('/lowla', methods=['POST', 'GET'])(self.run_lowla)
        self.lowla_app.route('/', methods=['POST', 'GET'])(self.run_lowla)

        host = socket.gethostbyname(socket.gethostname())
        port = random.randint(8000, 9000)
        url = 'http://{}:{}/lowla/'.format(host, port)

        if blocking:
            # TODO replace with send_context
            self.send_runinfo({'lowlaUrl': url})
            self.lowla_app.run(host='0.0.0.0', port=port, threaded=True)
        else:
            # self.lowla_thread = Thread(target=self.lowla_app.run,
            #                           kwargs={'host': host, 'port': port, 'threaded':True})
            self.flask_subprocess = Process(target=self.lowla_app.run,
                                            kwargs={'host': host, 'port': port, 'threaded':True})

            self.flask_subprocess.start()
            # TODO replace with send_context
            self.send_runinfo({'lowlaUrl': url})


    def stop_lowla_server(self):
        if hasattr(self, 'lowla_tread'):
            self.flask_subprocess.terminate()


    def run_lowla(self):
        """
        Run a lowla command
        :return:
        """

        try:
            task = Task(json=request.get_json())

            if self.lowla_callback_kargs:
                self.lowla_callback(task=task, executor=self, **self.lowla_callback_kargs)
            else:
                self.lowla_callback(task=task, executor=self)

            return make_response(jsonify(task.to_json()), 200)
        except Exception as e:
            return make_response('Failed to treat lowla : {}'.format(e), 500)


    def init_context(self):
        """
        Initialize the context of the client (connection information, current step...)
        :return:
        """
        # init the context file
        self.context = {
            'step': 0,
            'relay_url': os.getenv('HPCG_RELAY_URL', 'http://localhost:5351'),
            'host': socket.gethostname(),
            'jobId': self.job_id
        }

        with open(self.runlog + '/task.json') as f:
            task = json.load(f)
            self.context['task'] = {
                'name': task['name'],
                'id': task['_id']['$oid'],
                'num': task['num'],
            }
            self.context['cluster'] = task['context']['cluster']

        with open(self.context_file, 'w+') as f:
            json.dump(self.context, f, indent=4)

        self.logger.info('Initialize new context\n{}'.format(json.dumps(self.context, indent=4)))

        return

    def send_record(self, record):
        """
        Send a monitoring record to the CA through the batch relay
        :param record:
        :return:
        """
        record = {
            'time': int(time.time()),
            'step': self.context['step'],
            'data': record
        }

        with open(os.path.join(self.dir, 'records.json'), 'w+') as f:
            json.dump(record, f, indent=4)

        self.notif_manager.send_event(operation='record', payload=record)

        self.context['step'] = self.context['step'] + 1
        with open(self.context_file, 'w+') as f:
            json.dump(self.context, f, indent=4)
        return

    def send_runinfo(self, runinfo):
        """
        Send new run information to the CA through the batch relay
        :param runinfo:
        :return:
        """
        self.notif_manager.send_event(operation='runinfo', payload=runinfo)
        return

    def send_message(self, message):
        """
        Send a task message to the CA through the batch relay

        :param message:
        :return:
        """
        self.notif_manager.send_event(operation='message', payload={'message': message})

        return

    def send_output(self, output):
        """
        Send a task output or a patch to the CA through the batch relay

        :param output:
        :return:
        """

        if 'bo_class' in output and output['bo_class'] is not None:
            if output['type'] == 'bo':
                bo = output['value']

                if '_id' not in bo:
                    bo['_id'] = str(bson.objectid.ObjectId())

                self.send_bos(output['bo_class'], output['value'])
                bo_output = {
                    'name': output['name'],
                    'type': 'bo',
                    'objectClass': output['bo_class'],
                    'objectName': bo['name'],
                    'value': bo['_id']
                }

                if 'name' in output:
                    bo_output['name'] = output['name']
                    bo_output['objectName'] = output['name']
                output = bo_output
            elif output['type'] == 'bos':
                self.send_bos(output['bo_class'], output['value'])
                bos_output = {
                    'type': 'bos',
                    'objectClass': output['bo_class'],
                    'value': {
                        'filters': [{
                            'operator': 'eq',
                            'property': 'createdBy',
                            'type': output['type'],
                            'filterType': 'string',
                            'value': self.context['task']['id']
                        }]
                    }
                }

                if 'name' in output:
                    bos_output['name'] = output['name']
                output = bos_output

        self.notif_manager.send_event(operation='output', payload=output)
        return

    def send_transfer(self, transfer):
        """
        Send a new transfer or a patch to the CA through the batch relay

        :param transfer:
        :return:
        """
        self.notif_manager.send_event(operation='transfer', payload=transfer)
        return

    def send_log(self, log):
        """
        Send a new log concerning the current task

        :param transfer:
        :return:
        """
        self.notif_manager.send_event(operation='log', payload=log)
        return

    def send_detail(self, detail):
        """
        Send job details concerning the current task

        :param detail:
        :return:
        """
        self.notif_manager.send_event(operation='detail', payload=detail)
        return

    def send_bos(self, bo_class, bos, update=False):
        """
        Send business objects to the CA through the batch relay
        :param bo_class: the class of the bo to send
        :param bos: the business objects to be inserted in database
        :param update: tell whether the businesso bjects have to be updated ot inserted
        :return:
        """

        if isinstance(bos, list):
            for bo in bos:
                bo['createdBy'] = {
                    'id': self.context['task']['id'],
                    'name': self.context['task']['name']
                }
        else:
            bos['createdBy'] = {
                'id': self.context['task']['id'],
                'name': self.context['task']['name']
            }

        bo_json = {
            'update': update,
            'bo_class': bo_class,
            'bos': bos
        }

        self.notif_manager.send_event(operation='bos', payload=bo_json)
        return

