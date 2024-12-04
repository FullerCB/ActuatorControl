# /**********************************************************************
# * This is a Python programming script for the Modular Control System 
# * API.
# *
# * Author: Fuller Collins-Bilyeu
# **********************************************************************/

from MCSControlPythonWrapper.MCSControl_PythonWrapper import *
from Multimeter import continuity
import pandas as pd
import time


#Sub Functions
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
    if status != SA_OK:
        print(f"Error zeroing actuator {actuator_id}: {status}")


    # Check the result and report the status
    direction_str = "backward" if direction == SA_BACKWARD_DIRECTION else "forward"
    print(f"Actuator {actuator_id} is zeroing in the {direction_str} direction.")

def return_default():
    """
    Moves all actuators (X, Y, Z) to their default positions (0, 0, 0) and calibrates them.
    
    Utilizes the `is_movement_complete` function to verify movement completion.
    Includes status messages for each step of the process.

    Returns:
        None
    """
    # Default coordinates
    pos_x0 = 0
    pos_y0 = 0
    pos_z0 = 0

    print("RETURNING ACTUATORS TO DEFAULT POSITION")
    print("_________________________________________")

    # Move Z actuator to default position
    print("Returning Z...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, pos_z0, 0)

    # Check if Z movement is complete
    while True:
        SA_GetPosition_S(MCS_handle, 2, position_z)  # Assumes position_z is defined elsewhere
        if is_movement_complete(MCS_handle, act_z, pos_z0):
            print("Finished Z movement")
            break
        time.sleep(0.1)  # Small delay before checking again

    # Move X and Y actuators to default positions
    print("Returning X and Y...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y0, 0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x0, 0)

    # Check if X and Y movements are complete
    while True:
        if is_movement_complete(MCS_handle, act_x, pos_x0) and is_movement_complete(MCS_handle, act_y, pos_y0):
            print("Finished X Y movement")
            break
        time.sleep(0.1)  # Small delay before checking again

    # Calibrate all actuators
    print("Calibrating X, Y, Z...")
    zero_actuator(0)  # Calibrate X
    zero_actuator(1)  # Calibrate Y
    zero_actuator(2)  # Calibrate Z
    time.sleep(1.5)  # Allow time for calibration

    print("Zero Calibrated")
    print("_________________________________________")
    print("ACTUATORS IN DEFAULT POSITION")

#Major Functions
import pandas as pd

def tilt_calibrate():
    """
    Calibrates the aperture by moving the Z actuator down, slightly raising it,
    moving X actuator, and then lowering Z again to measure electrical continuity.
    The X and Z positions are recorded in pairs for 5 iterations.

    Returns:
        list: List of X and Z positions recorded in pairs.
    """
    # Return actuators to default positions
    return_default()

    print("Check for previous positions in 'xyz_positions.csv' if necessary.")
    input("Position the gold bar at the desired XY location. Press 'Enter' when done.")

    def get_int_input(prompt):
        """Helper function to get integer input from the user."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    # Get desired X and Y positions from the user
    pos_x1 = get_int_input("Provide X Position (microns): ") * 1000
    pos_y1 = get_int_input("Provide Y Position (microns): ") * 1000

    # Move X and Y into position
    print("Moving X and Y into position...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x1, 0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y1, 0)

    # Wait until X and Y movements are complete
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if (
            is_movement_complete(MCS_handle, act_x, pos_x1)
            and is_movement_complete(MCS_handle, act_y, pos_y1)
        ):
            print("Finished XY movement.")
            break
        time.sleep(0.1)

    # Set Z actuator speed
    SA_SetClosedLoopMoveSpeed_S(MCS_handle, act_z, 500000)

    input("Z actuator will begin to move. Ensure multimeter is properly set up. Press 'Enter' to start Z movement.")
    print("Finding Z Reference Point...")

    # Move Z actuator downward until continuity is detected
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, 10000000, 0)
    while True:
        print("Continuity Test Initialized and Running...")
        SA_GetPosition_S(MCS_handle, act_z, position_z)
        if continuity():
            SA_Stop_S(MCS_handle, act_z)
            print("Z actuator is touching the target.")
            SA_GetPosition_S(MCS_handle, act_z, position_z)
            pos_z1 = position_z.value
            break

    # Store X and Z positions in pairs for 5 iterations
    x_z_pairs = []
    for i in range(5):
        print(f"Iteration {i+1} of 5:")

        # Raise Z slightly
        SA_GotoPositionAbsolute_S(MCS_handle, act_z, pos_z1 - 500000, 0)
        time.sleep(1)

        # Move X slightly (e.g., by 50 microns)
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GotoPositionAbsolute_S(MCS_handle, act_x, position_x.value + 400000, 0)
        time.sleep(1)

        # Lower Z again
        SA_GotoPositionAbsolute_S(MCS_handle, act_z, pos_z1 + 100000, 0)
        while True:
            SA_GetPosition_S(MCS_handle, act_z, position_z)
            if continuity():
                SA_Stop_S(MCS_handle, act_z)
                print("Z actuator is touching the target.")
                break

        # Store the current X and Z positions
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_z, position_z)
        x_z_pairs.append((position_x.value, position_z.value))
        print(f"Recorded X: {position_x.value}, Z: {position_z.value}")

    return_default()
    # Store the recorded X and Z pairs in a CSV file
    df = pd.DataFrame(x_z_pairs, columns=["X_Position", "Z_Position"])
    df.to_csv("x_z_positions.csv", index=False)
    print("Calibration complete. Data saved to 'x_z_positions.csv'.")

    # Return the list of recorded X and Z pairs
    return x_z_pairs

def calibrate_aperture():
    """
    Calibrates the aperture by positioning actuators (X, Y, Z) and determining
    the reference point where electrical continuity is detected. Stores the 
    final positions in 'xyz_positions.csv'.

    Returns:
        tuple: Final positions (pos_x1, pos_y1, pos_z1) in microns.
    """

    def get_int_input(prompt):
        """Helper function to get integer input from the user."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    # Open the system - already done
    #ExitIfError(SA_OpenSystem(MCS_handle, locator, 'sync,reset'))

    # Return actuators to default positions
    return_default()

    print("Check for previous positions in 'xyz_positions.csv' if necessary.")
    input("Position the gold bar at the desired XY location. Press 'Enter' when done.")

    # Get desired X and Y positions from the user
    pos_x1 = get_int_input("Provide X Position (microns): ") * 1000
    pos_y1 = get_int_input("Provide Y Position (microns): ") * 1000

    # Move X and Y into position
    print("Moving X and Y into position...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x1, 0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y1, 0)

    # Wait until X and Y movements are complete
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if (
            is_movement_complete(MCS_handle, act_x, pos_x1)
            and is_movement_complete(MCS_handle, act_y, pos_y1)
        ):
            print("Finished XY movement.")
            break
        time.sleep(0.1)

    # Set Z actuator speed
    SA_SetClosedLoopMoveSpeed_S(MCS_handle, act_z, 500000)

    input("Z actuator will begin to move. Ensure multimeter is properly set up. Press 'Enter' to start Z movement.")
    print("Finding Z Reference Point...")

    # Move Z actuator downward until continuity is detected
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, 10000000, 0)
    while True:
        print("Continuity Test Initialized and Running...")
        SA_GetPosition_S(MCS_handle, act_z, position_z)
        if continuity():
            SA_Stop_S(MCS_handle, act_z)
            print("Z actuator is touching the target.")
            SA_GetPosition_S(MCS_handle, act_z, position_z)
            pos_z1 = position_z.value
            break

    # Return actuators to default positions
    return_default()

    # Store the final positions in a CSV file
    data = {"pos_x1": [pos_x1], "pos_y1": [pos_y1], "pos_z1": [pos_z1]}
    df = pd.DataFrame(data)
    df.to_csv("xyz_positions.csv", index=False)

    # Close the system - already done
    #ExitIfError(SA_CloseSystem(MCS_handle))

    print("Calibration complete. Final positions saved to 'xyz_positions.csv'.")
    return pos_x1, pos_y1, pos_z1


    '''
    Initial at X0 Y0  Z0
    Position gold bar
    Get tip location with optic block laser
    Move X/Y actuators above gold
    Slowly lower Z actuator until voltage output
    STOP record and store X1 Y1 Z1
    Raise Z, Return Z0 then X0 Y0
    '''

def align_aperture():
    """
    Aligns the aperture by moving actuators (X, Y, Z) to the positions stored in 'xyz_positions.csv'.
    Waits for the user to confirm alignment before returning to the default position.
    """
    # Define height from wafer in nm
    height = 10000
    # Load positions from CSV
    try:
        df = pd.read_csv("xyz_positions.csv")
        pos_x1 = int(df.loc[0, "pos_x1"])
        pos_y1 = int(df.loc[0, "pos_y1"])
        pos_z1 = int(df.loc[0, "pos_z1"]) - height
    except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
        print(f"Error reading positions from 'xyz_positions.csv': {e}")
        return

    # Move X and Y to the known positions
    print("Moving X and Y into position...")
    SA_GotoPositionAbsolute_S(MCS_handle, act_x, pos_x1, 0)
    SA_GotoPositionAbsolute_S(MCS_handle, act_y, pos_y1, 0)
    while True:
        SA_GetPosition_S(MCS_handle, act_x, position_x)
        SA_GetPosition_S(MCS_handle, act_y, position_y)
        if is_movement_complete(MCS_handle, act_x, pos_x1) and is_movement_complete(MCS_handle, act_y, pos_y1):
            print("Finished XY movement.")
            break
        time.sleep(0.1)

    # Move Z to the known position
    print("Starting Z movement...")
    SA_SetClosedLoopMoveSpeed_S(MCS_handle, act_z, 1000000)
    SA_GotoPositionAbsolute_S(MCS_handle, act_z, pos_z1, 0)
    while True:
        SA_GetPosition_S(MCS_handle, act_z, position_z)
        if is_movement_complete(MCS_handle, act_z, pos_z1):
            print("Z in position.")
            break
        time.sleep(0.1)

    # Wait for user confirmation
    while True:
        user_input = input("Aperture aligned. Ready to measure. Type 'finished' and press Enter to return aperture: ").lower()
        if user_input == "finished":
            break

    # Return actuators to the default position
    return_default()


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

# Define actuator IDs
actuator_ids = [0, 1, 2]  # Actuator IDs for X, Y, Z (adjust as necessary)
act_x = 0
act_y = 1
act_z = 2
position_x = ct.c_long()
position_y = ct.c_long()
position_z = ct.c_long()

#SYSTEM MOVEMENT - CALL WHATEVER FUNCTION YOU WANT HERE
tilt_calibrate()


#closing everything
ExitIfError(SA_CloseSystem(MCS_handle))