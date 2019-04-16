from __future__ import print_function
import serial
import time
import math
import matplotlib.pyplot as plt 
import sqlite3
from sqlite3 import Error
import numpy as np
import struct

def get_time_millis():
	return (int(round(time.time() * 1000)))

def get_time_seconds():
	return (int(round(time.time() * 1000000)))

class read_From_Arduino(object):
	def __init__(self,port,SIZE_STRUCT = 6, verbose = 0):
		self.port = port
		self.millis = get_time_millis()
		self.SIZE_STRUCT = SIZE_STRUCT
		self.verbose = verbose
		self.Data = -1
		self.t_init = get_time_millis()
		self.t = 0
		
		self.port.flushInput()
	
	def read_one_value(self):
		read = False
		while not read:
			myByte = self.port.read(1)
			print(myByte)
			if myByte == b'S':
				packed_data = self.port.read(self.SIZE_STRUCT)
				myByte = self.port.read(1)
				if myByte == b'E':
					self.t = (get_time_millis() - self.t_init)/1000.0
					unpacked_data = struct.unpack('<hhh',packed_data)
					print(unpacked_data)
					print(myByte)
					current_time = get_time_millis()
					time_elapsed = current_time - self.millis
					self.millis = current_time

					read = True

					self.Data = np.array(unpacked_data)
					return(True)
				
		return(False)
		 

	def get_X(self):
		self.read_one_value()
		return self.Data[0]

	def get_Y(self):
		self.read_one_value()
		return self.Data[1]

	def get_Yaw(self):
		self.read_one_value()
		return self.Data[2]

def create_connection(db_file):
	"""create conenction to the SQLite database:
	:param db_file: database file
	:return: Connection object or None
	"""

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
	return None

def create_data_Log(conn,data_Log):
	"""Create a new data log into the Distance_Data table
	:param conn:
	:param: data_Log
	:return:None
	"""
	#conn = sqlite3.connect("distance.db")
	try:
		sql = """INSERT INTO Distance_Data(time,data_X,data_Y,data_Yaw)
		         VALUES(?,?,?,?)"""
		curs = conn.cursor()
		#conn.commit()
		print("Comitted")
		curs.execute(sql,data_Log)
		print("Executed")
		#conn.close()
		#print("Closed")	
		return None
	except Error as e:
		print(e)
		print("Error from data log")
	return None

def get_Data():
	conn = sqlite3.connect("distance.db")
	curs = conn.cursor()
	conn.commit()
	data_T,data_X,data_Y,data_Yaw = 0, 0, 0, 0
	for row in curs.execute("SELECT * FROM Distance_Data"):
		data_T = row[1]
		data_X = row[2]
		data_Y = row[3]
		data_Yaw = row[4]
	conn.close()
	return data_T,data_X,data_Y,data_Yaw
	
fig = plt.figure() 
ax = fig.add_subplot(3,1,1)
ay = fig.add_subplot(3,1,2)
az = fig.add_subplot(3,1,3)
fig.show()
x1,y1 = [],[]
x2,y2 = [],[]
x3,y3 = [],[]

def plot_graph():
	data_T, data_X, data_Y, data_Yaw = get_Data()
	#while True:
	x1.append(data_T)
	y1.append(data_X)
	ax.plot(x1,y1,color = 'b')
	fig.canvas.draw()

	x2.append(data_T)
	y2.append(data_Y)
	ay.plot(x2,y2,color = 'b')
	fig.canvas.draw()

	x3.append(data_T)
	y3.append(data_Yaw)
	az.plot(x3,y3,color = 'b')
	fig.canvas.draw()
	
	time.sleep(0.001)


def main():
	then = time.time()
	Arduino = serial.Serial(port = '/dev/ttyACM0',baudrate = 9600, timeout = 0.5)
	read_From_Arduino_Instance = read_From_Arduino(Arduino, verbose = 10)	
	global flag 
	flag = 0
	database = "distance.db"
	#create a database connection
	conn = create_connection(database)
	conn.commit()	
	while True:
		now = time.time()
		data_T = now - then
		data_X = read_From_Arduino_Instance.get_X()
		data_Y = read_From_Arduino_Instance.get_Y()
		data_Yaw = read_From_Arduino_Instance.get_Yaw()
		with conn:
			data_Log = (int(data_T),int(data_X),int(data_Y),int(data_Yaw))
			if flag == 0:
				create_data_Log(conn,data_Log)
				flag = 1
			if flag == 1:
				plot_graph()
				flag = 0
	
        
if __name__ == '__main__':
    main()
