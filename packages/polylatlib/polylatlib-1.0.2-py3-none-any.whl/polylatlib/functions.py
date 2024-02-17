from math import sin, cos, radians

__all__ = [
    "check_if_coord",
    "is_positive_int",
    "is_supported_colour",
    "add_vectors",
    "change_to_cart_vector",
    "change_to_cart_list"
]

## VALUE CHECKING ##
def check_if_coord(value):
    if type(value) == tuple and len(value) == 2:
        ans = True
        for i in range(2):
            if type(value[i]) != int and type(value[i]) != float:
                ans *= False
        return bool(ans)
    else:
        return False

def is_positive_int(value):
    if value > 0 and type(value) == int:
        return True
    else:
        return False

def is_supported_colour(colour):
    colours = ["k", "r", "g", "b", "c", "m", "y"]
    if colour in colours:
        return True
    else:
        return False


## VECTOR MANIPULATION ##
def add_vectors(a, b):
    new_val = (a[0] + b[0], a[1] + b[1])
    new_val = (round(new_val[0], 6), round(new_val[1], 6))
    return new_val

def change_to_cart_vector(polar_vector):
    x = polar_vector[0]*cos(radians(polar_vector[1]))
    y = polar_vector[0]*sin(radians(polar_vector[1]))
    temp = (round(x, 3), round(y, 3))
    return temp

def change_to_cart_list(vector_list):
    temp = []
    for i in vector_list:
        vector = change_to_cart_vector(i)
        temp.append(vector)
    return temp