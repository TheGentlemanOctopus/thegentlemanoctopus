import threading
import socket
import Queue
import time

from core.audioAnalysis.BeatDetection import BeatDetection
from core.udp.udp_server import UDPServer

'''
AudioProcessing class is used to wrap all audio tasks
'''
class AudioProcessing(threading.Thread):
    """docstring for AudioProcessing"""

    def __init__(self, args, queues):
        '''
        args: dictionary from config file for audio
        queues: list of queues to receive audio data
        '''
        self.daemon = True
        self._running_flag = False
        self.stop  = threading.Event()
        threading.Thread.__init__(self)


        ''' create fft '''
        self.dataqueue = Queue.Queue(100)
        self.server = UDPServer(dataqueue)
        self.server.start()
        
        ''' create BeatDetection '''
        self.bd = BeatDetection(7, args['BD_threshold'], args['BD_stretch']))


    def terminate(self):
        self.stop.set()

    def run(self):

        try:
            while(not self.stop.wait(0.01)):
                
                if not self.dataqueue.empty():
                    
                    fft_data = self.dataqueue.queue[-1]
                    with self.dataqueue.mutex:
                        self.dataqueue.queue.clear()

                    ''' if queue available then pass to BD '''
                    beat_data = self.bd.detectBeat(fft_data)

                    ''' then pass through each queue in list '''
                    for q in queues:
                        with q.mutex:
                            q.queue.clear()
                        q.put(fft_data+beat_data)
            
            print 'Exiting thread', self.id
        finally:
            self._running_flag = False





if __name__ == '__main__':  

    d = {}
    d['BE_Enable'] = 1
    d['BD_threshold'] = 85
    d['BD_stretch'] = 18
    d['AG_Enable'] = 0
    d['AG_fft_extent_reset_time'] = 30

    qs = [Queue.Queue()]

    ap = AudioProcessing(d,qs)

    ap.start()

    while True:
        if not qs[0].empty():
            data = qs[0].get()
            print 'audio data: ', data