import threading
import socket
import Queue
import time
import random

from core.audioAnalysis.beatDetection import BeatDetection
from core.udp.udpServer import UDPServer


'''
AudioProcessing class is used to wrap all audio tasks
'''
class AudioProcessing(threading.Thread):
    """docstring for AudioProcessing
    TODO: check ctl queue
    """

    def __init__(self, args, op_queues, ctrl_queue=None):
        '''
        args: dictionary from config file for audio
        queues: list of queues to receive audio data
        '''
        threading.Thread.__init__(self)
        self.daemon = True
        self._running_flag = False
        self.stop = threading.Event()

        self.channels = args['FFT_channels']
        self.queues = op_queues

        self.ctrl = ctrl_queue
        self.sim = args['sim']
        ''' create fft '''
        self.dataqueue = Queue.Queue(100)
        
        if not self.sim:
            self.server = UDPServer(
                self.dataqueue,
                arduino_ip = args['Arduino_ip'],    
                start_port = args['UDP_start_port'],
                data_port = args['UDP_data_port'],
                fft_extent_reset_time = args['AG_fft_extent_reset_time'],
                autogainEnable = args['AG_Enable'],
                )
            self.server.start()
        
        ''' create BeatDetection '''
        self.bd = BeatDetection(7, args['BD_threshold'], args['BD_stretch'])


    def terminate(self):
        ''' to raise flag '''
        self.stop.set()

    def run(self):
        ''' main worker method '''
        try:
            while(not self.stop.wait(0.01)):
                ''' simulated '''
                if self.sim:
                    # print 'simulate'
                    self.simulate()
                    ''' real '''                
                elif not self.dataqueue.empty():

                    fft_data = self.dataqueue.queue[-1]
                    with self.dataqueue.mutex:
                        self.dataqueue.queue.clear()

                    ''' if queue available then pass to BD '''
                    beat_data = self.bd.detectBeat(fft_data)


                    ''' then pass through each queue in list '''
                    for q in self.queues:
                        with q.mutex:
                            q.queue.clear()
                        q.put(fft_data+beat_data)
            
            print 'Exiting thread', self.id
        finally:
            self._running_flag = False


    def simulate(self):
        ''' for simulating data when hardware is not attached '''

        fft_data = [random.randint(0,10) for x in xrange(self.channels)]
        bd_data = [bool(random.getrandbits(1)) for x in xrange(self.channels)]
        for q in self.queues:
            with q.mutex:
                q.queue.clear()
            q.put(fft_data+bd_data)



if __name__ == '__main__':  

    d = {}
    d['BE_Enable'] = 1
    d['BD_threshold'] = 85
    d['BD_stretch'] = 18
    d['AG_Enable'] = 1
    d['AG_fft_extent_reset_time'] = 30
    d['sim'] = 1
    qs = [Queue.Queue()]

    ap = AudioProcessing(d,qs)

    ap.start()

    while True:
        if not qs[0].empty():
            data = qs[0].get()
            print 'audio data: ', data