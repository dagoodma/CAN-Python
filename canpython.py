
from tkinter import *
import serial
import re
import threading
import queue
import time
from time import gmtime, strftime

global serialCAN

class CanData( ):
	def __init__(self):
		#Headers is the set of all CAN IDs which have been seen
		self.headers = set()
		#All of the currently applied filters
		self.filters = ()
		#A dictionary which contains all of the most recent messages for each header
		self.messages = {}
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
		self.button1.grid( row = 1, column = 1, columnspan = 1, sticky = E )
		self.button1["command"] = self.quit
		
		self.newMsgs = Button( self, text = "Captured\nMessages", width = 10 )
		self.newMsgs.grid( row = 2, column = 1, rowspan = 1, sticky = E )
		self.newMsgs["command"] = self.capMsg
		
		self.recieve = Button( self, text = "Begin\nReceiving\nMessages", width = 10 )
		self.recieve.grid( row = 3, column = 1, rowspan = 1, sticky = E )
		self.recieve["command"] = self.recievemessage
		
		self.updatefilters = Button( self, text = "Captured\nHeaders", width = 10 )
		self.updatefilters.grid( row = 4, column = 1, rowspan = 1, sticky = E )
		self.updatefilters["command"] = self.capturedHeaders
		
		self.savefilterb = Button( self, text = "Save\nFilters", width = 10 )
		self.savefilterb.grid( row = 5, column = 1, rowspan = 1, sticky = E )
		self.savefilterb["command"] = self.savefilters
		
		self.loadfb = Button( self, text = "load\nFilters", width = 10 )
		self.loadfb.grid( row = 6, column = 1, rowspan = 1, sticky = E )
		self.loadfb["command"] = self.loadfilters
		
		self.beginlog = Button( self, text = "Begin\nLog", width = 10 )
		self.beginlog.grid( row = 7, column = 1, rowspan = 1, sticky = E )
		self.beginlog["command"] = self.beginLoging
		
		self.stoplog = Button( self, text = "End\nLog", width = 10 )
		self.stoplog.grid( row = 8, column = 1, rowspan = 1, sticky = E )
		self.stoplog["command"] = self.endLog
		
		
		#This is the text box which contains the filters
		self.filters = Text( self, width = 90)
		self.filters.grid( row = 2, column = 0,rowspan = 4, sticky = W+E+N+S )
		
		
		self.mylabel = Label(self, text="Header (0x), Initial Offset, Msg, Length (bytes), Endianness , Scale, Skip, Msg, Length, Endianness, Skip...", width = 2, height = 2)
		self.mylabel.grid( row = 1, column = 0, sticky = W+E+N+S )
		
		self.label2 = Label(self, text="Raw Message                                            Decoded Message", width = 2, height = 2)
		self.label2.grid( row = 6, column = 0, sticky = W+E+N+S, rowspan = 1 )
		
		#This is the text box which contains the filtered messsages
		self.output = Text( self, width = 90)
		self.output.grid( row = 7, column = 0, rowspan = 6 , sticky = W+E+N+S )
		
		self.rowconfigure( 1, weight = 1 )
		self.columnconfigure( 1, weight = 1 )
		
		
	#end log closes the logfile and sets the loging flag to be false
	def endLog(self):
		if(self.dataBack.logflag == 1):
			self.dataBack.logflag = 0
			self.dataBack.logfile.close()
			
	#This function updates the filters stored in the back end to match what is showing on the screen
	#I would like to automate this at some point
	def filtersUpdate(self):
		rawfilters = self.filters.get(1.0, END)
		filtersparsed = rawfilters.split("\n")
		self.dataBack.filters = filtersparsed
		print(self.dataBack.filters)
		print(self.dataBack.filters[1])
		
		
	#This function opens the thread which handles the input from the serial port
	#It only needs to be run once, it is run by pressing the Recieve Messages button
	def recievemessage (self):
		print("Starting Second Thread");
		#self.message_queue is the queue which handles passing CAN messages between threads
		x = CanPort(self.message_queue, self)
		th=threading.Thread(target=x.getmessage)
		th.start()
			
		
	#This function allows filters in the window to be saved to a file
	def savefilters (self):
		from tkinter import filedialog
		#filename = filedialog.askopenfilename()
		filename = filedialog.asksaveasfilename() #This opens the built in TK dialog box to save a file
		if(filename != None):
			filterfile = open(filename, 'w') #Opens the provided file name for writing which will replace any existing data
			
			filterfile.write(self.filters.get(1.0, END))  #Writes the filters to the file
			
			filterfile.close() #closes the file

	def loadfilters (self):
		from tkinter import filedialog
		filename = filedialog.askopenfilename()  #This opens the built in TK dialog box to open a file
		if(filename != None):
			filterfile = open(filename, 'r')
			filters = filterfile.read()
			self.filters.delete(1.0,END)  #Clears all the filters for loading
			self.filters.insert(1.0,filters)   #Loads the filters from the file
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
	def parsesecton(self , parsedmsg, readindicie, dataindicie, filter):
		data = parsedmsg.group(4)
		
		a = self.dataBack.filters[filter]
			
		a = a.strip( ' ' )
		filterlist = a.split(",")
		if(filterlist[readindicie+3] == "l"): #if little endian is indicated the indicated number of bits are rearanged and stored in dataflipped
			#print("little endian detected")
			dataflipped = ""
			count = int(filterlist[readindicie+2])
			position = 0
			while(count > 0):
				dataflipped = data[position+dataindicie]+data[position+dataindicie+1]+dataflipped
				position = position + 2
				count = count - 1
		else:  #if little endian is not detected, big endian is assumed and the indicated number of bytes are read off of data and stored in dataflipped
			dataflipped = data[dataindicie:(dataindicie+2*int(filterlist[readindicie+2]))];
			#print("big endian detected")
		#print(dataflipped)
		self.output.insert(END, " "+filterlist[readindicie+1])  #adds the message from the filter to the output window
		#print(filterlist[readindicie+4])
		self.output.insert(END, int(dataflipped, 16)*float(filterlist[readindicie+4]) ) #converts the hex data in dataflipped to decimal and then multiplies by the user defined multiplier, then outputs
		outmsg = ""
		outmsg = filterlist[readindicie+1] + str(int(dataflipped, 16)*float(filterlist[readindicie+4]))
		if(parsedmsg.group(1) == None):
			self.dataBack.messages[parsedmsg.group(2)] = outmsg
		if(parsedmsg.group(2) == None):
			self.dataBack.messages[parsedmsg.group(1)] = outmsg
		
		
		
	#This is a function which handles the parsing of an entire CAN message
	#Most of the actual parsing is done through repeated calls to parssection which parses each section of the message
	def parsemessage (self , parsedmsg, filter):
	
		b = self.dataBack.filters[filter]
			
		list1 = b.split(",")
		#print(parsedmsg.group(2)) #prints the header
		self.dataBack.headers.add(parsedmsg.group(2)) #adds a new header to the set stored in the backend
		#print(self.dataBack.headers);
		outputmessage = ""
		if ((list1[0] == parsedmsg.group(1))or(list1[0] == parsedmsg.group(2))): #checks to see if the header matches
			#print("header detected")
			self.output.insert(END, "\n")
			self.output.insert(END, parsedmsg.groups())
			self.output.insert(END, "\n")
			self.output.insert(END, "Header: ")
			outputmessage = "\nHeader"
			if(parsedmsg.group(1) == None):
				self.output.insert(END, parsedmsg.group(2)) #prints the header if long 
				outputmessage = outputmessage + parsedmsg.group(2)
			if(parsedmsg.group(2) == None):
				self.output.insert(END, parsedmsg.group(1)) #prints the header if short
				outputmessage = outputmessage + parsedmsg.group(1)
			self.output.insert(END, ", BOD: ")
			outputmessage = outputmessage + ", BOD: " + parsedmsg.group(3)
			self.output.insert(END, parsedmsg.group(3)) #prints the number of bytes of data
			readindicie = 1 #readindicie points to the first unread field in the filter
			dataindicie = 0 #data indicie points to the first unread bit of data
			
			#if(parsedmsg.group(1) == None):
			#	self.dataBack.messages[parsedmsg.group(2)] = outputmessage
			#if(parsedmsg.group(2) == None):
			#	self.dataBack.messages[parsedmsg.group(1)] = outputmessage
				
			while(readindicie+5 <= len(list1)): #calls parsesection as long as there are still at least five unread filter fields
				dataindicie = dataindicie + 2*int(list1[readindicie])
				self.parsesecton(parsedmsg, readindicie, dataindicie, filter)
				dataindicie = dataindicie + 2*int(list1[readindicie+2])
				readindicie = readindicie + 5
				
	#Refreshout is triggered whenever a message is present in the message_queue.  It refreshes the GUI.
	def refreshout (self, event):
		#print(self.filterbox)
		#This pulls the unparsed message and writes it to the output field of the GUI
		rawmsg = self.message_queue.get()
		print(rawmsg);
		self.filtersUpdate()
		if(self.dataBack.logflag == 1):
			self.dataBack.logfile.write(rawmsg)
			self.dataBack.logfile.write("      " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
			self.dataBack.logfile.write("\n")
			
		#self.output.insert(END, self.message_queue.get())
		#self.output.insert(END, "                       ")
		#This pulls the parsed message and prints its components to the output field of the GUI
		#self.output.insert(END, self.message_queue.get().groups())
		#self.output.delete(0, END)
		filternumber = 0
		messageparsed = self.message_queue.get()
		while(filternumber < len(self.dataBack.filters)):
			self.parsemessage(messageparsed, filternumber);
			filternumber = filternumber + 1
		#self.output.insert(END, "\n")
		self.output.see(END)
	
	#Opens a new window which displays all of the headers which have been seen
	#Only displays headers up untill time button is pressed --- would like it to be live
	def capturedHeaders(self):
		# create child window
		win = Toplevel()
		# display message
		message = "Captured Headers:"
		Label(win, text=message).pack()
		self.headerstext = Text(win)
		self.headerstext.pack()
		length = len(self.dataBack.headers)
		self.headerstext.insert(END, self.dataBack.headers)
		self.headerstext.insert(END, '\n')
		self.headerstext.insert(END, length)
		while (length > 0):
			self.headerstext.insert(END, '\n')
			self.headerstext.insert(END, self.dataBack.headers[length])
			self.headerstext.insert(END, length)
			length = length - 1
			print("this ran")
		

		#message2 = "this is a test message"
		#self.headerstext.insert(END, message2) #This line works to add text
	
	#Shows the most recent version of messages in a new window
	#Only shows messages captured before the button press -- shuld be made to auto update
	def capMsg(self):
		# create child window
		msgs = Toplevel()
		# display message
		message = "Recently Seen Messages"
		Label(msgs, text=message).pack()
		self.msgstext = Text(msgs)
		self.msgstext.pack()
		self.msgstext.insert(END, self.dataBack.messages)
		

	
	

		
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