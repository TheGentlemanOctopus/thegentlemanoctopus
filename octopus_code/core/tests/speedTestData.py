import csv


class SpeedTestData:
    def __init__(self, t, framerate, cpu, mem):
        self.t = t
        self.framerate = framerate
        self.cpu = cpu
        self.mem = mem

    def save(self, file_handle):
        #Log data
        data = [self.t, self.framerate, self.cpu, self.mem]
        file_handle.write(",".join([str(x) for x in data]) + '\n')

def load_csv(filename):
    testData = []
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            testData.append(SpeedTestData(
                float(row[0]), 
                float(row[1]), 
                float(row[2]), 
                float(row[3])
            ))

    return testData