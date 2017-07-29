from Queue import Queue

# TODO: is there anything outside of the constructor that will actually be shared?
class Device(object):
    def __init__(self, control_queue=None, audio_stream_queue=None):
        # Initialise queues
        if not control_queue:
            control_queue = Queue(1)

        self.control_queue = control_queue

        # Initialise queues
        if not audio_stream_queue:
            audio_stream_queue = Queue(1)

        self.audio_stream_queue = audio_stream_queue


if __name__ == '__main__':
    control_queue = Queue(1)
    audio_stream_queue = Queue(1)

    device = Device(control_queue, audio_stream_queue)