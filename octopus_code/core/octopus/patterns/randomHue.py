from pattern import Pattern
from colorutils import Color
import random

class RandomHue(Pattern):
	def __init__(self):
		# self.register_param("red", 0, 255, 100)
		self.mid = 0

	def next_frame(self, octopus, data):

		self.mid = (self.mid + 1)%255

		for pixel in octopus.pixels():
			p = (self.mid + random.randint(1, 40)) % 255
			col = Color(hsv=(p, random.uniform(0.2,0.8) , random.uniform(0.2,0.8) ))
			pixel.color=(col.rgb)






