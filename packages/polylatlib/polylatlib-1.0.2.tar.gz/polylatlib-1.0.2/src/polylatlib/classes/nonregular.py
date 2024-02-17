"""
**********
Non Regular Polygon Classes
**********
Non Regular Polygon classes for PolyLatLib.

This file contains the non-regular classes and non-regular polygon presets for PolyLatLib, establishing
the key attributes for all non-regular polygons.

"""

import abc
from polylatlib.classes.base_shapes import Polygon, Lattice
from polylatlib.functions import add_vectors, change_to_cart_list

__all__ = [
    "NonRegularPolygon",
    "FourSided",
    "Rectangle",
    "Parallelogram"
]

class NonRegularPolygon(Polygon):
    """
    IMPLEMENT DOCUMENTATION
    """
    def __init__(self, start_point, rotation):
        """
        IMPLEMENT DOCUMENTATION
        """
        super().__init__()
        self.start_point = start_point
        self.rotation = rotation
        self.polygon_vectors = self.generate_polygon_vectors()

        self.generate_shape(start_point, 0, self.polygon_vectors)
    
    @abc.abstractmethod
    def generate_polygon_vectors(self):
        """
        IMPLEMENT DOCUMENTATION
        """

class FourSided(Polygon):
    """
    IMPLEMENT DOCUMENTATION
    """    
    def generate_lattice_from_vectors(self, layers, chg_vectors): 
        """
        IMPLEMENT DOCUMENTATION
        """
        lattice = Lattice(layers)
        
        radius_vec = add_vectors(chg_vectors[2], chg_vectors[3])

        even_numbers = list(range(0, 2*layers, 2))
        shape = 0
        for layer in range(layers):
            if layer == 0:
                lattice.generate_shape(self.start_point, shape, chg_vectors)
                shape += 1
            else:
                radius_vec = (round((layer*radius_vec[0]), 3), round((layer*radius_vec[1]), 3))
                start_vertex_pos = add_vectors(self.start_point, radius_vec)
                for i in range(4):
                    for _ in range(even_numbers[layer]):
                        lattice.generate_shape(start_vertex_pos, shape, chg_vectors)
                        start_vertex_pos = add_vectors(start_vertex_pos, chg_vectors[i])
                        shape += 1
        return lattice

class Rectangle(NonRegularPolygon, FourSided):
    """
    IMPLEMENT DOCUMENTATION
    """
    def __init__(self, width, height, start_point = (0, 0), rotation = 0):
        """
        IMPLEMENT DOCUMENTATION
        """
        self.height = height
        self.width = width
        super().__init__(start_point, rotation)
    
    def generate_change_vectors(self): 
        """
        IMPLEMENT DOCUMENTATION
        """
        return self.polygon_vectors

    def generate_polygon_vectors(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        ## CHANGE TO LIST OF VECTORS
        vectors = []
        for i in range(0, 4, 2):
            height_polar = (self.height, (i)*90 + self.rotation)
            width_polar = (self.width, (i + 1)*90 + self.rotation)
            vectors.append(height_polar)
            vectors.append(width_polar)
        return change_to_cart_list(vectors)
    
    def get_lattice_state(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        return True
    

class Parallelogram(NonRegularPolygon, FourSided):
    """
    IMPLEMENT DOCUMENTATION
    """
    def __init__(self, width, height, angle, start_point = (0, 0), rotation = 0):
        """
        IMPLEMENT DOCUMENTATION
        """
        self.height = height
        self.width = width
        self.angle = angle
        super().__init__(start_point, rotation)

    def generate_change_vectors(self): 
        """
        IMPLEMENT DOCUMENTATION
        """
        return self.polygon_vectors

    def generate_polygon_vectors(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        ## CHANGE TO LIST OF VECTORS
        vectors = []
        for i in range(0, 4, 2):
            height_polar = (self.height, (i + 1)*90 + self.angle + self.rotation)
            width_polar = (self.width, (i + 2)*90 + self.rotation)
            vectors.append(height_polar)
            vectors.append(width_polar)
        return change_to_cart_list(vectors)
    
    def get_lattice_state(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        return True