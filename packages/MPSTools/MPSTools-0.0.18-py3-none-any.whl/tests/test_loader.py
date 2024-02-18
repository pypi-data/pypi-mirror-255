#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_material_loader():
    from MPSTools.material_catalogue import loader
    loader.get_material_index(material_name='silica', wavelength=1550e-9)


def test_fiber_loader():
    from MPSTools.fiber_catalogue import loader
    loader.load_fiber_as_dict(fiber_name='SMF28', wavelength=1550e-9)

# -
