# Radial_slice_3d_array

![python3.7](https://img.shields.io/badge/python-3.7-green.svg)

# Requirements
Setup packages
```sh
pip install -r requirements.txt
```

# Documentation
## 1. Interpolation function
We call the scipy function [ RegularGridInterpolator ](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RegularGridInterpolator.html) to access the corresponding values of the points in 3darray.  
If the shape of your input volume (x,y,z) = (64,64,30), then
```sh
x = np.linspace(0, 63, 64)
y = np.linspace(0, 63, 64)
z = np.linspace(0, 29, 30)
```
Accessing the value on the position (x,y,z) = (2.1, 6.2, 8.3)
```sh
my_interpolating_function = RegularGridInterpolator((c, a, b), volume)
point = np.array([2.1, 6.2, 8.3])
value = my_interpolating_function(point)
```

## 2. Slice 
We want to take the radial slice around the center point lied on z=0 plane, and take the z-axis as the rotation axis. 
The following image is the examples which is refer to [documentations of pyvista](https://docs.pyvista.org/examples/01-filter/slicing.html).
![examples](./doc/slice.png)   

