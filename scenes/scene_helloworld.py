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
        # Create 1000 particles in a planar grid (e.g., 40 x 25) with randomized heights
        num_x = 40
        num_z = 25
        spacing = 0.05
        start_x = - (num_x // 2) * spacing
        start_z = - (num_z // 2) * spacing
        for i in range(num_x):
            for j in range(num_z):
                x = start_x + i * spacing
                # Randomize y between 0 and 0.5
                y = ti.random(ti.f32) * 0.5
                z = start_z + j * spacing
                self.add_particle(vec3(x, y, z), 1, vec3(1.0, 0.0, 0.0), 0.01)

    @ti.kernel
    def update_particles(self, dt: ti.f32):
        for i in range(self.renderer.num_particles[None]):
            # Update position
            self.renderer.particle_pos[i] += self.renderer.particle_velocity[i] * dt

            # Check if particle is on or above the floor
            on_floor = self.renderer.particle_pos[i][1] <= -0.5 + 0.05 and self.renderer.particle_velocity[i][1] <= 0

            # Only apply gravity if the particle is not resting on the floor
            if not on_floor:
                self.renderer.particle_velocity[i][1] -= 5.81 * dt

            # Bounce off the floor at y = -0.5
            if self.renderer.particle_pos[i][1] < -0.5 + 0.01:
                self.renderer.particle_pos[i][1] = -0.5 + 0.01

                if self.renderer.particle_velocity[i][1] < 0:
                    self.renderer.particle_velocity[i][1] *= -0.8  # Reverse and dampen velocity

                    # Stop very small bounces
                    if abs(self.renderer.particle_velocity[i][1]) < 0.25:
                        self.renderer.particle_velocity[i][1] = 0.0