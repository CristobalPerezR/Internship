# ALL IMPORTS
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl
import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import os
from os.path import isfile, join
from os import walk
import time

mpl.style.use("classic")

#Load all directories from all files into lists
def init_archives():
    fraw = []
    fCBV = []
    fOLC = [] #Outlier Cleaned

    for (dirpath, dirnames, filenames) in walk("..\\_TESS_lightcurves_raw"):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            pathTittle = full_path.split(os.sep)
            step = []
            step.append(full_path)
            step.append(pathTittle[-2])
            step.append(pathTittle[-1])
            fraw.append(step)

    for (dirpath, dirnames, filenames) in walk("..\\_TESS_lightcurves_median_after_detrended"):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            pathTittle = full_path.split(os.sep)
            step = []
            step.append(full_path)
            step.append(pathTittle[-2])
            step.append(pathTittle[-1])
            fCBV.append(step)

    for (dirpath, dirnames, filenames) in walk("..\\_TESS_lightcurves_outliercleaned"):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            pathTittle = full_path.split(os.sep)
            step = []
            step.append(full_path)
            step.append(pathTittle[-2])
            step.append(pathTittle[-1])
            fOLC.append(step)

    return fraw, fCBV, fOLC

def plotting3(lc_data, lc_dataCBV=None, lc_dataOLC=None, tittle="", axs=None):
    tess_data_raw = lc_data.to_records(index=False)
    tess_data_CBV = lc_dataCBV.to_records(index=False)
    tess_data_OLC = lc_dataOLC.to_records(index=False)

    # First Graph: Light Curve Raw
    axs[0].errorbar(tess_data_raw["JD"], tess_data_raw["MAG"], yerr=tess_data_raw["ERR"], fmt=".k", ecolor="gray", label=r"Light Curve")
    axs[0].grid(which="major")
    axs[0].legend(loc="lower left")
    axs[0].minorticks_on()
    axs[0].invert_yaxis()
    axs[0].set_title(f"{tittle} - Raw Data")
    axs[0].tick_params(which='both', direction='in', tick2On=True)
    axs[0].ticklabel_format(useOffset=False)

    # Second Graph: Light Curve after CBV
    axs[1].errorbar(tess_data_CBV["JD"], tess_data_CBV["MAG_Clean"], yerr=tess_data_CBV["ERR"], fmt=".k", ecolor="gray", label=r"Light Curve (After CBV)")
    axs[1].grid(which="major")
    axs[1].legend(loc="lower left")
    axs[1].minorticks_on()
    axs[1].invert_yaxis()
    axs[1].set_title(f"{tittle} - After CBV")
    axs[1].tick_params(which='both', direction='in', tick2On=True)
    axs[1].ticklabel_format(useOffset=False)

    # 3rd Graph: Light Curve after outlier Cleaner
    axs[2].errorbar(tess_data_OLC["JD"], tess_data_OLC["MAG"], yerr=tess_data_OLC["ERR"], fmt=".k", ecolor="gray", label=r"Light Curve Outlier Cleaned")
    axs[2].grid(which="major")
    axs[2].legend(loc="lower left")
    axs[2].minorticks_on()
    axs[2].invert_yaxis()
    axs[2].set_title(f"{tittle} - After OLC")
    axs[2].tick_params(which='both', direction='in', tick2On=True)
    axs[2].ticklabel_format(useOffset=False)

if __name__ == "__main__":
    fraw, fCBV, fOLC = init_archives()
    categories = []
    for i in range(len(fraw)):
        if fraw[i][1] not in categories:
            categories.append(fraw[i][1])

    #Plotting and Save on PDF
    i = 0
    j = 0
    inicio = time.time()
    while j < len(categories):
        while i < len(fraw) and fraw[i][1] == categories[j]:
            print(i, j)# Archive Index, Category Index
            data_raw = pd.read_csv(fraw[i][0], delim_whitespace=True, names=["JD", "MAG", "ERR"], na_values="*********")
            data_CBV = pd.read_csv(fCBV[i][0], delim_whitespace=True, names=["JD", "MAG_Clean", "MAG_After_CBV", "ERR"], na_values="*********")
            data_OLC = pd.read_csv(fOLC[i][0], delimiter=",", names=["JD", "MAG", "ERR"], na_values="*********")

            fig, axs = plt.subplots(3, 1, figsize=(10, 12))  # 3 rows y 1 column
            fig.subplots_adjust(hspace=0.3)
            title = (fraw[i][1] + " " + fraw[i][2])[:-3]
            
            plotting3(data_raw,data_CBV,data_OLC, title, axs)

            subsub = "LC_PDF"
            subpath = categories[j]+"_LightCurves"
            file = fraw[i][2][:-3] + ".pdf"
            os.makedirs(os.path.join(subsub, subpath), exist_ok=True)
            completePath = os.path.join(subsub,subpath, file)
            with PdfPages(completePath) as pdf:
                pdf.savefig()
            plt.close()
            i += 1
        j += 1
    fin = time.time()
    print(fin - inicio)