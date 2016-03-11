from pyspark import SparkContext, SparkConf
import json
import time
import random
import sys, traceback
from datetime import date, timedelta
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr

AWS_ACCESS_KEY_ID = "your access key id"
AWS_SECRET_ACCESS_KEY = "your secret access key"
AWS_DYNAMODB_REGION = "your dynamdb region"

def check_none(x):
	if x.get("PhoneNumber") and x.get("Action"):
		return True
	else:
		return False

def aggregator(list):
        action = {}
        for e in list:
		action[str(e)] = action[str(e)]+1 if action.get(str(e)) else 1
        return action

def do_update_item(table, key, attr_updates):
	try:
		response = table.update_item(
			Key = key,
			AttributeUpdates = attr_updates,
			ReturnConsumedCapacity = 'INDEXES'
		)
		return response
	except Exception as e:
		traceback.print_exc()	
		return None

def save_to_dynamodb(iterator):
	session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
			  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
			  region_name=AWS_DYNAMODB_REGION)
	dynamodb = session.resource('dynamodb')
	report_usage_monthly_table = dynamodb.Table('CMS_CallBlock_ReportUsageMonthly')
	for e in iterator:
		time_to_wait = 2
		key = {
			'PhoneNumber': e[0],
			'Date': the_process_date[:7]
		}
		attr_updates = {
			'Action_0': {
				'Value': 0 if not e[1].get("0") else e[1]["0"],
				'Action': 'ADD'
			},
			'Action_1': {
				'Value': 0 if not e[1].get("1") else e[1]["1"],
				'Action': 'ADD'
			},
			'Action_2': {
				'Value': 0 if not e[1].get("2") else e[1]["2"],
				'Action': 'ADD'
			},
			'AccumulateNums': {
				'Value': 1,
				'Action': 'ADD'
			}
		}
		response = do_update_item(report_usage_monthly_table, key, attr_updates)
		retry = True if response == None or response['ResponseMetadata']['HTTPStatusCode'] != 200 else False
		if retry:
			print response
		while retry:
			time_to_wait = time_to_wait * 2
			time.sleep(time_to_wait)
			response = do_update_item(report_usage_monthly_table, key, attr_updates)
			retry = True if response == None or response['ResponseMetadata']['HTTPStatusCode'] != 200 else False
			retry = False if time_to_wait > 1024 else retry

# spark
the_process_date = sys.argv[1]
conf = SparkConf().setAppName("Report Usage Count Daily").set("spark.storage.memoryFraction", "0.5").set("spark.core.connection.ack.wait.timeout", "5000").set("spark.akka.heartbeat.interval", "100").set("spark.akka.frameSize", "200").set("spark.driver.maxResultSize", "4g")
sc = SparkContext(conf=conf)
rank = sc.parallelize([])
try:
	this_line = sc.textFile("s3n://"+AWS_ACCESS_KEY_ID+":"+AWS_SECRET_ACCESS_KEY+"@cms-callblock-aps1/callblock/report_usage/*"+the_process_date+"*.txt")
	#this_line = sc.textFile("s3n://"+AWS_ACCESS_KEY_ID+":"+AWS_SECRET_ACCESS_KEY+"@cms-callblock-aps1/callblock/report_usage/ls.s3.ip-10-5-1-167.ap-southeast-1.compute.internal.2015-11-04T01.52.part1.txt")
	this_line_json = this_line.map(lambda x: json.loads(x))
	this_line_reduced = this_line_json.filter(lambda x: check_none(x)).map(lambda x: (x["PhoneNumber"], [x["Action"]])).reduceByKey(lambda x,y:x+y)
	#rank = rank.union(this_line_reduced)
	rank = this_line_reduced
except Exception as e:
	traceback.print_exc()

rank = rank.map(lambda x: (x[0], aggregator(x[1])))
rank.foreachPartition(save_to_dynamodb)
#rank = rank.collect()
#save_to_dynamodb(rank)

'''
{'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': 'MRTLAL8PCEP083FNAT72OF40OJVV4KQNSO5AEMVJF66Q9ASUAAJG'}, 'ConsumedCapacity': {'CapacityUnits': 2.0, 'GlobalSec
ondaryIndexes': {u'Date-index': {'CapacityUnits': 1.0}}, 'TableName': u'CMS_CallBlock_ReportUsageMonthly', 'Table': {'CapacityUnits': 1.0}}}
'''

'''
report_usage_monthly_table.update_item(
		Key = {
			'PhoneNumber': '123',
			'Date': the_process_date[:7]
		},
                AttributeUpdates = {
			'Action_0': {
				'Value': 1,
				'Action': 'ADD'
			},
			'Action_1': {
				'Value': 2,
				'Action': 'ADD'
			},
			'Action_2': {
				'Value': 0,
				'Action': 'ADD'
			}
		}
        )
'''
