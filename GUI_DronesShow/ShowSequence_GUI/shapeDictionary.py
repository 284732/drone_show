
""" This module defines a dictionary to hold shape configurations for different steps in a sequence. """


global SHAPES
SHAPES = ['Sphere', 'Grid', 'Circle', 'Line', 'Heart', 'Wave', 'Spiral', 'Number']

global parameters_dict
parameters_dict = {
    'Sphere': ['radius', 'center'],
    'Grid': ['radius', 'center', 'normal'],
    'Circle': ['radius', 'center', 'normal'],
    'Line': ['length', 'axis'],
    'Heart': ['size', 'center', 'plane'],
    'Wave': ['wavelength', 'amplitude', 'length', 'center'],
    'Spiral': ['radius_start', 'radius_end', 'height', 'turns', 'center'],
    'Number': ['digit', 'size', 'center', 'plane']
}

