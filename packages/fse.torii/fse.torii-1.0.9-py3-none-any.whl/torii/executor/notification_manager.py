#!/usr/bin/env python

import os
import json
import time

import requests
from requests import RequestException


class NotificationManager:

    def __init__(self, logger, context):
        pwd = os.getcwd()
        self.runlog = os.getenv('HPCG_RUN_LOG', pwd)

        try:
            import pydevd
            pydevd.settrace('localhost', port=12346, stdoutToServer=True, stderrToServer=True)
        except:
            pass

        self.logger = logger
        self.context = context

        # Error count
        self.error = 0

        # Retrieve path of notification log directory and file
        self.notif_log_dir = os.path.join(self.runlog, 'executor', self.context['jobId'])
        self.notif_log_filepath = os.path.join(self.runlog, 'executor', self.context['jobId'], 'notifications.json')

        # Create notification directory, if it does not exist
        if not os.path.isdir(self.notif_log_dir):
            os.mkdir(self.notif_log_dir)

    def send_event(self, operation, payload, first_attempt=True):
        """
        Send notification request to the batch relay.
        :param notification: Notification should be in JSON format.
        """
        self.logger.info('Sending event "{}" to the relay {} : {}'
                         .format(operation, self.context['relay_url'], json.dumps(payload, indent=4)))

        request = {
            'type': 'JOB_EVENT',
            'context': {
                'operation': operation,
                'host': self.context['host'],
                'task': self.context['task'],
                'jobId': self.context['jobId'],
                'date_begin': time.time()
            },
            'payload': payload
        }

        flush_logs = True
        try:
            self.send_event_request(request)

        except Exception as e:
            self.logger.exception('Failed to send the request to the relay : {}'.format(e))

            self.write_notification_log(request)
            flush_logs = False
            self.error += 1

        if flush_logs:
            self.send_notification_log()

    def send_event_request(self, request):
        """
        Send notification request to the batch relay.
        :param notification: Notification should be in JSON format.
        """

        r = requests.put(url=self.context['relay_url'], json=request)
        event = r.json()

        duration = time.time() - event['context']['date_begin']

        if 'status' in event and event['status'] == 'SUCCESS':
            self.logger.info('Request "{}" has succeed (duration = {})'
                             .format(event['context']['operation'], duration))
        else:
            self.logger.warning('Request "{}" has failed (status = {}, duration = {})'
                             .format(event['context']['operation'], event['status'], duration))

    def write_notification_log(self, notification):
        """
        Write notification in the notification log.
        :param notification: Notification should be in JSON format.
        """
        try:
            a = json.dumps(notification)
            with open(self.notif_log_filepath, 'a+') as f:
                f.write(a)
                f.write('\n')

        except Exception as e:
            self.logger.exception('Failed to log the notification : {}'.format(e))

    def send_notification_log(self):
        """
        Send all the notifications added in the notification log file to the batch relay.
        """
        try:
            if os.path.isfile(self.notif_log_filepath):
                lines = tuple(open(self.notif_log_filepath, 'r'))
                os.remove(self.notif_log_filepath)
                for line in lines:
                    self.send_event_request(json.loads(line.rstrip()))
        except Exception as e:
            self.logger.exception('Failed to flush the notification logs : {}'.format(e))
