# Radial slice on 3D numpy array

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
![examples](./doc/slice.png)

### Get interpolation points for radial slicing
Based on the regular interpolation function we mentioned above, we can resample the given point by using that Interpolator.
Now, we need to generate the coordinates lied on the radial slicing line (red line on the figure below).
We define two endpoints to represent the horizontal line passing through the center point (user-chosen), like this:
```sh
buffer = 50 # avoid there's no intersection between the line and the rectangle
a1 = np.array([0-buffer, 89])
a2 = np.array([512+buffer, 89])
```
Then, define the vertex of the rectangle by the list of points
```sh
np.array([0, 0), (0, 127), (511, 127), (511,0), (0,0)])
```
We use vectors to find the intersection between tweo line (line and one side of the rectangle) and record those points as endpoint.
```sh
endpoint1 = (0, 89)
endpoint2 = (511, 89)
x = np.linspace(endpoint1[0], endpoint2[0], output_w)
y = np.linspace(endpoint1[1], endpoint2[1], output_w)
# elements of the x and y represent the red line.
```
Since points on the red line will duplicate on each z-plane, 
we only need to give the element represent z.
```sh
index_z = np.linspace(0, output_w-1, output_w, dtype=np.float16)
index_z = np.repeat(index_z.reshape(-1,1), output_h)
```