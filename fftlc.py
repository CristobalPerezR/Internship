import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
import os
from os import walk
from astropy.timeseries import LombScargle
from matplotlib.backends.backend_pdf import PdfPages

mpl.style.use("classic")

def load_lc():
    fOLC = [] #Outlier Cleaned
    for (dirpath, dirnames, filenames) in walk("..\\_TESS_lightcurves_outliercleaned"):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            pathTittle = full_path.split(os.sep)
            step = []
            step.append(full_path)
            step.append(pathTittle[-2])
            step.append(pathTittle[-1])
            fOLC.append(step)

    return fOLC

def RSquare(data, y_fit):
    ss_res = np.sum((data["MAG"] - y_fit) ** 2)  # Suma de residuos al cuadrado
    ss_tot = np.sum((data["MAG"] - np.mean(data["MAG"])) ** 2)  # Total de variación
    r_squared = 1 - (ss_res / ss_tot)
    #print(f"R^2: {r_squared}")
    return r_squared

def fitt_finding(data):
    r_squared = 0
    k = 1
    while r_squared < 0.99 or k < 1000:
        #print(k)
        yfft = np.fft.fft(data["MAG"])
        yfft[k + 1:-k] = 0
        y_fit = np.fft.ifft(yfft).real
        r_squared = RSquare(data, y_fit)
        k += 1

    return y_fit, k

def periodogram(t, y, dy):
    # Periodograma Lomb-Scargle
    time_range = t.max() - t.min()
    ls = LombScargle(t, y, dy)
    minfreq = 1 / (time_range*1.5)

    freq, power = ls.autopower(nyquist_factor=1, minimum_frequency=minfreq)
    periods = 1 / freq
    best_period = periods[np.argmax(power)]

    return periods, power, best_period

def plot2_3(original, fitted, k, title, periods, power, best_period):
    fig = plt.figure(figsize=(16,8), layout="constrained")

    gs = GridSpec(3,6, figure=fig)  # <-----------------

    if best_period >= 5:
        c = 1
    elif best_period >= 2:
        c = 2
    else:
        c = 4

    ymin = original["MAG"].min() - 0.1
    ymax = original["MAG"].max() + 0.1

    ax0 = fig.add_subplot(gs[0, :3])
    ax0.errorbar(original["JD"], original["MAG"], yerr=original["ERR"], fmt=".k", ecolor="gray", label="Light Curve")
    ax0.plot(original["JD"], fitted, label="FFT %i mode" %k)
    ax0.grid(which="major")
    ax0.legend(loc="lower left", fontsize="10")
    ax0.minorticks_on()
    ax0.set_ylim(ymin, ymax)
    ax0.invert_yaxis()
    ax0.tick_params(which='both', direction='in', tick2On=True)
    ax0.ticklabel_format(useOffset=False)
    ax0.set_ylabel("Magnitude")
    ax0.set_xlabel("Julian Days")

    ax0z = fig.add_subplot(gs[1, :3])
    ax0z.errorbar(original["JD"], original["MAG"], yerr=original["ERR"], fmt=".k", ecolor="gray", label="Light Curve")
    ax0z.plot(original["JD"], fitted, label="FFT %i mode" %k)
    ax0z.grid(which="major")
    ax0z.legend(loc="lower left", fontsize="10")
    ax0z.minorticks_on()
    ax0z.set_ylim(ymin, ymax)
    ax0z.set_xlim(original["JD"].min(), original["JD"].min() + best_period * c)
    ax0z.invert_yaxis()
    ax0z.tick_params(which='both', direction='in', tick2On=True)
    ax0z.ticklabel_format(useOffset=False)
    ax0z.set_ylabel("Magnitude")
    ax0z.set_xlabel("Julian Days")

    ax1 = fig.add_subplot(gs[0, 3:])
    ax1.plot(original["JD"], fitted, label="FFT %i mode" %k)
    ax1.grid(which="major")
    ax1.legend(loc="lower left", fontsize="10")
    ax1.set_ylim(ymin, ymax)
    ax1.minorticks_on()
    ax1.invert_yaxis()
    ax1.tick_params(which='both', direction='in', tick2On=True)
    ax1.ticklabel_format(useOffset=False)
    ax1.set_xlabel("Julian Days")

    ax1z = fig.add_subplot(gs[1, 3:])
    ax1z.plot(original["JD"], fitted, label="FFT %i mode" %k)
    ax1z.grid(which="major")
    ax1z.legend(loc="lower left", fontsize="10")
    ax1z.minorticks_on()
    ax1z.set_ylim(ymin, ymax)
    ax1z.set_xlim(original["JD"].min(), original["JD"].min() + best_period * c)
    ax1z.invert_yaxis()
    ax1z.tick_params(which='both', direction='in', tick2On=True)
    ax1z.ticklabel_format(useOffset=False)
    ax1z.set_xlabel("Julian Days")

    ax2 = fig.add_subplot(gs[2, :])
    ax2.plot(periods, power, '-', c='black', lw=1, zorder=1)
    ax2.axvline(best_period, color="r", linestyle="-.", label=f"Best {best_period:.3f} días")
    ax2.set_xlim(0, periods[np.argmax(periods)]+1)
    ax2.set_ylim(-0.05, power.max() + 0.1)
    ax2.set_xlabel('Period (days)')
    ax2.set_ylabel('Power')
    ax2.legend()

    ax3 = ax2.twinx()
    ax3.set_ylim(0,10)
    ax3.set_ylabel(r'$\Delta BIC$')

    fig.suptitle(title)

if __name__ == "__main__":
    data = load_lc()
    categories = []
    for i in range(len(data)):
        if data[i][1] not in categories:
            categories.append(data[i][1])

    i, j = 0, 0
    while j < len(categories):
        while i < (len(data)) and data[i][1] == categories[j]:
            print(i,j)
            lc = pd.read_csv(data[i][0], delimiter=",", names=["JD", "MAG", "ERR"], na_values="*********")
            title = (data[i][1] + " " + data[i][2])[:-3]
            y_fit, k = fitt_finding(lc)

            ## Periodograma
            y = lc["MAG"]
            t = lc["JD"]
            dy = lc["ERR"]

            periods, power, best_period = periodogram(t, y, dy)
            plot2_3(lc, y_fit, k, title, periods, power, best_period)

            subsub = "LC_FFT_LS"
            subpath = categories[j]+"_FFT_LS"
            file = "ID %i"%i + "_" + data[i][2][:-3] + ".pdf"
            os.makedirs(os.path.join(subsub, subpath), exist_ok=True)
            completePath = os.path.join(subsub,subpath, file)
            with PdfPages(completePath) as pdf:
                pdf.savefig()
            plt.close()
            i += 1
        j += 1