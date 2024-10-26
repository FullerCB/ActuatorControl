# /**********************************************************************
# * This is a Python programming script for the Modular Control System 
# * API.
# *
# * Author: Fuller Collins-Bilyeu
# **********************************************************************/

from MCSControlPythonWrapper.MCSControl_PythonWrapper import *
from Multimeter import continuity
import time

#check dll version 
version = ct.c_ulong()
SA_GetDLLVersion(version)
print('DLL-version: {}'.format(version.value))

# Define the IP and port
ip = "192.168.1.200"
port = 5000
locator = f"network:{ip}:{port}"
locator = locator.encode('utf-8')

#/* All MCS commands return a status/error code which helps analyzing 
#   problems */
def ExitIfError(status):
    #init error_msg variable
    error_msg = ct.c_char_p()
    if(status != SA_OK):
        SA_GetStatusInfo(status, error_msg)
        print('MCS error: {}'.format(error_msg.value[:].decode('utf-8')))
    return

#initialize MCS control handle
MCS_handle = ct.c_ulong()

# Define actuator IDs
actuator_ids = [0, 1, 2]  # Actuator IDs for X, Y, Z (adjust as necessary)
act_x = 0
act_y = 1
act_z = 2
position_x = ct.c_long()
position_y = ct.c_long()
position_z = ct.c_long()

#Sub Functions
def zero_actuator(actuator_id):
    status = SA_FindReferenceMark_S(MCS_handle, actuator_id, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
    if status == SA_OK:
        print(f"Actuator {actuator_id} is zeroing.")
    else:
        print(f"Error zeroing actuator {actuator_id}: {status}")

def return_default():
    
    #default coordinates
    pos_x0 = 0
    pos_y0 = 0
    pos_z0 = 0

    print("RETURNING ACTUATORS TO DEFAULT POSITION")
    print("_________________________________________")

    print('Returning Z...')
    SA_GotoPositionAbsolute_S(MCS_handle,act_z,pos_z0,0)
    #completed movement check
    while True:
        SA_GetPosition_S(MCS_handle, 2, position_z)
        if abs(position_z.value - pos_z0) < (100):
            print('Finished Z movement')
            break
        time.sleep(0.1)  # Wait a bit before checking again


    print('Returning X and Y...')
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y0,0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x0,0)

    #completed movement check
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if abs(position_x.value - pos_x0) < (100) and abs(position_y.value - pos_y0) < (100):
            print('Finished X Y movement')
            break
        time.sleep(0.1)  # Wait a bit before checking again

    #calibrate all actuators 
    print("Calibrating X Y Z...")
    SA_FindReferenceMark_S(MCS_handle, 0, SA_BACKWARD_DIRECTION, 0, SA_AUTO_ZERO)
    SA_FindReferenceMark_S(MCS_handle, 1, SA_BACKWARD_DIRECTION, 0, SA_AUTO_ZERO)
    SA_FindReferenceMark_S(MCS_handle, 2, SA_BACKWARD_DIRECTION, 0, SA_AUTO_ZERO)
    time.sleep(1.5)
    print("Calibrated")
    print("_________________________________________")
    print("ACTUATORS IN DEFAULT POSITION")



#Major Functions
def calibrate_aperture():

    def get_int_input(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    return_default()
    void =  input("Position gold bar at desired XY. Press 'enter' when done.")
    pos_x1 = get_int_input("Provided X Position (microns): ") * 1000
    pos_y1 = get_int_input("Provided Y Position (microns): ") * 1000

    print("Moving X and Y into position...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x1,0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y1,0)
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if abs(position_x.value - pos_x1) < (100) and abs(position_y.value - pos_y1) < 100:
            time.sleep(0.1)
            print('Finished XY movement')
            break
        time.sleep(0.1)  # Wait a bit before checking again

    SA_SetClosedLoopMoveSpeed_S(MCS_handle, 2, 100000)
    input("Z actuator will begin to move. Ensure multimeter is properly setup. Press 'enter' to start Z movement")
    print("Finding Z Reference Point...")
    #move z actuator
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, 10000000,0)
    while True:
        SA_GetPosition_S(MCS_handle, act_z, position_z)
        if continuity():
            SA_Stop_S(MCS_handle, act_z)
            print('z touching')
            SA_GetPosition_S(MCS_handle, act_z, position_z)
            pos_z1 = position_z.value
            break 
    return_default()
    return pos_x1, pos_y1, pos_z1


    '''
    Initial at X0 Y0  Z0
    Position gold bar
    Get tip location with optic block laser
    Move X/Y actuators above gold
    Slowly lower Z actuator until voltage output
    STOP record and store X1 Y1 Z1
    Raise Z slightly, Return Z0 then X0 Y0
    '''


def align_aperture(pos_x1, pos_y1, pos_z1):
    #connect to system
    ExitIfError(SA_OpenSystem(MCS_handle, locator,'sync,reset'))
    print('systemIndex: {}'.format(MCS_handle.value))

    #move actuators to known position
    #pos_x1 = 1 #will be var
    #pos_y1 = 1 #will be var
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x1,0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y1,0)
    
    #completed movement check
    print("Moving X and Y into position...")
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if abs(position_x.value - pos_x1) < (100) and abs(position_y.value - pos_y1) < 100:
            time.sleep(0.1)
            print('Finished XY movement')
            break
        time.sleep(0.1)  # Wait a bit before checking again

    print('Starting Z movement...')
    #pos_z1 = 1 #will be var
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, pos_z1,0)
    while True:
        SA_GetPosition_S(MCS_handle, 1, position_z)
        if abs(position_z.value - pos_z1) < (100):
            time.sleep(0.1)
            print('Z in position')
            break
    
    time.sleep(0.5)

    while True:
        user_input = input("Aperture Aligned. Ready to measure. Type 'finished' and press enter to return aperture: ").lower()
        if user_input == 'finished':
            break
    
    #return function
    return_default()


    #exit
    ExitIfError(SA_CloseSystem(MCS_handle))

    """
    Initial at X0 Y0  Z0
    Move to X1 Y1
    Move to Z1 + estimated thickness of wafer * (1 + Precision % + FOS %)
    Send X-rays
    Raise Z slightly
    Return to Z0 then X0 Y0
    """

