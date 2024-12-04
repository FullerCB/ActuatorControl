from MCSControlPythonWrapper.MCSControl_PythonWrapper import *
import time

def is_movement_complete(handle, channel, target_position, threshold=0.99, interval=0.1, stop_checks=5):
    """
    Checks if the actuator has completed its movement either by:
    1. Reaching 99% (or specified threshold) of the target distance.
    2. Stopping its movement (position remains unchanged over multiple checks).

    Args:
        handle: The MCS system handle.
        channel (int): The actuator channel number.
        target_position (int): The target position in units of nanometers.
        threshold (float, optional): Percentage of total distance to consider movement complete (default is 0.99).
        interval (float, optional): Time interval (in seconds) to check position updates (default is 0.1).
        stop_checks (int, optional): Number of consecutive checks with no movement to consider the actuator stopped.

    Returns:
        bool: True if movement is complete or actuator stops moving, False otherwise.
    """
    # Get the initial position
    initial_pos = ct.c_long()
    SA_GetPosition_S(handle, channel, initial_pos)

    # Calculate the total distance to travel
    total_distance = abs(target_position - initial_pos.value)

    # Start moving towards the target position
    SA_GotoPositionAbsolute_S(handle, channel, target_position, 0)

    # Variables to track stopping condition
    no_movement_count = 0
    last_position = initial_pos.value

    # Poll the position until the movement is complete
    while True:
        current_pos = ct.c_long()
        SA_GetPosition_S(handle, channel, current_pos)

        # Calculate the distance covered
        distance_covered = abs(current_pos.value - initial_pos.value)

        # Check if 99% of the distance is covered
        if distance_covered >= threshold * total_distance:
            return True

        # Check if the actuator has stopped moving
        if current_pos.value == last_position:
            no_movement_count += 1
            if no_movement_count >= stop_checks:
                print("Movement stopped.")
                return True
        else:
            no_movement_count = 0  # Reset counter if movement resumes

        # Update the last position
        last_position = current_pos.value

        # Sleep for stability before the next check
        time.sleep(interval)

def zero_actuator(actuator_id):
    """
    Moves the specified actuator to its zero position by finding the reference mark.
    The direction is determined automatically based on the actuator's current position:
    - Backward if the position is positive.
    - Forward if the position is negative.

    Args:
        actuator_id (int): The ID of the actuator to zero.

    Returns:
        None
    """
    # Get the current position of the actuator
    current_position = ct.c_long()
    status = SA_GetPosition_S(MCS_handle, actuator_id, current_position)

    if status != SA_OK:
        print(f"Error reading position of actuator {actuator_id}: {status}")
        return

    # Determine the direction based on the current position
    if current_position.value > 0:
        direction = SA_BACKWARD_DIRECTION
    else:
        direction = SA_FORWARD_DIRECTION

    # Attempt to zero the actuator
    status = SA_FindReferenceMark_S(
        MCS_handle, 
        actuator_id, 
        direction, 
        0, 
        SA_AUTO_ZERO
    )

    # Check the result and report the status
    if status == SA_OK:
        direction_str = "backward" if direction == SA_BACKWARD_DIRECTION else "forward"
        print(f"Actuator {actuator_id} is zeroing in the {direction_str} direction.")
    else:
        print(f"Error zeroing actuator {actuator_id}: {status}")


    # Check the result and report the status
    direction_str = "backward" if direction == SA_BACKWARD_DIRECTION else "forward"
    print(f"Actuator {actuator_id} is zeroing in the {direction_str} direction.")

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

long_distance = int(21349431 / 2)
short_distance = int(11171637 / 2)



pos_z = 100000000
channel = 2
initial_pos = ct.c_long()
SA_GetPosition_S(MCS_handle, 2, initial_pos)
total_distance = pos_z - initial_pos.value# Calculate the total distance to cover

SA_SetClosedLoopMoveSpeed_S(MCS_handle, 2, 500000)
SA_GotoPositionAbsolute_S(MCS_handle, 2, pos_z, 0)
SA_GotoPositionAbsolute_S(MCS_handle, 0, 100000000, 0)
SA_GotoPositionAbsolute_S(MCS_handle, 1, 100000000, 0)
while True:
    position = ct.c_long()
    SA_GetPosition_S(MCS_handle, 2, position)
    if is_movement_complete(MCS_handle, channel, pos_z):
        break
    time.sleep(0.1)  # Wait a bit before checking again

print("All Finished!")
#status = SA_FindReferenceMark_S(MCS_handle, 0, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#status = SA_FindReferenceMark_S(MCS_handle, 1, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#status = SA_FindReferenceMark_S(MCS_handle, 2, SA_FORWARD_DIRECTION, 0, SA_AUTO_ZERO)
#if status == SA_OK:
    #print(f"Actuator 0 is zeroing.")

ExitIfError(SA_CloseSystem(MCS_handle))