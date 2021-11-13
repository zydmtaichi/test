import taichi as ti
from newnbody import adjustnbody

ti.init(arch=ti.x64)

bodies = adjustnbody(1000,1,3)

bodies.G[None] = 1e-3
expandsize = 0.3
initvel = 1
dt = 1e-4

if bodies.dim == 2:
    centerpos = ti.Vector([0.4,0.5])
else:
    centerpos = ti.Vector([0.0,0.0,0.0])

print(bodies.dim)


    
bodies.initial(centerpos,expandsize,initvel)

