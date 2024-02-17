"""
**********
Regular Polygon Classes
**********
Regular Polygon classes for PolyLatLib.

This file contains the regular classes and regular polygon presets for PolyLatLib, establishing the
key attributes for all regular polygons and automatic regular polygon generation methods.

"""

from math import sqrt, sin, cos, radians
from polylatlib.classes.base_shapes import Shape, Polygon, Lattice
from polylatlib.functions import change_to_cart_list, change_to_cart_vector, check_if_coord, add_vectors
from polylatlib.exception import PolyLatError, PolyLatNotCart

__all__ = [
    "RegularPolygon",
    "EquilateralTriangle",
    "Square",
    "Pentagon",
    "Hexagon",
    "Septagon",
    "Octagon"
]


class RegularPolygon(Polygon):
    """
    Regular polygons are defined to be polygons with all edges having equal length and all
    internal angles the same.

    Parameters
    ----------
    sides : int > 3
        The number of sides for the regular polygon (Attribute).
    edge_length : float > 0,
        Edge length for all edges of the shape (Attribute).
    centre : (x, y) - 2D Cartesian Coordinate
        Centre point for the shape. For regular polygons this is possible as the uniform nature
        of the shape results in an equal radius to each vertex in the polygon (Attribute).
    rotation : angle
        The angle, in degrees, to rotate the shape around the centre anti-clockwise. This value
        is cyclic with period 360 degrees (Attribute).

    Attributes
    ----------
    int_angle : float
        The angle between edges within the shape.
    theta : float
        The angle from one radii, from the centre to each vertex, to the next.
    radius : float
        The length from the centre to any vertex in a regular polygon.
    radius_vector : Vector (x, y)
        The vector from the centre to the initial vertex, with regard to rotation.

    Example
    -------
    >>> ADD EXAMPLE

    Notes
    -----
    Regular Polygons are defined by their number of sides and edge length. When
    initialised, RegularPolygon implements both these parameters along with a user
    defined centre for the shape and an angle of rotation. When called regular polygons
    are automatically generated with help from some variables detailed below;

    The polygons of this type can thus be defined simply by their number of sides and edge
    length. Along with a given centre and a rotation all further features of these shapes can
    be found through private class methods.
    """
    def __init__(self, sides: int, edge_length, centre, rotation):
        """
        Initialises a Regular Polygon object.

        Notes
        -----
        When initialised, a regular polygon with dictated number of sides is automatically
        generated using angle information and edge vectors. 
        """
        self.sides = sides
        self.edge_length = edge_length
        self.centre = centre
        self.rotation = rotation

        # Error Handling for input attributes.
        if self.sides < 3:
            raise ValueError(f"Argument 'sides' = {self.sides}. A regular polygon have at least 3 sides.")
        elif self.edge_length < 0:
            raise ValueError("Argument 'edge_length' = {self.edge_length}. Edges cannot be of negative length.".format(self=self))
        elif not check_if_coord(self.centre):
            raise PolyLatNotCart(self.centre)

        super().__init__()

        # Set Radius related attributes
        self.int_angle = round(((sides - 2)*180)/sides, 3)
        self.theta = 180 - self.int_angle
        self.radius = round((edge_length)/(2*sin(radians(self.theta/2))), 3)
        self.radius_vec = change_to_cart_vector((self.radius, rotation))

        # Generate polygon
        polygon_vectors = self.__generate_polygon_vectors()
        start_pos = add_vectors(centre, self.radius_vec)
        self.generate_shape(start_pos, 0, polygon_vectors)


    def __generate_polygon_vectors(self):
        """
        Generates and returns the edge vectors for a regular polygon.

        Returns
        -------
        edge_vectors : list
            List with edge vectors as values.
    
        Notes
        -----
        This private method is used in the generation of regular polygon onjects.
        """
        edge_vectors = []
        for i in range(self.sides):
            angle = i*self.theta + (180 - (self.int_angle/2)) + self.rotation
            edge_vectors.append(change_to_cart_vector((self.edge_length, angle)))
        return edge_vectors

    def get_lattice_state(self):
        """
        Returns True if lattice can be generated from current regular polygon. False otherwise.

        Returns
        -------
        boolean
            Returns True if lattice can be generated from current regular polygon. False if not.

        Notes
        -----
        This is a special lattice check for regular polygons as they have a well defined shape.
        """
        lattice_test = 360/self.int_angle
        return lattice_test.is_integer()



################## PRESETs for REGULAR POLYGONs ######################


class EquilateralTriangle(RegularPolygon):
    """
    PRESET SHAPE: Equilateral Triangle

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 0, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Equilateral triangles are 3 sided polygons with equal edge length and internal angle of 60
    degrees. The default Equilateral Triangle is generated "pointing" along the x-axis in the
    positive direction centred at the origin, (0, 0).
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 0):
        """
        Equilateral Triangles are initialised as Regular Polygons with 3 sides.
        """
        super().__init__(3, edge_length, centre, rotation)

    def generate_lattice_circular(self, layers: int):
        """
        Generates and returns the circular lattice for Equilateral Triangles.

        Parameters
        ----------
        layers : int > 0
            The number of desired layers in the lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of equilateral traingles in circular layers centred on the generating
            shape's centre.

        Notes
        -----
        Triangles in circular lattices have alternating orientaion for each layer.
        """
        polar_vectors = []
        for i in range(2*self.sides):
            polar_vectors.append((self.edge_length, 30 + (i + 1)*self.int_angle + self.rotation))
        chg_vectors = change_to_cart_list(polar_vectors)

        triangle_one = []
        for i in range(self.sides):
            triangle_one.append(chg_vectors[2*i + 1])
        triangle_two = []
        for i in range(self.sides):
            triangle_two.append(chg_vectors[len(chg_vectors) - (2*i + 1)])

        lattice = Lattice()
        shape = 0
        origin_vertex = add_vectors(self.centre, self.radius_vec)
        for layer in range(layers):
            if layer == 0:
                lattice.generate_shape(origin_vertex, shape, triangle_one)
            else:
                if layer % 2 == 0: # Odd Layers
                    origin_vertex = add_vectors(origin_vertex, chg_vectors[5])
                    origin_vertex = add_vectors(origin_vertex, chg_vectors[4])
                    vertex_pos = origin_vertex
                    for i in range(3):
                        for _ in range(int(layer/2)):
                            shape += 1
                            lattice.generate_shape(vertex_pos, shape, triangle_one)
                            vertex_pos = add_vectors(vertex_pos, chg_vectors[2*i])
                        for _ in range(int(layer/2)):
                            shape += 1
                            lattice.generate_shape(vertex_pos, shape, triangle_one)
                            vertex_pos = add_vectors(vertex_pos, chg_vectors[(2*i) + 1])
                else: # Even Layers
                    origin_vertex = add_vectors(origin_vertex, chg_vectors[2])
                    vertex_pos = origin_vertex
                    for i in range(3):
                        for _ in range(int((layer + 1)/2)):
                            shape += 1
                            lattice.generate_shape(vertex_pos, shape, triangle_two)
                            vertex_pos = add_vectors(vertex_pos, chg_vectors[2*i])
                        for _ in range(int((layer + 1)/2) - 1):
                            shape += 1
                            lattice.generate_shape(vertex_pos, shape, triangle_two)
                            vertex_pos = add_vectors(vertex_pos, chg_vectors[(2*i) + 1])
        return lattice

    def generate_lattice_stacked(self, rows, columns):
        """
        Generates and returns the stacked lattice for the Equilateral Triangles.

        Parameters
        ----------
        rows : int > 0
            The number of desired rows in the lattice.
        columns : int > 0
            The number of desired columns in the lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of equilateral traingles in stacked, row by columnn, layers centred on
            the generating shape's centre.

        Notes
        -----
        Triangles in stacked lattices have alternating orientaion row-wise and column-wise.

        """
        edge_vec_1 = list(self.get_edge_vectors().values())
        edge_vec_2 = [edge_vec_1[2], edge_vec_1[1], edge_vec_1[0]]

        edge_vec = [edge_vec_1, edge_vec_2]

        move_row = [edge_vec_1[0], edge_vec_1[2]]
        move_col = [edge_vec_1[2], (-edge_vec_1[0][0], -edge_vec_1[0][1])]

        lattice = Lattice()
        origin_vertex = add_vectors(self.centre, self.radius_vec)
        for i in range(rows):
            col_pos = origin_vertex
            if i % 2 == 0:
                for j in range(columns):
                    if j % 2 == 0:
                        lattice.generate_shape(col_pos, str(i) + "." + str(j), edge_vec[(i % 2)])
                    else:
                        lattice.generate_shape(col_pos, str(i) + "." + str(j), edge_vec[(i % 2) - 1])
                        col_pos = add_vectors(col_pos, move_col[0])
                        col_pos = add_vectors(col_pos, move_col[1])
                origin_vertex = add_vectors(origin_vertex, move_row[(i % 2)])
            else:
                for j in range(columns):
                    if j % 2 == 0:
                        lattice.generate_shape(col_pos, str(i) + "." + str(j), edge_vec[(i % 2)])
                        col_pos = add_vectors(col_pos, move_col[0])
                        col_pos = add_vectors(col_pos, move_col[1])
                    else:
                        lattice.generate_shape(col_pos, str(i) + "." + str(j), edge_vec[(i % 2) - 1])
                origin_vertex = add_vectors(origin_vertex, move_row[(i % 2)])
        return lattice

class Square(RegularPolygon):
    """
    PRESET SHAPE: Square

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 45, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Squares are 4 sided polygons with internal angles of 90 degrees. The default orientation
    of Squares is with its edges parallel to the axes. This means that unlike other preset
    regular polygons the initial vertex of the shape does not lie upon the x-axis.
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 45):
        """
        Squares are initialised as Regular Polygons with 4 sides.
        """
        super().__init__(4, edge_length, centre, rotation)

    def generate_lattice_circular(self, layers: int):
        """
        Generates and returns the circular lattice for Squares.

        Parameters
        ----------
        layers : int > 0
            The number of desired layers in the lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of squares in circular layers centred on the generating
            shape's centre.
        """
        chg_vectors = list(self.get_edge_vectors().values())

        lattice = Lattice()

        even_numbers = list(range(0, 2*layers, 2))
        shape = 0
        for layer in range(layers):
            radius_vec = (round((layer*2*self.radius_vec[0]) + self.radius_vec[0], 3), round((layer*2*self.radius_vec[1]) + self.radius_vec[1], 3))
            start_vertex_pos = add_vectors(self.centre, radius_vec)
            if layer == 0:
                lattice.generate_shape(start_vertex_pos, shape, chg_vectors)
                shape += 1
            else:
                for i in range(self.sides):
                    for _ in range(even_numbers[layer]):
                        lattice.generate_shape(start_vertex_pos, shape, chg_vectors)
                        start_vertex_pos = add_vectors(start_vertex_pos, chg_vectors[i])
                        shape += 1
        return lattice

    def generate_lattice_stacked(self, rows, columns):
        """
        Generates and returns the stacked lattice for the Squares.
        
        Parameters
        ----------
        rows : int > 0
            Number of rows in the stacked lattice.
        columns : int > 0
            Number of columns in the stacked lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of squares in stacked, row by columnn, layers centred on
            the generating shape's centre.

        Notes
        -----
        Note that the idea of "stacked" specifically refers to the default position of the shape. For
        squares this results in a (row x column) grid formation with the generating square (current
        polygon) is situated in the bottom left corner.
        """
        edge_vec = list(self.get_edge_vectors().values())
        move_row = edge_vec[3]
        move_col = edge_vec[2]
        lattice  = Lattice()
        start_pos = add_vectors(self.centre, self.radius_vec)
        for i in range(rows):
            vertex_pos = start_pos
            for j in range(columns):
                lattice.generate_shape(vertex_pos, str(i) + "." + str(j), edge_vec)
                vertex_pos = add_vectors(vertex_pos, move_col)
            start_pos = add_vectors(start_pos, move_row)
        return lattice

class Pentagon(RegularPolygon):
    """
    PRESET SHAPE: Pentagon

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 45, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Pentagons are 5 sided polygons with internal angles of 108 degrees.
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 0):
        """
        Pentagons are initialised as Regular Polygons with 5 sides.
        """
        super().__init__(5, edge_length, centre, rotation)


class Hexagon(RegularPolygon):
    """
    PRESET SHAPE: Hexagon

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 45, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Regular hexagons are 6 sided polygons with internal angles of 120 degrees. Similar to
    the Square preset, the default orientation of hexagons is with its "vertical "edges parallel
    to the y-axis. This means that unlike other preset regular polygons that the initial vertex of
    the shape does not lie upon the x-axis.
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 30):
        """
        Hexagons are initialised as Regular Polygons with 6 sides.
        """
        super().__init__(6, edge_length, centre, rotation)

    def generate_lattice_circular(self, layers: int):
        """
        Generates and returns the circular lattice for Hexagons.

        Parameters
        ----------
        layers : int > 0
            The number of desired layers in the lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of hexagons in circular layers centred on the generating
            shape's centre.
        """
        edgeLengthPlus = 1.5*self.edge_length
        halfHexHeight = round(sqrt(0.75*((self.edge_length)**2)), 2)
        vector_length = round(sqrt(edgeLengthPlus**2 + halfHexHeight**2), 2)
        polar_vectors = []
        for i in range(self.sides):
            polar_vectors.append((vector_length, i*(self.theta) + self.theta/2 + self.rotation))
        chg_vectors = change_to_cart_list(polar_vectors)

        lattice = Lattice()
        polygon_vectors = list(self.get_edge_vectors().values())

        shape = 1
        for layer in range(layers):
            if layer == 0:
                start_vertex_pos = add_vectors(self.centre, self.radius_vec)
                lattice.generate_shape(start_vertex_pos, 0, polygon_vectors)
            else:
                start_vertex_pos = add_vectors(start_vertex_pos, chg_vectors[4])
                lattice.generate_shape(start_vertex_pos, shape, polygon_vectors)
                for i in range(self.sides):
                    for _ in range(layer):
                        shape += 1
                        start_vertex_pos = add_vectors(start_vertex_pos, chg_vectors[i])
                        lattice.generate_shape(start_vertex_pos, shape, polygon_vectors)
        return lattice

    def generate_lattice_stacked(self, rows, columns):
        """
        Generates and returns the stacked lattice for the Hexagons.

        Parameters
        ----------
        rows : int > 0
            Number of rows in the stacked lattice.
        columns : int > 0
            Number of columns in the stacked lattice.

        Returns
        -------
        lattice : Lattice
            Lattice object of hexagons in stacked, row by columnn, layers centred on
            the generating shape's centre.

        Notes
        -----
        Note that the idea of "stacked" specifically refers to the default position of the shape.
        """
        edge_vec = list(self.get_edge_vectors().values())
        print(edge_vec)
        edgeLengthPlus = 1.5*self.edge_length
        halfHexHeight = round(sqrt(0.75*((self.edge_length)**2)), 2)
        vector_length = round(sqrt(edgeLengthPlus**2 + halfHexHeight**2), 2)
        move_row = change_to_cart_vector((vector_length, 30 + self.rotation))
        move_col = change_to_cart_vector((vector_length, self.rotation - 30))
        lattice  = Lattice()
        start_pos = add_vectors(self.centre, self.radius_vec)
        for i in range(rows):
            vertex_pos = start_pos
            for j in range(columns):
                lattice.generate_shape(vertex_pos, str(i) + "." + str(j), edge_vec)
                vertex_pos = add_vectors(vertex_pos, move_col)
            start_pos = add_vectors(start_pos, move_row)
        return lattice

class Septagon(RegularPolygon):
    """
    PRESET SHAPE: Septagon

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 45, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Septagons are 7 sided polygons with internal angles of 128.57 degrees.
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 0):
        """
        Septagons are initialised as Regular Polygons with 7 sides.
        """
        super().__init__(7, edge_length, centre, rotation)


class Octagon(RegularPolygon):
    """
    PRESET SHAPE: Octagon

    Parameters
    ----------
    edge_length : float > 0, Default = 1, optional
        The deired edge length.
    centre : (x, y) - 2D Cartesian Coordinate, Default = (0, 0), optional
        Centre position for the polygon.
    rotation : angle, Default = 45, optional
        The angle, in degrees, to rotate the polygon arounds its centre anti-clockwise.

    Notes
    -----
    Octagons are 8 sided polygons with internal angles of 135 degrees.
    """
    def __init__(self, edge_length: float = 1, centre = (0, 0), rotation: float = 0):
        """
        Octagons are initialised as Regular Polygons with 8 sides.
        """
        super().__init__(8, edge_length, centre, rotation)
