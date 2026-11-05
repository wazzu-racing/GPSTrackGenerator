import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

df = pd.read_csv("GPS_data.csv", 
                 usecols=["Latitude", "Longitude"])
#df = df.dropna() #drop all the rows with NAN values
df = df.iloc[190:] # drop the first 190 rows of the dataframe
df["Latitude"] = pd.to_numeric(df["Latitude"], errors='coerce') # convert Latitude column to numeric, set errors to NaN
df["Longitude"] = pd.to_numeric(df["Longitude"], errors='coerce') # convert Longitude column to numeric, set errors to NaN

print(df.shape) #just to view the number of rows and columns
#print(df.head())

plt.plot(df["Longitude"], df["Latitude"])
plt.title("Longitude vs Latitude")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

def radius():
    all_points = []
    avg_latitude = np.mean(df["Latitude"]) #get the average latitude of the dataframe
    df["X"] = df["Longitude"] * 111320 * np.cos(np.radians(avg_latitude)) #converting to meters using the average latitude because longitude changes with latitude
    df["Y"] = df["Latitude"] * 111320 #converting to meters

    for i in range(0, len(df) - 2, 3):
        a = float(df.iloc[i]["X"]), float(df.iloc[i]["Y"])
        b = float(df.iloc[i + 1]["X"]), float(df.iloc[i + 1]["Y"])
        c = float(df.iloc[i + 2]["X"]), float(df.iloc[i + 2]["Y"])
        points = np.array([a, b, c]) #combining three points into a single array
        origin = points.mean(axis=0) #axis=0 means we are taking the mean of each column, so we get the mean of x and y coordinates separately
        points = points - origin
        x = points[:, 0] #get the x coordinates of the points
        y = points[:, 1] #get the y coordinates of the points
        matrix = np.column_stack((x, y, np.ones(3))) #stack the x, y, and ones columns to create a matrix
        const = x**2 + y**2 #calculate the constant term for the equation of a circle
        det = np.linalg.det(matrix) #calculate the determinant of the matrix to check if the points are collinear
        if abs(det) < 1e-10:
            continue
        solution = np.linalg.solve(matrix, const) #solve the system of equations
        h = solution[0] / 2
        k = solution[1] / 2
        r = h**2 + k**2 - solution[2] #solve for the radius and check to see if it's less than 0
        if(r < 0):
            continue
        radius = np.sqrt(r)
        radius_inches = radius * 39.3701 #convert the radius from meters to inches
        all_points.append(radius_inches)

    print(all_points)

radius()