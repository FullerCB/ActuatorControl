from MCSControlPythonWrapper.MCSControl_PythonWrapper import *
import time

#check dll version 
version = ct.c_ulong()
SA_GetDLLVersion(version)
print('DLL-version: {}'.format(version.value))

# Define the IP and port
ip = "192.168.1.200"
port = 5000
locator = f"network:{ip}:{port}"

def ExitIfError(status):
    #init error_msg variable
    error_msg = ct.c_char_p()
    if(status != SA_OK):
        SA_GetStatusInfo(status, error_msg)
        print('MCS error: {}'.format(error_msg.value[:].decode('utf-8')))
    return

MCS_handle = ct.c_ulong() #initialize MCS control handle
ExitIfError(SA_OpenSystem(MCS_handle, locator.encode('utf-8'), options = 'sync,reset'))
print('systemIndex: {}'.format(MCS_handle.value))


SA_GotoPositionAbsolute_S(MCS_handle, 0, 10000000, 0)
SA_GotoPositionAbsolute_S(MCS_handle, 1, 10000000, 0)
SA_GotoPositionAbsolute_S(MCS_handle, 2, -200000, 0)

while True:
    position = ct.c_long()
    SA_GetPosition_S(MCS_handle, 0, position)
    print(position)
    if position.value > (9999000):
            break
    time.sleep(0.1)  # Wait a bit before checking again

#status = SA_FindReferenceMark_S(MCS_handle, 0, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#status = SA_FindReferenceMark_S(MCS_handle, 1, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#status = SA_FindReferenceMark_S(MCS_handle, 2, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#if status == SA_OK:
    print(f"Actuator 0 is zeroing.")

ExitIfError(SA_CloseSystem(MCS_handle))