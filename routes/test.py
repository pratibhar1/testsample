import os
from app import app
import unittest
import json
from routes import book

TEST_DB='inventory.db'


class FlaskTestCase(unittest.TestCase):
# # Test cases for the all book


    def test_get_department_valid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/department', \
                               content_type = 'application/json')
        self.assertEqual(response.status_code, 200)

    
    def test_get_booklist_valid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/booklist', \
                             content_type = 'application/json')
        self.assertEqual(response.status_code, 200)


    def test_get_book_valid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/book', query_string={'book_id':5}, \
                               content_type = 'application/json')
        self.assertEqual(response.status_code, 200)    


    def test_get_book_invalid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/book',query_string={'book_id':0},content_type='application/json')
        self.assertEqual(response.status_code,204)   


    def test_get_bookallocate_valid(self):
        tester = app.test_client()
        #if you miss any field in url (count)
        response=tester.get('http://localhost:5000/bookallocate',query_string={'book_id':12},content_type='application/json')
        self.assertEqual(response.status_code,200)       
       

    def test_get_bookallocate_invalid(self):
        tester = app.test_client()
        #if you miss any field in url (count)
        response=tester.get('http://localhost:5000/bookallocate',query_string={'book_id':0},content_type='application/json')
        self.assertEqual(response.status_code,204)       
        

    def test_get_bookallocatelist_valid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/bookallocatelist',query_string={'page':1,'count':5},content_type='application/json')
        self.assertEqual(response.status_code,200)  


    def test_get_bookallocatelist_invalid(self):
        tester = app.test_client()
        #if you miss any field in url (count)
        response=tester.get('http://localhost:5000/bookallocatelist',query_string={'page':1,'count':0},content_type='application/json')
        self.assertEqual(response.status_code,204)       


    def test_get_availablebooks_valid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/availablebooks',query_string={'page':1,'count':5},content_type='application/json')
        self.assertEqual(response.status_code,200)


    def test_get_availablebooks_invalid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/availablebooks',query_string={'page':1,'count':0},content_type='application/json')
        self.assertEqual(response.status_code,204)


    def test_get_mybooks_valid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/mybooks',query_string={'page':1,'count':2, 'employeeId': 714},content_type='application/json')
        self.assertEqual(response.status_code,200)


    def test_get_mybooks_invalid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/mybooks',query_string={'page':1,'count':0, 'employeeId': 0},content_type='application/json')
        self.assertEqual(response.status_code,204)
    
    
    def test_get_assignbooks_valid(self):
        tester = app.test_client()
        response=tester.get('http://localhost:5000/assignbooks',query_string = {'page':1,'count':5},content_type='application/json')
        self.assertEqual(response.status_code,200)
        

    def test_get_assignbooks_invalid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/assignbooks',query_string = {'page':1,'count':0},content_type='application/json')
        self.assertEqual(response.status_code,204)

    def test_readers_valid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/readers',query_string = {'book_id': 4}, content_type = 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_readers_invalid(self):
        tester = app.test_client()
        response = tester.get('http://localhost:5000/readers', query_string = {'book_id':0}, content_type = 'application/json')
        print '<<<<<<<<<<<<<ifhsdhfidghofho',response
        self.assertEqual(response.status_code, 204)
        
     
    def test_post_book_valid(self):
        tester = app.test_client()
        data = {
                 "book_name":"Basic Guide to Master Data Analytics", 
                "book_author":"Paul Kinley",
                "ISBN": "154708929",
                "rack_number":1,
                "department_id":2,
                "department_name":"html",
                 "price": 420,
                "quantity": 8,
                "Description":"How you can use data analytics to improve your business How to plan data analysis to know exactly what your target group wants How to implement descriptive analysis You will learn the exact techniques that are required to master Data Analytics"
             
                }
        response = tester.post('http://localhost:5000/book',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 201)       


    def test_post_book_invalid(self):
        tester = app.test_client()
        data = {
                "book_author":"Everett N McKay",
                "ISBN": "99921-58-10-1",
                "rack_number":1,
                "department_id":5,
                 "price": 125,
                "quantity": 8
                }
        response = tester.post('http://localhost:5000/book',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)       
    
    
    def test_post_request_book_valid(self):
        tester = app.test_client()
        data = {
             "employeeId":509,
            "book_id":10,
            "status":"request"
             }
        response = tester.post('http://localhost:5000/requestbook',data=json.dumps(data),content_type='application/json')
        print '<<<<<<<<<<jhfdsh',response
        self.assertEqual(response.status_code, 201)


    def test_post_request_book_invalid(self):
        tester = app.test_client()
        data = {
            "book_id":5,
            "requestDate":"03/12/2018" ,
            "status":"request"
             }
        response = tester.post('http://localhost:5000/requestbook',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)
    
    
    def test_put_book_valid(self):
        tester = app.test_client()
        data = {
            "ISBN": "8-902519-500687",
            "book_author": "bakshi",
            "book_id": 3,
            "book_name": "Designing Interfaces",
            "department_id":1,
            "price": 500,
            "quantity": 6,
            "rack_number": 10
             }
        response = tester.put('http://localhost:5000/book',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 200) 
    

    def test_put_book_invalid(self):
        tester = app.test_client()
        data = {
            "book_author": "bakshi",
            "book_name": "Designing Interfaces",
            "department_id":1,
            "price": 500,
            "quantity": 6,
            "rack_number": 10
             }
        response = tester.put('http://localhost:5000/book',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500) 


    def test_put_raeders_valid(self):
        tester = app.test_client()
        data = {
            "rating": 1,
            "allocation_id": 10
             }
        response = tester.put('http://localhost:5000/readers',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 200)    
    

    def test_put_raeders_invalid(self):
        tester = app.test_client()
        data = {
            "allocation_id": 10
             }
        response = tester.put('http://localhost:5000/readers',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)    
    
    
    def test_put_bookallocate_valid(self):
        tester = app.test_client()
        data = {
            "employeeId":100,
            "book_id":23,
            "assignedDate":"2018-02-28",
            "allocation_id":40
            }
        response = tester.put('http://localhost:5000/bookallocate',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 200)   
     
  
    def test_put_bookallocate_invalid(self):
        tester = app.test_client()
        data = {
            "employeeId":100,
            "assignedDate":"2018-02-28",
            "allocation_id":40
            }
        response = tester.put('http://localhost:5000/bookallocate',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)   
    

    def test_put_assign_book_returned_valid(self):
        tester = app.test_client()
        data = {
            "status": "returned",
            "allocation_id":1
               }
        response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 200)            
    

    def test_put_assign_book_returned_invalid(self):
        tester = app.test_client()
        data = {
            "allocation_id":1
               }
        response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)            
    
    # def test_put_assign_book_granted_valid(self):
    #     tester = app.test_client()
    #     data = {
    #      "status": "granted",
    #         "dueDate":11,
    #         "allocation_id":18
    #            }
    #     response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
    #     self.assertEqual(response.status_code, 200)   

    

    def test_put_assign_book_granted_invalid(self):
        tester = app.test_client()
        data = {
            "dueDate":11,
            "allocation_id":18
               }
        response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)  

    
    def test_put_assign_book_declined_valid(self):
        tester = app.test_client()
        data = {
            "status": "declined",
            "message":"cannot assign",
            "allocation_id":14
               }
        response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 200)

    

    def test_put_assign_book_declined_invalid(self):
        tester = app.test_client()
        data = {
            "message":"cannot assign",
            "allocation_id":14
               }
        response = tester.put('http://localhost:5000/assignbooks',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 500)

    
    def test_delete_bookallocate_valid(self):
        tester = app.test_client()
        data = {
           
            "rating":1,
            "returnedDate":"2010-19-10",
            "status":"returned",
            "allocation_id": 13  
               }
        response = tester.delete('http://localhost:5000/bookallocate',data=json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, 204)            
        
    
    # def test_delete_bookallocate_invalid(self):
    #     tester = app.test_client()
    #     data = {
    #             "allocation_id":5
    #            }
    #     response = tester.delete('http://localhost:5000/bookallocate',data=json.dumps(data),content_type='application/json')
    #     self.assertEqual(response.status_code, 500)            
        

if __name__ == "__main__":
    unittest.main()
    