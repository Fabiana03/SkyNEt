# This file contains various functions to use with the switch network
import serial
import numpy as np
import time

def init_serial(comport = 'COM3'):
    '''
    This function initializes a serial object that is used to 
    communicate with the Arduino
    '''
    ser = serial.Serial(port=comport, baudrate=9600, bytesize=8, 
                        parity='N', stopbits=1, write_timeout = 1, 
                        dsrdtr = True)
    return ser

def matrix_to_bytes(matrix):
    '''
    This function converts an 8x8 binary matrix into the proper serial
    signal of 8 bytes that can be sent over the serial port to the 
    Arduino.

    The first row of matrix corresponds to the switching configuration
    of C1.
    '''
    #send_string = '<'  # Start flag
    send_string = ''

    # Loop over each row of matrix
    # This code reverses bit order
    for ii in range(matrix.shape[0]):
        row_number = 0
        for jj in range(matrix.shape[1]): 
            row_number += int( 2**(7-jj) * matrix[ii, jj])
        send_string += str(row_number)
        if(ii < 7):
            send_string += ','  # Separator character

    #send_string += '>'  # End flag

    return send_string.encode()
            
def switch(ser, matrix):
    '''
    This is the main function that applies the switching configuration
    in matrix to the serial port ser.

    Input arguments
    ---------------
    ser; serial object, to be initialized with init_serial
    matrix; (8, 8) np.array, first row defines the switching 
            configuration of C1.
    '''
    send_string = matrix_to_bytes(matrix)

    ser.write('<'.encode())
    time.sleep(0.2)

    ser.write(send_string)
    time.sleep(0.2)

    ser.write('>'.encode())

def read_serial_out(ser): 
    '''
    this function reads out the com port (hopefully for enough time)
    and then prints it to the console
    TODO print to file or results
    '''
    time.sleep(0.2)
    while ser.inWaiting()!=0:
        lineToRead =ser.read_until(b'done',300)
        print(lineToRead.decode())
        ser.flushInput()
        time.sleep(0.2)

def connect_single_device(ser, device_number):
    '''
    This function connects the device number device_number (0-7)
    to the BNC connectors
    '''
    matrix = np.zeros((8, 8))
    matrix[:, device_number-1] = 1
    switch(ser, matrix)
    read_serial_out(ser)

def connect_matrix(ser, connect_matrix):
    '''
    this function connects a specified matrix connection 
    to the BNC connectors
    See the config file for more information on how to
    build this matrix
    '''
    switch(ser,connect_matrix)
    read_serial_out(ser)