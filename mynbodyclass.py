import taichi as ti

@ti.data_oriented
class adjustnbody:
    def __init__(self,N,mass,dimension=2):
        self.PI = ti.atan2(1,1)*4
        self.G = ti.field(ti.f32,shape=())
        
        self.dim = dimension
        self.n = N
        self.mass = mass
        self.pos = ti.Vector.field(self.dim,ti.f32,self.n)
        self.vel = ti.Vector.field(self.dim,ti.f32,self.n)
        self.force = ti.Vector.field(self.dim,ti.f32,self.n)
        self.color = ti.Vector.field(3,ti.f32,self.n)
        
        
    def display(self,canvas,scene,camera,r=0.005,c=(1,1,1)):
        canvas.set_background_color((17/255,47/255,65/255)) #没文档
        if self.dim == 2:
            canvas.circles(self.pos,radius=r,color=c)
        else:
            scene.set_camera(camera)
            scene.ambient_light((0,0,0))
            scene.particles(self.pos,radius=r,color=c)
            scene.point_light(pos=(0.5,1.5,0.5),color=(0.5,0.5,0.5))
            scene.point_light(pos=(0.5,1.5,1.5),color=(0.5,0.5,0.5))
            canvas.scene(scene)
            
            
    @ti.func
    def clear(self):
        for i in self.force:
            for j in ti.static(range(self.dim)):
                self.force[i][j] = 0
                
    @ti.kernel
    def initial(self,center:ti.template(),expand_size:ti.f32,init_vel:ti.f32):
        for i in range(self.n):
            if self.n == 1:
                self.pos[i] = center
                for j in ti.static(range(self.dim)):
                    self.vel[i][j] = 0
            elif self.dim == 3:
                offset = ti.Vector([ti.random(),ti.random(),ti.random()])-ti.Vector([expand_size,expand_size,expand_size])*0.5
                originvel = ti.Vector([-offset[1],offset[0],0])*init_vel
                self.pos[i] = center+offset
                self.vel[i] = originvel
            
            elif self.dim == 2:
                offset = ti.Vector([ti.random(),ti.random()])-ti.Vector([expand_size,expand_size])*0.5
                originvel = ti.Vector([-offset[1],offset[0]])*init_vel
                self.pos[i] = center+offset
                self.vel[i] = originvel
            
            
            
    @ti.kernel
    def computeforce(self):
        self.clear()
        for i in range(self.n):
            p = self.pos[i]
            for j in range(i):
                diff = self.pos[j]-p
                r = diff.norm(1e-2)
                f = self.G[None]*self.mass*self.mass*(1.0/r)**3*diff
                self.force[i] += f
                self.force[j] += -f
                
    @ti.kernel
    def update(self,dt:ti.f32):
        for i in self.vel:
            self.vel[i] += dt*self.force[i]/self.mass
            self.pos[i] += dt*self.vel[i]
            
            
