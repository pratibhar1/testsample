#!flask/bin/python
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from flask_restful import reqparse 
from flask_restful import Resource
from flask import jsonify, request
from flask_restful import reqparse
from flask_restful import Resource
from flask import  jsonify, abort, make_response, request, session, g

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from uuid import uuid4

from werkzeug.datastructures import MultiDict

import pymysql
import logging
import logging
import hashlib
import datetime
import smtplib
import kaptan
import os




config = kaptan.Kaptan(handler="json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))
environment = config.get('environment')

class UserRole(Resource):
	def get(self):
		logger=logging.getLogger('UserRole GET Method')
		logger.info("Entered UserRole GET Method")

		try:
			cursor=g.appdb.cursor()
		except:
			logger.error("variables from url", exc_info=True)
		
		query=""" SELECT * FROM user_role;"""
		cursor.execute(query,)
		roles=cursor.fetchall()

		return jsonify({"status":"success","roles":roles})


class UserLogin(Resource):
	def post(self):
		logger=logging.getLogger('UserLogin')
		logger.info("Entered UserLogin POST Method")
           
		try:
			print(request.json)
			user   = request.json
			userid = user["userid"]
			password = user["password"]
			role_id = user["role_id"]
			username = userid if "@ojas-it.com" in userid else userid+"@ojas-it.com"
			cursor = g.appdb.cursor()

		except:
			logger.error("variables from url", exc_info=True)

		#if role_id == 11:
		# query = """SELECT e.employeeId, e.employeeName, e.email, ur.role_name,
		# 			e.gender, e.password FROM employee e INNER JOIN
		# 			user_role ur ON ur.role_id = e.role_id WHERE
		# 			e.role_id = %s AND e.email= %s AND e.flag =2"""

		# a=cursor.execute(query,(role_id,username))
		# print(a)
		# else:
		query = """SELECT e.employeeId, e.employeeName, e.email, ur.role_name, 
		 			e.gender, e.password FROM employee e
					INNER JOIN user_role ur ON ur.role_id = e.role_id 
					WHERE e.email= %s AND e.flag=2"""
		
		a=cursor.execute(query,(username,))
		#print(a)
		result = cursor.fetchall()
		
		if len(result)>0:

			saltciphertext = result[0]['password']
			salt = saltciphertext[0:32]
			cipher_db = saltciphertext[32:]
			cipher_front = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
			print(cipher_front)

			if cipher_front == cipher_db:
				result[0].pop('password')
				token = uuid4().hex
				employeeName = result[0]['employeeName']
				session[employeeName] = token
				code=200
				status = 'user logged in successfully'
				return jsonify({"status":status,"response":result, "token":token})
			else:
				status = 'incorrect password'
				result = userid
				code=204
		else:
			status = 'Username or Password is incorrect'
			result = '%s does not exist'%userid
			code=204

		return jsonify({"status":status,"response":result,"code":code})


class UserLogout(Resource):
	def delete(self,employeeName):
		logger=logging.getLogger('UserLogout DELETE Method')
		logger.info("Entered UserLogout DELETE Method")
		
		cursor = g.appdb.cursor()
		if session.has_key(employeeName):
			token = session[employeeName]
			session.pop(employeeName, None)
			
			
			status = "logged out successfully"
		else:
			status = 'not logged in'

		logger.info("Exiting from UserLogout DELETE method")
		return jsonify({"status":status,"username":employeeName})


class AddUser(Resource):

	def get(self):
		logger = logging.getLogger("Users GET  method")
		logger.info('Entered into Users GET method')
			
		if 'page' and 'count' in request.args:
			try:
				cursor = g.appdb.cursor()
			except:
				logger.error('Database connection or url parameters error', exc_info=True)

			page = int(request.args.get('page'))
			count = int(request.args.get('count'))
			
			start = (page-1)*count
			query1 = """SELECT COUNT(*) AS total_employees FROM employee WHERE flag != 0"""
			cursor.execute(query1)
			result1 = cursor.fetchall()
			
			query = """SELECT e.employeeId, e.employeeName, e.email,DATE_FORMAT
						(e.joiningDate,'%%m/%%d/%%Y') AS joiningDate,
						ur.role_name, e.gender FROM employee e  INNER JOIN
						user_role ur ON ur.role_id = e.role_id WHERE 
					e.flag != 0 LIMIT %s,%s"""

			cursor.execute(query,(start,count))
			result = cursor.fetchall()
			status = 'success'
			statuscode = 200
			total = len(result)
			total_pages = result1[0]['total_employees']/count if len(result)>0 else 0
			total_employees = result1[0]['total_employees'] if len(result)>0 else 0
	
		else:
			status = 'request parameter book and page is missing'
			result = []
			statuscode = 204

		logger.info('Exited from the Users GET Method')
		return jsonify({"status":"success","response":result,
				"current_employees":total, "page":page,"total_pages":total_pages,
				"per_page":count,"total_employees":total_employees})

	def post(self):
		logger = logging.getLogger("Add_user")
		logger.info('Entered into Add_user  post method')
		try:
			cursor = g.appdb.cursor()
		except:
			logger.error("DB connection or url parameters error", exc_info=True)
		
		value = request.json
		employeeId = value["employeeId"]
		employeeName = value["employeeName"]
		email = value["email"]
		role_id = int(value["role_id"])
		gender = value["gender"]
		#joiningDate = value["joiningDate"]
		joiningDate="2010-10-10"
		now = datetime.datetime.now()
		createDate = now.strftime("%Y-%m-%d %H:%M:%S")

		status = ''
		response = ''


		check = """SELECT employeeId, employeeName FROM employee
					WHERE employeeId = %s""" %employeeId
		cursor.execute(check,)
		verify = cursor.fetchall()
		
		if len(verify) == 0:
			try:
				sender = config.get('fromemail')
				#smtppass = base64.decodestring(config.get(b'smtppass'))
				smtppass = config.get('smtppass')
				smtpserver = config.get("smtpserver")
				smtpport = config.get("smtpport")
				receipient = email

				msg = MIMEMultipart('alternative')
				msg['Subject'] = "check the Link"
				msg['From'] = sender
				msg['To'] = receipient

				text = """Dear %s!\n Please complete the registration process.
							\n Here is the link.\nYour Employee id: %s 
							\nhttp://127.0.0.1:5500/index.html#/setpassword/%s/%s
				             Please set your password as early as possible to avoid the url expiration
				             """%(employeeName,employeeId,employeeName,employeeId)
			   
				part = MIMEText(text, 'plain')

				msg.attach(part)
				mail = smtplib.SMTP(smtpserver, smtpport)

				mail.ehlo()
				mail.starttls()

				mail.login(sender, smtppass)
				mail.sendmail(sender, receipient, msg.as_string())
				mail.quit()
				
			except smtplib.SMTPException as e:
				logger.error(str(e))
			
			else:

				query = '''INSERT INTO employee (employeeId, employeeName, email,
								 joiningDate,  role_id, createDate, gender)
							VALUES (%s,%s,%s,%s,%s,%s,%s);'''
				
				cursor.execute(query,(employeeId, employeeName, email,
				joiningDate, role_id, createDate, gender))
				g.appdb.commit()

				status = 'Success'
				response = 'registration mail sent to employee successfully'

		else:
			status = 'Failed'
			response = 'employeeId already signed up'
		
		logger.info('Exited from Add_User post method')
		return jsonify({"status":status, "employeeId":employeeId, "response":response })


	def put(self):
		logger = logging.getLogger("Add_user")
		logger.info('Entered into set password  put method')
		# try:
		cursor = g.appdb.cursor()
		value = request.json
		employeeId = value["employeeId"]
		query = """SELECT * FROM employee WHERE flag = 1 AND employeeId = %s"""
		cursor.execute(query,(employeeId))
		verify = cursor.fetchall()

		if len(verify) == 1:
			if verify[0]['flag'] == 1:

				password = value["password"]
				salt = uuid4().hex
				cipher = hashlib.sha256((password+salt).encode('utf-8')).hexdigest()
				pass_db = salt+cipher
				

				update = """UPDATE employee SET PASSWORD = %s,  flag = 2 WHERE employeeId = %s ;"""
				cursor.execute(update,(pass_db,employeeId))
				g.appdb.commit()
				status = 'password updated successfully'
			elif verify[0]['flag']==2:
				status = 'Oops! link already used and password been set.'
		else:
			status = 'password already been updated'

		return jsonify({"status":status, "employeeId":employeeId})


	def delete(self, employeeId):
		logger = logging.getLogger("DeleteEmployee")
		logger.info('Entered into DeleteEmployee DELETE method')

		try:
			now = datetime.datetime.now()
			cursor = g.appdb.cursor()
			releivingDate = now.strftime("%Y-%m-%d %H:%M:%S")

		except:
			logger.warn("there is some issue with the db")

		book ="""SELECT b.book_name, ba.assignedDate, e.employeeName 
			FROM book_allocation ba INNER JOIN book b ON ba.book_id = b.book_id 
			INNER JOIN employee e ON e.employeeId = ba.employeeId 
			WHERE ba.employeeId = %s AND ba.status= 'granted';"""

		cursor.execute(book,(employeeId))
		books = cursor.fetchall()

		inventory = """SELECT  dd.deviceName, ia.status, i.serial_number, i.assetId, 
		ia.allocation_id, DATE_FORMAT(ia.dateAssigned ,'%%m/%%d/%%Y') 
		AS dateAssigned FROM inventory_allocation ia
		INNER JOIN inventories i ON i.inventory_id = ia.inventoryId 
		JOIN device_details dd ON (i.deviceId = dd.deviceId) 
		WHERE ia.flag = 1 AND  employeeId = %s"""


		cursor.execute(inventory, (employeeId, ))
		inventories = cursor.fetchall()

		if len(books) > 0 or len(inventories)> 0:
			return make_response(jsonify({"inventories": inventories, "books": books, 
				"response":"unable to relieve", "status":"Failure"}), 200)

		else:
			query = """ UPDATE employee SET releivingDate = %s, flag = 0 
						WHERE employeeId = %s;"""
			cursor.execute(query,(releivingDate, employeeId))
			g.appdb.commit()


		logger.info('Exiting from DeleteEmployee DELETE method')
		return make_response(jsonify({"status": "relieved", "response": "employee successfully relieved"}), 200)


class UpdateUser(Resource):
	def put(self):
		logger = logging.getLogger("Add_user")
		logger.info('Entered into set password  put method')
		#employeeId= request.args.get('employeeId')
		#if role_id == 11:
		#try:
		cursor = g.appdb.cursor()
		value = request.json
		employeeName = value["employeeName"]
		email = value["email"]
		gender = value["gender"]
		employeeId=value["employeeId"]
		#joiningDate = value["joiningDate"]
		joiningDate="2010-10-10"
		now = datetime.datetime.now()
		createDate = now.strftime("%Y-%m-%d %H:%M:%S")

		query = """SELECT employeeId, employeeName from employee where employeeId= %s"""
		cursor.execute(query,(employeeId,))
		res=cursor.fetchall()
		if any(res):


			update = """UPDATE employee SET employeeName = %s, email = %s,
							 joiningDate = %s,  gender = %s WHERE employeeId = %s AND flag=2;"""
			cursor.execute(update,( employeeName, email,
			joiningDate, gender, employeeId))
			g.appdb.commit()
		
			status = 'Success'
			response = 'updated employee successfully'

		else:
			status = 'Failed'
			response = 'Unable to updated employee'
		
		logger.info('Exited from Add_User post method')
		return jsonify({"status":status, "employeeId":employeeId, "response":response })


class ForgotPassword(Resource):

	def post(self):
		logger = logging.getLogger("ForgotPassword")
		logger.info('Entered into ForgotPassword post method')
		import sys  

		reload(sys)  
		sys.setdefaultencoding('utf8')
		try:
			cursor = g.appdb.cursor()
			value = request.json

		except:
			logger.error("DB connection or url parameters error", exc_info=True)
		
		email = value["email"]
		role_id = value["role_id"]
		now = datetime.datetime.now()
	
		check = """SELECT employeeId, employeeName, email, joiningDate, role_id
						FROM employee WHERE email=%s AND flag=2 AND role_id=%s"""

		cursor.execute(check,(email,role_id))
		verify = cursor.fetchall()

		if len(verify)>0:

			if email == verify[0]['email']:
				try:
					sender = config.get('fromemail')
					#smtppass = base64.decodestring(config.get('smtppass'))
					smtppass = config.get('smtppass')
					smtpserver = config.get("smtpserver")
					smtpport = config.get("smtpport")
					receipient = email

					msg = MIMEMultipart('alternative')
					msg['Subject'] = "Change password"
					msg['From'] = sender
					msg['To'] = receipient

					text = """
							Dear %s!\n
							Please click the below link to change your password. 
			     			http://127.0.0.1:5500/index.html#/resetpassword/%s

			     			Thanks and Regards,
			     			Inventory Developing Team,
			     			OJAS innovative Techologies,
			     			Hyderabad.
			     			"""%(verify[0]['employeeName'],verify[0]['employeeId'])
				
					part = MIMEText(text, 'plain')

					msg.attach(part)
					mail = smtplib.SMTP(smtpserver, smtpport)

					mail.ehlo()
					mail.starttls()

					mail.login(sender, smtppass)
					mail.sendmail(sender, receipient, msg.as_string())
					
					mail.quit()
					status = "success"
					response = "Link has been mailed"

				except smtplib.SMTPException as e:
					logger.error(str(e))
				
		else:
			status = 'Failed'
			response = 'User does not exsist'
		
		logger.info('Exited from Add_User post method')
		return jsonify({"status":status, "response":response})

	
class ChangePassword(Resource):
	def put(self):
			logger = logging.getLogger("ForgotPassword")
			logger.info('Entered into change password  put method')
			# try:
			cursor = g.appdb.cursor()
			value = request.json
			employeeId = value["employeeId"]
			query = """SELECT * FROM employee WHERE flag = 2 AND employeeId = %s"""
			cursor.execute(query,(employeeId,))
			verify = cursor.fetchall()

			if len(verify) == 1:
				if verify[0]['flag'] == 2:

					password = value["password"]
					salt = uuid4().hex
					cipher = hashlib.sha256(password+salt).hexdigest()
					pass_db = salt+cipher
					

					update = """UPDATE employee SET PASSWORD = %s WHERE employeeId = %s ;"""
					cursor.execute(update,(pass_db,employeeId))
					g.appdb.commit()
					status = 'password updated successfully'
				elif verify[0]['flag']==2:
					status = 'Oops! link already used and password been Changed.'
			else:
				status = 'password changed successfully'

			return jsonify({"status" : status, "employeeId" : employeeId})


class ResetPassword(Resource):
	def put(self):
			logger = logging.getLogger("ForgotPassword")
			logger.info('Entered into change password  put method')
			try:
				cursor = g.appdb.cursor()
				value = request.json
				employeeId = value["employeeId"]
				query = """SELECT * FROM employee WHERE flag = 2 AND employeeId = %s"""
				cursor.execute(query,(employeeId,))
				verify = cursor.fetchall()

			except:
				logger.error("variables from url", exc_info=True)

			if len(verify) == 1:
				password = value["password"]
				salt = uuid4().hex
				cipher = hashlib.sha256(password+salt).hexdigest()
				pass_db = salt+cipher
				

				update = """UPDATE employee SET PASSWORD = %s WHERE employeeId = %s ;"""
				cursor.execute(update,(pass_db,employeeId))
				g.appdb.commit()
				status = 'password updated successfully'

			else:
				status = 'employeeId is incorrect'

			return jsonify({"status" : status, "employeeId" : employeeId})


class ProfilePicture(Resource):
	def put(self):
		logger = logging.getLogger("ProfilePicture Upload")
		logger.info('Entered into ProfilePicture put method')

		try:
			cursor = g.appdb.cursor()
			employeeId = int(request.form['employeeId'])
			image = request.files['picture']
			mime = image.filename
			bencode =base64.b64encode(image.read())
		
		except:
			logger.error("variables from url", exc_info=True)

		
		query = """UPDATE employee SET profile_pic = %s WHERE employeeId = %s ;"""
		cursor.execute(query,(bencode,employeeId))
		g.appdb.commit()

		logger.info('Exited from ProfilePicture put method')
		return jsonify({"status" : "success", 'employeeId' : employeeId,
						 "response" : "profile_picture has been set successfully"})

	
	def get(self):
		logger = logging.getLogger("ProfilePicture Upload")
		logger.info('Entered into ProfilePicture get method')

		if 'employeeId' in request.args:
			try:
				cursor = g.appdb.cursor()			
				employeeId = request.args.get('employeeId')
		
			except:
				logger.error("variables from url", exc_info=True)

			
			query = """SELECT profile_pic FROM employee WHERE employeeId = %s AND flag =2"""
			
			cursor.execute(query,(employeeId))
			profile_pic = cursor.fetchone()
			status = 'success'
			statuscode = 200

		else:
			status = 'request parameters profile_pic is missing'
			profile_pic = []
			statuscode = 204


		logger.info('Exited from ProfilePicture put method')
		return jsonify({"status" : "success", 'profile_pic' : profile_pic})
