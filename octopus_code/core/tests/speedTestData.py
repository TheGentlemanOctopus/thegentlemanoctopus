import csv


class SpeedTestData:
    def __init__(self, t, framerate, cpu, mem):
        self.t = t
        self.framerate = framerate
        self.cpu = cpu
        self.mem = mem

    # This should be saved in the order of the constructors input args
    def save(self, file_handle):
        #Log data
        data = [self.t, self.framerate, self.cpu, self.mem]
        file_handle.write(",".join([str(x) for x in data]) + '\n')

# Retruns a list of SpeedTestData objects
def load_csv(filename):
    testData = []

    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        return [SpeedTestData(*row) for row in csvreader]

    return testData