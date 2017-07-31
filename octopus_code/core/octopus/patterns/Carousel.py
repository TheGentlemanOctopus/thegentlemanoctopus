from pattern import Pattern

class Carousel(Pattern):
    # Speed is in degress per second
    def __init__(self, speed=180):
        self.register_param("speed", 0, 1080)

    def main(self):

        



if __name__ == '__main__':
    carousel = Carousel()