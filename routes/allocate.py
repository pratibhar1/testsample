#!flask/bin/python
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from flask import Flask, jsonify, abort, make_response, request, g, config
from flask_restful import reqparse
from flask_restful import Resource

import datetime 
import logging
import pymysql
import json
import logging.config
import sys

import smtplib
import kaptan
import os




config = kaptan.Kaptan(handler="json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))
environment = config.get('environment')

class InventoryAllocation(Resource):
    def get(self):

        logger = logging.getLogger("InventoryAllocation")
        logger.info('Entered into InventoryAllocation GET method')

        try:
            if 'allocation_id' in request.args:
                allocation_id = request.args.get('allocation_id')
                # now = datetime.datetime.now()
          #       entry1 = now.strftime("%Y-%m-%d %H:%M:%S")
                cursor = g.appdb.cursor()

                query = """SELECT ia.allocation_id, ia.employeeId, e.employeeName,
                            ia.floorNumber, ia.cubicle, 
                            DATE_FORMAT(ia.dateAssigned,'%%m/%%d/%%Y')
                            AS dateAssigned, ia.message, ia.requestedDate FROM inventory_allocation ia JOIN inventories i
                            ON (i.inventory_id = ia.inventoryId) JOIN employee e ON
                            (e.employeeId = ia.employeeId)WHERE ia.flag = 1 AND 
                        ia.allocation_id = %s AND i.flag = 1 ;"""

                device = """SELECT i.deviceId FROM inventory_allocation ia INNER JOIN inventories i 
                            ON ia.inventoryId = i.inventory_id WHERE ia.allocation_id = %s"""
                cursor.execute(device,(allocation_id))
                deviceId = cursor.fetchone()['deviceId']

                assignedQuery = """SELECT inventoryId FROM inventory_allocation WHERE flag =1"""
                cursor.execute(assignedQuery)
                assigned = [inventoryId['inventoryId'] for inventoryId in cursor.fetchall()]

                availableQuery = """SELECT inventory_id, serial_number, assetId FROM inventories WHERE flag=1 AND deviceId = %s"""
                cursor.execute(availableQuery, (deviceId))
                available = [device for device in cursor.fetchall() if device['inventory_id'] not in assigned]

                cursor.execute(query,(allocation_id))
                invento = cursor.fetchone()
                status="success"
                statuscode=200
            else:
                status="request parameter allocation_id missing"
                invento=[]
                statuscode=204
                available=[]

            cursor.execute(query,(allocation_id))
            invento = cursor.fetchall()[0]

        except:
            logger.warn("there is some issue with the db")

        logger.info('Exiting from InventoryAllocation GET method')
        return jsonify({"status": status,"response":invento, "available":available})

    def post(self):
        logger = logging.getLogger("InventoryAllocation")
        logger.info('Entered into InventoryAllocation POST method')

        try:
            products=''
            now = datetime.datetime.now()
            cursor = g.appdb.cursor()
            alloc = request.json
            form = '%m/%d/%Y'
            products = alloc['assetId']
            print(products)


        except:
            logger.warn("there is some issue with the db")


        query1 = """SELECT employeeId from employee where employeeId = %s AND flag=2"""
        cursor.execute(query1,(alloc['employeeId'],))
        validate = cursor.fetchall()
        if any(validate):
            for product in products:

                    query = """INSERT INTO inventory_allocation(employeeId, inventoryId,
                                    dateAssigned, floorNumber, cubicle) VALUES
                            (%s,%s,str_to_date(%s,%s),%s,%s);"""

                    cursor.execute(query, (alloc['employeeId'], product, alloc['dateAssigned'],
                    form, alloc['floorNumber'], alloc['cubicle']))
                    g.appdb.commit()
            status = "success"
            response = "devices are successfully alloted"
        else:
            status = "failure"
            response = "Invalid employeeId"



        logger.info('Exiting from InventoryAllocation POST method')
        return jsonify({"status": status, "inserted":response})

    def put(self):
        logger = logging.getLogger("InventoryAllocation")
        logger.info('Entered into InventoryAllocation PUT method')

        #try:
        now = datetime.datetime.now()
        entry = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor = g.appdb.cursor()
        update = request.json
        form = '%m/%d/%Y'
        print(update)

        query = """UPDATE inventory_allocation SET inventoryId = %s,employeeId = %s, 
                         floorNumber = %s, cubicle = %s, dateAssigned = str_to_date(%s,%s), message=%s WHERE allocation_id = %s;"""

        cursor.execute(query, (update['inventoryId'], update['employeeId'],update['floorNumber'],update['cubicle'],
        update['dateAssigned'], form,update['message'], update['allocation_id']))
        g.appdb.commit()
        # except:
        # 	logger.warn("there is some issue with the db")


        logger.info('Exiting from InventoryAllocation PUT method')
        return jsonify({"status":"Updated","allocation_id":update['allocation_id']})


class DeleteAllocation(Resource):
    def put(self):
        logger = logging.getLogger("InventoryAllocation")
        logger.info('Entered into InventoryAllocation DELETE method')


        try:
            now = datetime.datetime.now()
            cursor = g.appdb.cursor()
            message = request.json['reason']
            allocation_id = request.json['allocation_id']
            releasingDate = now.strftime("%Y-%m-%d %H:%M:%S")

            query = """UPDATE inventory_allocation SET flag = 0, releasingDate = %s, 
                        message=%s where allocation_id = %s ;"""
            cursor.execute(query,(releasingDate, message,  allocation_id))
            g.appdb.commit()

        except:
            logger.warn("there is some issue with the db")

        logger.info('Exiting from InventoryAllocation DELETE method')
        return jsonify({"status": "Updated", "response": "deleted"})


class AllocationList(Resource):
    def get(self):

        logger = logging.getLogger("InventoryAllocation")
        logger.info('Entered into InventoryAllocation GET method')

        if "page" and "count" in request.args:

            try:
                cursor = g.appdb.cursor()
                page = int(request.args.get('page'))
                count = int(request.args.get('count'))
                start = (page-1)*count

            except:
                logger.warn("there is some issue with the db")

            query1 = """SELECT COUNT(*) AS total_allocation FROM
                        inventory_allocation WHERE flag =1 """
            cursor.execute(query1)
            inventor1 = cursor.fetchall()

            query2 = """SELECT ia.allocation_id, ia.employeeId , dd.deviceName,
                        ia.status, e.employeeName, i.assetId, i.serial_number,
                        DATE_FORMAT(ia.dateAssigned ,'%%m/%%d/%%Y') AS dateAssigned,
                        ia.floorNumber, ia.cubicle FROM inventory_allocation ia 
                        INNER JOIN inventories i ON i.inventory_id = ia.inventoryId
                        INNER JOIN device_details dd ON i.deviceId = dd.deviceId
                        INNER JOIN employee e ON e.employeeId=ia.employeeId WHERE 
                        ia.flag = 1  """

            cursor.execute(query2)
            inventor2 = cursor.fetchall()
            total_inventories2 = len(inventor2)

            query = query2 +"""  LIMIT %s,%s;"""

            cursor.execute(query,(start,count))
            inventor = cursor.fetchall()
            total_inventories = len(inventor)
            total_pages = inventor1[0]['total_allocation']/count if len(inventor)>0 else 0
            total = inventor1[0]['total_allocation'] if len(inventor)>0 else 0
            statuscode=200
            return jsonify({"status": "success", "response":inventor,
                    "total_inventories":total_inventories2,  "per_page":count,
                    "page":page, "total_pages":total_pages,"total":total})

        else:
            statuscode=204
            return jsonify({"status": "page/ count not found", "response": "failure"})

        logger.info('Exiting from InventoryAllocation GET method')


class DeviceList(Resource):
    def get(self):
        logger = logging.getLogger("DeviceList")
        logger.info('Entered into DeviceList GET method')

        try:
            cursor = g.appdb.cursor()
            assignedQuery = """SELECT inventoryId FROM inventory_allocation WHERE flag =1"""
            cursor.execute(assignedQuery)
            assigned = [inventoryId['inventoryId'] for inventoryId in cursor.fetchall()]

            availableQuery = """SELECT inventory_id, serial_number, assetId FROM inventories WHERE flag=1"""
            cursor.execute(availableQuery)
            available = [device for device in cursor.fetchall() if device['inventory_id'] not in assigned]

        except:
            logger.warn("there is some issue with the db")


        logger.info("Exiting from DeviceList GET method")
        return jsonify({"status":"success", "available":available})


class RequestForReplace(Resource):
    def post(self):
        logger = logging.getLogger("RequestForReplace")
        logger.info('Entered into RequestForReplace POST method')

        try:
            cursor = g.appdb.cursor()
            req = request.json

            now = datetime.datetime.now()
            requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")

        except:
            logger.warn("there is some issue with the db")

        query = """INSERT INTO inventory_allocation (employeeId, inventoryId,
                    requestedDate, status, message, floorNumber, cubicle)
                VALUES (%s,%s,%s,%s,%s,%s,%s);"""

        cursor.execute(query,(req['employeeId'], req['inventoryId'],
        requestedDate, req['status'], req['message'], req['floorNumber'],
        req['cubicle']))
        g.appdb.commit()

        newId = cursor.lastrowid
        logger.info('Exiting from RequestForReplace POST method')
        return jsonify({"status": "success", "response":newId})

    def put(self):

        logger = logging.getLogger("RequestForReplace")
        logger.info('Entered into RequestForReplace PUT method')

        try:
            now = datetime.datetime.now()
            requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")
            cursor = g.appdb.cursor()
            update = request.json
            form = '%m/%d/%Y'

            query = """UPDATE inventory_allocation SET  requestedDate = %s,
                        status = %s, message = %s WHERE allocation_id = %s AND
                    flag=1 ;"""

            cursor.execute(query, (requestedDate, update['status'],
            update['message'], update['allocation_id']))
            g.appdb.commit()

        except Exception as e:
            logger.error(str(e))


        logger.info('Exiting from InventoryAllocation PUT method')
        return jsonify({"status": "Updated", "allocation_id": update['allocation_id']})



# class Request(Resource):

#     def put(self):
#         logger = logging.getLogger("Add_user")
#         logger.info('Entered into request_user  post method')
#         try:
#             cursor = g.appdb.cursor()
#         except:
#             logger.error("DB connection or url parameters error", exc_info=True)

#         value = request.json
#         employeeId = value["employeeId"]
#         #employeeName = value["employeeName"]
#         email = value["email"]
#         message = value["message"]
#         # role_id = int(value["role_id"])
#         # gender = value["gender"]
#         # #joiningDate = value["joiningDate"]
#         # joiningDate="2010-10-10"
#         now = datetime.datetime.now()
#         createDate = now.strftime("%Y-%m-%d %H:%M:%S")

#         status = ''
#         response = ''


#         check = """SELECT a.employeeId FROM inventory_allocation
#                     WHERE employeeId = %s And status='requested' """ %employeeId
#         cursor.execute(check,)
#         verify = cursor.fetchall()
#         print(verify)

#         if len(verify) != 0:
#             try:
#                 sender = config.get('fromemail')
#                 #smtppass = base64.decodestring(config.get(b'smtppass'))
#                 smtppass = config.get('smtppass')
#                 smtpserver = config.get("smtpserver")
#                 smtpport = config.get("smtpport")
#                 receipient = email

#                 msg = MIMEMultipart('alternative')
#                 msg['Subject'] = "check the Link"
#                 msg['From'] = sender
#                 msg['To'] = receipient

#                 text = """Dear !\n Please complete the registration process.
#                             \n Here is the link.\nYour Employee id: %s 
#                             \nhttp://127.0.0.1:5500/index.html#/setpassword
#                              we will replace or solve your issue soon.
#                              """%(employeeId)

#                 part = MIMEText(text, 'plain')

#                 msg.attach(part)
#                 mail = smtplib.SMTP(smtpserver, smtpport)

#                 mail.ehlo()
#                 mail.starttls()

#                 mail.login(sender, smtppass)
#                 mail.sendmail(sender, receipient, msg.as_string())
#                 mail.quit()

#             except smtplib.SMTPException as e:
#                 logger.error(str(e))

#             else:

#                 query = '''update employee e, inventory_allocation a set a.message=%s where e.email=%s and a.employeeId=%s'''

#                 cursor.execute(query,(message,email,employeeId))
#                 g.appdb.commit()

#                 status = 'Success'
#                 response = 'registration mail sent to employee successfully'

#         else:
#             status = 'Failed'
#             response = 'employeeId already signed up'

#         logger.info('Exited from Add_User post method')
#         return jsonify({"status":status, "employeeId":employeeId, "response":response })


class RequestIn(Resource):


    def post(self):
        logger = logging.getLogger("Request inventory for replace")
        logger.info('Entered into Request inventory for replace  POST method')

       # try:
        cursor = g.appdb.cursor()
        req = request.json
        employeeId = req["employeeId"]
        employeeName = req["employeeName"]
        message = req["message"]
        #email = req["email"]
        now = datetime.datetime.now()
        requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")
        form ="%d/%m/%Y"
            
        # except:
        #     logger.warn("there is some issue with the db")

        check = """SELECT e.email FROM  employee e inner join  inventory_allocation a on e.employeeId=a.employeeId
                    WHERE a.employeeId = %s And a.status='requested' """
        cursor.execute(check,(employeeId,))
        verify = cursor.fetchall()
        print(verify)
        if len(verify) != 0:
            try:
                sender = config.get('fromemail')
                #smtppass = base64.decodestring(config.get(b'smtppass'))
                smtppass = config.get('smtppass')
                smtpserver = config.get("smtpserver")
                smtpport = config.get("smtpport")
                receipient = verify[0]['email']
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "check the Link"
                msg['From'] = sender
                msg['To'] = receipient

                text = """Dear %s!\n  of employeeId %s\n %s.
                             """%(employeeName,employeeId,message)

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
                query = """INSERT INTO replacement (allocation_id,message,status,resolvedDate, requestedDate) VALUES (%s,%s,%s,str_to_date(%s,%s),%s);"""
                cursor.execute(query,(req['allocation_id'],req['message'], req['status'],req['resolvedDate'],form, requestedDate))
                g.appdb.commit()

                #newId = cursor.lastrowid
                status = 'Success'
                response = 'registration mail sent to employee successfully'
        else:
            status = 'Failed'
            response = 'employee not requested'

        logger.info('Exiting from Request inventory for replace POST method')
        return make_response(jsonify({"status": status, "response":response}), 201)


    # def put(self):

    #     logger = logging.getLogger("RequestForReplace")
    #     logger.info('Entered into RequestForReplace PUT method')

    #     try:
    #         now = datetime.datetime.now()
    #         requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")
    #         cursor = g.appdb.cursor()
    #         update = request.json
    #         form = '%m/%d/%Y'

    #         query = """UPDATE replacement SET  requestedDate = %s,resolvedDate=str_to_date(%s,%s),
    #                     status = %s, message = %s WHERE allocation_id = %s AND
    #                 flag=1 ;"""

    #         cursor.execute(query, (requestedDate,update['resolvedDate'],form,update['status'],
    #         update['message'], update['allocation_id']))
    #         g.appdb.commit()

    #     except Exception as e:
    #         logger.error(str(e))


    #     logger.info('Exiting from InventoryAllocation PUT method')
    #     return jsonify({"status": "Updated", "allocation_id": update['allocation_id']})


# class RequestBook(Resource):


#     def post(self):
#         logger = logging.getLogger("RequestingBook")
#         logger.info('Entered into RequestingBook POST method')

#         try:
#             cursor = g.appdb.cursor()
#             req = request.json
#             now = datetime.datetime.now()
#             requestedDate = now.strftime("%Y-%m-%d %H:%M:%S")
            
#         except:
#             logger.warn("there is some issue with the db")

#         query = """INSERT INTO book_allocation (employeeId,  book_id, requestedDate, 
#                     status) VALUES (%s,%s,%s,%s);
#                 """
#         cursor.execute(query,(req['employeeId'], req['book_id'], requestedDate, req['status'])) 
#         g.appdb.commit()

#         newId = cursor.lastrowid
#         logger.info('Exiting from RequestingBook POST method')
#         return make_response(jsonify({"status": "success", "response":newId}), 201)


# def put(self):
#         logger = logging.getLogger("AvailableBooks")
#         logger.info('Entered into AvailableBooks PUT method')

#         try:
#             cursor = g.appdb.cursor()
#             bookal = request.json

#         except:
#             logger.warn("there is some issue with the db")

#         if bookal['status'] == "returned":
#             now = datetime.datetime.now()
#             returnDate = now.strftime("%Y-%m-%d %H:%M:%S") 
#             query = """UPDATE book_allocation SET returnDate = %s, 
#                         status = %s WHERE allocation_id = %s;"""

#             cursor.execute(query,(returnDate, bookal['status'],  bookal['allocation_id'] ))
#             g.appdb.commit()
#             di = {"response": bookal['status'], "allocation_id": bookal['allocation_id'],\
#                   "status": "success"}

#         elif bookal['status'] == "granted":
#             now = datetime.datetime.now()
#             assignedDate = now.strftime("%Y-%m-%d")
#             dat = datetime.datetime.strptime(assignedDate, "%Y-%m-%d")
#             dueDate = dat + timedelta(days=bookal['dueDate'])
#             dueDate = str(dueDate)[:-9]

#             query = """UPDATE book_allocation SET assignedDate = %s, status = %s, 
#                     dueDate = %s WHERE allocation_id = %s ;
#                     """
#             cursor.execute(query,(assignedDate,bookal['status'], dueDate, \
#                            bookal['allocation_id']))
#             g.appdb.commit()
#             di = {"status": bookal['status'], "allocation_ id":bookal['allocation_id'],\
#                   "dueDate":dueDate}
        
#         elif bookal['status'] == "declined":
#             query = """UPDATE book_allocation SET status = %s, message = %s WHERE \
#                     allocation_id = %s AND flag = 1;
#                     """
#             cursor.execute(query,(bookal['status'], bookal['message'], \
#                            bookal['allocation_id']))
#             g.appdb.commit()
#             di = {"status": bookal['status'], "allocation_id": bookal['allocation_id'],\
#                   "message": bookal['message']}
#         logger.info('Exiting from AvailableBooks PUT method')
#         return make_response(jsonify(di), 200)