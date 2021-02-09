# import required libraries
import pandas as pd  # pandas for data processing
import matplotlib.pyplot as plt  # for plotting data
from statistics import mean  # to calculate the average value
import numpy as np  # to define arrays
from tkinter import Tk  # to create the searching file window
from tkinter.filedialog import askopenfilename  # to get the file path


g = 9.81  # define the gravitational acceleration constant

Tk().withdraw()  # create a window
file_path = askopenfilename()  # ask for the file path on the created window


df = pd.read_csv(file_path)  # read the dataframe existing on the path

columns_names = ['Time', 'Left', 'Right']  # define the 3 main columns

mass = float(df.iloc[0, 1])  # extract the mass value from the dataframe
freq = float(df.iloc[1, 1])  # extract the frequency from the dataframe

# read the tare value
if str(df.iloc[6, 0]) == 'Tare':  # if there is a tare for each foot
    tare_left = float(df.iloc[6, 1])
    tare_right = float(df.iloc[6, 2])
elif str(df.iloc[6, 0]) == 'Z Tare':  # if there is a global tare
    tare = float(df.iloc[6, 1])

df = df.tail(-9).astype(float)  # drop the first 8 lines of the data frame (not useful anymore)
df.columns = columns_names  # reset the columns name
df = df.reset_index(drop=True)  # reset the index

try:  # to avoid the error of undefined tare_left and tare_right variables
    df['Left'] = df['Left'] - tare_left  # deduct the tare values
    df['Right'] = df['Right'] - tare_right
    df['Total Force'] = df['Left'] + df['Right']  # define new column for the total force
    df['Net Force'] = df['Total Force']  # define new column for the net force
except:
    df['Total Force'] = df['Left'] + df['Right']
    df['Net Force'] = df['Total Force']


df['Asymmetry'] = df['Left'] - df['Right']  # define the asymmetry column

peak_force = df['Net Force'].max()  # find the max value of the net force
print('Peak force : ', peak_force, 'N')  # print the peak force value

thres = 0.01 * peak_force  # define a threshold to drop the beginning and the end of the data reading and ploting
indexNames = df[df['Net Force'] < g * mass - thres].index  # get the index of the values less than the threshold
start_point = list(indexNames)[0]  # get the first index
end_point = list(indexNames)[-1]  # get the last index
df = df.iloc[start_point:end_point]  # crop the dataframe

# define the acceleration column
df['Acceleration'] = df['Net Force'] / float(mass) - g

# define the velocity column
df['Velocity'] = df['Acceleration'] / freq
df['Velocity'] = df['Velocity'].cumsum()

# define the displacement column
df['Displacement'] = df['Velocity'] / freq * 100
df['Displacement'] = df['Displacement'].cumsum()

# define the power and print the power peak value
df['Power'] = df['Net Force'] * df['Velocity']
peak_power = df['Power'].max()
print('Peak Power : ', peak_power, 'W')

# define and print the jump height
jump_height = df['Displacement'].max()
print('Jump Height : ', jump_height, 'cm')

unweighting_t = float(df.iloc[0, 0])  # define the instant of the beginning of the unweighting phase

# define the instant of the beginning of the breaking phase
indexNames = df[df['Net Force'] - g * mass > 0].index
braking_t = float(df.iloc[list(indexNames)[0] - start_point, 0])

# define the instant of the beginning of the fligh phase and it's duration
indexNames = df[(df['Net Force'] < g*mass) & (df['Time'] > braking_t)].index
flight_t = float(df.iloc[list(indexNames)[0] - start_point, 0])
flight_duration = float(df.iloc[list(indexNames)[-1] - start_point, 0]) - \
                  float(df.iloc[list(indexNames)[0] - start_point, 0])

# define the instant of the beginning of the propulsive phase
indexNames = df[df['Time'] < flight_t].idxmax(axis=0)
propulsive_t = float(df.iloc[int(indexNames['Net Force']) - start_point, 0])

# define the RFD column
sLength = len(df['Time'])
df['RFD'] = pd.Series(np.zeros(sLength), index=df.index)
prev_row = df['Net Force'].iloc[0]
for i, row in df.iterrows():
    df['RFD'].loc[i] = (float(row['Net Force']) - prev_row) * freq  # the formula used is delta(force)/detlat(time)
    prev_row = float(row['Net Force'])


# getting the useful data
data = list(df['Time'].iloc[:list(indexNames)[0] - start_point + 2]), \
       list(df['Net Force'].iloc[:list(indexNames)[0] - start_point + 2]), \
       list(df['Power'].iloc[:list(indexNames)[0] - start_point + 2]), \
       list(df['RFD'].iloc[:list(indexNames)[0] - start_point + 2])


fig, ax = plt.subplots(2)  # instantiate 2 figures


ax[0].axhline(y=g * mass, color='k')  # draw horizontal line of the body weight on the first graph
ax[1].axhline(y=0, color='k')  # draw horizontal line of the 0 on the second graph

# printing info
print('Unweighting duration :', round(braking_t - unweighting_t, 4), 's')
print('Braking duration :', round(-braking_t + propulsive_t, 4), 's')
print('Propulsive duration :', round(flight_t - propulsive_t, 4), 's')
print('Flight duration :', round(flight_duration, 4), 's')


# Unweighting phase
start = data[0].index(unweighting_t)  # define the beginning of the phase
end = data[0].index(braking_t)  # define the end of the phase
i_data = data[0][start:end], data[1][start:end]  # crop data to fit with the phase
power_data = data[2][start:end]  # save power data
ax[0].fill_between(i_data[0], g*mass,  i_data[1], color='orange', alpha=0.5)  # draw the phase on the graph

# Braking phase
start = end  # define the beginning of the phase
end = data[1].index(max(data[1]))  # define the end of the phase
i_data = data[0][start:end], data[1][start:end]  # crop data to fit with the phase
power_data += data[2][start:end]  # save power data
RFD_data = data[3][start:end]  # save RFD data
ax[0].fill_between(i_data[0], g*mass,  i_data[1], color='r', alpha=0.5)  # draw the phase on the graph
# print useful info
print('Peak Pre-Flight Force : ', round(i_data[1][-1], 3), 'N')
print('Peak Pre-Flight RFD : ', round(max(RFD_data), 3), 'N/s')
avg_RFD = round(mean(RFD_data), 3)
print('Average Force Development in breaking phase : ', avg_RFD, 'N/s')

# Propulsive phase
start = end  # define the beginning of the phase
end = data[0].index(flight_t)  # define the end of the phase
i_data = data[0][start:end], data[1][start:end]  # crop data to fit with the phase
power_data += data[2][start:end]  # save power data
RFD_data = data[3][start:end]  # save RFD data
ax[0].fill_between(i_data[0], g*mass,  i_data[1], color='g', alpha=0.5)  # draw the phase on the graph
# print useful info
avg_RFD = round(mean(RFD_data), 3)
print('Average Force Development in propulsive phase : ', avg_RFD, 'N/s')
print('Peak Pre-Flight Power : ', max(power_data), 'W')

# plot the net force line on the first graph
df.plot(x='Time', y='Net Force', kind='line', ax=ax[0])

# plot the asymmetries data, left right and difference
df.plot(x='Time', y='Left', kind='line', ax=ax[1])
df.plot(x='Time', y='Right', kind='line', ax=ax[1])
df.plot(x='Time', y='Asymmetry', kind='line', ax=ax[1])

# put text labels on each phase
ax[0].text((unweighting_t + braking_t)/2, g*mass * 1.7, "Unweighting\nPhase", size=9, ha="center", va="center",
           bbox=dict(boxstyle="round",fc=(1, 0.8, 0.3), ))
ax[0].text((braking_t + propulsive_t)/2, peak_force * 0.65, "Braking\nPhase", size=9, ha="center", va="center",
           bbox=dict(boxstyle="round",fc=(1, 0.5, 0.5), ))
ax[0].text(flight_t, peak_force * 0.8, "Propulsive\nPhase", size=9, ha="center", va="center",
           bbox=dict(boxstyle="round",fc=(0.4, 0.8, 0.4), ))

# show the plots window
plt.show()



