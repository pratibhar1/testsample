import os
from app import app
from routes import book
import unittest
TEST_DB='inventory.db'
import json

class FlaskTestCase(unittest.TestCase):
	
	def test_get_userrole(self):
		tester = app.test_client()
		data={
			"employeeId":509,
			"book_id":1,
			"status":"requsted"
		}
		response = tester.post('http://localhost:5000/requestbook',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)
    


	# def test_get_adduser_valid(self):
	# 	tester = app.test_client()
	# 	response=tester.get('http://localhost:5000/adduser',query_string={'page':1,'count':5},content_type='application/json')
	# 	self.assertEqual(response.status_code,200)
	

	# def test_get_adduser_invalid(self):
	# 	tester = app.test_client()  
	# 	response=tester.get('http://localhost:5000/adduser',query_string={'page':1, 'count': 0},content_type='application/json')
	# 	self.assertEqual(response.status_code,204)
	

	# def get_profile_picture_valid(self):
	# 	tester = app.test_client()
	# 	response = tester.get('http://127.0.0.1:5000/profilepicture', query_string = {'employeeId':682}, content_type = 'application/json')
	# 	self.assertEqual(response.status_code, 200)


if __name__=='__main__':
	unittest.main()
