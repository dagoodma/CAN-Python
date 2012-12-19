CAN-Python
==========

Getting CAN-Python Working
Connect cables
Determine COM port number and correct �COM5� in getmessage() at approximately line 300
Launch the program
Add filters to the filters widnow using the correct formating
Click update filters
Click begin receiving messages on the right hand side
Raw CAN messages will appear in the output window, followed by a parsed version if they match the filter

Filters must be of the form: Header (0x), Initial Offset, Msg, Length (bytes), Endianness , Scale, Skip, Msg, Length, Endianness, Skip...

Spaces in filters are ignored and parsing takes place at commas

An example filter:
07B,0,Voltage on temp sensor: ,2,lu,.001,0,temp: ,2,lu,.01,0,d rail v: ,2,lu,.01,0,rail v: ,2,l,.01

This filter parses the default message spit out by the CAN node. It looks for the header 07B then skips 0 bytes prints the header �Voltage on temp sensor:�,and interprets the next two bytes as little endian unsigned which it then converts to binary and outputs. Little endian is indicated by denoted with an �l�.  Anything other than an �l� is interpreted as big endian. The pattern then repeats with skip 0 bytes (which may or may not be working), print �temp��ect
