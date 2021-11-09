import taichi as ti


G = 1
PI = 3.1415926
disappear_dis = 0.03

@ti.data_oriented
class celestialobjest:
    def __init__(self,N,mass):
        self.N = N
        self.mass = mass
        self.pos = ti.Vector.field(2,ti.f32,self.N)
        self.vel = ti.Vector.field(2,ti.f32,self.N)
        self.force = ti.Vector.field(2,ti.f32,self.N)
        
    def visualize(self,gui,radius=2,color=0xffffff):
        gui.circles(self.pos.to_numpy(),radius=radius,color=color)
        
    @ti.func
    def count(self):
        return self.N
        
    @ti.func
    def location(self):
        return self.pos
        
    @ti.func
    def clear(self):
        for i in self.force:
            self.force[i] = ti.Vector([0.0,0.0])
    
    @ti.func
    def Mass(self):
        return self.mass
        
    @ti.kernel
    def initial(self,centerx:ti.f32,centery:ti.f32,size:ti.f32,init_vel:ti.f32):
        for i in range(self.N):
            if self.N == 1:
                self.pos[i] = ti.Vector([centerx,centery])
                self.vel[i] = ti.Vector([0.0,0.0])
            else:
                angle, dis = self.pickrandomlocation(i,self.N)
                offset = ti.Vector([ti.cos(angle),ti.sin(angle)])
                center = ti.Vector([centerx,centery])
                self.pos[i] = center + dis*offset*size
                self.vel[i] = ti.Vector([-ti.sin(angle),ti.cos(angle)])
                self.vel[i] *= init_vel
                
    @ti.kernel
    def computeforce(self):
        self.clear()
        for i in range(self.N):
            p = self.pos[i]
            for j in range(i):
                diff = self.pos[j]-p
                r = diff.norm(1e-2)
                f = G*self.Mass()*self.Mass()*(1.0/r)**3*diff
                self.force[i] += f
                self.force[j] += -f
    @ti.kernel
    def update(self,dt:ti.f32):
        for i in range(self.N):
            self.vel[i] += dt*self.force[i]/self.Mass()
            self.pos[i] += dt*self.vel[i]
            
@ti.data_oriented
class star(celestialobjest):
    def __init__(self,N,mass):
        super().__init__(N,mass)
        
    @staticmethod
    @ti.func
    def pickrandomlocation(i,n):
        angle = 2*PI*i/ti.cast(n,ti.f32)
        dis = 1
        return angle, dis
    
@ti.data_oriented
class planet(celestialobjest):
    def __init__(self,N,mass):
        super().__init__(N,mass)
        self.disappearstatus = ti.Vector.field(1,ti.i32,self.N)
        
    @ti.kernel
    def initial(self,centerx:ti.f32,centery:ti.f32,size:ti.f32,init_vel:ti.f32):
        super().initial(centerx,centery,size,init_vel)
        for i in range(self.N):
            self.disappearstatus = ti.Vector([0])
    @ti.func
    def disappear(self):
        return self.disappearstatus
        
    @staticmethod
    @ti.func
    def pickrandomlocation(i,n):
        angle = 2*PI*ti.random()
        dis = (ti.sqrt(ti.random()) * 0.7 + 0.3)
        return angle, dis
        
    @ti.kernel
    def computeforce(self,stars:ti.template()):
        self.clear()
        for i in range(self.N):
            if self.disappearstatus[i][0] == 0:
                p = self.pos[i]
                for j in range(i):
                    diff = self.pos[j]-p
                    r = diff.norm(1e-2)
                    f = -G*self.Mass()*self.Mass()*(1.0/r)**3*diff
                    self.force[i] += f
                    
                for k in range(stars.count()):
                    diff = stars.location()[k]-p
                    r = diff.norm(1e-2)
                    f = G*self.Mass()*stars.Mass()*(1.0/r)**3*diff
                    self.force[i] += f
                    stars.force[k] += -f
                    
    @ti.kernel
    def update(self,dt:ti.f32):
        for i in range(self.N):
            if self.disappearstatus[i][0] == 0:
                self.vel[i] += dt*self.force[i]/self.Mass()
                self.pos[i] += dt*self.vel[i]
                    
@ti.data_oriented
class blackhole(celestialobjest):
    def __init__(self,N,mass):
        super().__init__(N,mass)
        
    @ti.kernel
    def computeforce(self,planets:ti.template()):
        self.clear()
        for i in range(planets.count()):
            if planets.disappear()[i][0] == 0:
                p = planets.location()[i]
                for j in range(i):
                    if planets.disappear()[i][0] == 0:
                        diff = planets.location()[j]-p
                        r = diff.norm(1e-2)
                        f = G*planets.Mass()*planets.Mass()*(1.0/r)**3*diff
                        planets.force[i] += f
                        planets.force[j] += -f
                for k in range(self.N):
                    diff_bm = p-self.pos[k]
                    diffbmnorm = diff_bm.norm(1e-5)
                    if diffbmnorm < disappear_dis:
                        planets.disappearstatus[i] = ti.Vector([1])
                        planets.vel[i] = ti.Vector([0,0])
                        planets.pos[i] = ti.Vector([-50000,-50000])*(ti.random()-0.5)
                        f = -G * m * bm * (1.0/diffbmnorm)**3 * diff_bm
                        planets.force[i] += f
                        self.force[k] += -f
