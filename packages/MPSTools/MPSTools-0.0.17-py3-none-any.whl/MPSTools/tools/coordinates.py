#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from dataclasses import dataclass
from typing import Self

from MPSPlots import render2D, render3D


@dataclass
class CylindricalCoordinates:
    rho: numpy.ndarray
    phi: numpy.ndarray
    z: numpy.ndarray

    def to_cartesian(self) -> object:
        x = self.rho * numpy.cos(self.phi)
        y = self.rho * numpy.sin(self.phi)
        z = self.z

        cartesian_coordinate = CartesianCoordinates(x=x, y=y, z=z)

        return cartesian_coordinate

    def to_cylindrical(self):
        return self


@dataclass
class CartesianCoordinates:
    x: numpy.ndarray
    """ Must be 1D-vector """
    y: numpy.ndarray
    """ Must be 1D-vector """
    z: numpy.ndarray
    """ Must be 1D-vector """

    is_structured: bool = False
    is_3D: bool = False

    @property
    def x_boundaries(self) -> float:
        return numpy.min(self.x), numpy.max(self.x)

    @property
    def y_boundaries(self) -> float:
        return numpy.min(self.y), numpy.max(self.y)

    @property
    def dx(self) -> float:
        if self.is_structured:
            x_min, x_max = self.x_boundaries()
            delta_x = x_max - x_min
            return delta_x / self.n_x

        else:
            raise ValueError('dx value cannot be infered from unstructured mesh')

    @property
    def dy(self) -> float:
        if self.is_structured:
            y_min, y_max = self.x_boundaries()
            delta_y = y_max - y_min
            return delta_y / self.n_y

        else:
            raise ValueError('dy value cannot be infered from unstructured mesh')

    @property
    def dz(self) -> float:
        if self.is_structured:
            z_min, z_max = self.x_boundaries()
            delta_z = z_max - z_min
            return delta_z / self.n_z

        else:
            raise ValueError('dz value cannot be infered from unstructured mesh')

    @classmethod
    def generate_from_boundaries(
            cls,
            x_limits: list = [-1, 1],
            y_limits: list = [-1, 1],
            z_limits: list = [-1, 1],
            x_points: int = 100,
            y_points: int = 100,
            z_points: int = 100):

        cls.is_structured = True
        cls.is_3D = True

        x = numpy.linspace(x_limits[0], x_limits[1], x_points)
        y = numpy.linspace(y_limits[0], y_limits[1], y_points)
        z = numpy.linspace(z_limits[0], z_limits[1], z_points)

        instance = CartesianCoordinates(
            x=x,
            y=y,
            z=z
        )

        instance.is_structured = True
        instance.is_3D = True

        return instance

    @classmethod
    def generate_from_cube(
            cls,
            length: float,
            center: tuple = (0, 0, 0),
            n_points: int = 100):
        """
        Construct the coordinate system from a structured cube structure.

        :param      cls:       The cls
        :type       cls:       CartesianCoordinates
        :param      length:    The length of the side of the square
        :type       length:    float
        :param      center:    The center
        :type       center:    tuple
        :param      n_points:  The number of points for each dimension [x, y, z]
        :type       n_points:  int
        """
        x0, y0, z0 = center

        x = numpy.linspace(-length / 2, length / 2, n_points) + x0
        y = numpy.linspace(-length / 2, length / 2, n_points) + y0
        z = numpy.linspace(-length / 2, length / 2, n_points) + z0

        x_mesh, y_mesh, z_mesh = numpy.meshgrid(x, y, z)

        instance = CartesianCoordinates(
            x=x_mesh,
            y=y_mesh,
            z=z_mesh
        )

        instance.is_structured = True
        instance.is_3D = True
        # instance.dx = abs(x[1] - x[0])
        # instance.dy = abs(y[1] - y[0])
        # instance.dz = abs(z[1] - z[0])
        instance.n_x = instance.n_y, instance.n_z = n_points

        return instance

    @classmethod
    def generate_from_square(
            cls,
            length: float,
            center: tuple = (0, 0),
            n_points: int = 100):
        """
        Construct the coordinate system from a structured square structure.

        :param      cls:       The cls
        :type       cls:       CartesianCoordinates
        :param      length:    The length of the side of the square
        :type       length:    float
        :param      center:    The center
        :type       center:    tuple
        :param      n_points:  The number of points for each dimension [x, y]
        :type       n_points:  int
        """
        x0, y0 = center

        x = numpy.linspace(-length / 2, length / 2, n_points) + x0
        y = numpy.linspace(-length / 2, length / 2, n_points) + y0

        cls.n_x = cls.n_y = n_points

        x_mesh, y_mesh = numpy.meshgrid(y, x)

        instance = CartesianCoordinates(
            x=x_mesh.T,
            y=y_mesh.T,
            z=0
        )

        instance.is_structured = True
        instance.is_3D = False
        # instance.dx = abs(x[1] - x[0])
        # instance.dy = abs(y[1] - y[0])
        instance.n_x = instance.n_y = n_points

        return instance

    @classmethod
    def generate_from_fibonacci_2D(
            cls,
            radius: float,
            center: tuple = (0, 0),
            n_points: int = 100):
        """
        Construct the coordinate system from a unstructured Fibonacci mesh.

        :param      cls:       The cls
        :type       cls:       CartesianCoordinates
        :param      length:    The length of the side of the square
        :type       length:    float
        :param      center:    The center
        :type       center:    tuple
        :param      n_points:  The number of points for each dimension [x, y]
        :type       n_points:  int
        """
        x0, y0 = center

        alpha = 0
        golden_ratio = (1 + numpy.sqrt(5)) / 2  # golden ratio

        angle_stride = 360 * golden_ratio

        b = round(alpha * numpy.sqrt(n_points))  # number of boundary points

        x, y = numpy.zeros(n_points), numpy.zeros(n_points)

        theta = numpy.arange(1, n_points + 1) * angle_stride

        radius = numpy.ones(n_points)

        idx_list = numpy.arange(1, n_points + 1)

        radius = numpy.sqrt(idx_list - 0.5) / numpy.sqrt(n_points - (b + 1) / 2)

        radius[idx_list > n_points - b] = 1

        x = radius.copy() * numpy.cos(theta) + x0
        y = radius.copy() * numpy.sin(theta) + y0

        instance = CartesianCoordinates(
            x=x.ravel(),
            y=y.ravel(),
            z=0
        )
        instance.is_structured = False
        instance.is_3D = False
        instance.n_x = instance.n_y = n_points

        return instance

    def radius(idx, n_points, b):
        if idx > n_points - b:
            return 1.0
        else:
            return numpy.sqrt(idx - 0.5) / numpy.sqrt(n_points - (b + 1) / 2)

    @classmethod
    def generate_from_disc(
            cls,
            radius: float,
            center: tuple = (0, 0),
            n_points: int = 100):
        """
        Construct the coordinate system from a structured square structure.

        :param      cls:       The cls
        :type       cls:       CartesianCoordinates
        :param      length:    The length of the side of the square
        :type       length:    float
        :param      center:    The center
        :type       center:    tuple
        :param      n_points:  The number of points for each dimension [x, y]
        :type       n_points:  int
        """
        x0, y0 = center

        rho = numpy.linspace(0, radius, n_points)
        phi = numpy.linspace(0, 2 * numpy.pi, n_points)

        x = numpy.outer(rho, numpy.cos(phi)) + x0
        y = numpy.outer(rho, numpy.sin(phi)) + y0

        instance = CartesianCoordinates(
            x=x.ravel(),
            y=y.ravel(),
            z=0
        )

        instance.is_structured = True
        instance.is_3D = False
        instance.dx = abs(x[1] - x[0])
        instance.dy = abs(y[1] - y[0])
        instance.n_x = instance.n_y = n_points

        return instance

    def to_cylindrical(self) -> object:
        rho = numpy.sqrt(self.x**2 + self.y**2)
        phi = numpy.arctan2(self.y, self.x)

        cylindrical_coordinate = CylindricalCoordinates(
            rho=rho,
            phi=phi,
            z=self.z
        )

        return cylindrical_coordinate

    def to_cartesian(self) -> Self:
        return self

    def shift_coordinates(self, shift: tuple) -> Self:
        """
        Shift the coordinates with a certain values

        :param      shift:  The shift [x], [x, y] or [x, y, z]
        :type       shift:  tuple

        :returns:   The self instance
        :rtype:     Self
        """
        coordinates = (self.x, self.y, self.z)
        for coordinate, element in zip(coordinates, shift):
            coordinate += element

        return self

    def scale_coordinates(self, scale: tuple) -> Self:
        """
        Scale the coordinates with a certain factor

        :param      scale:  The shift [x], [x, y] or [x, y, z]
        :type       scale:  tuple

        :returns:   The self instance
        :rtype:     Self
        """
        coordinates = (self.x, self.y, self.z)
        for coordinate, element in zip(coordinates, scale):
            coordinate *= element

        return self

    def plot(self) -> render2D.SceneList | render3D.SceneList:
        """
        Plots the coordinate structure

        :returns:   The scene instance
        :rtype:     render2D.SceneList | render3D.SceneList
        """
        if self.is_3D is True:
            return self.plot_3D()
        else:
            return self.plot_2D()

    def plot_2D(self) -> render2D.SceneList:
        """
        Plots the coordinate structure if it's a 2D structure

        :returns:   The scene instance
        :rtype:     render2D.SceneList
        """
        scene = render2D.SceneList()

        ax = scene.append_ax(aspect_ratio='equal')

        ax.add_scatter(x=self.x, y=self.y)

        return scene

    def plot_3D(self) -> render3D.SceneList:
        """
        Plots the coordinate structure if it's a 3D structure

        :returns:   The scene instance
        :rtype:     render3D.SceneList
        """
        scene = render3D.SceneList()

        ax = scene.append_ax()

        coordinates = numpy.c_[self.x, self.y, self.z].T

        ax.add_unstructured_mesh(
            coordinates=coordinates,
            scalar_coloring=None
        )

        return scene

    def centering(self) -> None:
        """
        Recenter the coordinates around the value zero

        :param      factor:         The factor
        :type       factor:         float
        :param      zero_included:  Indicates if zero included
        :type       zero_included:  bool

        :returns:   { description_of_the_return_value }
        :rtype:     None
        """
        x_mean = self.x.mean()
        y_mean = self.y.mean()

        self.shift_coordinates([x_mean, y_mean])


def vector_cyl2cart(cylindrical_vector: numpy.ndarray, vector_position: CartesianCoordinates | CylindricalCoordinates) -> tuple:
    """
    Takes a cylindrical vector as inputs as well as its cartesian position and returns
    the cartesian vector.

    :param      cylindrical_vector:  The cylindrical vector
    :type       cylindrical_vector:  { type_description }
    :param      vector_position:     The vector position
    :type       vector_position:     { type_description }

    :returns:   The vector in the cartesian basis
    :rtype:     CartesianCoordinates
    """
    vrho, vphi, vz = cylindrical_vector

    cylindrical_position = vector_position.to_cylindrical()

    vx = vrho * numpy.cos(cylindrical_position.phi) - vphi * numpy.sin(cylindrical_position.phi)
    vy = vrho * numpy.sin(cylindrical_position.phi) + vphi * numpy.cos(cylindrical_position.phi)
    vz = vz

    vector = CartesianCoordinates(x=vx, y=vy, z=vz)

    return vector


# -
