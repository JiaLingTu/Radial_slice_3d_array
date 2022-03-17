# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 22:18:22 2022

@author: JiaLing _Tu
"""
import numpy as np
from matplotlib import pyplot as plt
def get_intersect(a1, a2, b1, b2):
    """ 
    Returns the point of intersection of the lines passing through a2,a1 and b2, b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return (float('inf'), float('inf'))
    return (np.around(x/z), np.around(y/z))

def rotate_points(point, center_point, angle):
    """
    Rotate points about a center point by specific angle.

    Parameters
    ----------
    point : ndarray
        Point need to be rotated.
    center_point : ndarray
        The rotate center for other points.
    angle : float, int
        Rotate angle.

    Returns
    -------
    ndarray
        Result point.

    """
    point = point - center_point
    rotate_matrix = np.array([[np.cos(angle*np.pi/180), -np.sin(angle*np.pi/180)],
                              [np.sin(angle*np.pi/180), np.cos(angle*np.pi/180)]])
    new_point = rotate_matrix.dot(point)
    return new_point + center_point

def intersect_line_rect(line, rect):
    """
    Find the intersection of a line and a rectangle.
    Line represents the slicing line on the top-face plane, and 
    Rectangular represents the frame of the top-face plane.
            En-face:
            (0,0)                                 (511,0)
            ----------------------------------------
            |                                      |
            |                                      |
            |                                      |
      (0,64)|__________________line________________|(511,64)
            |                                      |
            |                                      |
            |                                      |
            |                                      |
            ----------------------------------------
            (0, 127)                            (511, 127)

    Parameters
    ----------
    line : ndarray
        The endpoints of this line.
        Ex: line= np.array([(0,64), (511,64)])
    rect : ndarray
        The vertex of the rectangle.
        And the first point shold repeat again on the last element.
        Ex: rect = np.array([0, 0), (0, 127), (511, 127), (511,0), (0,0)])

    Returns
    -------
    intersection : list
        The coordinate of the intersection.

    """
    intersection = []
    constraint = rect[2]
    a1, a2 = line
    for i in range(len(rect)-1):
        b1, b2 = rect[i], rect[i+1]
        res = get_intersect(a1, a2, b1, b2)
        if res == (np.inf, np.inf):
            pass
        elif res[0] < 0 or res[0] > constraint[0] or res[1] < 0 or res[1] > constraint[1]:
            pass
        else:
            intersection.append(get_intersect(a1, a2, b1, b2))
            
    return intersection

def sort_tuple(tuple_List):
    if len(tuple_List)==1: # 不需要排序
        pass
    else:
        tuple_List.sort()
    return tuple_List

def intersect_line_rect2(contrain, rotate_center, m):
    x0, y0 = rotate_center
    constraint_x,  constraint_y= contrain
    intersections = []
    
    # vertical line
    if m>constraint_y:
        intersection = [(x0, 0), (x0, constraint_y)]
        return intersection
    
    # horizontal line
    if m==0:
        intersection = [(0, y0), (constraint_x, y0)]
        return intersection  
      
    # x = 0
    y = m*(0-x0) + y0
    if  y > constraint_y or y < 0:
        pass
    else:
        intersections.append((0, y))
    
    # x = constraint_x
    y = m*(constraint_x-x0) + y0
    if y > constraint_y or y < 0:
        pass
    else:
        intersections.append((constraint_x, y))
    
    # y = 0
    x = (0-y0)/m + x0
    if x > constraint_x or x < 0:
        pass
    else:
        # print((0-y0)/m + x0)
        intersections.append((x, 0))
    
    # y = constraint_y
    x = (constraint_y-y0)/m + x0
    if x > constraint_x or x < 0:
        pass
    else:
        # print((constraint_y-y0)/m + x0)
        intersections.append((x, constraint_y))
    return intersections


def plot_radial(img, S):
    plt.figure()
    for i in range(len(S)):
        plt.plot(np.linspace(S[i]['p1'][0], S[i]['p2'][0], 100), np.linspace(S[i]['p1'][-1], S[i]['p2'][-1], 100), 'r')   
    plt.imshow(img)