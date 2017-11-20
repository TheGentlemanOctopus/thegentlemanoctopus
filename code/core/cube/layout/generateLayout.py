import numpy as np
import json
import os

import Cube


def export(cube, filepath):
    ''' Export octopus into a json file that is compatible with gl server and import '''
    
    # Include metadata in the first pixel object
    # TODO: a bit hacky is there a better way?
    pixel_d = [ {'point': pixel} for pixel in cube.pixels]
    
    # pixels[0]['metadata'] = {
    #     'mantle_radius': self.mantle_radius,
    #     'tentacle_length' : self.tentacle_length,
    #     'pixels_per_strip': self.pixels_per_strip
    # } 
    
    # Dump to file
    with open(os.path.join(os.path.dirname(__file__), filepath), 'w') as f:
        f.write(json.dumps(pixel_d, indent=4))



# def Import(filepath):
#     ''' contructs a octopus layout from a json file created by OctopusLayout.export '''
#     try:
#         with open(filepath) as data_file:    
#             data = json.load(data_file)
#     except Exception:
#         raise Exception("Could load octopus from " + filepath)

#     # Hacky but I don't feel like messing with the gl_Server right now
#     if (not data) or (not "metadata" in data[0]):
#         raise Exception("Could not find octopus metadata in", filepath)

#     metadata = data[0]["metadata"]

#     return OctopusLayout(
#         metadata["mantle_radius"], 
#         metadata["tentacle_length"],
#         metadata["pixels_per_strip"] 
#         )



# Just your everyday octopus :)
if __name__ == '__main__':
    cube = Cube.Cube(origin=(0,0,0))

    filepath = 'cubeLayout.json'
    export(cube,filepath)

    # How to import octopuses
    #new_octopus = Import(filepath)
    #new_octopus.export(filepath)

