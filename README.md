CAN-Python
==========

Getting CAN-Python Working
Connect cables
Determine COM port number and correct “COM5” in getmessage() at approximately line 260
Launch the program
Click begin receiving messages on the right hand side
Raw CAN messages will appear in the output window, followed by a parsed version if they match the filter

Filters must be of the form: Header (0x), Initial Offset, Msg, Length (bytes), Endianness , Scale, Skip, Msg, Length, Endianness, Skip...

Spaces in filters are ignored and parsing takes place at commas

An example filter:
07B,0,Voltage on temp sensor: ,2,l,.001,0,temp: ,2,l,.01,0,d rail v: ,2,l,.01,0,rail v: ,2,l,.01

This filter parses the default message spit out by the CAN node. It looks for the header 07B then skips 0 bytes prints the header “Voltage on temp sensor:”,and interprets the next two bytes as little endian which it then converts to binary and outputs. Little endian is indicated by denoted with an ‘l’.  Anything other than an ‘l’ is interpreted as big endian. The pattern then repeats with skip 0 bytes (which may or may not be working), print “temp”…ect



Issues/Bugs(to be fixed):

-Only filter 1 works
-Many of the buttons on the right do nothing
-Resizing the window expands the buttons and not the output widget
-If you type an invalid filter, the program will encounter errors trying to parse it but will recover when the filter is corrected
-If the program receives a message with a header which matches a filter but not enough data 
-spaces can't be added after messages because they are stripped


Features to Add:
Turn filters on/off
Save output to text file
