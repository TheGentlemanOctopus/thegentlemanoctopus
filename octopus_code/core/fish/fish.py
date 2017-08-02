import Queue
import time
from core.octopus.device import Device
from core.Serial.SerialThread import SerialThread

# TODO: is there anything outside of the constructor that will actually be shared?
''' TODO move thread inheritence to device '''
class Fish(Device):
    ''' interface for a sound reactive fish '''
    def __init__(self, conf, control_queue=None, audio_stream_queue=None, name="FishThread"):
        self.ctrl_q = control_queue
        self.audio_q = audio_stream_queue
        Device.__init__(self, control_queue=self.ctrl_q, audio_stream_queue=self.audio_q)
        
        self.dataQueue = Queue.Queue(1000)

        self.serialTh = SerialThread(
            self.dataQueue,
            sim=conf['sim'],
            port=conf['port'], 
            baud=conf['baud'], 
            name='FishThread'
            )
        self.serialTh.start()



    # TODO: Make this non-blocking
    def run(self):
        print 'fsh run\n'
        ''' check audio queue '''
        while  True:
            if not self.audio_q.empty():
                ''' take latest element '''
                msg = self.audio_q.queue[-1]
                # print msg
                # ''' clear old data '''
                # with self.audio_q.mutex:
                #     self.audio_q.queue.clear()
                ''' pass beat data to serial thread '''
                self.dataQueue.put(msg[7:])
            time.sleep(1.0/10000.0);



if __name__ == '__main__':
    control_queue = Queue(1)
    audio_stream_queue = Queue(1)

    device = Fish(control_queue, audio_stream_queue)
    device.start()
    print "Running device...."
