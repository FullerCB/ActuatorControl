# /**********************************************************************
# * This is a file containing multimeter functions
# * Default is configured for: TekPower TP9605BT True RMS AC/DC Multimeter
# **********************************************************************/


#for multimeter: TekPower TP9605BT True RMS AC/DC Multimeter
def continuity():
    if touching() == True:
        return True
    else:
        return False