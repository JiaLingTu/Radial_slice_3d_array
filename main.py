#%%
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from matplotlib import pyplot as plt

def coords_img2vol(annotated_points, slc):
    """
    This function is to convert the points which is on the image plane
    to the top-face plane. 

    Parameters
    ----------
    annotated_points : tuple, list, ndarray
        Keypoints found on slicing image.
        
    slc : Dict
        Dict object which records information about each slicing image.

    Returns
    -------
    list
        Coordinate on top-face.

    """
    if not np.any(annotated_points) :
        return [0,0]
    # p1, p2 are endpoints of the slicing line
    p1x, p1y = slc['p1']
    p2x, p2y = slc['p2']

    # index_x, index_y
    output_w, output_h = slc['slc'].shape
    index_x = np.linspace(p1x, p2x, output_w, dtype=np.float16)
    index_y = np.linspace(p1y, p2y, output_w, dtype=np.float16)
    
    # interp method1
    point_u, point_v = annotated_points
    point_b = index_x[point_u]
    point_c = index_y[point_u]
    
    # interp method2
    # 要比一下精度準確度 目前是method1比較準但why...?
    t = (point_u+1) / output_w
    point_b_2, point_c_2 = (1-t) * np.array(slc['p1']) + t * np.array(slc['p2'])
    
    return [point_b, point_c]

def get_intersect(a1, a2, b1, b2):
    """ 
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
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

def RadialSlice(volume, angle, rotate_center=None, output_size=(512,512)):
    """
     Get many slices at different bearings all centered around a user-chosen location.
     Generate a few normal vectors to rotate a slice around the z-axis.

    Parameters
    ----------
    volume : ndarray
        The shape of it should be (c, a, b).
    angle : list, int, float
        angle is a number -> it'll slice the volume every {angle} degrees. 
        angle is a list -> it'll use this sequence as angle list to slice the volume.
    rotate_center : tuple, optional
        A user-chosen location for rotation center.
        The default is None.
    output_size : tuple, optional
        The shape of the output image.
        The default is (512,512).

    Returns
    -------
    Slices : Dict.
            'angle': angle_list[i],
            'slc': slc,  # slicing image
            'rotate_center': rotate_center,
            'p1': p1,   # first endpoint of radial slicing line
            'p2': p2,   # second endpoint of radial slicing line

    """
    line_buffer = 100
    # define axis
    nc, na, nb = volume.shape
    c = np.linspace(0, nc-1, nc)
    a = np.linspace(0, na-1, na)
    b = np.linspace(0, nb-1, nb)   
    
    # define an interpolating function from this volume
    my_interpolating_function = RegularGridInterpolator((c, a, b), volume)
    # Inintial horizontal line (one b-scan)
    if rotate_center is not None:
        a1 = np.array([0-line_buffer, rotate_center[1]])
        a2 = np.array([nb+line_buffer, rotate_center[1]])
    else:
        a1 = np.array([0-line_buffer, nc//2])
        a2 = np.array([nb+line_buffer, nc//2])
    
    # 可以自己輸入角度序列
    if isinstance(angle, int) or isinstance(angle, float):
        angle_list = np.arange(0, 180, angle )
    else :
        angle_list = list(angle)
    
    
    Slices = {}
    for i in range(len(angle_list)):
        
        # Rotated line LinString
        new_a1 = rotate_points(point=a1, center_point=rotate_center, angle=angle_list[i])
        new_a2 = rotate_points(point=a2, center_point=rotate_center, angle=angle_list[i])

        # intersection
        intersections = intersect_line_rect(line=[new_a1, new_a2] , rect=[(0, 0), (0, nc-1), (nb-1, nc-1), (nb-1,0), (0,0)])
        print('angle{}:{}'.format(angle_list[i], intersections))
        if angle_list[i] == 0:
            p1, p2 = intersections
        elif angle_list[i] < 90:
            p1, p2 = sort_tuple(intersections)
        else :  # 為了讓照片都是從左邊畫到右邊, 阿不然影像會有一個flip
            p2, p1 = intersections
        p1x, p1y = p1
        p2x, p2y = p2

        # index_x, index_y
        output_w, output_h = output_size
        index_x = np.linspace(p1x, p2x, output_w, dtype=np.float16)
        index_y = np.linspace(p1y, p2y, output_w, dtype=np.float16)
        index_xz = np.tile(index_x, output_h)
        index_yz = np.tile(index_y, output_h)
        
        # [0,0,0,...0,1,1,1,1...1,2,2,2....,output_h-1,output_h-1,output_h-1] 
        index_z = np.linspace(0, output_w-1, output_w, dtype=np.float16)
        index_z = np.repeat(index_z.reshape(-1,1), output_h)
        
        pts = np.stack((index_yz, index_z, index_xz ), axis=-1)
        
        # Slices
        slc = my_interpolating_function(pts)
        slc = slc.reshape(output_size)
        
        Slices[i] = {
            'angle': angle_list[i],
            'slc': slc,
            'rotate_center': rotate_center,
            # endpoint of radial slicing line
            'p1': p1, 
            'p2': p2,
        }

    return Slices


if __name__=="__main__":
    vol = np.random.random((128, 512, 512))
    slices = RadialSlice(volume=vol, rotate_center=(10, 20), angle=15, output_size=(64, 64))
    plt.imshow(slices[0]['img'])
# %%
