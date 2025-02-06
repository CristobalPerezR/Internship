import numpy as np
import os
from os import walk
import corner
import matplotlib.pyplot as plt
import json
from matplotlib.backends.backend_pdf import PdfPages

def plotting(title, label, data1, data2, data3=None, data4=None, data5=None, data6=None):
    try:
        data11 = np.column_stack((data1, data2, data3))
        data12 = np.column_stack((data4, data5, data6))
    except:
        data11 = np.column_stack((data1, data2))
        data12 = np.column_stack((data4, data5))
    
    figure = corner.corner(data11, color="red", labels=label)
    corner.corner(data12, color="blue", labels=label, fig=figure)
    plt.suptitle(title)
    plt.show()

if __name__ == '__main__':
    with open('total.json', 'r') as f:
        data = json.load(f)

    i = 0
    while i < len(data):
        j = 1
        while j < 11:
            if j == 1:
                tlabels = ["Amplitude","Beyonds","Median Abs"]
            elif j == 4:
                tlabels = ["Median BRP","Percent Amplitude","Percent Amplitude Flux"]
            elif j == 7:
                tlabels = ["RCS","S. Kurtosis","MaxSlopes"]
            else:
                tlabels = ["Std","LinearTrend"]

            try:
                plotting((data[i][0] + " and " + data[i+1][0]), tlabels,
                        data[i][j],data[i][j+1],data[i][j+2],
                        data[i+1][j], data[i+1][j+1], data[i+1][j+2])
            except:
                plotting(title=(data[i][0] + " and " + data[i+1][0]), label=tlabels,
                        data1=data[i][j],data2=data[i][j+1],data3=None,
                        data4=data[i+1][j], data5=data[i+1][j+1], data6=None)
            subsub = "LC_CORNERS"
            subpath = data[i][0] + " and " + data[i+1][0] + "_Corners"
            
            if len(tlabels) == 3:
                file = tlabels[0] + "_" + tlabels[1] + "_" + tlabels[2] + ".pdf"
            else:
                file = tlabels[0] + "_" + tlabels[1] + ".pdf"

            os.makedirs(os.path.join(subsub, subpath), exist_ok=True)
            completepath = os.path.join(subsub, subpath, file)
            with PdfPages(completepath) as pdf:
                pdf.savefig()
            plt.close()
            j += 3
        i += 2