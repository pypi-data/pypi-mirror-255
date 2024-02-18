#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import numpy
from pathlib import Path

from MPSTools.material_catalogue.loader import get_material_index


def load_fiber_as_dict(fiber_name: str, wavelength: float = None, order: str = 'in-to-out') -> dict:
    """
    Loads the fiber parameters as dictionary.

    :param      fiber_name:      The fiber name
    :type       fiber_name:      str
    :param      wavelength:      he wavelength, can be None if no material is describing the fiber
    :type       wavelength:      float
    :param      order:           The order of the layer ['in-to-out' or 'out-to-in']
    :type       order:           str

    :returns:   The fiber parameters dictionnary
    :rtype:     dict
    """
    assert order.lower() in ['in-to-out', 'out-to-in'], f'Order: {order} has to be either "in-to-out" or "out-to-in"'
    output_dict = {}

    cwd = Path(__file__).parent

    file = cwd.joinpath(f'./fiber_files/{fiber_name}.yaml')

    assert file.exists(), f'Fiber file: {fiber_name} does not exist.'

    configuration = yaml.safe_load(file.read_text())

    copy_configuration = configuration

    outer_layer = None
    for layer_idx, current_layer in configuration['layers'].items():

        output_dict[layer_idx] = current_layer

        index = current_layer.get('index')
        NA = current_layer.get('NA')
        name = current_layer.get('name')
        radius = current_layer.get('radius')
        material = current_layer.get('material')

        if outer_layer is not None:
            assert radius <= outer_layer.get('radius'), f'Layer declaration order for {file} is not from outer-most to inner-most as it should be.'

        assert numpy.count_nonzero([material, NA, index]), f"Either NA or index has to be provided for the layer: {name}."

        if NA is not None:
            assert bool(outer_layer), 'Cannot compute NA if no outer layer is defined.'
            outer_index = outer_layer.get('index')
            output_dict[layer_idx]['index'] = numpy.sqrt(NA**2 + outer_index**2)

        if material is not None:
            assert bool(wavelength), 'Cannot evaluate material refractive index if wavelength is not provided.'
            output_dict[layer_idx]['index'] = get_material_index(
                material_name=material,
                wavelength=wavelength
            )

        outer_layer = output_dict[layer_idx]

    if order == 'out-to-in':
        reversed_dict = {}
        for key in reversed(list(output_dict.keys())):
            reversed_dict[key] = output_dict[key]

        output_dict = reversed_dict

    for _, layer in output_dict.items():
        layer.pop("NA", None)
        layer.pop("material", None)

    copy_configuration['layers'] = output_dict

    return copy_configuration

# -
