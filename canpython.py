
from tkinter import *
import serial
import re
import threading
import queue
import time

global serialCAN

class CanData( ):
	def __init__(self):
		#Headers is the set of all CAN IDs which have been seen
		self.headers = set()
		#All of the currently applied filters
		self.filters = []
		#A dictionary which contains all of the most recent messages for each header
		self.messages = []
		#A flag to indicate if loging is enabled
		self.logflag = 0
		#The file where loging will takeplace if it is turned on
		self.logfile = None
		

class GridDemo( Frame ):

	#This initializes the Tkinter GUI
	def __init__( self, dataBack ):
		Frame.__init__( self )
		self.master.title( "CAN-USB" )
		
		self.dataBack = dataBack
		
		self.message_queue = queue.Queue()

		self.serialdata = queue.Queue(50)
		
		self.regex = re.compile(r"(?:t([0-9a-fA-F]{3})|T([0-9a-fA-F]{8}))(\d)([^\r]*)")
		
		self.master.rowconfigure( 0, weight = 1 )
		self.master.columnconfigure( 0, weight = 1 )
		self.grid( sticky = W+E+N+S )

		self.button1 = Button( self, text = "Quit", width = 10 )
		self.button1.grid( row = 1, column = 1, columnspan = 1, sticky = W+E+N+S )
		self.button1["command"] = self.quit
		
		self.filterbox = IntVar()
		self.decodebutton = Checkbutton( self, text = "Apply Filters", width = 10, variable = self.filterbox, onvalue = 1, offvalue = 0 )
		self.decodebutton.grid( row = 7, column = 1, rowspan = 5, sticky = W+E+N+S )
		
		self.recieve = Button( self, text = "Begin\nReceiving\nMessages", width = 10 )
		self.recieve.grid( row = 12, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.recieve["command"] = self.recievemessage
		
		self.updatefilters = Button( self, text = "Captured\nHeaders", width = 10 )
		self.updatefilters.grid( row = 2, column = 1, rowspan = 5, sticky = W+E+N+S )
		self.updatefilters["command"] = self.capturedHeaders
		
		self.savefilterb = Button( self, text = "Save\nFilters", width = 10 )
		self.savefilterb.grid( row = 17, column = 1, rowspan = 2, sticky = W+E+N+S )
		self.savefilterb["command"] = self.savefilters
		
		self.loadfb = Button( self, text = "load\nFilters", width = 10 )
		self.loadfb.grid( row = 19, column = 1, rowspan = 2, sticky = W+E+N+S )
		self.loadfb["command"] = self.loadfilters
		
		self.beginlog = Button( self, text = "Begin\nLog", width = 10 )
		self.beginlog.grid( row = 22, column = 1, rowspan = 2, sticky = W+E+N+S )
		self.beginlog["command"] = self.beginLoging
		
		self.stoplog = Button( self, text = "End\nLog", width = 10 )
		self.stoplog.grid( row = 25, column = 1, rowspan = 2, sticky = W+E+N+S )
		self.stoplog["command"] = self.endLog
		
		self.rowconfigure( 1, weight = 1 )
		self.columnconfigure( 1, weight = 1 )

		global a
		a = StringVar()
		self.filter1 = Entry(self, textvariable = a)
		self.filter1.grid( row = 3, column = 0, sticky = W+E+N+S )
		a.set("07B,0,Voltage on temp sensor: ,2,l,.001,0,temp: ,2,l,.01,0,d rail v: ,2,l,.01,0,rail v: ,2,l,.01")
		
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
		
		
		self.mylabel = Label(self, text="Header (0x), Initial Offset, Msg, Length (bytes), Endianness , Scale, Skip, Msg, Length, Endianness, Skip...", width = 2, height = 2)
		self.mylabel.grid( row = 1, column = 0, sticky = W+E+N+S )
		
		self.label2 = Label(self, text="Raw Message                                            Decoded Message", width = 2, height = 2)
		self.label2.grid( row = 18, column = 0, sticky = W+E+N+S )
		
		self.output = Text( self, width = 90, height = 15 )
		self.output.grid( row = 19, column = 0, sticky = W+E+N+S )
		
		
	
	def endLog(self):
		if(self.dataBack.logflag == 1):
			self.dataBack.logflag = 0
			self.dataBack.logfile.close()
		
	
	#This function needs to be updated or discarded before being commented
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


		
	#This function opens the thread which handles the input from the serial port
	#It only needs to be run once, it is run by pressing the Recieve Messages button
	def recievemessage (self):
		print("Starting Second Thread");
		#self.message_queue is the queue which handles passing CAN messages between threads
		x = CanPort(self.message_queue, self)
		th=threading.Thread(target=x.getmessage)
		th.start()
			
		
	#This function is depreciated and shuld probably be deleated.  Its functionality shuld be (Has been) moved to the CANport thread
	def savefilters (self):
		from tkinter import filedialog
		#filename = filedialog.askopenfilename()
		filename = filedialog.asksaveasfilename() #This opens the built in TK dialog box to save a file
		if(filename != None):
			filterfile = open(filename, 'w') #Opens the provided file name for writing which will replace any existing data
			
			filterfile.write(self.filter1.get())  #Writes the filter to the file folowed by a new line charicter
			filterfile.write('\n')
			filterfile.write(self.filter2.get())
			filterfile.write('\n')
			filterfile.write(self.filter3.get())
			filterfile.write('\n')
			filterfile.write(self.filter4.get())
			filterfile.write('\n')
			filterfile.write(self.filter5.get())
			filterfile.write('\n')
			filterfile.write(self.filter6.get())
			filterfile.write('\n')
			filterfile.write(self.filter7.get())
			filterfile.write('\n')
			filterfile.write(self.filter8.get())
			filterfile.write('\n')
			filterfile.write(self.filter9.get())
			filterfile.write('\n')
			filterfile.write(self.filter10.get())
			filterfile.write('\n')
			filterfile.write(self.filter11.get())
			filterfile.write('\n')
			filterfile.write(self.filter12.get())
			filterfile.write('\n')
			filterfile.write(self.filter13.get())
			filterfile.write('\n')
			filterfile.write(self.filter14.get())
			filterfile.write('\n')
			filterfile.write(self.filter15.get())
			filterfile.write('\n')
			
			filterfile.close() #closes the file

	def loadfilters (self):
		from tkinter import filedialog
		filename = filedialog.askopenfilename()  #This opens the built in TK dialog box to open a file
		if(filename != None):
			filterfile = open(filename, 'r')
			filtertext = filterfile.read()
			filters = filtertext.split("\n")
			
			self.filter1.delete(0,END)  #Clears all the filters for loading
			self.filter2.delete(0,END)
			self.filter3.delete(0,END)
			self.filter4.delete(0,END)
			self.filter5.delete(0,END)
			self.filter6.delete(0,END)
			self.filter7.delete(0,END)
			self.filter8.delete(0,END)
			self.filter9.delete(0,END)
			self.filter10.delete(0,END)
			self.filter11.delete(0,END)
			self.filter12.delete(0,END)
			self.filter13.delete(0,END)
			self.filter14.delete(0,END)
			self.filter15.delete(0,END)
			
			self.filter1.insert(0,filters[0])   #Loads the filters from the file
			self.filter2.insert(0,filters[1])
			self.filter3.insert(0,filters[2])
			self.filter4.insert(0,filters[3])
			self.filter5.insert(0,filters[4])
			self.filter6.insert(0,filters[5])
			self.filter7.insert(0,filters[6])
			self.filter8.insert(0,filters[7])
			self.filter9.insert(0,filters[8])
			self.filter10.insert(0,filters[9])
			self.filter11.insert(0,filters[10])
			self.filter12.insert(0,filters[11])
			self.filter13.insert(0,filters[12])
			self.filter14.insert(0,filters[13])
			self.filter15.insert(0,filters[14])
			
			filterfile.close() #closes the filter save file

	def beginLoging (self):
		from tkinter import filedialog
		filename = filedialog.asksaveasfilename() #This opens the built in TK dialog box to save a file
		if(filename != None):
			logfile = open(filename, 'w') #Opens the provided file name for writing which will replace any existing data
			self.dataBack.logflag = 1
			self.dataBack.logfile = logfile
		
	#This is a function which parses the repeating section of the filter
	#parsedmsg is the CAN message broken up into it's components
	#readindicie indicates which of the repeating section is being parsed
	#dataindicie points to the first unparsed piece of data in the CAN message
	def parsesecton(self , parsedmsg, readindicie, dataindicie):
		data = parsedmsg.group(4)
		a = self.filter1.get() #read in a filter, remove spaces and seperate it at commas
		a = a.strip( ' ' )
		filterlist = a.split(",")
		if(filterlist[readindicie+3] == "l"): #if little endian is indicated the indicated number of bits are rearanged and stored in dataflipped
			print("little endian detected")
			dataflipped = ""
			count = int(filterlist[readindicie+2])
			position = 0
			while(count > 0):
				dataflipped = data[position+dataindicie]+data[position+dataindicie+1]+dataflipped
				position = position + 2
				count = count - 1
		else:  #if little endian is not detected, big endian is assumed and the indicated number of bytes are read off of data and stored in dataflipped
			dataflipped = data[dataindicie:(dataindicie+2*int(filterlist[readindicie+2]))];
			print("big endian detected")
		print(dataflipped)
		self.output.insert(END, " "+filterlist[readindicie+1])  #adds the message from the filter to the output window
		print(filterlist[readindicie+4])
		self.output.insert(END, int(dataflipped, 16)*float(filterlist[readindicie+4]) ) #converts the hex data in dataflipped to decimal and then multiplies by the user defined multiplier, then outputs

		
		
	#This is a function which handles the parsing of an entire CAN message
	#Most of the actual parsing is done through repeated calls to parssection which parses each section of the message
	def parsemessage (self , parsedmsg):
		b = self.filter1.get() #imports the user's filter then splits it based on commas and stores the list to list1
		list1 = b.split(",")
		print(parsedmsg.group(2))
		self.dataBack.headers.add(parsedmsg.group(2)) #adds a new header to the set stored in the backend
		#print(self.dataBack.headers);
		if ((list1[0] == parsedmsg.group(1))or(list1[0] == parsedmsg.group(2))): #checks to see if the header matches
			print("header detected")
			self.output.insert(END, "\n")
			self.output.insert(END, parsedmsg.groups())
			self.output.insert(END, "\n")
			self.output.insert(END, "Header: ")
			if(parsedmsg.group(1) == None):
				self.output.insert(END, parsedmsg.group(2)) #prints the header if long 
			if(parsedmsg.group(2) == None):
				self.output.insert(END, parsedmsg.group(1)) #prints the header if short
			self.output.insert(END, ", BOD: ")
			self.output.insert(END, parsedmsg.group(3)) #prints the number of bytes of data
			readindicie = 1 #readindicie points to the first unread field in the filter
			dataindicie = 0 #data indicie points to the first unread bit of data
			while(readindicie+5 <= len(list1)): #calls parsesection as long as there are still at least five unread filter fields
				dataindicie = dataindicie + 2*int(list1[readindicie])
				self.parsesecton(parsedmsg, readindicie, dataindicie)
				dataindicie = dataindicie + 2*int(list1[readindicie+2])
				readindicie = readindicie + 5
				
	#Refreshout is triggered whenever a message is present in the message_queue.  It refreshes the GUI.
	def refreshout (self, event):
		#print(self.filterbox)
		if(self.filterbox):
			#This pulls the unparsed message and writes it to the output field of the GUI
			rawmsg = self.message_queue.get()
			print(rawmsg);
			if(self.dataBack.logflag == 1):
				self.dataBack.logfile.write(rawmsg)
				self.dataBack.logfile.write("\n")
				
			#self.output.insert(END, self.message_queue.get())
			#self.output.insert(END, "                       ")
			#This pulls the parsed message and prints its components to the output field of the GUI
			#self.output.insert(END, self.message_queue.get().groups())
			#self.output.delete(0, END)
			self.parsemessage(self.message_queue.get());
			#self.output.insert(END, "\n")
			self.output.see(END)
	
	def capturedHeaders(self):
		# create child window
		win = Toplevel()
		# display message
		message = "Captured Headers:"
		Label(win, text=message).pack()
		self.headerstext = Text(win)
		self.headerstext.pack()
		self.headerstext.insert(END, self.dataBack.headers)

		#message2 = "this is a test message"
		#self.headerstext.insert(END, message2) #This line works to add text
		

	
	

		
#CanPort is the thread which handles direct comunication with the CAN device. CanPort initializes the connection and then recieves
#and parses standard CAN messages. These messages are then passed to the Grid thread via the message_queue queue where they are
#added to the GUI
class CanPort():
	def __init__( self, message_queue, mainwindow ):
		self.message_queue = message_queue
		self.mainwindow = mainwindow
		
	def getmessage (self):
		print("Waiting for new message");
		#opens a serial connection called serialCAN on COM5 at 57600 Baud code which allows for a selection of COM ports shuld be added
		serialCAN = serial.Serial("COM5", 57600)
		#compiles a regular expression to parse both the short and long form messages as defined in the CAN-USB manual
		self.regex = re.compile(r"(?:t([0-9a-fA-F]{3})|T([0-9a-fA-F]{8}))(\d)([^\r]*)")
		#determines that the serial port has opened correctly
		print(serialCAN.isOpen())
		temp = None
		#initializes the CAN-USB device to 250Kbit/s which is the maritime standard
		#if the CAN device is not closed properly this may take up to ~20 seconds to clear the serial buffer of old messages
		while(temp != b'\r'):
			time.sleep(.2)
			#initialize the CAN-USB device at 250Kbits/s
			serialCAN.write(b'S5\r')
			print(temp)
			temp = serialCAN.read()
		time.sleep(1)
		#Opens the CAN port to begin reciveing messages
		serialCAN.write(b'O\r')
		time.sleep(1)
		#Sets the CAN port to disable timestamps
		serialCAN.write(b'Z0\r')
		while(1):
			charicter = None
			msg = b""
			#Reads in charicters from the serial stream until a \r is encounterd which demarks the end of a CAN message
			while(charicter != b'\r'):
				charicter = serialCAN.read()
				#appends the newly read charicter to the message being built
				msg = msg + bytes(charicter)
			msg = msg.decode('utf-8')
			#print (msg)
			#Trys the recieved message against the regular expression to see if message matches the recognized format
			msgparsed = self.regex.search(msg)
			#if the message is of the recognized format it is added to the message queue along with all of the parsed groups
			if msgparsed:
				#print(msgparsed.groups())
				self.message_queue.put(msg)
				self.message_queue.put(msgparsed)
				try:
					self.mainwindow.event_generate("<<rout>>", when = 'tail')
				except TclError:
					#Tells the CAN-USB device to close the CAN port
					serialCAN.write(b'C\r')
					#Terminates the serial connection
					serialCAN.close()
					break
			else:
				print ("msg failed to parse")
			

	
def main():
	backend = CanData()
	GD = GridDemo(backend)
	
	GD.bind('<<rout>>', GD.refreshout)
	GD.mainloop()
	GD.destroy()

if __name__ == "__main__":
	 main()