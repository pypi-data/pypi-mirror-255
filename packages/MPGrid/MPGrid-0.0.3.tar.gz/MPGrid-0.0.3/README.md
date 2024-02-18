# MPGrid
Python Library for Finite Difference Calculation

# Install

```
> pip install MPGrid
```

# References
+ DATA
  + True = 1
  + False = 0
  + BoundInsulate = 0
  + BoundPeriodic = 1
  + InterCond = 0
  + InterTrans = 1

## Class clone(...), copy(...), new(...), read(...)
+ clone(grid) : clone grid
  + grid : grid data
+ copy(grid, (x0, y0, z0), (x1, y1, z1)) : copy grid
  + grid : grid data
  + x0, y0, z0 : start point of region
  + x1, y1, z1 : end point of region
+ new(nx, ny, nz, ntype, [local_coef=FALSE]) : create new grid
  + nx, ny, nz : number of elements in x, y, z direction
  + ntype : number of types
  + local_coef : local coefficient mode if true 
+ read(fname, [version=2]) : read grid from file
  + fname : file name
  + version : version of data format
+ CLASS METHODS
  + ave_val((x0, y0, z0), (x1, y1, z1)) : average values of region
  + count_type(type, (x0, y0, z0), (x1, y1, z1)) : count type in region
  + cylinder_type(type, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill type in cylinder shape
  + cylinder_update(update, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill update in cylinder
  + cylinder_val(val, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill value in cylinder shape
  + ellipsoid_type(type, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill type in ellipsoid shape
  + ellipsoid_update(update, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill update in ellipsoid shape
  + ellipsoid_val(val, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill value in ellipsoid shape
  + estimate_dt([ratio=1.0]) : estimate dt
  + fill_local_coef((cx, cy, cz), (x0, y0, z0), (x1, y1, z1)) : fill value
  + fill_type(type, (x0, y0, z0), (x1, y1, z1)) : fill type
  + fill_update(update, (x0, y0, z0), (x1, y1, z1)) : fill update
  + fill_val(val, (x0, y0, z0), (x1, y1, z1)) : fill value
  + gauss_random(type, num, spdis, (x0, y0, z0), (x1, y1, z1)) : set type by gauss random
  + get_coef(i, j) : get coefficient
  + get_inter(i, j) : get interface type
  + get_inter_coef(i, j) : get interface type and coefficient
  + get_local_coef((x, y, z)) : get local coefficient
  + get_rhoc(i) : get coefficient, rhoc x c
  + get_type((x, y, z)) : get type
  + get_update((x, y, z)) : get update
  + get_val((x, y, z)) : get value
  + ref_local_coef() : reflect local coefficient with coefficient table
  + set_coef1(coef, i, j) : set coefficient
  + set_coef3((coef_x, coef_y, coef_z), i, j) : set coefficient
  + set_inter1(inter, i, j) : set interface type
  + set_inter3((inter_x, inter_y, inter_z), i, j) : set interface type
  + set_inter_coef1(inter, coef, i, j) : set interface type and coefficient
  + set_inter_coef3((inter_x, inter_y, inter_z), (coef_x, coef_y, coef_z), i, j) : set interface type and coefficient
  + set_local_coef((cx, cy, cz), (x, y, z)) : set local coefficient
  + set_local_coef1(c, type0, type1) : set local coefficient by type
  + set_local_coef3((cx, cy, cz), type0, type1) : set local coefficient by type
  + set_rhoc(rhoc, i) : set coefficient, rhoc x c
  + set_type(type, (x, y, z)) : set type
  + set_update(update, (x, y, z)) : set update
  + set_val(val, (x, y, z)) : set value
  + solve(dt, nloop) : solve
  + uniform_random(type, num, (x0, y0, z0), (x1, y1, z1)) : set type by uniform random
  + write(fname, comp) : write grid data
+ CLASS DATA
  + bound = (xl, yl, zl, xu, yu , zu) : boundary condition (Updateable)
  + element = (ex, ey, ez) : size of element (Updateable)
  + local_coef : flag of local coefficient mode
  + ntot : total number of allocated elements
  + ntype : number of type
  + rand_seed = seed : seed of random number (Updateable)
  + size : cell size
  + step : calculated step
