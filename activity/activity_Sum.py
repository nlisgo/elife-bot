import boto.swf
import json
import random
import datetime

import activity

"""
Sum activity
"""

class activity_Sum(activity.activity):
	
	def do_activity(self, data = None):
		"""
		Sum activity, do the work, in this case
		sum the data and return true
		"""
		self.logger.info('data: %s' % json.dumps(data, sort_keys=True, indent=4))
		self.result = sum(data["data"])
		return True