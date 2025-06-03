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
        self.set_directional_light((0, 1, 0), 0.1, (0.1, 0.1, 0.1))

    @ti.kernel
    def initialize_particles(self):
        # Create a single particle at the origin
        self.add_particle(vec3(0.0, 0.0, 0.0), 1, vec3(1.0, 0.0, 0.0), 0.05)

    @ti.kernel
    def update_particles(self, dt: ti.f32):
        for i in range(self.renderer.num_particles[None]):
            self.renderer.particle_pos[i] += self.renderer.particle_velocity[i] * dt

            self.renderer.particle_velocity[i][1] -= 9.81 * dt  # Gravity effect

            # Bounce off the floor at y = -0.5
            if self.renderer.particle_pos[i][1] < -0.5:
                self.renderer.particle_pos[i][1] = -0.5
                if self.renderer.particle_velocity[i][1] < 0:
                    self.renderer.particle_velocity[i][1] *= -0.8  # Reverse and dampen velocity