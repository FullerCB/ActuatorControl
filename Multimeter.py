# /**********************************************************************
# * This is a file containing multimeter functions
# * Default is configured for: Arduino UNO R4
# **********************************************************************/


#for Arduino UNO R4
import serial
import time

# Initialize the serial connection
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

def continuity():
    try:
        arduino.flushInput()  # Clear any stale data
        data = arduino.readline().decode().strip()
        return data == "1"
    except Exception as e:
        print(f"Error: {e}", " \n STOPPING MOVEMENT")
        return True
