import csv
import subprocess
import numpy as np

class IntegrationTestData:
    def __init__(self, t, framerate, cpu, mem, pattern_name):
        self.t = float(t)
        self.framerate = float(framerate)
        self.cpu = float(cpu)
        self.mem = float(mem)
        self.pattern_name = pattern_name

    # This should be saved in the order of the constructors input args
    def save(self, file_handle):
        #Log data
        data = [self.t, self.framerate, self.cpu, self.mem, self.pattern_name]
        file_handle.write(",".join([str(x) for x in data]) + '\n')

# Returns a list of SpeedTestData objects,
# Sample period is test time in seconds between row captures
def load_csv(filename, sample_period=0):

    previous_take = -np.inf

    time_series = []

    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')

        for row in csvreader:
            data = IntegrationTestData(*row)

            if data.t - previous_take > sample_period:
                time_series.append(data)
                previous_take = data.t

    return time_series
