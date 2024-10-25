""" Based on https://github.com/DYK-Team/Brushed_DC_motor_solver/blob/master/main.py

Estimates DC motor parameters based on measurements of current, angular speed,
and output torque at no load, at (close to) rated load, and at stall.

Computes idealized characteristics that take into account a constant internal 
friction torque.

Further reading: https://support.maxongroup.com/hc/en-us/articles/360001900933-Formulae-Handbook
"""

import dataclasses as dc
import math

import matplotlib.pyplot as plt
import numpy as np


@dc.dataclass
class MeasurementEntry:
    U: float  # voltage
    wmax: float  # no-load angular speed
    I0: float  # no-load current
    wr: float  # angular speed (perhaps rated)
    Tr: float  # torque (perhaps rated)
    Ir: float  # current (perhaps rated)
    Tmax: float  # stall torque
    Imax: float  # stall current
    reduction_ratio: float = 1

    def normalize(self):
        r = self.reduction_ratio
        return (
            dc.replace(
                self,
                wmax=self.wmax * r,
                wr=self.wr * r,
                Tr=self.Tr / r,
                Tmax=self.Tmax / r,
                reduction_ratio=1,
            ),
            r,
        )


kgcm = 9.8 * 0.01  # Nm
rpm = 2 * math.pi / 60  # rad/ss

m = MeasurementEntry(12, 214 * rpm, 0.15, 171 * rpm, 2.3 * kgcm, 1, 9 * kgcm, 6, 37.3)
mn, reduction_ratio = m.normalize()

print(m)
print(mn)

Ua = mn.U
Imax = mn.Imax
Ra = Ua / Imax
Toutmax = mn.Tmax
dwdT1 = (mn.wr - mn.wmax) / mn.Tr
dwdT2 = -mn.wr / (mn.Tmax - mn.Tr)
dwdT = -mn.wmax / mn.Tmax
dTdI1 = mn.Tr / (mn.Ir - mn.I0)
dTdI = mn.Tmax / (mn.Imax - mn.I0)
KM = dTdI
Tf = KM * mn.I0
wmax0 = mn.wmax - Tf * dwdT
KF = Ua / wmax0

# KM = (Toutmax + Tf) / Imax
# KF = (Ua - (mn.Tr + Tf) / KM * Ra) / mn.wr
# assert np.isclose(KM, KF)
# wmax0 = Ua / KF
# Tf = KM * (Ua - KF * wmax0) / Ra

# Motor constants example:
# Ra = 3.41  # Armature resistance, Ohms
# KF = 6.589e-3  # Back-EMF constant, Vs/rad
# KM = 6.59e-3  # Torque constant, Nm/A
# Tf = 1.3e-4  # Friction torque, Nm
# TODO: friction torque component that is proportional to shear force?

# Input parameters:
# Ua = 6.0  # Armature voltage, V

# Output characteristics:
I0 = Tf / KM  # No-load armature current, A
Imax = Ua / Ra  # maximum current
Tmagmax = Imax * KM  # maximum magnetic torque, Nm
wmax0 = Ua / KF  # maximum angular speed without friction, rad/s
wmax = wmax0 - Ra * Tf / (KF * KM)  # maximum angular speed with friction, rad/s
# wmax = wmax0 * (1. - Tf / Tmagmax)  # maximum angular speed with friction, rad/s
hmax = (KM / KF) * (1.0 - ((Ra * Tf) / (Ua * KM)) ** 0.5) ** 2  # maximum efficiency
Pmmax = (Ua**2 * KM) / (4.0 * KF * Ra)  # maximum mechanical power, W
dwdT = Ra / (KF * KM)  # dw/dT slope, rad/(sNm)

print("Output characteristics:")
print("Maximum angular speed = ", format(wmax, ".3e"), " rad/s")
print("Maximum torque = ", format(Tmagmax, ".3e"), " Nm")
print("Maximum efficiency = ", format(hmax * 100, ".3e"), "%")
print("Maximum mechanical power = ", format(Pmmax, ".3e"), " W")
print("No-load armature current = ", format(I0, ".3e"), " A")
print("dw/dT slope = ", format(dwdT, ".3e"), " rad/(sNm)")

# Arrays for graphs
N = 1000  # Number of points in the graph
Tmag = Tf + (Tmagmax - Tf) * np.linspace(0, 1, N)  # magnetic torque (array)
Tout = Tmag - Tf  # measurable output torque
w = Ua / KF - (Ra * Tmag) / (KF * KM)  # angular speed
# w = Ua / KF - (Ra * Tout) / (KF * KM)  # angular speed
I = Tmag / KM  # current
Pm = w * Tout  # mechanical power
h = (KM / KF) * (1.0 - (Ra * Tmag) / (Ua * KM)) * (1.0 - Tf / Tmag)  # efficiency


def plot(T, label_to_characteristic, title="DC motor characteristics"):
    # Colors for each characteristic, can be customized further if needed
    colors = plt.cm.tab10(range(len(label_to_characteristic)))

    # Plot additional characteristics with separate y-axes on the left
    ax_list = []  # Keep track of the axes
    for i, (y_label, (y, measurements, min_max)) in enumerate(
        label_to_characteristic.items()
    ):
        if i == 0:
            fig, ax_new = plt.subplots()  # Create the initial figure and first axis
            plt.xlabel("Torque [Nm]")
        else:
            ax_new = ax_list[0].twinx()  # Create a new y-axis
        if min_max is not None:
            ax_new.set_ylim(*min_max)
        else:
            pass
            ax_new.set_ylim(0, max([max(y)] + list(measurements[1])) * 1.02)
        ax_new.set_xlim(0, max([max(T)] + list(measurements[0])) * 1.02)
        ax_list.append(ax_new)
        ax_new.plot(T, y, color=colors[i])
        ax_new.scatter(*measurements, color=colors[i])
        ax_new.set_ylabel(y_label, color=colors[i])
        ax_new.tick_params(axis="y", labelcolor=colors[i])

        if i > 0:
            # Move the new axis to the left side
            ax_new.spines["left"].set_position(
                ("outward", 50 * i)
            )  # Offset each label to avoid overlap
            ax_new.yaxis.set_label_position("left")
            ax_new.yaxis.tick_left()

            # Hide the right spine, since we don't need labels on the right
            ax_new.spines["right"].set_visible(False)

    # Displaying the plot
    plt.title(title)
    plt.tight_layout()
    plt.show()


plot(
    Tout,
    {
        "Angular speed [rad/s]": (
            w,
            ([0, mn.Tr, mn.Tmax], [mn.wmax, mn.wr, 0]),
            None,
        ),
        "Output power [W]": (Pm, ([], []), None),
        "Current [A]": (I, ([0, mn.Tr, mn.Tmax], [mn.I0, mn.Ir, mn.Imax]), None),
        "Efficiency": (h, ([], []), (0, 1)),
    },
    title=f"DC motor characteristics ({Ua} V)",
)
