import activity
import json
import boto.swf
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import importlib
import os
import starter

"""
ConvertJATS.py activity
"""
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

class activity_ProcessNewS3File(activity.activity):
    def __init__(self, settings, logger, conn=None, token=None, activity_task=None):
        activity.activity.__init__(self, settings, logger, conn, token, activity_task)

        self.name = "ProcessNewS3File"
        self.version = "1"
        self.default_task_heartbeat_timeout = 30
        self.default_task_schedule_to_close_timeout = 60 * 5
        self.default_task_schedule_to_start_timeout = 30
        self.default_task_start_to_close_timeout = 60 * 5
        self.description = "Process a newly arrived S3 file"
        self.logger = logger
        # TODO : better exception handling

    def do_activity(self, data=None):
        """
        Do the work
        """
        if self.logger:
            self.logger.info('data: %s' % json.dumps(data, sort_keys=True, indent=4))

        # TODO : Multiple activities will need this information so abstract this work
        filename = data["data"]["filename"]
        bucketname = data["data"]["bucket"]

        # TODO : more properties, etag, etc. contents only if required though
        # ( and would require download from S3)

        if self.logger:
            self.logger.info("File %s has arrived, deciding workflow" % filename)

        # TODO : in reality this will centralise (for the elife bot) the logic used
        # to determine which workflow will be started to handle this file, based
        # upon file name, type, version and possibly contents
        starter_name = 'starter_ProcessXMLArticle'
        module_name = "starter." + starter_name
        module = importlib.import_module(module_name)
        reload_module(module)
        full_path = "starter." + starter_name + "." + starter_name + "()"
        s = eval(full_path)
        # TODO : etag too?
        s.start(ENV=self.settings.__name__, bucket=bucketname, filename=filename)

        return True

def reload_module(module_name):
    """
    Given an module name,
    attempt to reload the module
    """
    try:
        reload(eval(module_name))
    except:
        pass