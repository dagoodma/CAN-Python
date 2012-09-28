
from tkinter import *
import serial
import re
import threading
import queue

global arduino

class GridDemo( Frame ):
	def update_filters(self):
		a = self.filter1.get()
		a = a.strip( ' ' )
		list1 = a.split(",")
		if len(list1) >= 5:
			print ("If header is ");
			print (list1[0]);
			print (" then skip ");
			print (list1[1]);
			print (" bytes. And interperate the next ");
			print (list1[3]);
			if list1[2] == "I":
				print ( "bytes as an integer")
			
			if list1[2] == "F":
				print ( "bytes as a float")
			
			if list1[2] == "UI":
				print ( "bytes as an unisgned int")

	def decode(self):
		b = self.filter4.get ()
		print (b)
		a = self.filter1.get()
		a = a.strip( ' ' )
		list1 = a.split(",")
		if b.startswith(list1[0]):
			print ("header recognized")
			number = b[len(list1[0]) + int(list1[1]): len(list1[0]) + int(list1[1]) + int(list1[3])]
			print (number)
			if list1[2] == "I":
				print (int(number, 2))
			if list1[2] == "F":
				print ( "bytes as a float")
			if list1[2] == "UI":
				print (number[0])
				if number[0] == '0':
					print (int(number, 2))
				if number[0] == '1':
					print(((int(number, 2) ^ (2**4-1))+1) * -1)

		else: 
			print ("header not recognized");
		

	def recievemessage (self):
		print("Starting Second Thread");
		## Run the thread and the GUI main loop
		x = CanPort(self.message_queue, self)
		th=threading.Thread(target=x.getmessage)
		th.start()
			
		

	def initconnnection (self):
		arduino = serial.Serial("COM3", 9600)
		print ("connection initialized")
		arduino.write("s4")
	
	def refreshout (self, event):
		print ("refreshout ran")
		self.output.insert(INSERT, self.message_queue.get())
		self.output.insert(INSERT, "                       ")
		self.output.insert(INSERT, self.message_queue.get().groups())
		self.output.insert(INSERT, "\n")
		self.output.see(END)
		
	
	def __init__( self ):
		Frame.__init__( self )
		self.master.title( "Grid" )
		
		self.message_queue = queue.Queue()

		self.serialdata = queue.Queue(50)
		
		self.regex = re.compile(r"(?:t([0-9a-fA-F]{3})|T([0-9a-fA-F]{8}))(\d)([^\r]*)")
		
		self.master.rowconfigure( 0, weight = 1 )
		self.master.columnconfigure( 0, weight = 1 )
		self.grid( sticky = W+E+N+S )

		self.button1 = Button( self, text = "Quit", width = 10 )
		self.button1.grid( row = 1, column = 1, columnspan = 1, sticky = W+E+N+S )
		self.button1["command"] = self.quit
		
		self.decodebutton = Button( self, text = "Decode", width = 10 )
		self.decodebutton.grid( row = 7, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.decodebutton["command"] = self.decode
		
		self.recieve = Button( self, text = "Begin\nRecieving\nMessages", width = 10 )
		self.recieve.grid( row = 12, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.recieve["command"] = self.recievemessage
		
		self.updatefilters = Button( self, text = "Update Filters", width = 10 )
		self.updatefilters.grid( row = 2, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.updatefilters["command"] = self.update_filters
		
		self.initcon = Button( self, text = "Initiate\nConnection", width = 10 )
		self.initcon.grid( row = 17, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.initcon["command"] = self.initconnnection
		
		self.rowconfigure( 1, weight = 1 )
		self.columnconfigure( 1, weight = 1 )

		global a
		a = StringVar()
		self.filter1 = Entry(self, textvariable = a)
		self.filter1.grid( row = 3, column = 0, sticky = W+E+N+S )
		a.set("101001,4,I,7,9")
		
		self.filter2 = Entry(self)
		self.filter2.grid( row = 4, column = 0, sticky = W+E+N+S )
		self.filter2.insert( INSERT, "Add a filter..." )
		
		self.filter3 = Entry(self)
		self.filter3.grid( row = 5, column = 0, sticky = W+E+N+S )
		self.filter3.insert( INSERT, "Add a filter..." )
		
		self.filter4 = Entry(self)
		self.filter4.grid( row = 6, column = 0, sticky = W+E+N+S )
		self.filter4.insert( INSERT, "101001101001010100100111010" )
		
		self.filter5 = Entry(self)
		self.filter5.grid( row = 7, column = 0, sticky = W+E+N+S )
		self.filter5.insert( INSERT, "Add a filter..." )
		
		self.filter6 = Entry(self)
		self.filter6.grid( row = 8, column = 0, sticky = W+E+N+S )
		self.filter6.insert( INSERT, "Add a filter..." )
		
		self.filter7 = Entry(self)
		self.filter7.grid( row = 9, column = 0, sticky = W+E+N+S )
		self.filter7.insert( INSERT, "Add a filter..." )
		
		self.filter8 = Entry(self)
		self.filter8.grid( row = 10, column = 0, sticky = W+E+N+S )
		self.filter8.insert( INSERT, "Add a filter..." )
		
		self.filter9 = Entry(self)
		self.filter9.grid( row = 11, column = 0, sticky = W+E+N+S )
		self.filter9.insert( INSERT, "Add a filter..." )
		
		self.filter10 = Entry(self)
		self.filter10.grid( row = 12, column = 0, sticky = W+E+N+S )
		self.filter10.insert( INSERT, "Add a filter..." )
		
		self.filter11 = Entry(self)
		self.filter11.grid( row = 13, column = 0, sticky = W+E+N+S )
		self.filter11.insert( INSERT, "Add a filter..." )
		
		self.filter12 = Entry(self)
		self.filter12.grid( row = 14, column = 0, sticky = W+E+N+S )
		self.filter12.insert( INSERT, "Add a filter..." )
		
		self.filter13 = Entry(self)
		self.filter13.grid( row = 15, column = 0, sticky = W+E+N+S )
		self.filter13.insert( INSERT, "Add a filter..." )
		
		self.filter14 = Entry(self)
		self.filter14.grid( row = 16, column = 0, sticky = W+E+N+S )
		self.filter14.insert( INSERT, "Add a filter..." )
		
		self.filter15 = Entry(self)
		self.filter15.grid( row = 17, column = 0, sticky = W+E+N+S )
		self.filter15.insert( INSERT, "Add a filter..." )
		
		
		self.mylabel = Label(self, text="Header, Initial Offset, Type, Length, Skip, Type, Length, Skip...", width = 2, height = 2)
		self.mylabel.grid( row = 1, column = 0, sticky = W+E+N+S )
		
		self.label2 = Label(self, text="Raw Message                         Decoded Message", width = 2, height = 2)
		self.label2.grid( row = 18, column = 0, sticky = W+E+N+S )
		
		self.output = Text( self, width = 90, height = 15 )
		self.output.grid( row = 19, column = 0, sticky = W+E+N+S )

class CanPort():
	def __init__( self, message_queue, mainwindow ):
		self.message_queue = message_queue
		self.mainwindow = mainwindow
		
	def getmessage (self):
		print("Waiting for new message");
		arduino = serial.Serial("COM3", 9600)
		self.regex = re.compile(r"(?:t([0-9a-fA-F]{3})|T([0-9a-fA-F]{8}))(\d)([^\r]*)")
		while(1):
			msg = arduino.readline()
			msg = msg.decode('utf-8')
			print (msg)
			msgparsed = self.regex.search(msg)
			if msgparsed:
				#print(msgparsed.groups())
				self.message_queue.put(msg)
				self.message_queue.put(msgparsed)
				try:
					self.mainwindow.event_generate("<<rout>>", when = 'tail')
				except TclError:
					break
				
				#GridDemo.output.insert( INSERT, msg )
			else:
				print ("msg failed to parse")
			

	
def main():

	GD = GridDemo()
	
	GD.bind('<<rout>>', GD.refreshout)
	GD.mainloop()
	GD.destroy()

if __name__ == "__main__":
	 main()