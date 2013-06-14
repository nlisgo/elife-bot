import os
# Add parent directory for imports, so activity classes can use elife-api-prototype
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import boto.swf
import settings as settingsLib
import log
import json
import random
import datetime
import os
from optparse import OptionParser

import provider.simpleDB as dblib

"""
Amazon SWF LensArticlePublish starter
"""

def start(ENV = "dev", all = True, last_updated_since = None, docs = None):
	# Specify run environment settings
	settings = settingsLib.get_settings(ENV)
	
	# Log
	identity = "starter_%s" % int(random.random() * 1000)
	logFile = "starter.log"
	#logFile = None
	logger = log.logger(logFile, settings.setLevel, identity)
	
	# Simple connect
	conn = boto.swf.layer1.Layer1(settings.aws_access_key_id, settings.aws_secret_access_key)

	if(all == True):
		# Publish all articles, use SimpleDB as the source
		docs = get_docs_from_SimpleDB(ENV)

	elif(last_updated_since is not None):
		# Publish only articles since the last_modified date, use SimpleDB as the source
		docs = get_docs_from_SimpleDB(ENV, last_updated_since)
	
	if(docs):
		for doc in docs:
			
			document = doc["document"]
			elife_id = doc["elife_id"]
	
			id_string = elife_id
	
			# Start a workflow execution
			workflow_id = "LensArticlePublish_%s" % (id_string)
			workflow_name = "LensArticlePublish"
			workflow_version = "1"
			child_policy = None
			execution_start_to_close_timeout = str(60*60*2)
			input = '{"data": ' + json.dumps(doc) + '}'
	
			try:
				response = conn.start_workflow_execution(settings.domain, workflow_id, workflow_name, workflow_version, settings.default_task_list, child_policy, execution_start_to_close_timeout, input)
	
				logger.info('got response: \n%s' % json.dumps(response, sort_keys=True, indent=4))
				
			except boto.swf.exceptions.SWFWorkflowExecutionAlreadyStartedError:
				# There is already a running workflow with that ID, cannot start another
				message = 'SWFWorkflowExecutionAlreadyStartedError: There is already a running workflow with ID %s' % workflow_id
				print message
				logger.info(message)

def get_docs_from_SimpleDB(ENV = "dev", last_updated_since = None):
	"""
	Get the array of docs from the SimpleDB provider
	"""
	docs = []
	
	# Specify run environment settings
	settings = settingsLib.get_settings(ENV)
	
	db = dblib.SimpleDB(settings)
	db.connect()
	
	if(last_updated_since is not None):
		xml_item_list = db.elife_get_article_S3_file_items(file_data_type = "xml", latest = True, last_updated_since = last_updated_since)
	else:
		# Get all
		xml_item_list = db.elife_get_article_S3_file_items(file_data_type = "xml", latest = True)
		
	for x in xml_item_list:
		tmp = {}
		elife_id = str(x['name']).split("/")[0]
		document = 'https://s3.amazonaws.com/' + x['item_name']
		tmp['elife_id'] = elife_id
		tmp['document'] = document
		docs.append(tmp)
	
	return docs

if __name__ == "__main__":

	# Add options
	parser = OptionParser()
	parser.add_option("-e", "--env", default="dev", action="store", type="string", dest="env", help="set the environment to run, either dev or live")
	(options, args) = parser.parse_args()
	if options.env: 
		ENV = options.env

	start(ENV)