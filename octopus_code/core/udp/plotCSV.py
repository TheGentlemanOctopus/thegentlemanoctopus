import matplotlib.pyplot as plt
import sys
import numpy as np
import csv


if __name__=='__main__':
    if len(sys.argv) < 2:
        print "specify csv file as first arg"
        quit()
    

    filename = sys.argv[1]

    fft_data = []
    with open(filename, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csv_reader:
            fft_data.append([int(x) for x in row])

    plt.pcolor(fft_data)
    plt.colorbar()
    plt.xlabel('Band')
    plt.ylabel('Time (index)')
    plt.show()