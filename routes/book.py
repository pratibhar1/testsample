from flask import Flask, jsonify, abort, make_response, request, g, session
from flask_restful import reqparse
from flask_restful import Resource
from datetime import datetime, timedelta

import datetime
import logging 
import pymysql
import json
import logging.config
import sys


class Department(Resource):
	#fetches the list of departments with ids
	def get(self):
		logger = logging.getLogger("Department")
		logger.info('Entered into Department GET method')
		try:		
			cursor = g.appdb.cursor()
			query = "SELECT * FROM department;"
			cursor.execute(query)
			departments = cursor.fetchall()
		
		except:
			logger.warn("there is some issue with the db")

		logger.info('Exiting from Department GET method')
		return make_response(jsonify({"status": "success", "response": departments}), 200)


class BookList(Resource):
	#fetches list of books 
	def get(self):
		logger = logging.getLogger("BookList")
		logger.info('Entered into BookList GET method')
		books=0

		try:
			cursor = g.appdb.cursor()
			query = """SELECT b.book_id, b.book_name, d.department_name ,b.description
					FROM book b, department d WHERE (b.department_id = d.department_id) 
					"""
			cursor.execute(query)
			books = cursor.fetchall()
			print(books)
			#total = len(books)
		except:
			logger.warn("there is some issue with the db")			

		logger.info('Exiting from BookList GET method')
		return jsonify({"status" : "success", "response" : books, "total_books" : "total"})
	

class Readers(Resource):
	#fetches the list of departments with ids

	def get(self):

		logger = logging.getLogger("Readers")
		logger.info('Entered into Readers GET method')
		
		if 'book_id' in request.args:

			try:
				book_id = request.args.get('book_id')
				cursor = g.appdb.cursor()

			except:
				logger.warn("there is some issue with the db")
			
			query = """SELECT ba.book_id,count(ba.book_id) as Readers FROM book_allocation ba 
						INNER JOIN book b ON b.book_id = ba.book_id WHERE ba.book_id = %s 
						AND status = "returned" OR status = "granted";"""

			cursor.execute(query,(book_id))
			readers = cursor.fetchall()[0]['Readers']

			query1 = """SELECT FORMAT(sum(rating)/5, 1) AS rating FROM book_allocation 
						WHERE book_id = %s"""
			cursor.execute(query1, (book_id))
			rating = cursor.fetchall()[0]['rating']

			query2 = """SELECT ba.allocation_id, b.book_name, b.description, b.book_author, d.department_name, 
						b.quantity-COUNT(ba.book_id) AS available FROM book b 
						INNER JOIN department d ON d.department_id = b.department_id 
						LEFT JOIN book_allocation ba ON b.book_id=ba.book_id 
						WHERE ba.book_id=%s AND ba.status='granted'"""
			cursor.execute(query2, (book_id))
			des = cursor.fetchall()
			
			logger.info('Exiting from Readers GET method')
			return make_response(jsonify({"status":"success", "readers": readers, \
				"rating": rating, "book_id" : int(book_id), "description": des[0]}), 200)

		else:
			des=[]
			status_code = 204
			status = 'requested parameter book_id is not found'
			logger.info('Exiting from Readers GET method')
			return make_response(jsonify({"status":status,"status_code":status_code}))


	
	def put(self):
		logger = logging.getLogger("Readers")
		logger.info('Entered into Readers PUT method')
		
		try:
			cursor = g.appdb.cursor()
			rating = request.json
		except:
			logger.warn("there is some issue with the db")

		query = """UPDATE book_allocation SET rating = %s WHERE allocation_id = %s ;"""
		cursor.execute(query,(rating['rating'], rating['allocation_id']))
		g.appdb.commit()
		newId = cursor.lastrowid

		logger.info('Exiting from Readers PUT method')
		return jsonify({"status": "success", "response" : rating['allocation_id'],"newId":newId}) 


	# def post(self):
	# 	logger = logging.getLogger("Readers")
	# 	logger.info('Entered into Readers PUT method')

	# 	try:
	# 		cursor = g.appdb.cursor()
	# 		rating = request.json
	# 		now = datetime.datetime.now()
	# 		returnDate = now.strftime("%Y-%m-%d %H:%M:%S")
	# 	except:
	# 		logger.warn("there is some issue with the db")

	# 	query = """INSERT INTO  book_allocation (book_id,rating, returnDate,status ) VALUES (%s,%s,%s,%s);"""
	# 	cursor.execute(query,(rating['book_id'], rating['rating'], returnDate, rating['status']))
	# 	g.appdb.commit()
	# 	newId = cursor.lastrowid


	# 	logger.info('Exiting from Readers PUT method')
	# 	return jsonify({"status": "success", "response" : newId})
		
class Book(Resource):
	#fetch the book details on particular book_id

	def get(self):
		logger = logging.getLogger("Book")
		logger.info('Entered into Book GET method')

		if 'book_id' in request.args:

			try:
				book_id = request.args.get('book_id')
				cursor = g.appdb.cursor()
				
			except:
				logger.warn("there is some issue with the db")

			query = """SELECT d.department_name,b.book_id, b.book_name,b.book_author,d.department_id, b.ISBN, 
					b.rack_number, b.price, b.quantity, d.department_name, 
					DATE_FORMAT(b.book_entry_date,'%%m/%%d/%%Y') AS book_entry_date, 
					b.Description FROM book b INNER JOIN department d 
					ON b.department_id = d.department_id 
					where b.book_id = %s ;
					"""		
			cursor.execute(query,(book_id))
			book = cursor.fetchall()

			if len(book) == 0:
				return make_response(jsonify({}), 204)

			logger.info('Exiting from Book GET method')
			return make_response(jsonify({"status": "success", "response": book}), 200)

		else:
			status_code = 204
			status = 'requested parameter book_id is not found'
			book = []
			return make_response(jsonify({"status": status, "status_code":status_code}))

	#To insert a new book
	def post(self):
		logger = logging.getLogger("Book")
		logger.info('Entered into Book POST method')

		try:
			now = datetime.datetime.now()
			entry = now.strftime("%Y-%m-%d %H:%M:%S")
			cursor = g.appdb.cursor()
			book = request.json
			description = book['Description'].encode('ascii','ignore')

		except:
			logger.warn("there is some issue with the db")


		if 'department_name' in book.keys():
			select = '''SELECT department_id FROM department WHERE Lower(department_name) =LOWER(%s) '''
			cursor.execute(select,(book['department_name']))
			result = cursor.fetchall()
			department_id = result[0]['department_id'] if len(result)>0 else 0 
			
			if department_id == 0:
				query = """INSERT INTO department (department_name) VALUES (%s);"""
				cursor.execute(query,(book['department_name'],))
				g.appdb.commit()
				book['department_id'] = cursor.lastrowid
			else:
				book['department_id'] = department_id

		query1 = """INSERT INTO book (book_name,book_author,ISBN,rack_number,
					department_id, price,quantity,book_entry_date,Description) VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
		cursor.execute(query1, (book['book_name'], book['book_author'], book['ISBN'],
						book['rack_number'], int(book['department_id']), book['price'], 
						book['quantity'], entry,description))
		g.appdb.commit()
		newId = cursor.lastrowid	

		logger.info('Exiting from Book POST method')
		return make_response(jsonify({"status": "success", "newId": newId}), 201)  


	#To make changes to the existing book
	def put(self):
		logger = logging.getLogger("Book")
		logger.info('Entered into Book PUT method')

		try:
			now = datetime.datetime.now()
			entry = now.strftime("%Y-%m-%d %H:%M:%S")
			cursor = g.appdb.cursor()	
			book = request.json
			description = book['Description']

		except:
			logger.warn("there is some issue with the db")
		

		query = """UPDATE book SET book_name = %s, book_author = %s, ISBN = %s, 
					rack_number = %s, department_id = %s, price = %s, 
					quantity = %s, book_entry_date = %s, Description = %s
				WHERE book_id = %s ;
				"""
		cursor.execute(query,(book['book_name'], book['book_author'], book['ISBN'],\
					   book['rack_number'], book['department_id'], book['price'], book['quantity'], \
					   entry, description, book['book_id']))

		g.appdb.commit()
		
		logger.info('Exiting from Book PUT method')

		return make_response(jsonify({"status": "Updated", "book_id":book['book_id']}), 200)


class BookAllocate(Resource):


	def get(self):
		logger = logging.getLogger("BookAllocate")
		logger.info('Entered into BookAllocate GET method')

		if 'book_id' in request.args:

			try:
				book_id = request.args.get('book_id')
				cursor = g.appdb.cursor()
				query = """SELECT b.book_id, ba.employeeId, b.book_name, b.ISBN, b.book_author,
						DATE_FORMAT(ba.assignedDate,'%%m/%%d/%%Y') AS assignedDate FROM 
						book_allocation ba,book b WHERE flag = 1 AND b.book_id = ba.book_id 
						AND b.book_id = %s
						"""
				cursor.execute(query,(book_id))
				books = cursor.fetchall()

				if len(books) == 0:
					return make_response(jsonify({}), 204)

			except:
				logger.warn("there is some issue with the db")

			logger.info('Exiting from BookAllocate GET method')
			return make_response(jsonify({"status": "success", "response": books}), 200)
			
		else:
			status_code = 204
			status = 'requested parameter book_id not found'
			books = []
			return make_response(jsonify({"status":status, "status_code":status_code}))

	def put(self):
		logger = logging.getLogger("BookAllocate")
		logger.info('Entered into BookAllocate PUT method')

		try:
			
			cursor = g.appdb.cursor()
			bookal = request.json
			query = """UPDATE book_allocation SET employeeId = %s, book_id = %s, 
			assignedDate = %s WHERE allocation_id = %s AND flag = 1 ;
			"""
			cursor.execute(query,(bookal['employeeId'], bookal['book_id'],\
				bookal['assignedDate'], bookal['allocation_id']))
			g.appdb.commit()
			
		except:
			logger.warn("there is some issue with the db")
		
		logger.info('Exiting from BookAllocate PUT method')
		return make_response(jsonify({"status": "Updated", "book_id": bookal['book_id']}), 200)


	def delete(self):
		logger = logging.getLogger("BookAllocate")
		logger.info('Entered into BookAllocate DELETE method')

		try:
			now = datetime.datetime.now()
			returnDate = now.strftime("%Y-%m-%d %H:%M:%S")
			cursor = g.appdb.cursor()
			allocation_id = request.json['allocation_id']
			rating =request.json['rating']
			status = request.json['status']

			query = """UPDATE book_allocation SET flag = 0, rating = %s,
					status = %s, returnDate = %s WHERE allocation_id = %s;
					"""
			cursor.execute(query,(rating, status, returnDate, allocation_id))
			g.appdb.commit()
	
		except:
			logger.warn("there is some issue with the db")

		logger.info('Exiting from BookAllocate PUT method')
		return make_response(jsonify({"status": "Updated", "response": "deleted", "rating": rating}), 204)


class BookAllocateList(Resource):


	def get(self):


		if 'page' and 'count' in request.args:

			cursor = g.appdb.cursor()
			page = int(request.args.get('page'))
			count = int(request.args.get('count'))
			start = (page-1)*count

			query1 = """ SELECT COUNT(*) AS total_books FROM book """
			cursor.execute(query1)
			books1 = cursor.fetchall()

			query = """SELECT ba.employeeId, b.book_name, b.ISBN, b.book_author, \
					DATE_FORMAT(ba.assignedDate,'%%m/%%d/%%Y') AS assignedDate \
					FROM book_allocation ba INNER JOIN book b ON b.book_id = ba.book_id\
					 WHERE flag = 1 LIMIT %s,%s ;
					 """
			cursor.execute(query,(start,count))
			books = cursor.fetchall()

			if len(books) == 0:
				return make_response(jsonify({}), 204)

			total=len(books)
			total_pages = books1[0]['total_books']/count if len(books1)>0 else 0
			total_books = books1[0]['total_books'] if len(books1)>0 else 0
			return make_response(jsonify({"status": "success", "response": books,"total": total,\
							"page": page, "total_pages": total_pages, "per_page": count,\
							"total_books": total_books}), 200) 

		else:
			status_code = 204
			status = 'requested parameters page and count not found'
			books = []
			return make_response(jsonify({"status":status, "status_code":status_code}))
		

class AvailableBooks(Resource):


	def get(self):
		logger = logging.getLogger("AvailableBooks")
		logger.info('Entered into AvailableBooks GET method')
		
		if 'page' and 'count' in request.args:

			try:
				cursor = g.appdb.cursor()
				page = int(request.args.get('page'))
				count = int(request.args.get('count'))
				start = (page-1)*count
				
				query1 = """SELECT COUNT(*) AS total_books FROM book """
				cursor.execute(query1)
				books1 = cursor.fetchall()

				if len(books1) == 0:
					return make_response(jsonify({}), 204)
				
				query2 = """ SELECT b.book_id, b.book_name, b.book_author,b.price, \
						d.department_name, b.ISBN, b.rack_number, b.quantity FROM book b INNER JOIN \
						department d ON b.department_id = d.department_id LEFT JOIN book_allocation ba\
						ON b.book_id = ba.book_id GROUP BY b.book_id DESC LIMIT %s,%s;
						"""
				cursor.execute(query2,(start,count))
				books2 = cursor.fetchall()
				total2=len(books2)

				# if len(books2) == 0:
				# 	return make_response(jsonify({}), 204)

				# query = """SELECT b.book_id, b.book_name,b.Description, b.book_author, b.price, \
				# 		d.department_name, b.ISBN, b.rack_number, b.quantity FROM book b INNER JOIN \
				# 		department d ON b.department_id = d.department_id LEFT JOIN \
				# 		book_allocation ba ON b.book_id = ba.book_id GROUP BY b.book_id ORDER BY \
				# 		b.book_id DESC LIMIT %s,%s;
				# 		"""
				# cursor.execute(query,(start,count))
				# books = cursor.fetchall()

				# if len(books) == 0:
				# 	return make_response(jsonify({}), 204)

				#total=len(books)
				total_pages = books1[0]['total_books']/count if len(books2)>0 else 0
				total_books = books1[0]['total_books'] if len(books2)>0 else 0
				
			except:
				logger.warn("there is some issue with the db")

			return make_response(jsonify({"status": "success", "response": books2,"total": total2, "page": page,\
							"total_pages": total_pages, "per_page": count, "total_books": total_books}), 200)
		else:
			status_code = 204
			status = 'requested parameters page and count are not found'
			return make_response(jsonify({"status":status, "status_code":status_code}))


class RequestBook(Resource):


	def post(self):
		logger = logging.getLogger("RequestingBook")
		logger.info('Entered into RequestingBook POST method')

		try:
			cursor = g.appdb.cursor()
			req = request.json
			now = datetime.datetime.now()
			requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")
			
		except:
			logger.warn("there is some issue with the db")

		query = """INSERT INTO book_allocation (employeeId,  book_id, requestedDate, 
					status) VALUES (%s,%s,%s,%s);
				"""
		cursor.execute(query,(req['employeeId'], req['book_id'], requestedDate, req['status']))	
		g.appdb.commit()

		newId = cursor.lastrowid
		logger.info('Exiting from RequestingBook POST method')
		return make_response(jsonify({"status": "success", "response":newId}), 201)  


class AssignBooks(Resource):


	def get(self):
		logger = logging.getLogger("AssignBooks")
		logger.info('Entered into AssignBooks GET method')

		if 'page' and 'count' in request.args:

			try:
				cursor = g.appdb.cursor()
				page = int(request.args.get('page'))
				count = int(request.args.get('count'))
				start = (page-1)*count
				
				countquery = """SELECT COUNT(ba.allocation_id)AS total_books 
								FROM book_allocation ba, 
								book b,employee e,department d WHERE b.book_id = ba.book_id 
								AND e.employeeId = ba.employeeId AND 
								d.department_id = b.department_id """
				cursor.execute(countquery)
				totalassigned = cursor.fetchall()

				if len(totalassigned) == 0:
					return make_response(jsonify({}), 204)
				
				query = """SELECT e.employeeId, e.employeeName, b.book_name, b.book_author, 
						d.department_name, ba.allocation_id, 
						DATE_FORMAT(ba.dueDate,'%%m/%%d/%%Y') AS dueDate, 
						DATE_FORMAT(ba.requestedDate,'%%m/%%d/%%Y') AS requestedDate, 
						DATE_FORMAT(ba.assignedDate,'%%m/%%d/%%Y') AS assignedDate,
						ba.status FROM book_allocation ba,book b,employee e,department d WHERE 
						b.book_id = ba.book_id AND e.employeeId = ba.employeeId AND 
						d.department_id = b.department_id GROUP BY allocation_id ORDER BY 
						 allocation_id DESC LIMIT %s,%s;
						"""
				cursor.execute(query,(start,count))
				books = cursor.fetchall()

				if len(books) == 0:
					return make_response(jsonify({}), 204)

				total = len(books)
				total_pages = totalassigned[0]['total_books']/count if len(totalassigned)>0 else 0
				total_books = totalassigned[0]['total_books'] if len(totalassigned)>0 else 0
				
			except:
				logger.warn("there is some issue with the db")

			return make_response(jsonify({"status": "success", "response": books,"total": total, "page": page, \
				"total_pages": total_pages, "per_page": count,"total_books": total_books}), 200)

		else:
			status_code = 204
			status = 'requested parameters page and count are not found'
			return make_response(jsonify({"status":status, "status_code":status_code}))
			

	def put(self):
		logger = logging.getLogger("AvailableBooks")
		logger.info('Entered into AvailableBooks PUT method')

		try:
			cursor = g.appdb.cursor()
			bookal = request.json

		except:
			logger.warn("there is some issue with the db")

		if bookal['status'] == "returned":
			now = datetime.datetime.now()
			returnDate = now.strftime("%Y-%m-%d %H:%M:%S") 
			query = """UPDATE book_allocation SET returnDate = %s, 
						status = %s WHERE allocation_id = %s;"""

			cursor.execute(query,(returnDate, bookal['status'],  bookal['allocation_id'] ))
			g.appdb.commit()
			di = {"response": bookal['status'], "allocation_id": bookal['allocation_id'],\
				  "status": "success"}

		elif bookal['status'] == "granted":
			now = datetime.datetime.now()
			assignedDate = now.strftime("%Y-%m-%d")
			dat = datetime.datetime.strptime(assignedDate, "%Y-%m-%d")
			dueDate = dat + timedelta(days=bookal['dueDate'])
			dueDate = str(dueDate)[:-9]

			query = """UPDATE book_allocation SET assignedDate = %s, status = %s, 
					dueDate = %s WHERE allocation_id = %s ;
					"""
			cursor.execute(query,(assignedDate,bookal['status'], dueDate, \
						   bookal['allocation_id']))
			g.appdb.commit()
			di = {"status": bookal['status'], "allocation_ id":bookal['allocation_id'],\
				  "dueDate":dueDate}
		
		elif bookal['status'] == "declined":
			query = """UPDATE book_allocation SET status = %s, message = %s WHERE \
					allocation_id = %s AND flag = 1;
					"""
			cursor.execute(query,(bookal['status'], bookal['message'], \
						   bookal['allocation_id']))
			g.appdb.commit()
			di = {"status": bookal['status'], "allocation_id": bookal['allocation_id'],\
				  "message": bookal['message']}
		logger.info('Exiting from AvailableBooks PUT method')
		return make_response(jsonify(di), 200)


class MyBooks(Resource):

	def get(self):
		logger = logging.getLogger("MyBooks")
		logger.info('Entered into MyBooks GET method')
 
		if 'page' and 'count' and 'employeeId' in request.args:

			try:
				cursor = g.appdb.cursor()
				page = int(request.args.get('page'))
				count = int(request.args.get('count'))
				employeeId = request.args.get('employeeId')

			except:
				logger.warn("there is some issue with the db")

			start = (page-1)*count

			
			query = """SELECT ba.allocation_id, b.book_name, b.book_id, b.book_author, dp.department_name,
					b.ISBN, ba.status, DATE_FORMAT(ba.requestedDate,'%%m/%%d/%%Y') AS 
					requestedDate, DATE_FORMAT(ba.assignedDate,'%%m/%%d/%%Y') AS 
					assignedDate, ba.message, DATE_FORMAT(ba.dueDate,'%%m/%%d/%%Y') AS  
					dueDate, DATE_FORMAT(ba.returnDate,'%%m/%%d/%%Y') AS returnDate FROM 
					book_allocation ba, department dp, book b WHERE ba.employeeId= %s 
					AND dp.department_id=b.department_id AND b.book_id=ba.book_id LIMIT %s,%s;
					"""
			cursor.execute(query,(employeeId,start,count))
			books = cursor.fetchall()

			totalbooks = """SELECT COUNT(*) AS total_books FROM book_allocation where employeeId = %s"""
			cursor.execute(totalbooks, (employeeId))
			total_books = cursor.fetchall()[0]["total_books"]
			
			# if len(books) == 0:
			# 	return make_response(jsonify({}), 200)
			if len(books) == 0:
				return make_response(jsonify({}), 204)
			
			return make_response(jsonify({"status" : "success", "response" : books,  
							"total_books" : total_books, "page" : page, 
							"total_pages" : total_books/count, "per_page" : count}), 200)

		else:
			status_code = 204
			status = 'requested parameters page and count are not found'
			return make_response(jsonify({"status":status, "status_code":status_code}))
# def put(self):
# 		logger = logging.getLogger("InventoryAllocation")
# 		logger.info('Entered into InventoryAllocation PUT method')

# 		#try:
# 		now = datetime.datetime.now()
# 		entry = now.strftime("%Y-%m-%d %H:%M:%S")
# 		cursor = g.appdb.cursor()
# 		update = request.json
# 		form = '%m/%d/%Y'
# 		print(update)

# 		now = datetime.datetime.now()
# 		requestedDate = now.strftime("%Y-%m-%d %H:%M:%S") 
# 		query = """UPDATE inventory_allocation SET  
# 					 floorNumber = %s, cubicle = %s, dateAssigned = str_to_date(%s,%s), requestedDate=%s WHERE allocation_id = %s;"""

# 	# query = """UPDATE inventory_allocation SET inventoryId = %s,employeeId = %s, 
# 	# 				 floorNumber = %s, cubicle = %s, dateAssigned = str_to_date(%s,%s), message=%s, status WHERE allocation_id = %s;"""

# 		cursor.execute(query, (update['floorNumber'],update['cubicle'],
# 		update['dateAssigned'], form,requestedDate, update['allocation_id']))
# 		g.appdb.commit()

# 		# if update['status'] == "repaired":
# 		# 	now = datetime.datetime.now()
# 		# 	requestedDate = now.strftime("%Y-%m-%d %H:%M:%S") 
# 		# 	query = """UPDATE inventory_allocation SET inventoryId = %s,employeeId = %s, 
# 		# 				 floorNumber = %s, cubicle = %s, dateAssigned = str_to_date(%s,%s), message=%s, status =%s, requestedDate=%s WHERE allocation_id = %s;"""

# 		# # query = """UPDATE inventory_allocation SET inventoryId = %s,employeeId = %s, 
# 		# # 				 floorNumber = %s, cubicle = %s, dateAssigned = str_to_date(%s,%s), message=%s, status WHERE allocation_id = %s;"""

# 		# 	cursor.execute(query, (update['inventoryId'], update['employeeId'],update['floorNumber'],update['cubicle'],
# 		# 	update['dateAssigned'], form,update['message'],update['status'],requestedDate, update['allocation_id']))
# 		# 	g.appdb.commit()
# 		# else:
# 		# 	logger.warn("there is some issue with the db")

		
# 		logger.info('Exiting from InventoryAllocation PUT method')
# 		return jsonify({"status":"Updated","allocation_id":update['allocation_id']}) 