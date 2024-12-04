from Multimeter import continuity

i = False
while i == False:
    i = continuity()
    print('Is there continuity?: ', i)

# Define actuator IDs
actuator_ids = [0, 1, 2]  # Actuator IDs for X, Y, Z (adjust as necessary)
act_x = 0
act_y = 1
act_z = 2
position_x = ct.c_long()
position_y = ct.c_long()
position_z = ct.c_long()