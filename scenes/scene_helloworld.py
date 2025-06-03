import taichi as ti
from taichi.math import vec3

from rendering.scene import Scene

@ti.data_oriented
class SceneHelloWorld(Scene):

    def __init__(self, args):
        super().__init__(args)

        # Set the floor to a light gray color
        self.set_floor(-0.5, (0.8, 0.8, 0.8))

        # Set a directional light with a white color
        self.set_directional_light((0, 0, 1), 0.1, (1.0, 1.0, 1.0))

    @ti.kernel
    def initialize_particles(self):
        # Create a single particle at the origin with a radius of 0.05
        self.add_particle(vec3(0.0, 0.0, 0.0), 1, (1.0, 0.0, 0.0), 0.2)