from flask import Flask, jsonify, abort, make_response, request, g
from flask_restful import reqparse
from flask_restful import Resource

import datetime
import logging
import pymysql
import json 
import logging.config
import sys

        
class Inventories(Resource):

    def get(self):
        # This GET method will fetch a single inventory details based on the inventory id
        logger = logging.getLogger("inventories")
        logger.info('Entered into inventories GET method')

        if "inventory_id" in request.args:

            try:
                inventory_id = request.args.get('inventory_id')
                token = request.args.get('token')
                cursor = g.appdb.cursor()
                
            except:
                logger.warn("there is some issue with the db")
            
            query1 = """SELECT deviceId FROM inventories WHERE inventory_id = %s;"""
            cursor.execute(query1, ( inventory_id,))
            deviceId = cursor.fetchall()
            
            query = """SELECT i.inventory_id, dd.deviceName, (SELECT COUNT(*) FROM inventories) AS total_inventories, pb.brandName, i.assetId, i.product_price, 
                        DATE_FORMAT(i.purchase_date,'%%m/%%d/%%Y') AS purchase_date,i.vendorId, i.brandId, i.deviceId, i.contract_period, i.serial_number, va.vendorName, va.address, va.contact 
    					
                        FROM inventories i,vendor_address va,device_details dd,product_brand pb WHERE i.vendorId = va.vendorId 
                        AND i.deviceId = dd.deviceId AND i.brandId= pb.brandId AND flag = 1 AND inventory_id=%s;"""
            
            cursor.execute(query,(inventory_id,))
            invent = cursor.fetchall()
            return jsonify({"status": "success","response": invent})

        else:
            return jsonify({"status": "failure","response": "allocation_id not found"})          

        logger.info('Exiting from Inventories GET method')
        

    def post(self):
        # Using this Post Method we can add a new inventory
        logger = logging.getLogger("Inventories")
        logger.info('Entered into Inventories POST method')

        try:
            now = datetime.datetime.now()
            entry_date = now.strftime("%Y-%m-%d %H:%M:%S")
            cursor = g.appdb.cursor()
            inv = request.json
            form ="%d/%m/%Y"
                
        except:
            logger.warn("there is some issue with the db")


        if 'vendorName' in inv.keys():
            dic ={}
            query = '''SELECT vendorId from vendor_address WHERE LOWER(vendorName) = LOWER(%s)'''
            cursor.execute(query,(inv['vendorName']))
            result = cursor.fetchall()

            vendorId = result[0]['vendorId'] if len(result)>0 else 0
      
            if vendorId == 0:
                query1 = """INSERT INTO vendor_address (vendorName, address, contact) 
                            VALUES (%s,%s,%s);"""
                cursor.execute(query1,(inv["vendorName"],inv["address"],inv["contact"]))
                g.appdb.commit()    
                inv['vendorId'] = cursor.lastrowid

            else:
                inv['vendorId'] = vendorId

        if 'deviceName' in inv.keys():
            
            query = '''SELECT deviceId FROM device_details WHERE LOWER(deviceName) = LOWER(%s)'''
            cursor.execute(query,(inv['deviceName']))
            result = cursor.fetchall()

            deviceId = result[0]['deviceId'] if len(result)>0 else 0
      
            if deviceId == 0:
                query1 = """INSERT INTO device_details (deviceName) VALUES (%s);"""
                cursor.execute(query1,(inv["deviceName"]))
                g.appdb.commit()    
                inv['deviceId'] = cursor.lastrowid

            else:
                inv['deviceId'] = deviceId

        if 'brandName' in inv.keys():
            
            query = '''SELECT brandId from product_brand WHERE LOWER(brandName) = LOWER(%s)'''
            cursor.execute(query,(inv['brandName']))
            result = cursor.fetchall()
            print(result)

            brandId = result[0]['brandId'] if len(result)>0 else 0
            print(brandId)
            if brandId == 0:
                query1 = """INSERT INTO product_brand (brandName) VALUES (%s);"""
                cursor.execute(query1,(inv["brandName"]))
                g.appdb.commit()    
                inv['brandId'] = cursor.lastrowid

            else:
                inv['brandId'] = brandId


        query = """INSERT INTO inventories (assetId, serial_number, product_price, 
                    purchase_date, contract_period, entry_date, vendorId, 
                    deviceId, brandId) 
                    VALUES (%s,%s,%s,str_to_date(%s,%s),%s,%s,%s,%s,%s);"""
        
        cursor.execute(query,(inv['assetId'], inv['serial_number'], 
                        inv['product_price'], inv['purchase_date'], form, 
                        inv['contract_period'],entry_date,int(inv['vendorId']), 
                        int(inv['deviceId']),int(inv['brandId'])))
        g.appdb.commit()
        newId = cursor.lastrowid

        print(newId)
        
        logger.info('Exiting from Inventories POST method')
        return jsonify({"status": "success", "new Inventory_id":newId})


    def put(self):
        #This PUT method used to make changes to a particular inventory based on the inventory_id
        logger = logging.getLogger("Inventories")
        logger.info('Entered into Inventories PUT method')


        try:
            cursor = g.appdb.cursor()
            form = '%m/%d/%Y'
            updt = request.json

        except:
            logger.warn("there is some issue with the db")
            
        query = """UPDATE inventories SET assetId = %s, serial_number = %s, 
                    product_price = %s, purchase_date = str_to_date(%s,%s), 
                    contract_period = %s, vendorId = %s, deviceId = %s, 
                    brandId = %s WHERE inventory_id = %s;"""

        cursor.execute(query, (updt['assetId'], updt['serial_number'], 
                        updt['product_price'], updt['purchase_date'], form,
                        updt['contract_period'], updt['vendorId'], updt['deviceId'], 
                        updt['brandId'], updt['inventory_id']))
        g.appdb.commit()

        logger.info('Exiting from Inventories PUT method')
        return jsonify({"status": "Updated", "inventory_id": updt['inventory_id']}) 
         

    def delete(self, inventory_id):
        #This delete method will delete single inventory details based on the inventory Id 
        logger = logging.getLogger("Inventories")
        logger.info('Entered into Inventories DELETE method')

        try:
            now = datetime.datetime.now()
            cursor = g.appdb.cursor()

            query = """UPDATE inventory_allocation SET flag = 0 WHERE inventoryId = %s;"""
            cursor.execute(query, (inventory_id, ))
            g.appdb.commit()

           
            query = """UPDATE inventories SET flag = 0 where inventory_id = %s ;"""
            cursor.execute(query, (inventory_id, ))
            g.appdb.commit()
        
        except:
            logger.warn("there is some issue with the db")

        logger.info('Exiting from Inventories PUT method')
        return jsonify({"status": "Updated", "response": "deleted"})


class InventoryList(Resource):

    def get(self):
        #This GET method will fetch all the inventory details as a list
        logger = logging.getLogger("Inventories")
        logger.info('Entered into Inventories GET method')

        if "page" and "count" in request.args:

            try:
                cursor = g.appdb.cursor()
                page = int(request.args.get('page'))
                count = int(request.args.get('count'))
                start = (page-1) * count
                
            except:
                logger.warn("there is some issue with the db")
        

            total = """SELECT i.inventory_id, dd.deviceName, pb.brandName, i.assetId, i.product_price, 
                        i.contract_period, i.serial_number, va.vendorName, va.address, va.contact, i.serial_number,
                        DATE_FORMAT(i.purchase_date,'%%m/%%d/%%Y') AS purchase_date  FROM 
                        inventories i, device_details dd, vendor_address va, product_brand pb
                        WHERE va.vendorId = i.vendorId AND dd.deviceId = i.deviceId AND i.brandId = pb.brandId AND i.flag=1
                        AND i.inventory_id NOT IN (SELECT inventoryId FROM inventory_allocation WHERE flag =1)
                        """
            cursor.execute(total,)
            totalcount = len(cursor.fetchall())

            query = total + """ LIMIT %s,%s;"""

            cursor.execute(query, (start, count))
            inventory = cursor.fetchall()
            
            total_pages = totalcount/count if totalcount>0 else 0

            logger.info('Exiting from Inventories GET method')
            return jsonify({"status" : "success", "response": inventory, 
                             "total_inventories" : totalcount, "per_page" : count, 
                             "page" : page, "total_pages":total_pages})
        else:
            return jsonify({"status" : "failure", "response": "page and count not found"})
                


class MyInventory(Resource):

    def get(self):
        #This GET method will fetch inventory details of a particular employee 
        logger = logging.getLogger("MyInventory")
        logger.info('Entered into MyInventory GET method')

        if "employeeId" in request.args:

            try:
                employeeId = request.args.get('employeeId')
                cursor = g.appdb.cursor()
                
            except:
                logger.warn("there is some issue with the db")

            query = """SELECT  dd.deviceName, ia.status, i.serial_number, i.assetId, 
                        ia.allocation_id, DATE_FORMAT(ia.dateAssigned ,'%%m/%%d/%%Y') 
                        AS dateAssigned FROM inventory_allocation ia
                        INNER JOIN inventories i ON i.inventory_id = ia.inventoryId 
                        INNER JOIN device_details dd ON (i.deviceId = dd.deviceId) 
                        WHERE ia.flag = 1 AND  employeeId = %s"""
            
            cursor.execute(query, (employeeId, ))
            inventory = cursor.fetchall()
            return jsonify({"status" : "success", "response" : inventory})
        else:
            return jsonify({"status" : "failure", "response" : "employee id not found"})
                
        logger.info('Exiting from MyInventory GET method')
        


class VendorAddress(Resource):

    def get(self):
        #: This GET method will fetch all vendor addresses as a list
        logger = logging.getLogger("VendorAddress")
        logger.info('Entered into VendorAddress GET method')

        try:
            cursor = g.appdb.cursor()

        except:
            logger.warn("there is some issue with the db")

        query = """SELECT * FROM vendor_address;"""
        cursor.execute(query,)
        address = cursor.fetchall()

        logger.info('Exiting from VendorAddress GET method')
        return jsonify({"status" : "success", "response" : address})


class DeviceDetails(Resource):
    
    def get(self):
        #: This GET method will fetch all devices as a list
        logger = logging.getLogger("DeviceDetails")
        logger.info('Entered into device details GET method')

        try:
            cursor = g.appdb.cursor()

        except:
            logger.warn("there is some issue with the db")

        query = """SELECT * FROM device_details;"""
        cursor.execute(query,)
        devices = cursor.fetchall()

        logger.info('Exiting from device details GET method')
        return jsonify({"status" : "success","devices" : devices})


class ProductBrand(Resource):

    def get(self):
        #: This GET method will fetch all product brands as a list
        logger = logging.getLogger("ProductBrand")
        logger.info('Entered into product brand GET method')

        try:
            cursor = g.appdb.cursor()

        except:
            logger.warn("there is some issue with the db")

        query = """SELECT * FROM product_brand;"""
        cursor.execute(query,)
        brands = cursor.fetchall()
        names = [brand['brandName'] for brand in brands]

        logger.info('Exiting from product brand GET method')
        return jsonify({"status" : "success","brands" : brands, 'names':names})


class TotalInventoryDetails(Resource):

    def get(self):
        #: This GET method will fetch all product brands as a list
        logger = logging.getLogger("TotalInventoryDetails")
        logger.info('Entered into total inventory details GET method')

        try:
            cursor = g.appdb.cursor()

        except:
            logger.warn("there is some issue with the db")
        totalInventory = []
        devicequery = '''SELECT deviceId, deviceName FROM device_details'''
        cursor.execute(devicequery,)
        devices = cursor.fetchall()

        for device in devices:

            inventory = {}
            availabequery = '''SELECT COUNT(*) as total FROM inventories WHERE deviceId = %s AND flag=1'''
            cursor.execute(availabequery,(device['deviceId']))
            total = cursor.fetchone()

            print(total)
            
            allotedquery = '''SELECT count(*) as alloted FROM inventory_allocation ia INNER JOIN inventories inv WHERE ia.inventoryId= inv.inventory_id AND inv.deviceId=%s AND ia.flag=1 AND inv.flag=1'''
            cursor.execute(allotedquery, (device['deviceId']))
            alloted = cursor.fetchone()
            print(alloted)

            inventory['available'] = total['total'] - alloted['alloted'] 
            inventory.update(device)
            inventory.update(total)
            inventory.update(alloted)
            totalInventory.append(inventory)
            #print(totalInventory)
        
        logger.info('Exiting from total inventory details GET method')
        return jsonify({"status" : "success", "totalInventory" : totalInventory})


class AllotedDetails(Resource):

    def get(self):
        #: This GET method will fetch all product brands as a list
        logger = logging.getLogger("AllotedDetails")
        logger.info('Entered into alloted details GET method')

        try:
            cursor = g.appdb.cursor()
            deviceId = request.args.get('deviceId')

        except:
            logger.warn("there is some issue with the db")

        query = """SELECT * FROM inventory_allocation ia INNER JOIN inventories inv
                 WHERE ia.inventoryId= inv.inventory_id AND inv.deviceId=%s AND ia.flag=1 AND inv.flag=1"""
        
        cursor.execute(query, (deviceId,))
        devices = cursor.fetchall()

        logger.info('Exiting from alloted details GET method')
        return jsonify({"status" : "success", "Alloted": devices})


class AvailableDetails(Resource):

    def get(self):
        
        #: This GET method will fetch all product brands as a list
        logger = logging.getLogger("AvailableInventoryDetails")
        logger.info('Entered into available inventory details GET method')

        try:
            cursor = g.appdb.cursor()
            deviceId = request.args.get('deviceId')

        except:
            logger.warn("there is some issue with the db")
    
        query = """SELECT i.serial_number, i.assetId, dd.deviceName, pb.brandName 
            FROM inventories i, device_details dd, product_brand pb
            WHERE i.deviceId = %s AND i.inventory_id 
            NOT IN (SELECT inventoryId FROM inventory_allocation WHERE flag=1)
            AND dd.deviceId = i.deviceId AND pb.brandId = i.brandId AND i.flag =1"""
    
        cursor.execute(query, (deviceId,))
        available = cursor.fetchall()

        logger.info('Exiting from available inventory details GET method')
        return jsonify({"status" : "success", "available": available})

class DeleteInventory(Resource):

    def delete(self, deviceId):
            logger = logging.getLogger("DeleteEmployee")
            logger.info('Entered into DeleteEmployee DELETE method')

           
            query = """ UPDATE  inventories SET  flag = 0 
                        WHERE deviceId = %s;"""
            cursor.execute(query,(deviceId))
            g.appdb.commit()


            logger.info('Exiting from DeleteEmployee DELETE method')
            return make_response(jsonify({"status": "relieved", "response": "employee successfully relieved"}), 200)


