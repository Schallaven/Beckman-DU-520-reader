#!/usr/bin/env python

'''
Script written by Dr. Sven Kochmann, December 2015

A python script that listens for input from a Beckman DU 520 instrument
and forwards this input to a file. This is a console program (does not
work in IDLE due to khbit) but I tried to make it a little userfriendly.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

# Necessary imports
import serial
import os
import sys
import time
import khbit

# Variables
set_port        = "COM3"
set_baudrate    = 19200
set_bytesize    = serial.EIGHTBITS
set_parity      = serial.PARITY_NONE
set_timeout     = 0 # 0 = non_blocking, do not set it to False (blocking!)

# Start of main program
# ---------------------
# Display some introduction-text
print(  "\n"
        "Beckman DU 520 Reader\n"
        "---------------------\n"
        "\n"
        "Using the following settings for the connection:\n"
        "" + set_port + ", " + str(set_baudrate) + " Baud, " + str(set_bytesize) + " Bits, Parity:" ),
        
if set_parity == serial.PARITY_NONE:
    print("None")
elif set_parity == serial.PARITY_EVEN:
    print("Even")
elif set_parity == serial.PARITY_ODD:
    print("Odd")
else:
    print("Unknown")

print(  "Timeout for readout: " + str(set_timeout) + (" (non-blocking)" if set_timeout == 0 else "s") + "\n" )

# Ask user for experiment name
print(  "The program will create a subfolder for your data."
        " Data will saved with sequential numbers and timestamp. Filenames will have the form 'Data XXX.txt'." )

experimentname = raw_input("Please provide a folder name for your experiment(s): ")

# Did not provide anything? :(
if len(experimentname) == 0:
    experimentname = "Random experiment"

# Generate name for folder
folderbasename = time.strftime('%Y-%m-%d') + ' - ' + experimentname
foldername = folderbasename

# Check if the folder exists, if yes add 001 or the like
i = 1
while os.path.exists( foldername ):
    foldername = folderbasename + ' - ' + ('%03d' % i)
    i += 1

# Create the folder
try:
    os.makedirs(foldername)
except:
    print("Could not create the folder :(")
    print("Check if you used any symbols, which might be a problem for folders, such as '\\' or ':' and try again")
    raise

# Open serial connection for listening
ser = serial.Serial( set_port, set_baudrate, bytesize=set_bytesize, parity=set_parity, timeout=set_timeout )

# Could not open?
if not ser.isOpen():
    print("Could not open the port for listening :(. Check parameters!")
    sys.exit()

# Give the user a hint how to exit the program
print( "\n" )
print( "Listening now at " + set_port + "... If you want to exit this program, just press 'q'" )

# Now that we are listening, do this more or less infinite
key = ''

# Initialize console input
kb = khbit.KBHit()

# Set the buffer to zero
buffer_content = ""

# File number
nofile = 1

# Main loop, exit when key 'q' is pressed
while not key == 'q':
    
    # Key pressed? 
    if kb.kbhit():
        key = kb.getch()

    # Read byte for byte and display on output
    readbyte = ser.read(1)

    if not readbyte == '':
        # Send by the instrument for end-of-stream
        if ord(readbyte) == 12:
            # Print length of buffer (+1 is the terminal byte, which is not added to the buffer but was received!)
            print("%d bytes received" % (len(buffer_content)+1))
            
            # Print buffer
            print(buffer_content)

            # Generate filename
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            filename = "Data " + ("%03d" % nofile) + ".txt"

            # Print message to user
            print("Data written to '" + filename + "'.")

            # Open file 
            datafile = open( foldername + '/' + filename, "w")

            # Write to file
            datafile.write("Data recorded as set of '" + foldername + "' at " + timestamp + ".\r\n")
            datafile.write(buffer_content)

            # Close file
            datafile.close()

            # Empty the buffer
            buffer_content = ""

            # Increase file number
            nofile += 1
            
        # All other characters will go directly in our buffer
        else:
            # Buffer was empty before? Then print status message for user
            if len(buffer_content) == 0:
                print("Receiving data..."),

            # Add read byte to buffer    
            buffer_content += readbyte            
    

# Set the console input back to normal
kb.set_normal_term()
    
# Close 
ser.close()





