import csv


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

# Retruns a list of SpeedTestData objects
def load_csv(filename):
    print "writing"
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        return [IntegrationTestData(*row) for row in csvreader]
