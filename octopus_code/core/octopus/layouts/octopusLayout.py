import numpy as np
import json
import os

from tentacle import Tentacle
from mantle import Mantle


#TODO: color mappings
class OctopusLayout:
    ''' An octopus layout represents the morphology and spatial distribution of its chromatophores'''
    def __init__(self, mantle_radius, tentacle_length, pixels_per_strip):
        ''' mantle_radius is the radius of its mantle 
            tentacle_length is the unit length of each tentacle
            each tentacle has two led_strips each with pixels_per_strip chromatophores
        ''' 
        self.mantle_radius = mantle_radius
        self.tentacle_length = tentacle_length
        self.pixels_per_strip = pixels_per_strip

        # Cotruct Tentacles
        self.tentacles = []
        for theta in np.linspace(0, (14.0/8.0)*np.pi, 8):
            self.tentacles.append(Tentacle(mantle_radius, theta, tentacle_length, pixels_per_strip))

        # Construct mantle pixels
        self.mantle = Mantle(mantle_radius, pixels_per_strip)

    def clone(self):
        ''' create a new identical octopus layout from an existing one'''
        return OctopusLayout(self.mantle_radius, self.tentacle_length, self.pixels_per_strip)

    def pixels(self):
        ''' returns list of all pixels by concatenating along each strip from base-->tip, base-->tip '''
        pixels = []
        for leg in self.tentacles:
            pixels.extend(leg.pixels())

        return pixels

    def pixels_zig_zag(self):
        ''' returns list of all pixels by concatenating along each strip from base-->tip, tip-->base etc.. '''
        pixels = []
        for tentacle in self.tentacles:
            pixels.extend(tentacle.pixels_zig_zag())

        return pixels

    def pixels_spiral(self):
        ''' return list of pixels in an outward spiral like fashion '''

        # Create list of all pixels
        pixels = []

        led_strips = []
        for tentacle in self.tentacles:
            led_strips.extend(tentacle.led_strips)

        # Spiral Town
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

    def opc_pixels(self):
        pixels = self.pixels_zig_zag()


    def export(self, filepath):
        ''' Export octopus into a json file that is compatible with gl server and import '''
        
        # Include metadata in the first pixel object
        # TODO: a bit hacky is there a better way?
        pixels = [{'point': pixel.location.tolist()} for pixel in self.pixels_zig_zag()]
        pixels[0]['metadata'] = {
            'mantle_radius': self.mantle_radius,
            'tentacle_length' : self.tentacle_length,
            'pixels_per_strip': self.pixels_per_strip
        } 
        
        # Dump to file
        with open(os.path.join(os.path.dirname(__file__), filepath), 'w') as f:
            f.write(json.dumps(pixels, indent=4))
    
        print "Output File: ", len(pixels)-1, "pixels"
    
    def clear_pixels(self):
        ''' resets all pixels to black '''
        for pixel in self.pixels():
            pixel.color = (0,0,0)

    def pixel_colors(self):
        return [pixel.color for pixel in self.pixels()]

def Import(filepath):
    ''' contructs a octopus layout from a json file created by OctopusLayout.export '''
    try:
        with open(filepath) as data_file:    
            data = json.load(data_file)
    except Exception:
        raise Exception("Could load octopus from " + filepath)

    # Hacky but I don't feel like messing with the gl_Server right now
    if (not data) or (not "metadata" in data[0]):
        raise Exception("Could not find octopus metadata in", filepath)

    metadata = data[0]["metadata"]

    return OctopusLayout(
        metadata["mantle_radius"], 
        metadata["tentacle_length"],
        metadata["pixels_per_strip"] 
        )


def plot_octopus(octopus_layout):
    ''' MPL plots Ffor testing '''
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D


    pixels = octopus_layout.generate_pixel_locations()
    x = [pixel[0] for pixel in pixels]
    y = [pixel[1] for pixel in pixels]
    z = [pixel[2] for pixel in pixels]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x,y,z)
    plt.show()

# Just your everyday octopus :)
if __name__ == '__main__':
    octopus = OctopusLayout(0.5, 3, 31)

    filepath = 'octopusLayout.json'
    octopus.export(filepath)

    # How to import octopuses
    #new_octopus = Import(filepath)
    #new_octopus.export(filepath)

