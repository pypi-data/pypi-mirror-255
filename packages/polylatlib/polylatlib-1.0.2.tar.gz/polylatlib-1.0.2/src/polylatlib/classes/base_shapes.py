"""
**********
Base Shape Classes
**********
Base Shape classes for PolyLatLib.

This file contains the bases shape classes for all shape objects in PolyLatLib, dictating their base
structure and behaviour.

"""

import abc
from math import sqrt, sin, cos, radians
from polylatlib.exception import *
from polylatlib.functions import add_vectors, is_positive_int, is_supported_colour, check_if_coord


### SHAPE (Parent Base Class) ###
class Shape():
    """
    Shape is the base parent class for all shape objects. This class implements the basic features
    and methods of vertices and edges for all shapes.

    Attributes
    ----------
    vertices : 
        The list of all vertex names.
    vertices_info : 
        The list of vertex tuples of vertices along with their associated property dictionary.
        This dictionary contains the vertex properties position, size, and colour.
    .edges :
        The list of edges. Edges are stored as 2-tuples of the vertices at either end of the edge.
    .edge_info : The list of tuples of edges along with their associated information dictionary.
        This dictionary contains the edge weight and colour.
    
    Example
    -------
    # Drawing a custom 'house' shape using matplotlib.
    >>> A = Shape()
    >>> A.add_vertex(1, (1, 1), 10, "r")
    >>> A.add_vertex(2, (4, 1), 2, "g")
    >>> A.add_vertex(3, (4, 3), 6, "k")
    >>> A.add_vertex(4, (1, 3))
    >>> A.add_vertex(5, (2.5, 4))
    >>> A.add_edge(1, 2, 2, "c")
    >>> A.add_edge(2, 3, 3, "m")
    >>> A.add_edge(3, 4, 4, "y")
    >>> A.add_edge(4, 1, 5, "k")
    >>> A.add_edge(3, 5)
    >>> A.add_edge(4, 5)
    >>> A.draw_shape()
    <Matplotlib window displaying a multi-coloured house>

    Notes
    -----
    The shape class includes all the methods related specifically to vertices and edges. Through
    these methods the shape can be built piece-meal with the addition of vertices and edges to the
    shape object, as well as be used to update vertex information (using the '.update' methods),
    or retrieve a vertex's, or edge's, specific property dictionary (using the '.get' methods).

    The final method of the shape object (currently) utilises the OpenCV library to create and
    canvas and draw the created shape.
    """
    def __init__(self):
        """
        Initialise a Shape object to be populated with vertices and edges.

        Example
        -------
        >>> A = Shape()
        >>> for i in range(5):
        >>>     A.add_vertex(i) # adding veritces 0 through 4 to A.
        >>> A.add_edge(0, 1)
        >>> A.add_edge(1, 8, 4)
        >>> print(A.vertices)
        [0, 1, 2, 3, 4, 8]
        >>> print(A.edges_info)
        [((0, 1), {weight: 1, colour: "k"}), ((1, 8), {weight: 4, colour: "k"})]

        Notes
        -----
        When initialised a Shape is an empty object with the capacity for the addition of vertices
        and edges.
        """
        self.vertices = []
        self.vertices_info = []
        self.edges = []
        self.edges_info = []
    
    def __str__(self):
        """
        Returns the type and a summary of the shape.

        Returns
        -------
        info : string
            Basic information of the shape object. Indicates the shape type, number of verticies,
            and number of sides.

        Example
        -------
        >>> A = Shape()
        >>> for in in range(5):
        >>>     A.add_edge(i, i + 1)
        >>> print(A)
        Shape:
        - Num. of Vertices: 6,
        - Num. of Edges: 5

        """
        return (
            f"""
            Type : {type(self).__name__}
            Number of Vertices : {len(self.vertices)}
            Number of Edges : {len(self.edges)}
            """
        )

    def __len__(self):
        """
        Returns the number of edges (i.e number of sides) in the shape. Use: 'len(A)'.

        Returns
        -------
        sides : int
            Number of edges in the shape.

        Example
        -------
        >>> A = Shape()
        >>> for in in range(5):
        >>>     A.add_edge(i, i + 1)
        >>> print(len(A))
        5
        """
        return len(self.edges)
    
    def __contains__(self, a):
        """
        Returns True if a vertex or edge exists in the shape, False otherwise.

        Parameters
        ----------
        a : vertex or edge,
            A vertex or edge element that may be contained in the shape.

        Returns
        -------
        boolean
            True if 'a' is in the shape, False if not.

        Example
        -------
        >>> A = EquilateralTriangle()
        >>> ("0-0", "0-1") in A
        True

        """
        # First Checks if input could be an edge
        if type(a) == tuple and len(a) == 2:
            # checks both edge directions
            for edge in [a, (a[1], a[0])]:
                if edge in self.edges:
                    return True
        # Otherwise checks against vertices
        else:
            try:
                return a in self.vertices
            except TypeError:
                return False

    def add_vertex(self, vertex_for_adding, position = None, size: int = 4, colour = "b"):
        """
        Adds a desired vertex to the shape, with associated properties; positon, size, and
        colour. 

        Parameters
        ----------
        vertex_for_adding : vertex,
            The desired name for a vertex in the shape. These can be strings, numbers, or
            collections.
        position : (x, y) - 2D Cartesian Coordinate, Default = None, optional
            The desired position for the vertex in the form of a coordinate 2-tuple. New vertices
            have no postion by deafult allowing for the creation of a graph-like object.
        size : int, Default = 4, optional
            Size property to be ustilised upon drawing of the shape.
        colour : colour, Default = "b", optional
            Colour property to be utilisied upon drawing of the shape. Colour can be chosen from
            the options: black - "k"; red - "r"; green - "g"; blue - "b"; cyan - "c"; magenta -
            "m"; yellow - "y". 

        Example
        -------
        >>> A = Shape()
        >>> A.add_vertex(1) # 'Abstract' vertex called '1' with no position.
        >>> A.add_vertex("Hello", (2, 3))   # A vertex called 'Hello' at position (2, 3).
        >>> A.add_vertex("example", colour = "r")
        >>> print(A.vertices)
        [1, "Hello", "example"]

        Notes
        -----
        A vertex is a point in space that can exist independently, or as the end of an 
        edge/ multiple edges. You cannot have multiple vertices of the same name, though you can
        have multiple vertices occupying the same position. Vertex properties are its position,
        size, and colour.
        
        If initialised with no position the vertex can be considered an 'abstract' vertex with
        position = None. This vertex is more akin to a node in a graph-like object and can still
        be utilisied in the creation of edges resulting in a shape with no set structure except
        for defined edges and vertices.

        When initialised with a position the vertex becomes a recognisable point in the R x R 
        Cartesian space with an x and y position. This position can also be imagined as the
        vector from the origin to the point of the vertex.

        Size and colour are utilisied in the drawing of the shape with size indicating the radius
        of the circle drawn at the vertex point. Colour is self-explanatory.
        """
        # Checks vertex does not already exist
        if vertex_for_adding not in self.vertices:
            # Checks position of vertex is Cartesian coord. or None
            if not check_if_coord(position) and position != None:
                raise PolyLatNotCart(position)
            elif not is_positive_int(size):
                raise PolyLatNotPosInt(size)
            elif not is_supported_colour(colour):
                raise PolyLatNotColour(colour)
            
            info = {
                "position": position,
                "size": size,
                "colour": colour
            }
            self.vertices.append(vertex_for_adding)
            self.vertices_info.append((vertex_for_adding, info))
        else:
            ### change this to update system????
            raise PolyLatError(f"Vertex '{vertex_for_adding}' already exists.")

    def update(self, item_for_update, prop, value):
        """
        Updates the desired property for a given item, either a vertex or an edge.

        Parameters
        ----------
        item_for_update : vertex or edge
            A vertex or edge to have the desired property updated.
        prop : vertex or edge property
            Vertex property's are "position", "size", or "colour". Edge property's are
            "weight", or "colour".
        value : property dependent
            The new value to be inserted into the desired property for the given vertex.
        
        Examples
        --------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")
        >>> A.update(1, "position", (1, 1))
        >>> print(A.vertices_info)
        [(1, {'position': (1, 1), 'size': 4, 'colour': 'b'}), (2, {'position': None, 'size': 4,
        'colour': 'b'})]

        Notes
        -----
        This method dynamically detects if the item entered is an edge or a vertex and then
        proceeds to call the specific update method as nessecary.

        See Also
        --------
        update_edge()
        update_vertex()

        """
        if item_for_update in self:
            # Check if item is edge
            if type(item_for_update) == tuple:
                self.update_edge(item_for_update, prop, value)
            # Else the item is a vertex
            else:
                self.update_vertex(item_for_update, prop, value)
        else:
            raise PolyLatNotExist(item_for_update)


    def update_vertex(self, vertex_for_update, prop, value):
        """
        Updates the desired property for a given vertex.

        Parameters
        ----------
        vertex_for_update : vertex
            A prexisting vertex in the shape to be updated.
        property : "position", "size", or "colour"
            The desired vertex property for update.
        value : property dependent value
            New value to be inserted into vertex information dictionary for desired attribute.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                    # Adds 2 vertices and an edge
        >>> A.update_vertex(1, "position", (1, 1))
        >>> print(A.vertices_info)
        [(1, {'position': (1, 1), 'size': 4, 'colour': 'b'}), (2, {'position': None, 'size': 4,
        'colour': 'b'})]

        See Also
        --------
        update_vertex_position()
        update_vertex_size()
        update_vertex_colour()

        """
        # Checks vertex existence
        if vertex_for_update in self.vertices:
            # Method selector
            try:
                method_name = "update_vertex_" + prop
                method = getattr(self, method_name)
                method(vertex_for_update, value)
            except AttributeError:
                raise PolyLatNotProp(prop)
        else:
            raise PolyLatNotExist(vertex_for_update)
    
    def update_vertex_position(self, vertex_for_update, value):
        """
        Updates the position for a given vertex.

        Parameters
        ----------
        vertex_for_update : vertex
            A prexisting vertex in the shape to be updated.
        value : (x, y) - 2D Cartesian Coordinate
            New value to be inserted into vertex information dictionary for position.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                # Adds 2 vertices and an edge
        >>> A.update_vertex_position(1, (1, 1))
        >>> print(A.vertices_info)
        [(1, {'position': (1, 1), 'size': 4, 'colour': 'b'}), (2, {'position': None, 'size': 4,
        'colour': 'b'})]

        """
        if vertex_for_update in self.vertices:
            if check_if_coord(value):
                index = self.vertices.index(vertex_for_update)
                self.vertices_info[index][1]["position"] = value
            else:
                raise PolyLatNotCart(value)
        else:
            raise PolyLatNotExist(vertex_for_update)
    
    def update_vertex_size(self, vertex_for_update, value):
        """
        Updates the size for a given vertex.

        Parameters
        ----------
        vertex_for_update : vertex
            A prexisting vertex in the shape to be updated.
        value : int > 0
            New value to be inserted into vertex information dictionary for size.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                # Adds 2 vertices and an edge
        >>> A.update_vertex_size(1, 20)             # Sets vertex size to 20
        >>> print(A.vertices_info)
        [(1, {'position': None, 'size': 20, 'colour': 'b'}), (2, {'position': None, 'size': 4,
        'colour': 'b'})]

        """
        if vertex_for_update in self.vertices:
            if is_positive_int(value):
                index = self.vertices.index(vertex_for_update)
                self.vertices_info[index][1]["size"] = value
            else:
                raise PolyLatNotPosInt(value)
        else:
            raise PolyLatNotExist(vertex_for_update)
    
    def update_vertex_colour(self, vertex_for_update, value):
        """
        Updates the colour for a given vertex.

        Parameters
        ----------
        vertex_for_update : vertex
            A prexisting vertex in the shape to be updated.
        value : colour
            New value to be inserted into vertex information dictionary for colour.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                # Adds 2 vertices and an edge
        >>> A.update_vertex_size(1, "r")            # Sets vertex colour to red
        >>> print(A.vertices_info)
        [(1, {'position': None, 'size': 20, 'colour': 'r'}), (2, {'position': None, 'size': 4,
        'colour': 'b'})]

        """
        if vertex_for_update in self.vertices:
            if is_supported_colour(value):
                index = self.vertices.index(vertex_for_update)
                self.vertices_info[index][1]["colour"] = value
            else:
                raise PolyLatNotColour(value)
        else:
            raise PolyLatNotExist(vertex_for_update)
    
    def get_vertex_info(self, desired_info):
        """
        Returns a specific property dictionary for all vertices.

        Parameters
        ----------
        desired_info : "position", "size", or "colour"
            Desired property to return property dictionary for all vertices.
        
        Returns
        -------
        vertex_info : dictionary
            Property dictionary with vertices as keys, and the desired property ('deired_info')
            as values.
        
        Example
        -------
        >>> A = pl.Square(2, (1, 1), 45)                    # A square centred on (1, 1) with side length 2 
        >>> A.add_vertex("Centre", (1, 1), 8, "r")          # Red central vertex at (1, 1)
        >>> print(A.get_vertex_info("position"))
        {'0-0': (2.0, 2.0), '0-1': (0.0, 2.0), '0-2': (0.0, 0.0), '0-3': (2.0, 0.0), 'Centre': (1, 1)}

        Notes
        -----
        This method returns a very usable collection of all vertices in the shape with their
        associated desired property.

        See Also
        --------
        get_vertex_positions()
        get_vertex_sizes()
        get_vertex_colours()

        """
        try:
            vertex_info = {}
            for vertex in self.vertices_info:
                vertex_info[vertex[0]] = vertex[1][desired_info]
            return vertex_info
        except:
            raise PolyLatNotExist(desired_info)

    def get_vertex_positions(self):
        """
        Returns the property dictionary of vertex positions.

        Returns
        -------
        vertex_info : dictionary
            Position dictionary for all vertices in the shape. The vertices as keys and their
            positions as the values.
        
        Example
        -------
        >>> A = Shape()
        >>> for i in range(5):
        >>>     A.add_vertex(i, (i + 1, i + 2))
        >>> A.get_vertex_positions()
        {0: (1, 2), 1: (2, 3), 2: (3, 4), 3: (4, 5), 4: (5, 6)}

        """
        return self.get_vertex_info("position")

    def get_vertex_sizes(self):
        """
        Returns the property dictionary of vertex sizes.

        Returns
        -------
        vertex_info : dictionary
            Size dictionary for all vertices in the shape. The vertices as keys and their
            sizes as the values.
        
        Example
        -------
        >>> A = Shape()
        >>> for i in range(5):
        >>>     A.add_vertex(i, size = (i + 1)*10)
        >>> A.get_vertex_sizes()
        {0: 10, 1: 20, 2: 30, 3: 40, 4: 50}

        """
        return self.get_vertex_info("size")
    
    def get_vertex_colours(self):
        """
        Gets the property dictionary of vertex colours.

        Returns
        -------
        vertex_info : dictionary
            Colour dictionary for all vertices in the shape. The vertices as keys and their
            colours as the values.
        
        Example
        -------
        >>> A = Shape()
        >>> for i in range(0, 6, 2):                    # Alternating blue and red vertices.
        >>>     A.add_vertex(i)
        >>>     A.add_vertex(i + 1, colour="r")
        >>> A.get_vertex_colours()
        {0: "b", 1: "r", 2: "b", 3: "r", 4: "b", 5: "r"}

        """
        return self.get_vertex_info("colour")

    def add_edge(self, vertex_one, vertex_two, weight = 1, colour = "k"):
        """
        Adds a desired edge to the shape between 2 vertices, with associated properties; weight and
        colour.

        Parameters
        ----------
        vertex_one : vertex
            The vertex for the one end of the edge.
        vertex_two : vertex
            The vertex name for the other end of the edge. 
        weight : int > 0, Default = 1, optional
            Weight property to be utilisied upon drawing of the shape.
        colour : colour, Default = "k", optional
            Colour property to be utilisied upon drawing of the shape. Colour can be chosen
            from the options: black - "k"; red - "r"; green - "g"; blue - "b"; cyan - "c";
            magenta - "m"; yellow - "y". 
        
        Example
        -------
        >>> A = Shape()
        >>> A.add_edge(1, 2)                                # Adding edge between to new vetrices, 1, and 2.
        >>> A.add_edge("Hello", "World", 3)                 # An edge between 'Hello' and 'World' with weight 3.
        >>> A.add_edge("Hello", "xmpl", colour = "r")       # Establishing edge between exsiting vertex "Hello" and new vertex "xmpl".
        >>> print(A.edges)
        [(1, 2), ("Hello", "World"), ("Hello", "xmpl")]

        Notes
        -----
        Edges are a connecting line between two vertices and are stored as a tuple of these two
        defining vertices. You cannot have multiple edges between the same two vertices and
        thus edges are uniquely defined by their vertex pair, this also means that
        (a, b) = (b, a). Edge properies are weight and size. Weight references the 'thickness'
        of the edge line and colour is self-explanatory. These properties utilised in the
        drawing of shapes. 

        Vertices not pre-exsiting within the shape are automatically generated and added with
        no position and default size and colour.
        """
        # Checks if edge (in either direction) pre-exists
        if (vertex_one, vertex_two) not in self:
            self.edges.append((vertex_one, vertex_two))
            info = {
                "weight": weight,
                "colour": colour
            }
            self.edges_info.append((vertex_one, vertex_two, info))
            # Adds new vertices if needed
            for vertex in (vertex_one, vertex_two):
                if vertex not in self.vertices:
                    self.add_vertex(vertex)
        else:
            raise PolyLatError(f"Edge '{(vertex_one, vertex_two)}' already exists in the shape.")
    
    def update_edge(self, edge_for_update, prop, value):
        """
        Updates a desired property for a specific edge.

        Parameters
        ----------
        edge_for_update : 2-tuple, vertex pair
            A prexisting edge in the shape to be updated.
        property: "weight" or "colour"
            The desired edge property for update.
        value: propery dependent value
            New value to be inserted into edge information dictionary for desired attribute.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                # Adds 2 vertices and an edge
        >>> A.update_edge((1, 2), "colour", "r")    # Sets edge colour to red
        >>> print(A.edges_info)
        [(1, 2, {'weight': 2, 'colour': 'r'})]

        Notes
        -----
        This method perfroms the relevant update method depending upon the given edge.

        See Also
        --------
        update_edge_weight()
        update_edge_colour()

        """
        # Checks existence of edge in shape
        if type(edge_for_update) == tuple and len(edge_for_update) == 2:
            if edge_for_update in self:
                # Method selector
                try:
                    method_name = "update_edge_" + prop
                    method = getattr(self, method_name)
                    method(edge_for_update, value)
                except AttributeError:
                    raise PolyLatNotProp(prop)
            else:
                raise PolyLatError(f"'{edge_for_update}' does not exist.")
        else:
            raise PolyLatError(f"{edge_for_update} is not an edge.")

    def update_edge_weight(self, edge_for_update, value):
        """
        Updates the weight for a specific edge.

        Parameters
        ----------
        edge_for_update : 2-tuple, vertex pair
            A prexisting edge in the shape to be updated.
        value: int > 0
            New value to be inserted into edge information dictionary for weight.

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")            # Adds 2 vertices and an edge
        >>> A.update_edge_weight((1, 2), 4)     # Sets edge weight to 4
        >>> print(A.edges_info)
        [(1, 2, {'weight': 4, 'colour': 'r'})]

        """
        if is_positive_int(value):
            if edge_for_update in self.edges:
                index = self.edges.index(edge_for_update)
            elif (edge_for_update[1], edge_for_update[0]) in self.edges:
                index = self.edges.index((edge_for_update[1], edge_for_update[0]))
            else:
                raise PolyLatNotExist(edge_for_update)
            self.edges_info[index][2]["weight"] = value
        else:
            raise PolyLatNotPosInt(value)
    
    def update_edge_colour(self, edge_for_update, value):
        """
        Updates the colour for a specific edge.

        Parameters
        ----------
        edge_for_update : 2-tuple, vertex pair
            A prexisting edge in the shape to be updated.
        value: colour
            New value to be inserted into edge information dictionary for colour.
            Colour can be chosen from: black - "k"; red - "r"; green - "g";
            blue - "b"; cyan - "c"; magenta - "m"; yellow - "y".

        Example
        -------
        >>> A = pl.Shape()
        >>> A.add_edge(1, 2, 2, "c")                # Adds 2 vertices and an edge
        >>> A.update_edge_colour((1, 2), "y")       # Sets edge colour to yellow
        >>> print(A.edges_info)
        [(1, 2, {'weight': 2, 'colour': 'y'})]

        """
        if is_supported_colour(value):
            if edge_for_update in self.edges:
                index = self.edges.index(edge_for_update)
            elif (edge_for_update[1], edge_for_update[0]) in self.edges:
                index = self.edges.index((edge_for_update[1], edge_for_update[0]))
            else:
                raise PolyLatNotExist(edge_for_update)
            self.edges_info[index][2]["colour"] = value
        else:
            raise PolyLatNotColour(value)

    def get_edge_info(self, desired_info):
        """
        Returns a specific property dictionary for all edges in the shape.

        Parameters
        ----------
        desired_info : "weight" or "colour"
            Desired property to return information about.
        
        Returns
        -------
        edge_info : dictionary
            Property dictionary with edges as keys, and the desired property ('desired_info') as
            values.

        Example
        -------
        >>> A = pl.Square()
        >>> A.update_edge_colour(("0-1", "0-2"), "y")
        >>> print(A.get_edge_info("colour"))
        {('0-0', '0-1'): 'k', ('0-1', '0-2'): 'y', ('0-2', '0-3'): 'k', ('0-3', '0-0'): 'k'}

        Notes
        -----
        This method reurns a very usable collection of all edges in the shape with their associated
        desired property.

        See Also
        --------
        get_edge_weights()
        get_edge_colours()

        """
        try:
            edge_info = {}
            for edge in self.edges_info:
                edge_info[(edge[0], edge[1])] = edge[2][desired_info]
            return edge_info
        except:
            raise PolyLatError(f"'{desired_info}' is not an edge property.")

    def get_edge_weights(self):
        """
        Returns the property dictionary of edge weights.

        Returns
        -------
        edge_info : dictionary
            Weight dictionary for all edges in the shape. The edges as keys and their weights as
            the values
        
        Example
        -------
        >>> A = Shape()
        >>> for i in range(5):
        >>>     A.add_edge(i, i + 1, (i + 1)*10)
        >>> A.get_edge_weights()
        {(0, 1): 10, (1, 2): 20, (2, 3): 30, (3, 4): 40, (4, 5): 50}

        """
        return self.get_edge_info("weight")
    
    def get_edge_colours(self):
        """
        Returns the property dictionary of edge colours.

        Returns
        -------
        edge_info : dictionary
            Colour dictionary for all edges in the shape. The edges as keys and their colours as
            the values.
        
        Example
        -------
        >>> A = Shape()
        >>> for i in range(5):
        >>>     A.add_edge(i, i + 1, colour = colours[i])
        >>> A.get_vertex_colours()
        {(0, 1): "black", (1, 2): "red", (2, 3): "green", (3, 4): "blue", (4, 5): "yellow"}

        """
        return self.get_edge_info("colour")

    def get_edge_vectors(self):
        """
        Returns the vectors of the edges in the shape in the form of a dictionary.
        
        Returns
        -------
        edge_vectors : dictionary
            Dictionary with edges as keys and their vectors as values.

        Example
        -------
        >>> A = Shape()
        >>> for i in range(3):
        >>>     A.add_vertex(i, (i, i + (-1)**i)
        >>> A.add_edge(0, 1)
        >>> A.add_edge(1, 2)
        >>> A.add_edge(0, 2)
        >>> print(A.get_edge_vectors())
        {(0, 1): (1, -1), (1, 2): (1, 3), (0, 2): (2, 2)}
        
        Notes
        -----
        Edge vectors are the vectors from the first vertex in the edge to the second as the
        vertex pairs are stored. If needed, the vector in the opposite direction is simply the
        same vector with neagtive x, and y, values.
       
        This method calculates and returns the true edge vectors for all edge present within the
        shape. Calculation of these vectors from the property dictionaries is the prefered
        method to retrieve this information as vectors used for generation in child classes can
        be overwritten in some circumstances (i.e generate polygon automatically closes the shape
        if input vectors do not do so).

        See Also
        --------
        get_edge_vector()
        """
        edge_vectors = {}
        for edge in self.edges:
            pos_one = self.get_vertex_positions()[edge[0]]
            pos_two = self.get_vertex_positions()[edge[1]]
            # Raises error upon any vertex with no position
            if pos_one == None or pos_two == None:
                raise TypeError("Edge vectors cannot be generated as one or more vertices in an edge do not have a position.")
            vector = (pos_two[0] - pos_one[0], pos_two[1] - pos_one[1])
            edge_vectors[edge] = vector
        return edge_vectors
    
    def get_edge_vector(self, edge):
        """
        Returns specific edge vector for a desired edge.

        Returns
        -------
        vector : 2-tuple
            Vector from the first vertex in the edge to the second.
        
        Example
        -------
        >>> A = lg.Shape()
        >>> for i in range(3):
        >>>     A.add_vertex(i, (i, i + (-1)**i))
        >>> A.add_edge(0, 1)
        >>> A.add_edge(1, 2)
        >>> A.add_edge(0, 2)
        >>> print(A.get_edge_vector((2, 1)))    # Note reversed vertices still works.
        (1, 3)

        See Also
        --------
        get_edge_vectors
        """
        for e in [edge, (edge[1], edge[0])]:
            if e in self.edges:
                return self.get_edge_vectors()[e]
        raise PolyLatNotExist(edge)

    def generate_shape(self, vertex_pos, shape_name, vectors):
        """
        Generates a named shape from a series of edge vectors staring at a given point.
        
        Parameters
        ----------
        vertex_pos : (x, y) - 2D Cartesian Coordinate
            Start position for the initial vertex in the shape.
        shape_name : string, int, or float
            This is the overiding shape name dictating all the vertex names within the shape.
            Vertex names are of the form; 'shape_name-k', where k is number of the vertex.
        vectors : list
            This should be an ordered list of edge vectors. This method runs through the list in
            order to generate the polygon.

        Example
        -------
        >>> vecs = [(0, 1), (1, 1), (-1, 2)]
        >>> A = pl.Shape()
        >>> A.generate_shape((0, 0), "Example", vecs)
        >>> A.draw_shape()
        <MatPlotLib drawing of shape graph>

        Notes
        -----
        This method checks for pre-existence of vertices before adding new ones, i.e we cannot
        have multiple vetrices occupying the same position. This method does not close the shape
        automatically.
        """
        edge_list = []
        for k in range(len(vectors) + 1):
            vertex_dict = self.get_vertex_positions()
            found = False
            # Check if a vertex in within a small radius (1/100) to vector start,
            # If found choose existing vertex instead - this accounts for floating point error
            for key in vertex_dict.keys():
                if (vertex_pos[0] - vertex_dict[key][0])**2 + (vertex_pos[1] - vertex_dict[key][1])**2 <= (1/100)**2: ## Change to edge_length!!
                    edge_list.append(key)
                    found = True
                    break
            # Else create new vertex in that spot
            if found == False:
                self.add_vertex(str(shape_name) + "-" + str(k), vertex_pos)
                edge_list.append(str(shape_name) + "-" + str(k))
            # Move along next vector if not at end of vector list
            if k != len(vectors):
                vertex_pos = add_vectors(vertex_pos, vectors[k])
        for e in range(len(vectors)):
            if (edge_list[e], edge_list[e + 1]) not in self:
                self.add_edge(edge_list[e], edge_list[e + 1])
        
    def generate_from_vectors(self, start_pos, vectors):
        """
        Generates and returns lattice type object of the current shape repeated with positions
        according to given vectors.

        Parameters
        ----------
        start_pos : (x, y) - 2D Cartesian Coordinate
            Start position for the initial vertex in the shape.
        vectors : list
            List of vectors to describe positions for the current shape to be drawn in.
        
        Returns
        -------
        lattice : Lattice
            Lattice object of the current shape drawn in position described by the input vectors.

        Example
        -------
        >>> shape_vec = [(0, 1), (1, 1), (-1, 2)]
        >>> A = pl.Shape()
        >>> A.generate_shape((0, 0), "Example", shape_vec)
        >>> lat_vec = [(3, 3), (0, -2), (1, 1)]
        >>> lat_A = A.generate_from_vectors((0, 0), lat_vec)
        >>> lat_A.draw_shape()
        <Matplotlib drawing of repeated shape lattice>

        Notes
        -----
        This method takes the existing shape and creates a new Lattice object of repeated copies
        of that shape. The number of copies present in the lattice is (num. of vectors) + 1.
        This is because this method first generates the original shape in the starting position
        given and proceeds to repeat the shape in positions dictated by the provided vectors.

        This method also accounts for the preexistence of vertices in the shape.
         
        """
        lattice = Lattice()
        edge_vec = list(self.get_edge_vectors().values())
        lattice.generate_shape(start_pos, "0", edge_vec)
        for i in range(len(vectors)):
            start_pos = add_vectors(start_pos, vectors[i])
            lattice.generate_shape(start_pos, str(i + 1), edge_vec)
        return lattice
    
    def draw_shape(self, axis = "off"):
        """
        Draws the current shape using the MatPlotLib library.

        Parameters
        ----------
        axis : "on" or "off" (Default "off")
            Set as "on" to view x and y axis in plot. Set as "off" to view plot as blank
            canvas.

        Notes
        -----
        Uses the Matplotlib library to visualise the current shapem, accounting for vertex
        properties (position, size, and colour) and edge properties (weight and colour).

        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("Matplotlib required for draw_shape()")
        except RuntimeError:
            print("Matplotlib unable to open display")
            raise
        
        fig, ax = plt.subplots()
        # Adds edges to figure
        vertex_positions = self.get_vertex_positions()
        for edge in self.edges_info:
            pos1 = vertex_positions[edge[0]]
            pos2 = vertex_positions[edge[1]]
            weight = edge[2]["weight"]
            colour = edge[2]["colour"]
            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], color=colour, lw=weight)  
        # Adds vertices to figure
        for vertex in self.vertices_info:
            pos = vertex[1]["position"]
            size = vertex[1]["size"]
            col = vertex[1]["colour"] + "o"
            ax.plot([pos[0]], [pos[1]], col, markersize=size)
        ax.axis(axis)
        fig.set_tight_layout(True)
        plt.show()


############################################################################################

class Polygon(Shape):
    """
    Polygon class to encapsulate the closed definition of polygons.

    Example
    -------
    >>> ADD EXAMPLE

    Notes
    -----
    A polygon is defined as a 2-dimensional closed shape with straight sides. The polygon class
    therefore implements methods that adhere to this definition as well as establishes the potential
    ability for a lattice to be generated from the polygon.

    Similar to its superclass, a polygon object can be built piece-meal through addition of vertices
    and edges however this does not ensure the required closed nature of a polygon. Instead, by 
    using 'generate polygon', the shape can be generated from a dictionary of vectors that describe
    the edges of the shape.
    
    Polygons can also potentially be organised into a regular repeated arrangement called a lattice.
    If this is possible for the polygon a series of change vectors (the vectors between iterations
    of the shapes in the lattice) can then be defined and the lattice can be generated. 

    """
    def __init__(self):
        """
        Initialises a Polygon object, inherits from Shape..

        """
        super().__init__()

    def generate_lattice(self, layers, lat_type):
        """
        Generates the polygon's lattice in a given number of layers centred on the staring
        polygon. Uses the methods; 'generate_change_vectors' a 'generate_lattice_from_vectors'.

        Parameters
        ----------
        layers : int > 0
            The number of layers to be generated around the original polygon. If 1 is input
            the original shape is just generated.
        
        Returns
        -------
        lattice : Lattice class object specific to current generating shape.

        Example
        -------
        >>> ADD EXAMPLE

        Notes
        -----
        ADD NOTES
        """
        if self.get_lattice_state():
            if lat_type == "circular":
                return self.generate_lattice_circular(layers)
            elif lat_type == "stacked":
                return self.generate_lattice_stacked(layers)
            else:
                raise PolyLatNotProp(lat_type)  
        else:
            print("Lattice not possible with this shape.")


    @abc.abstractmethod
    def generate_lattice_stacked(self, layers):
        """
        Abstract method that generates and returns the stacked lattice for polygons. To be defined
        in child classes.
        """

    @abc.abstractmethod
    def generate_lattice_circular(self, layers):
        """
        Abstract method that generates and returns the circular lattice for polygons. To be defined
        in child classes.
        """

    @abc.abstractmethod
    def get_lattice_state(self):
        """
        Abstract method that returns whether or not a polygon can have a lattice generated from it.
        To be defined in child classes.
        """

############################################################################################

        
class Lattice(Shape):
    """
    IMPLEMENT DOCUMENTATION
    """
    def __init__(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        super().__init__()
    
    def __set_lattice_type(self, lattice_type):
        """
        IMPLEMENT DOCUMENTATION
        """
        # Stacked, circular, custom...
        self.lattice_type = lattice_type 

    def get_shape_num(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        ## Using Euler's Formula: v - e + f = 2 (f includes outside face)
        # Only works if connected planar graph.
        return 1 - len(self.vertices) + len(self)

    def get_shape_sides(self):
        """
        IMPLEMENT DOCUMENTATION
        """
        ## This returns the No. of sides of the shpe in the lattice....
        edge_vecs = list(self.get_edge_vectors().values())
        initial_vertex_pos = self.vertices_info[0][1]["position"]
        i = 0
        pos = initial_vertex_pos
        for vec in edge_vecs:
            pos = add_vectors(pos, vec)
            i += 1
            if pos == initial_vertex_pos:
                break
        return i
