#%%
import numpy as np
from scipy.interpolate import RegularGridInterpolator
# import cProfile
import utils

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
    # define axis
    nc, na, nb = volume.shape
    c = np.linspace(0, nc-1, nc)
    a = np.linspace(0, na-1, na)
    b = np.linspace(0, nb-1, nb)
    
    # define an interpolating function from this volume
    my_interpolating_function = RegularGridInterpolator((c, a, b), volume)
    
    # 可以自己輸入角度序列
    if isinstance(angle, int) or isinstance(angle, float):
        angle_list = np.arange(0, 180, angle )
    else :
        angle_list = list(angle)
    slope_list = [np.tan(i*np.pi/180) for i in angle_list]
    if rotate_center is None:
        rotate_center = (nb//2, nc//2)
        
    Slices = {}
    # pr = cProfile.Profile()
    # pr.enable()  
    for i in range(len(slope_list)):
        intersections = utils.intersect_line_rect2(contrain=(nb-1, nc-1), rotate_center=rotate_center, m=slope_list[i])
    # pr.disable()    
    # pr.print_stats()
        if len(intersections)!=2:
            raise ValueError
    
        if angle_list[i] == 0:
            p1, p2 = intersections
        elif angle_list[i] < 90:
            p1, p2 = utils.sort_tuple(intersections)
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
    slices = RadialSlice(volume=vol, rotate_center=(289, 78), angle=15, output_size=(64, 64))
    utils.plot_radial(vol.sum(2), slices)
