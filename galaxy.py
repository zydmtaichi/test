import taichi as ti
from celestial import star, planet

ti.init(arch=ti.cpu)

if __name__ == '__main__':

    stars = star(N=3,mass=1000)
    stars.initial(0.5,0.5,0.2,10)
    planets = planet(N=500,mass=1)
    planets.initial(0.5,0.5,0.4,10)
    blackholeins = blackhole(N=1,mass=20000)
    blackholeins.initial(0.5,0.5,0.4,10)
    
    my_gui = ti.GUI("galaxy",(800,800))

    h = 1e-5

    while my_gui.running:
        stars.computeforce()
        planets.computeforce(stars)
        blackholeins.computeforce(planets)
        for celestialobject in (stars, planets, blackholeins):
            celestialobject.update(h)
            
        stars.visualize(my_gui,radius=10,color=0xffd500)
        planets.visualize(my_gui)
        my_gui.show()
        
