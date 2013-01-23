CAN-Python
==========

*   Source: https://github.com/bapsmith/CAN-Python

CAN-Python -- CAN Bus Message Debugger

This is a tool for interpretting and printing messages from a CAN bus connected to the PC.

### Install ###

This module requires that you have python 2.7 or 3.3 installed. Find it [here](http://www.python.org/download/). 

Also, you must have pyserial installed. Download it [here](http://pypi.python.org/pypi/pyserial).

### Usage ###

#### Connecting and Launching ####
To use the CAN-Python connect the CAN node to the computer with a USB cable. Next you must determine the COM port number (Windows), or the directory in the */dev* folder where the device was mounted (Mac, Unix). Now, launch the program by executing it with your shell. You can also launch it by running:

    python CAN-python.py

Once you have launched *CAN-Python*, you must enter the directory or port number that was determined earlier.

#### Receiving Messages ####

Click *Begin Receiving Messages* on the right hand side to start filtering messages. Raw CAN messages will appear in the output window, and will be followed by a parsed version of the message if they match the filter.

#### Customizing Filters ####

Add filters to the filter window with the correct format..., then click *Update Filters*.

Filters must be written in the following format, where spaces are ignored and fields are delimited by commas:

    Header (0x), Initial Offset, Msg, Length (bytes), Endianness, Scale, Skip, Msg, Length, Endianness, Skip...


Here is an example:
   
    07B,0,Voltage on temp sensor: ,2,lu,.001,0,temp: ,2,lu,.01,0,d rail v: ,2,lu,.01,0,rail v: ,2,l,.01

The above filter parses the default message spit out by the CAN node. It looks for the header '*07B*' and then skips 0 bytes, prints the message '*Voltage on temp sensor:*'. The next two bytes are interpreted as unsigned little endian, which is denoted by a '*l*'.  Anything other than an '*l*' is interpreted as big endian.

### Bugs ###
Skip 0 bytes (which may or may not be working), print �temp��ect

