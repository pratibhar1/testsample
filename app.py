#!flask/bin/python
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 11:39:43 2018

@author: OJAS innovative technologies
"""
from flask import Flask, jsonify, abort, make_response, request, session, g, render_template
from flask_cors import CORS
from flask_restful import reqparse
from flask_restful import Resource, Api
import sys
import atexit
#from apscheduler.scheduler import Scheduler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pandas as pd
import datetime
from functools import reduce
import kaptan
import os
import time
import logging
import pymysql
import json
import logging.config
from uuid import uuid4
import sys
import datetime
from functools import reduce
import logging
logging.basicConfig()

from routes.book import Book, Department, BookList, BookAllocate, Readers, \
						BookAllocateList, AvailableBooks, RequestBook, \
						AssignBooks, MyBooks

from routes.inventory import Inventories, InventoryList, MyInventory, \
							 	VendorAddress, DeviceDetails, ProductBrand, \
							 	TotalInventoryDetails, AllotedDetails, AvailableDetails,DeleteInventory

from routes.allocate import InventoryAllocation, AllocationList, DeviceList, \
							RequestForReplace, DeleteAllocation,  RequestIn

from routes.auth import UserRole, AddUser, UserLogin, UserLogout, \
						ForgotPassword, ChangePassword, ResetPassword, \
						ProfilePicture,UpdateUser

app = Flask(__name__)
key = uuid4().hex
app.secret_key = key

config = kaptan.Kaptan(handler = "json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))
environment = config.get('environment')

api = Api(app)
CORS(app)
logger = logging.getLogger(__name__)

   
def connect_db():
	"""Connects to the specific database."""
	
	try:
		db = pymysql.connect(host = config.get('dbhost'),  # your host, usually localhost
							 user = config.get("dbuser"),  # your username
						     passwd = config.get("dbpass"),  # your password
						 	 db = config.get("dbname"), 
						 	 cursorclass = pymysql.cursors.DictCursor,
						 	 sql_mode = "STRICT_TRANS_TABLES")  # name of the data base
		return db
	
	except:
		logger.error('Failed to Connect to the database', exc_info=True)
		sys.exit("not able to connect to database")


def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'appdb'):
		g.appdb = connect_db()
	return g.appdb


@app.before_request
def before_request():
	g.appdb = get_db()
	

@app.teardown_request
def teardown_request(exception):
	
	if hasattr(g, 'appdb'):
		g.appdb.close()


@app.before_first_request
def setup_logging(default_path = 'logconf.json', default_level = logging.INFO, 
					env_key = 'LOG_CFG_PATH'):
	"""Setup logging configuration"""
	
	path = default_path
	value = os.getenv(env_key, None)
	if value:
		path = value
	if os.path.exists(path):
		with open(path, 'rt') as f:
			config = json.load(f)
		logging.config.dictConfig(config)
	else:
		logging.basicConfig(level = default_level)


@app.route('/')
def hello():
	
	return '<h1>Welcome to Inventory Application</h1>'

#: URLs
api.add_resource(Department, '/department', endpoint = 'Department')
api.add_resource(Book, '/book', endpoint = 'Book')
api.add_resource(BookList, '/booklist', endpoint = 'BookList')
api.add_resource(BookAllocate, '/bookallocate', endpoint = 'BookAllocate')
api.add_resource(BookAllocateList, '/bookallocatelist', endpoint = 'BookAllocateList')
api.add_resource(AvailableBooks, '/availablebooks', endpoint = 'AvailableBooks')
api.add_resource(RequestBook, '/requestbook', endpoint = 'RequestBook')
api.add_resource(AssignBooks, '/assignbooks', endpoint = 'AssignBooks')
api.add_resource(MyBooks, '/mybooks', endpoint = 'MyBooks')
api.add_resource(Readers, '/readers', endpoint = 'Readers')

#api.add_resource(Request, '/request', endpoint = 'Request')

api.add_resource(RequestIn, '/requesting', endpoint = 'RequestIn')


api.add_resource(Inventories, '/inventories', endpoint = 'Inventories')
api.add_resource(UpdateUser, '/user',endpoint='UpdateUser')
api.add_resource(Inventories, '/deleteinventory/<int:inventory_id>', 
					methods = ['DELETE'])
api.add_resource(DeleteInventory, '/delete/<int:deviceId>', 
					methods = ['DELETE'])
api.add_resource(InventoryList, '/inventory', endpoint = 'InventoryList')
api.add_resource(DeviceList, '/devicelist', endpoint = 'DeviceList')
api.add_resource(MyInventory, '/myinventory', endpoint = 'MyInventory')
api.add_resource(VendorAddress, '/vendoraddress', endpoint = 'VendorAddress')
api.add_resource(DeviceDetails, '/devicedetails', endpoint = 'DeviceDetails')
api.add_resource(ProductBrand, '/productbrand', endpoint = 'ProductBrand')
api.add_resource(TotalInventoryDetails, '/inventorydetails', endpoint = 'TotalInventoryDetails')
api.add_resource(AllotedDetails, '/alloted', endpoint = 'AllotedDetails')
api.add_resource(AvailableDetails, '/available', endpoint = 'AvailableDetails')


api.add_resource(InventoryAllocation, '/allocate', endpoint = 'InventoryAllocation')
api.add_resource(DeleteAllocation, '/deleteallocation', endpoint = 'DeleteAllocation')
api.add_resource(AllocationList, '/allocatelist', endpoint = 'AllocationList')
api.add_resource(RequestForReplace, '/replace', endpoint = 'RequestForReplace')


api.add_resource(UserRole, '/roles', endpoint = 'Userrole')
api.add_resource(AddUser, '/adduser', endpoint = 'AddUser')
api.add_resource(ProfilePicture, '/profilepicture', methods = ['PUT','GET'])
api.add_resource(AddUser, '/relieveemployee/<int:employeeId>', methods = ['DELETE'])
api.add_resource(UserLogin, '/login', endpoint = 'UserLogin')
api.add_resource(UserLogout, '/logout/<string:employeeName>', methods = ['DELETE'])
api.add_resource(ForgotPassword, '/forgotpassword', endpoint = 'ForgotPassword')
api.add_resource(ChangePassword, '/changepassword', endpoint = 'ChangePassword')
api.add_resource(ResetPassword, '/resetpassword', endpoint = 'ResetPassword')



# cron = Scheduler(daemon=True)
#
# # Explicitly kick off the background thread
# cron.start()
#
# @cron.interval_schedule(seconds=10)
# def job_function():
# 	with app.app_context():
# 		sender = config.get('fromemail')
# 		expiry = config.get('expiry')
# 		#now = datetime.now()
# 		#today = now.strftime("%d-%m-%Y")
# 		#start_date = datetime.strptime(today, '%d-%m-%Y')
# 		#to_date = start_date + timedelta(days=expiry)
# 		#end_date = to_date.strftime('%d-%m-%Y')
# 		smtppass = config.get('smtppass')
# 		smtpserver = config.get("smtpserver")
# 		smtpport = config.get("smtpport")
# 		receipient = "ahmad.baig@ojas-it.com"
# 		msg = MIMEMultipart('alternative')
# 		msg['Subject'] = "Inventories next expiry dates"
# 		msg['From'] = sender
# 		msg['To'] = receipient
# 		db = connect_db()
# 		cursor = db.cursor()
# 		query = 'SELECT expiry_date FROM inventories WHERE expiry_date = DATE_ADD(CURDATE(), INTERVAL %s DAY)'%(expiry)
# 		cursor.execute(query,)
# 		dates = cursor.fetchall()
# 		d = []
# 		for i in dates:
# 			d.append(list(i.values()))
# 		s = reduce(lambda x, y: x+y, d)
# 		m = []
# 		for i in s:
# 			str(i)
# 			m.append(str(i))
# 		start_date = [datetime.strptime(x, '%Y-%m-%d').strftime('%d-%m-%Y') for x in m]
# 		# F= []
# 		# for i in dates:
# 		# 	k=list(i.values())
# 		# 	F.append(k)
# 		# for h in F:
# 		# 	start_date = datetime.strptime(str(h), '%m/%d/%Y').strftime('%d-%m-%Y')
# 		# #timestamp = pd.to_datetime(dates.values())
# 		# #timestamp = timestamp.strftime("%Y%m%d")
#         f=[['assetId', 'assetId'], ['deviceName', 'deviceName'], ['brandName', 'brandName'], ['27-01-2019', '27-01-2019', '27-01-2019', '27-01-2019', '27-01-2019', '27-01-2019', '27-01-2019']]
# 	    kk = render_template('index.html', value=f)
# 	    text = """Inventories Upcoming Expiry Dates is %s"""%(kk,)
# 		part = MIMEText(text, 'plain');
# 		part2 = MIMEText(kk,'html')
# 		msg.attach(part2)
# 		mail = smtplib.SMTP(smtpserver, smtpport)
#
# 		mail.ehlo()
# 		mail.starttls()
#
# 		mail.login(sender, smtppass)
# 		mail.sendmail(sender, receipient, msg.as_string())
# 		mail.quit()
#
#
# # Shutdown your cron thread if the web process is stopped
# atexit.register(lambda: cron.shutdown(wait=False))



port=5000
if __name__ == '__main__':
	
	app.run(host = config.get("host"), debug = config.get("debug"), 
			threaded = True, port = port)
