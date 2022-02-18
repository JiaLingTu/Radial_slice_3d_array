import numpy as np
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry import LineString
from shapely import affinity

def RadialSlice(volume, rotate_center, angle, output_size=(512,512)):    
    line_buffer = 100
    # define axis
    nc, na, nb = volume.shape
    c = np.linspace(0, nc-1, nc)
    a = np.linspace(0, na-1, na)
    b = np.linspace(0, nb-1, nb)
    
    # define an interpolating function from this volume
    my_interpolating_function = RegularGridInterpolator((c, a, b), volume)
    # Inintial horizontal line (one b-scan)
    if rotate_center:
        lineObj = LineString( [(0-line_buffer, rotate_center[1]),(nb+line_buffer, rotate_center[1])] )
    else:
        lineObj = LineString( [(0-line_buffer, nc//2),(nb+line_buffer, nc//2)] )
    
    # 可以自己輸入角度序列
    if isinstance(angle, int) or isinstance(angle, float):
        angle_list = np.arange(0, 180, angle )
    else :
        angle_list = list(angle)
    Slices = {}
    for i in range(len(angle_list)):
        
        # Enface LinString
        enface = LineString([(0, 0), (0, nc-1), (nb-1, nc-1), (nb-1,0), (0,0)])
        
        # Rotated line LinString
        line_rot = affinity.rotate(lineObj, angle_list[i], rotate_center)

        # intersection
        intersections = enface.intersection(line_rot)
        if angle_list[i]<=90:
            p1, p2 = [(pt.x, pt.y) for pt in intersections.geoms]
        else :  # 為了讓照片都是從左邊畫到右邊, 阿不然超過90度的旋轉影像都會有一個flip
            p2, p1 = [(pt.x, pt.y) for pt in intersections.geoms]
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
        
        # shape
        slc_length = np.power(np.power(p2x-p1x, 2) + np.power(p2y-p1y, 2), 0.5)
        # get rotate center on slice image
        
        if p2x-p1x:
            left_length = (rotate_center[0]-p1x)/abs(p2x-p1x) * output_w
        else:
            left_length = (rotate_center[1]-p1y)/abs(p2y-p1y) * output_w
        left_length = int(left_length)
        # 乘乘除除之後 290可能會變成 290.76 會有問題, 之後看看保留浮點數勒?

        # Slices
        slc = my_interpolating_function(pts)
        slc = slc.reshape(output_size)

        Slices[i] = {
            'angle': angle_list[i],
            'slc': slc,
            'rotate_center': rotate_center,
            'cu_on_slc': left_length,
            'shape': slc_length,
            'intersections': intersections,
            'index_x': index_x,
            'index_y':index_y,
        }

    return Slices

if __name__=="__main__":
    img = np.random.random((64, 64, 64))