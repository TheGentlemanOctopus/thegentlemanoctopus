
# TODO: is there anything outside of the constructor that will actually be shared?
class Device:
    def __init__(self, control_queue, audio_stream_queue):
        self.control_queue = control_queue
        self.audio_stream_queue = audio_stream_queue