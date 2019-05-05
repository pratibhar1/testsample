import os
from app import app
from routes import book
import unittest
TEST_DB='inventory.db'
import json
import xlrd
import more_itertools
from collections import OrderedDict
import simplejson as json

class FlaskTestCase(unittest.TestCase):






	
	def test_post_requestbook(self):
		
		tester = app.test_client()
		# Open the workbook and select the first worksheet
		wb = xlrd.open_workbook('testbook.xlsx')
		sh = wb.sheet_by_index(0)
		# List to hold dictionaries
		cars_list = []
		# Iterate through each row in worksheet and fetch values into dict
		for rownum in range(1, sh.nrows):
		    cars = OrderedDict()
		    row_values = sh.row_values(rownum)
		    cars['employeeId'] = row_values[0]
		    cars['book_id'] = row_values[1]
		    cars['status'] = row_values[2]
		    #cars['miles'] = row_values[3]
		    cars_list.append(cars)
		# Serialize the list of dicts to JSON
		j = json.dumps(cars_list)
		# Write to file
		with open('datab11.json', 'w') as f:
		    f.write(j)
		with open("datab11.json") as my_data_file:
		    my_data = json.load(my_data_file)
		print(my_data)
		for i in my_data:
			j=i

		#     print(i)


		# for i in data:
		#try:
			response = tester.post('http://localhost:5000/requestbook',json=j,content_type='application/json')
			
			print(response.status_code)
			#print(i['employeeId'])
			assert response.status_code==201
			# if not j['book_id']
			# 	print('the book_id is not exist')
			# elif not j['employeeId']:
			# 	print('the employeeId is not exist')
			# elif not j['book_id']:
			# 	print('the book_id is not exist')

			print('this id is successfully executeed',j)
		#except:
			# if not j['book_id']:
			# 	print('the book_id is not exist')
			# if not j['employeeId']:
			print('the employeeId is not exist')
			#if not j['book_id']:
			# 	print('the book_id is not exist')
			print('there is some problem with id',j['book_id'],j['employeeId'])
	def test_get_book(self):
		
		tester = app.test_client()
		# data= [
		# 	{
		# "employeeId":509,
		# 			"book_id":1,
		# 			"status":"11"
		# },
		# {
		# 	"employeeId":714,
		# 			"book_id":2
		# },
		# {
		# 	"employeeId":680,
		# 			"book_id":2
		# }

		# ]
		# print(data)
		#Open the workbook and select the first worksheet
		wb = xlrd.open_workbook('testbook1.xlsx')
		sh = wb.sheet_by_index(0)
		# List to hold dictionaries
		cars_list = []
		# Iterate through each row in worksheet and fetch values into dict
		for rownum in range(1, sh.nrows):
		    cars = OrderedDict()
		    row_values = sh.row_values(rownum)
		    print(row_values)
		    #cars['employeeId'] = row_values[0]
		    cars['book_id'] = row_values[0]
		    # cars['count'] = row_values[0]
		    # cars['page'] = row_values[1]
		    cars_list.append(cars)
		# Serialize the list of dicts to JSON
		j = json.dumps(cars_list)
		# Write to file
		with open('data1.json', 'w') as f:
		    f.write(j)
		with open("data1.json") as my_data_file:
		    my_data = json.load(my_data_file)
		print(my_data)
		for i in my_data:
			j=i
			print(j)


		# for i in data:
		#try:
			response = tester.get('http://localhost:5000/bookgk',query_string={'book_id':j['book_id']},content_type='application/json')
			print(response)
			print(response.status_code)
			#print(i['employeeId'])
			assert response.status_code==200
			# if not j['book_id']:
			# 	print('the book_id is not exist')
			# elif not j['employeeId']:
			# 	print('the employeeId is not exist')
			# elif not j['book_id']:
			# 	print('the book_id is not exist')

		# 	print('this id is successfully executeed',j)
		# #except:
		# 	if not j['book_id']:
		# 		print('the book_id is not exist')
		# 	if not j['employeeId']:
		# 		print('the employeeId is not exist')
		# 	if not j['book_id']:
		# 		print('the book_id is not exist')
		# 	print('there is some problem with id',j)





if __name__=='__main__':
	unittest.main()








# # from flask import Flask 

# # app=Flask(__name__)
# # @app.route("/<string:name>/<int:id>")

# # def hi(name,id):
# # 	return 'good morning %s,%d'%(name,id)
# # if __name__ == '__main__':
# # 	app.run(debug=True,port=5000) 



# # from flask import Flask,request
# # from flask_restful import Resource,Api
# # app=Flask(__name__)
# # api=Api(app)
# # todo={}
# # #@app.route("/")
# # class Apple(Resource):
# # 	def get(self,id):
# # 		return {id:todo[id]}
# # 	def put(self,id):
# # 		todo[id]=request.args[id]
# # 		return {id:todo[id]}
# # api.add_resource(Apple,'/<int:id>')
# # if __name__ == '__main__':
# # 	app.run(debug=True)


# from flask import Flask,jsonify,make_response,request
# from flask_restful import Resource,Api
# import pymysql
# import logging
# app=Flask(__name__)
# api=Api(app)

# logging.basicConfig(filename='api.log',level=logging.DEBUG)
# class Hello(Resource):
# 	def get(self):
# 		logger=logging.getLogger('get method')
# 		logger.info('entered into get method')
# 		try:
# 			db = pymysql.connect(host = '192.168.1.95',  # your host, usually localhost
# 								 user = 'root',  # your username
# 							     passwd = 'root',  # your password
# 							 	 db = 'inn', 
# 							 	 cursorclass = pymysql.cursors.DictCursor,#---------- to get the record in key:value(dictionary) pair
# 							 	 sql_mode = "STRICT_TRANS_TABLES")
# 			cursor = db.cursor()
# 			page=int(request.args.get('page'))
# 			count=int(request.args.get('count'))
# 			print(page)
# 			print(count)
# 			start=(page-1)*count
# 			query = "SELECT count(*) as total FROM addr;"
# 			cursor.execute(query)
# 			departments = cursor.fetchall()
# 			totalp=departments[0]['total']/count if len(departments)>0 else 0
# 			totalc=departments[0]['total'] if len(departments)>0 else 0
# 			myjson=jsonify({"status": "success", "response": departments[0],"totalpages":totalp,"totalcount":totalc,"pages":page,"count":count})
# 			print(myjson)
# 			print(type(myjson))
# 			print(dir(myjson))
# 			return make_response(myjson, 200)
# 		except Exception as e:
# 			logger.error(str(e))
			
# 		logger.info('exit from get method')

# 	def post(self):
# 		logger=logging.getLogger('post method')
# 		logger.info('post method')
# 		try:
# 			db = pymysql.connect(host='192.168.1.95', user='root',passwd='root',db='inn',cursorclass=pymysql.cursors.DictCursor,sql_mode = "STRICT_TRANS_TABLES")
# 			cursor=db.cursor()
# 			print(request.json)
# 			name10=request.json['name1']
# 			name20=request.json['name2']
# 			name30=request.json['name3']
# 			query = ("""INSERT INTO addr (name1,name2,name3) VALUES ('%s','%s','%s');"""%(name10,name20,name30))
# 			print(query)
# 			cursor.execute(query)
# 			db.commit()
# 			newId=cursor.lastrowid
# 			print(newId)			
# 			return jsonify({"status":"success","response":newId})
# 		except Exception as e:
# 			logger.error(str(e))
# 		logger.info('exit from the post method')


# 	def put(self):
# 		logger=logging.getLogger('put method')
# 		logger.info('eneterd into put method')
# 		try:
# 			db=pymysql.connect(host='192.168.1.95',user='root',passwd='root',db='inn',cursorclass=pymysql.cursors.DictCursor)
# 			cursor=db.cursor()
# 			print(request.json)
# 			name1=request.json['name1']
# 			name3=request.json['name3']
# 			query=("""UPDATE addr set name3='%s' WHERE name1='%s';"""%(name3,name1))
# 			print(query)
# 			cursor.execute(query)
# 			db.commit()
# 			return jsonify({"status":"success","response":name3})
# 		except Exception as e:
# 			logger.error(str(e))
# 		logger.info('exit from the put method')

# 	def delete(self):
# 		logger=logging.getLogger('delete method')
# 		logger.info('enetered into delete method')
# 		try:
# 			db=pymysql.connect(host='102.168.1.95',user='root', passwd='root',db='inn',cursorclass=pymysql.cursors.DictCursor)
# 			cursor=db.cursor()
# 			data=request.json
# 			name1 = data['name1']+'%'
# 			print(name1)
# 			query = "DELETE FROM addr where name1 like %s"
# 			cursor.execute(query,(name1))
# 			db.commit()
# 			return jsonify({"status":"deleted"})
# 		except Exception as e:
# 			logger.error(str(e))
# 		logger.info('exit from delete method')



# api.add_resource(Hello,'/hi')
# if __name__ == '__main__':
# 	app.run(debug=True,port=5001)
