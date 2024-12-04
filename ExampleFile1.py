#storing data
import pandas as pd

data = {
"pos_x1": [1.3, 4],
"pos_y1": [9, 6],
"pos_z1": [14, 3],
}

df = pd.DataFrame(data)

df.to_csv("xyz_positions.csv", index=False)

positionsDF = pd.read_csv("xyz_positions.csv")

cal_x, cal_y, cal_z = positionsDF.iloc[0,:]

print(cal_x,cal_y,cal_z)