#!/usr/bin/env python

'''
'''
import logging

import traceback

from torii.data import Struct, Task, Cluster, ToriiObject

import os
import sys
import json as jsonlib
import atexit


#
# Class Picom
#
class PolicyExecutor():

    def __init__(self, log_level=logging.DEBUG):

        try:

            # Init the logger
            self.__setup_log(log_level)

            # Load picom from disk
            with open('task.json', 'r') as file:
                json = jsonlib.load(file)
                self.task = Task(json, None)

            # Load informations
            self.clusters = self.__load_objects_from_dir('clusters', Cluster)

            # Dump files at exit signal
            self._do_dump = True
            atexit.register(self.__dump)


        except:
            self._logger.info('Exception at init: %s' % str(sys.exc_info()))
            raise

    def __setup_log(self, level=None):
        """
        Performs the setup of the log system
        Thanks to Laurent Pailhes (Sogeti) contribution
        """
        self._logger = logging.getLogger('torii')
        self._logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # and a file handler
        handler = logging.FileHandler('policy.log')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        class Redirect(object):
            """
            File like object that logs everything passed to its write method
            """
            def __init__(self, level, logger):
                self.level = level
                self.logger = logger

            def write(self, data):
                data = data.strip()  # removing blanks and newlines
                if data:
                    self.logger.log(self.level, "'%s'", data)

        # replacing
        redirect_logger = logging.getLogger('torii.redirect')

        class RedirectAdapter(logging.LoggerAdapter):
            """
            Prepends all msg with a text specifying the origin stream of the capture.
            """
            def __init__(self, logger, stream_name):
                super(RedirectAdapter, self).__init__(logger, {'stream': stream_name})

            def process(self, msg, kwargs):
                return '[Captured from %s] %s' % (self.extra['stream'], msg), kwargs


        # storing standards out for further use
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        # replacing the stdout and stderr with our redirections
        sys.stdout = Redirect(logging.INFO, RedirectAdapter(redirect_logger, "stdout"))
        sys.stderr = Redirect(logging.WARN, RedirectAdapter(redirect_logger, "stderr"))

        TB_TPL = "File: '{0}': line {1} in {2}\n-> {3}\nLocals:\n{4}"

        def repr_tb(tb):
            """
            Traceback representation
            """
            filename, linenum, function_name, text = traceback.extract_tb(tb, 1)[0]
            local_vars = ["{0}{1}: {2}".format(' ' * 4, v, repr(tb.tb_frame.f_locals[v])) for v in tb.tb_frame.f_locals]
            return TB_TPL.format(filename, linenum, function_name, text, "\n".join(local_vars))

        def hook(exc_type, exc_value, tb):
            """
            "last chance" hook that loggs in error full stack and variables values
            """
            traces = ["Uncaught exception {0} : {1}\n".format(exc_type, exc_value)]
            while tb is not None:
                traces.append(repr_tb(tb))
                tb = tb.tb_next
            traces.append("\n")

            self._logger.error("\n\n".join(traces))

            # dump also on stderr
            self.stderr.write("".join(traces))
            self._do_dump = False

        # installing the hook
        sys.excepthook = hook

    def __load_objects_from_dir(self, directory, type=ToriiObject):
        try:
            objects = []

            # Load the template tasks, sorted to make sure it is always in the same task order
            obj_files = sorted(os.listdir(directory))
            for filename in obj_files:
                if filename.endswith('.json'):
                    json = jsonlib.load(open(os.path.join(directory, filename), 'r'))
                    objects.append(type(json))

            self._logger.info('Load {0} objects from {1} : {2}'
                              .format(directory, len(objects), ', '.join([object.name for object in objects])))

            return objects

        except:
            self._logger.error('Cannot read objects from ' + directory + ': ' + str(sys.exc_info()))
            raise


    def __dump(self):
        try:
            if self._do_dump:
                sys.stdout = self.stdout
                sys.stderr = self.stderr

                # Dump the task diff on stdout and on disk
                patch = self.task.diff
                jsonlib.dump(patch, open('task.patch', 'w+'), indent=4, sort_keys=True)
                print(jsonlib.dumps(patch, indent=4, sort_keys=True))

                # Insert a blank in the log
                self._logger.info('')

        except:
            self._logger.info('Exception at __dump: %s' % str(sys.exc_info()))
            raise

        return


    def exit(self, signal=0):
        self.__dump()
        os._exit(signal)
        return

    #
    # Public methods
    #

    @property
    def logger(self):
        return self._logger


