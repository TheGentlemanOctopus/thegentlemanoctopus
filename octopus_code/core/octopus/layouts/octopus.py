import numpy as np
import json
import os

#TODO: color mappings

class Octopus:
    def __init__(self, mantle_radius, leg_length, pixels_per_strip):
        self.mantle_radius = mantle_radius
        self.leg_length = leg_length
        self.pixels_per_strip = pixels_per_strip

        self.legs = []

        for theta in np.linspace(0, (14.0/8.0)*np.pi, 8):
            self.legs.append(Leg(mantle_radius, theta, leg_length, pixels_per_strip))

    def clone(self):
        return Octopus(self.mantle_radius, self.leg_length, self.pixels_per_strip)

    def pixels(self):
        pixels = []
        for leg in self.legs:
            pixels.extend(leg.pixels())

        return pixels

    # Base --> Tip; Tip --> Base, Base --> Tip ....
    def pixels_zig_zag(self):
        pixels = []
        for leg in self.legs:
            pixels.extend(leg.pixels_zig_zag())

        return pixels

    def pixels_spiral(self):
        pixels = []

        led_strips = []
        for leg in self.legs:
            led_strips.extend(leg.led_strips)

        count = -1
        traversed_count = 0
        while traversed_count < len(led_strips):
            count += 1
            traversed_count = 0

            for i in range(len(led_strips)):
                led_strip = led_strips[i].pixels

                if count >=len(led_strip):
                    traversed_count += 1
                    continue

                pixels.append(led_strip[count])

        return pixels



    def export(self, filepath):
        #Hacky, but gl_server doesn't mind
        #and I don't want to edit the gl_server right now
        pixels = [{'point': pixel.location.tolist()} for pixel in self.pixels_zig_zag()]
        pixels[0]['metadata'] = {
            'mantle_radius': self.mantle_radius,
            'leg_length' : self.leg_length,
            'pixels_per_strip': self.pixels_per_strip
        } 
        
        with open(os.path.join(os.path.dirname(__file__), filepath), 'w') as f:
            f.write(json.dumps(pixels, indent=4))
    
        print "Output File: ", len(pixels)-1, "pixels"
    
    def clear_pixels(self):
        for pixel in self.pixels():
            pixel.color = (0,0,0)

    def pixel_colors(self):
        return [pixel.color for pixel in self.pixels()]

def ImportOctopus(filepath):
    try:
        with open(filepath) as data_file:    
            data = json.load(data_file)
    except Exception:
        raise Exception("Could load octopus from " + filepath)

    # Hacky but I don't feel like messing with the gl_Server right now
    if (not data) or (not "metadata" in data[0]):
        raise Exception("Could not find octopus metadata in", filepath)

    metadata = data[0]["metadata"]

    return Octopus(
        metadata["mantle_radius"], 
        metadata["leg_length"],
        metadata["pixels_per_strip"] 
        )

class Leg:
    def __init__(self, r, theta, length, nPixels):
        self.led_strips = []

        dTheta = np.pi/32
        for angle in [theta + dTheta, theta - dTheta]:
            base = [r*np.cos(angle), r*np.sin(angle), 0]
            direction = [np.cos(angle), np.sin(angle), 0]
            self.led_strips.append(LedStrip(base, length, direction, nPixels))

    def pixels(self):
        pixels = []
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels)

        return pixels

    # Base --> Tip; Tip --> Base, Base --> Tip ....
    def pixels_zig_zag(self):
        pixels = []
        flip = False
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels[::-1] if flip else led_strip.pixels)
            flip = not flip

        return pixels

class LedStrip:
    def __init__(self, base, length, direction, nPixels):
        self.base = base
        self.length = length
        self.direction = direction/np.linalg.norm(direction)
        
        dP = (self.length/float(nPixels - 1)) * self.direction
        self.pixels = [Pixel(self.base + i*dP) for i in range(nPixels)]

    #Always starting from the base, excess pixels/colored are ignored
    def put_pixels(self, colors):
        for i in range(np.min([len(self.pixels), len(colors)])):
            self.pixels[i].color = colors[i]

class Pixel:
    def __init__(self, location, color=(0,0,0)):
        self.location = location
        self.color = color

def plot_octopus(octopus):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D


    pixels = octopus.generate_pixel_locations()
    x = [pixel[0] for pixel in pixels]
    y = [pixel[1] for pixel in pixels]
    z = [pixel[2] for pixel in pixels]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x,y,z)
    plt.show()

# Just your everyday octopus :)
if __name__ == '__main__':
    octopus = Octopus(0.5, 3, 31)

    filepath = 'octopus.json'
    octopus.export(filepath)

    # How to import octopuses
    #new_octopus = ImportOctopus(filepath)
    #new_octopus.export(filepath)

