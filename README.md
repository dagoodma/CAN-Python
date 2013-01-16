CAN-Python
==========

## Usage

### Connecting and Launching
To use the CAN-Python connect the CAN node to the computer with a USB cable. Next you must determine the COM port number (Windows), or the directory in the */dev* folder where the device was mounted (Mac, Unix). Now, launch the program by executing it with your shell. You can also launch it by running:

    python CAN-python.py

Once you have launched *CAN-Python*, you must enter the directory or port number that was determined earlier.

### Customizing Filters

Add filters to the filter window with the correct format..., then click *Update Filters*.


Filters must be of the form: Header (0x), Initial Offset, Msg, Length (bytes), Endianness , Scale, Skip, Msg, Length, Endianness, Skip...

Spaces in filters are ignored and parsing takes place at commas

An example filter:
07B,0,Voltage on temp sensor: ,2,lu,.001,0,temp: ,2,lu,.01,0,d rail v: ,2,lu,.01,0,rail v: ,2,l,.01

This filter parses the default message spit out by the CAN node. It looks for the header 07B then skips 0 bytes prints the header �Voltage on temp sensor:�,and interprets the next two bytes as little endian unsigned which it then converts to binary and outputs. Little endian is indicated by denoted with an �l�.  Anything other than an �l� is interpreted as big endian. The pattern then repeats with skip 0 bytes (which may or may not be working), print �temp��ect

### Receiving Messages

Click *Begin Receiving Messages* on the right hand side to start filtering messages. Raw CAN messages will appear in the output window, and will be followed by a parsed version of the message if they match the filter.

