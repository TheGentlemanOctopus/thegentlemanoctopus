import threading 
import Queue
import time

# TODO: is there anything outside of the constructor that will actually be shared?
class Device(threading.Thread):
    ''' Generic interface for a sound reactive thing, such as a GentlemanOctopus
    or a school of fish
    '''
    def __init__(self, control_queue=None, audio_stream_queue=None):
        ''' inputs should be queues '''
        threading.Thread.__init__(self)
        self.process = None
        self.daemon = True

        # Initialise queues
        if not control_queue:
            control_queue = Queue.Queue(1)

        self.control_queue = control_queue

        # Initialise queues
        if not audio_stream_queue:
            audio_stream_queue = Queue.Queue(1)

        self.audio_stream_queue = audio_stream_queue


    # TODO: Make this non-blocking
    def run(self, timeout=0):
        ''' Run a sound reactive thing for a given aount of time (blocking)'''
        run_start = time.time()

        # 0 Means forever-and-ever-and-ever
        if not timeout:
            timeout = float("inf")

        # Generate the patterns
        while time.time() - run_start < timeout:
            loop_start = time.time()

            try:
                self.update()

            except Exception as e:
                print e

            loop_end = time.time() - loop_start
            loop_time = self.period - loop_end

            # Sleep to give time for other processes
            time.sleep(max(0, self.period - loop_end))

    def update(self):
        pass


if __name__ == '__main__':
    control_queue = Queue(1)
    audio_stream_queue = Queue(1)

    device = Device(control_queue, audio_stream_queue)
    device.start()
    print "Running device...."
    # device.run(2)