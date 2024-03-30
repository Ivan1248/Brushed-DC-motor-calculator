#
# Solver for brushed DC motors
# Further reading: https://support.maxongroup.com/hc/en-us/articles/360001900933-Formulae-Handbook
#
# Dr. Dmitriy Makhnovskiy, City College Plymouth, England
# 30.03.2024
#

import matplotlib.pyplot as plt
import csv

# Motor constants used in the model:
Va = 6.0 # Armature voltage, V
Ra = 3.41  # Armature resistance, Ohms
La = 7.5e-5  # Armature inductance, H
KF = 6.589e-3  # Back-EMF constant, V x s / rad
J = 1.0e-7  # Rotor moment of inertia, kg x m^2
KM = 6.59e-3  # Torque constant, N x m / A
Tf = 1.3e-4  # Friction torque, N x m
N = 1000  # Number of points in the graph

# Characteristic parameters:
maxw0 = Va / KF  # Maximum angular speed without the friction torque, rad / s
maxw = Va / KF - (Tf * Ra) / (KF * KM)  # Maximum angular speed with the friction torque, rad / s
maxTmag = (Va * KM) / Ra  # Maximum magnetic torque, N x m
maxh = (KM / KF) * (1.0 - ((Ra * Tf) / (Va * KM))**0.5)**2  # Maximum efficiency
maxPL = (Va**2 * KM) / (4.0 * KF * Ra)  # Maximum power, W
I0 = Tf / KM  # No-load armature current, A
TIa = 1.0 / KM  # Torque-to-current coefficient, A/(Nxm)
Vaw = 1.0 /KF  # Voltage-to-speed coefficient (no load), rad/(Vxs)
dwdT = Ra / (KF * KM)  # dw/dT slope
alfa = (maxTmag -Tf) / J  # Maximum angular acceleration (no load), rad/s^2
print('Maximum speed = ', format(maxw, ".3e"), ' rad/s' )
print('Maximum torque = ', format(maxTmag, ".3e"), ' Nm')
print('Maximum efficiency h = ', format(maxh * 100, ".3e"), '%')
print('Maximum mechanical power = ', format(maxPL, ".3e"), ' W')
print('No-load armature current = ', format(I0, ".3e"), ' A')
print('Torque-to-current coefficient = ', format(TIa, ".3e"), ' A/(Nm)')
print('Voltage-to-speed coefficient (no load) = ', format(Vaw, ".3e"), 'rad/(Vs)')
print('dw/dT slope = ', format(dwdT, ".3e"), ' rad/(sNm)')
print('Maximum angular acceleration (no load) = ', format(alfa, ".3e"), ' rad/s^2')

# Arrays for graphs
wx = [0.0 + maxw0 * i / (N - 1) for i in range(N)]  # Angular speed array
Tx = [Tf + (maxTmag - Tf) * i / (N - 1) for i in range(N)]  # Magnetic torque array
T_w = [(Va * KM) / Ra - (KF * KM * w) / Ra for w in wx]  # Speed-to-torque characteristics
w_T = [Va / KF - (Ra * T) / (KF * KM) for T in Tx]  # Torque-to-speed characteristics
PL_T = [(Va / KF -(T * Ra) / (KF * KM)) * T for T in Tx]  # Torque-to-power characteristics
h_T = [(KM / KF) * (1.0 - (Ra * T) / (Va * KM)) * (1.0 - Tf / T) for T in Tx]  # Torque-to-efficiency characteristics

# Function to plot graphs and write arrays to files
def plot_and_save_data(x, y, x_label, y_label, graph_title, filename):
    # Plotting the graph
    plt.plot(x, y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(graph_title)

    # Adding detailed grid
    plt.grid(True)

    # Saving data to CSV file
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([x_label, y_label])  # Write header
        for i in range(len(x)):
            csv_writer.writerow([x[i], y[i]])

    # Displaying the plot
    plt.show()

x_label = 'Speed, rad/s'
y_label = 'Torque, Nm'
graph_title = 'Speed-to-torque characteristics'
filename = 'Speed-to-torque_characteristics.csv'
plot_and_save_data(wx, T_w, x_label, y_label, graph_title, filename)

x_label = 'Torque, Nm'
y_label = 'Speed, rad/s'
graph_title = 'Torque-to-speed characteristics'
filename = 'Torque-to-speed_characteristics.csv'
plot_and_save_data(Tx, w_T, x_label, y_label, graph_title, filename)

x_label = 'Torque, Nm'
y_label = 'Power, W'
graph_title = 'Torque-to-power characteristics'
filename = 'Torque-to-power_characteristics.csv'
plot_and_save_data(Tx, PL_T, x_label, y_label, graph_title, filename)

x_label = 'Torque, Nm'
y_label = 'Efficiency, %'
graph_title = 'Torque-to-efficiency characteristics'
filename = 'Torque-to-efficiency_characteristics.csv'
h_T = [h_T * 100.0 for h_T in h_T]  # Transferring to %
plot_and_save_data(Tx, h_T, x_label, y_label, graph_title, filename)
