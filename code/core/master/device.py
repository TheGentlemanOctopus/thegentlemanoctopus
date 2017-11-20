import numpy as np
from multiprocessing import Process, Queue
import datetime

# import opc

'''
Inherit this class and overide the next frame method
'''

class Device(Process):
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, frame_period=100, opc_ip='127.0.0.1:7890'):
        Process.__init__(self)
        ''' location is the coordinate of the pixel'''
        self.frame_period = frame_period
        self.audio_queue = Queue()
        self.pixel_queue = Queue()
        self.control_queue = Queue()
        print 'Period:', self.frame_period
        self.audio_data = [0.0,0.0,0.0,0.0,0.0,'a','b','c','d','e']
        # self.client = opc.Client(opc_ip)
        # if self.client.can_connect():
        #     print('    connected to %s' % opc_ip)
        # else:
        #     # can't connect, but keep running in case the server appears later
        #     print('    WARNING: could not connect to %s' % opc_ip)
        # print('')

        # self.current_animation = None

    def get_audio_queue(self):
        return self.audio_queue

    def get_pixel_queue(self):
        return self.pixel_queue

    def get_control_queue(self):
        return self.control_queue

    def run(self):

        last_frame = datetime.datetime.now()

        while True:
            
            now = datetime.datetime.now()
            delta = (now-last_frame).total_seconds()*1000

            ''' check queues '''
            self.check_audio_queue()
            self.check_control_queue()

            # if delta >= self.frame_period:
            if delta >= self.current_animation.frame_period:
                last_frame = now
                
                ''' update animation '''
                self.current_animation.next_frame(self.audio_data)


    def next_frame(self):
        print 'Hello world! Delete me I am redundant'

    def check_audio_queue(self):
        ''' polls the audio queue for new data '''
        if not self.audio_queue.empty():
            self.audio_data = self.audio_queue.get()
            # self.update_audio(self.audio_data)
            return True
        else:
            return None
        
    def check_control_queue(self):
        ''' polls the control queue for requests '''
        if not self.control_queue.empty():
            msg = self.control_queue.get()
            if msg == 'get_colours':
                self.pixel_queue.put(self.get_colours())
            return msg
        else:
            return None



if __name__ == '__main__':

    d = Device(frame_period=1000)
    d.daemon = True
    d.start()


