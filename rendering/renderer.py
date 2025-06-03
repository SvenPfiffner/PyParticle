import taichi as ti

from .utils import (eps, inf, out_dir, ray_aabb_intersection)

MAX_RAY_DEPTH = 4
use_directional_light = True

DIS_LIMIT = 100

MAT_LAMBERTIAN = 1
MAT_LIGHT = 2

@ti.data_oriented
class Renderer:
    def __init__(self, image_res, up, exposure=3, max_particles=100):
        self.image_res = image_res
        self.aspect_ratio = image_res[0] / image_res[1]
        self.vignette_strength = 0.9
        self.vignette_radius = 0.0
        self.vignette_center = [0.5, 0.5]
        self.current_spp = 0

        self.color_buffer = ti.Vector.field(3, dtype=ti.f32)
        self.bbox = ti.Vector.field(3, dtype=ti.f32, shape=2)
        self.fov = ti.field(dtype=ti.f32, shape=())


        self.light_direction = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.light_direction_noise = ti.field(dtype=ti.f32, shape=())
        self.light_color = ti.Vector.field(3, dtype=ti.f32, shape=())


        self.exposure = exposure

        self.camera_pos = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.look_at = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.up = ti.Vector.field(3, dtype=ti.f32, shape=())

        self.floor_height = ti.field(dtype=ti.f32, shape=())
        self.floor_color = ti.Vector.field(3, dtype=ti.f32, shape=())

        self.background_color = ti.Vector.field(3, dtype=ti.f32, shape=())

        ti.root.dense(ti.ij, image_res).place(self.color_buffer)

        self.max_particles = max_particles
        self.num_particles = ti.field(dtype=ti.i32, shape=())
        self.particle_pos = ti.Vector.field(3, dtype=ti.f32)
        self.particle_color = ti.Vector.field(3, dtype=ti.f32)
        self.particle_material = ti.field(dtype=ti.i8)
        self.particle_radius = ti.field(dtype=ti.f32)
        self.particle_velocity = ti.Vector.field(3, dtype=ti.f32)

        particle_node = ti.root.dense(ti.i, self.max_particles)
        particle_node.place(self.particle_pos,
                            self.particle_color,
                            self.particle_material,
                            self.particle_radius,
                            self.particle_velocity)


        self._rendered_image = ti.Vector.field(3, float, image_res)
        self.set_up(*up)
        self.set_fov(0.23)

        self.floor_height[None] = 0
        self.floor_color[None] = (1, 1, 1)

    @ti.func
    def add_particle(self, pos: ti.types.vector(3, ti.f32),
                     color: ti.types.vector(3, ti.f32),
                     material: ti.i8,
                     radius: ti.f32,
                     velocity: ti.types.vector(3, ti.f32)):
        
        if self.num_particles[None] < self.max_particles:
            new_idx = ti.atomic_add(self.num_particles[None], 1)
            self.particle_pos[new_idx] = pos
            self.particle_color[new_idx] = color
            self.particle_material[new_idx] = material
            self.particle_radius[new_idx] = radius
            self.particle_velocity[new_idx] = velocity
        else:
            print("Max particles reached, cannot add more. Consider increasing max_particles.")

    @ti.kernel
    def update_particles(self, dt: ti.f32):
        for i in range(self.num_particles[None]):
            self.particle_pos[i] += self.particle_velocity[i] * dt

            self.particle_velocity[i][1] -= 9.81 * dt  # Gravity effect

            # Simple collision with the floor
            if self.particle_pos[i][1] < self.particle_radius[i] and self.particle_velocity[i][1] < -0.2:
                self.particle_velocity[i][1] *= -0.5

            #Change color over time (e.g., fade red component)
            self.particle_color[i][0] = ti.max(0.0, self.particle_color[i][0] - 0.1 * dt)


    def set_directional_light(self, direction, light_direction_noise,
                              light_color):
        direction_norm = (direction[0]**2 + direction[1]**2 +
                          direction[2]**2)**0.5
        self.light_direction[None] = (direction[0] / direction_norm,
                                      direction[1] / direction_norm,
                                      direction[2] / direction_norm)
        self.light_direction_noise[None] = light_direction_noise
        self.light_color[None] = light_color


    @ti.func
    def ray_march(self, p, d):
        dist = inf
        if d[1] < -eps:
            dist = (self.floor_height[None] - p[1]) / d[1]
        return dist

    @ti.func
    def sdf_normal(self, p):
        return ti.Vector([0.0, 1.0, 0.0])  # up

    @ti.func
    def sdf_color(self, p):
        return self.floor_color[None]
    
    @ti.func
    def ray_sphere_intersection(self, sphere_pos, sphere_radius, o, d):
        op = sphere_pos - o
        b = op.dot(d)
        det_sq = b * b - op.dot(op) + sphere_radius * sphere_radius
        intersect = 0
        t = inf

        if det_sq >= 0:
            det = ti.sqrt(det_sq)
            t1 = b - det
            t2 = b + det
            if t1 > eps:
                t = t1
                intersect = 1
            elif t2 > eps: # Origin is inside the sphere, t1 is negative or zero
                pass

        return intersect, t
    
    @ti.func
    def trace_particles(self, eye_pos, d):
        closest_t = inf
        hit_normal_val = ti.Vector([0.0, 0.0, 0.0])
        hit_color_val = ti.Vector([0.0, 0.0, 0.0])
        hit_material_val = ti.i8(0)
        hit_light_flag = 0

        for i in range(self.num_particles[None]):
            p_pos = self.particle_pos[i]
            p_radius = self.particle_radius[i]

            is_hit, t = self.ray_sphere_intersection(p_pos, p_radius, eye_pos, d)

            if is_hit and t < closest_t:
                closest_t = t
                hit_point = eye_pos + t * d
                hit_normal_val = (hit_point - p_pos).normalized()
                hit_color_val = self.particle_color[i]
                hit_material_val = self.particle_material[i]

        if hit_material_val == MAT_LIGHT:
            hit_light_flag = 1

        # This dummy_idx is to maintain signature similar to dda_voxel for next_hit if needed,
        # but particle highlighting would work differently (e.g. with hit_particle_idx)
        dummy_idx = ti.Vector([0,0,0])

        return closest_t, hit_normal_val, hit_color_val, hit_light_flag, dummy_idx


    @ti.func
    def next_hit(self, pos, d, t):
        closest = inf
        normal = ti.Vector([0.0, 0.0, 0.0])
        c = ti.Vector([0.0, 0.0, 0.0])
        hit_light = 0
        closest_particle, normal_particle, c_particle, hit_light_particle, _ = self.trace_particles(pos, d)

        if closest_particle < closest:
            closest = closest_particle
            normal = normal_particle
            c = c_particle
            hit_light = hit_light_particle

        ray_march_dist = self.ray_march(pos, d)
        if ray_march_dist < DIS_LIMIT and ray_march_dist < closest:
            closest = ray_march_dist
            normal = self.sdf_normal(pos + d * closest)
            c = self.sdf_color(pos + d * closest)
            hit_light = 0  # Floor is not a light source

        return closest, normal, c, hit_light

    @ti.kernel
    def set_camera_pos(self, x: ti.f32, y: ti.f32, z: ti.f32):
        self.camera_pos[None] = ti.Vector([x, y, z])

    @ti.kernel
    def set_up(self, x: ti.f32, y: ti.f32, z: ti.f32):
        self.up[None] = ti.Vector([x, y, z]).normalized()

    @ti.kernel
    def set_look_at(self, x: ti.f32, y: ti.f32, z: ti.f32):
        self.look_at[None] = ti.Vector([x, y, z])

    @ti.kernel
    def set_fov(self, fov: ti.f32):
        self.fov[None] = fov

    @ti.func
    def get_cast_dir(self, u, v):
        fov = self.fov[None]
        d = (self.look_at[None] - self.camera_pos[None]).normalized()
        fu = (2 * fov * (u + ti.random(ti.f32)) / self.image_res[1] -
              fov * self.aspect_ratio - 1e-5)
        fv = 2 * fov * (v + ti.random(ti.f32)) / self.image_res[1] - fov - 1e-5
        du = d.cross(self.up[None]).normalized()
        dv = du.cross(d).normalized()
        d = (d + fu * du + fv * dv).normalized()
        return d

    @ti.kernel
    def render(self):
        ti.loop_config(block_dim=256)
        for u, v in self.color_buffer:
            d = self.get_cast_dir(u, v)
            pos = self.camera_pos[None]
            t = 0.0

            contrib = ti.Vector([0.0, 0.0, 0.0])
            throughput = ti.Vector([1.0, 1.0, 1.0])
            c = ti.Vector([1.0, 1.0, 1.0])

            depth = 0
            hit_light = 0
            hit_background = 0

            # Tracing begin
            for bounce in range(MAX_RAY_DEPTH):
                depth += 1
                closest, normal, c, hit_light = self.next_hit(pos, d, t)
                hit_pos = pos + closest * d
                if not hit_light and normal.norm() != 0 and closest < 1e8:
                    d = out_dir(normal)
                    pos = hit_pos + 1e-4 * d
                    throughput *= c

                    if ti.static(use_directional_light):
                        dir_noise = ti.Vector([
                            ti.random() - 0.5,
                            ti.random() - 0.5,
                            ti.random() - 0.5
                        ]) * self.light_direction_noise[None]
                        light_dir = (self.light_direction[None] +
                                     dir_noise).normalized()
                        dot = light_dir.dot(normal)
                        if dot > 0:
                            hit_light_ = 0
                            dist, _, _, hit_light_ = self.next_hit(
                                pos, light_dir, t)
                            if dist > DIS_LIMIT:
                                # far enough to hit directional light
                                contrib += throughput * \
                                    self.light_color[None] * dot
                else:  # hit background or light voxel, terminate tracing
                    hit_background = 1
                    break

                # Russian roulette
                max_c = throughput.max()
                if ti.random() > max_c:
                    throughput = [0, 0, 0]
                    break
                else:
                    throughput /= max_c
            # Tracing end

            if hit_light:
                contrib += throughput * c
            else:
                if depth == 1 and hit_background:
                    # Direct hit to background
                    contrib = self.background_color[None]
            self.color_buffer[u, v] += contrib

    @ti.kernel
    def _render_to_image(self, samples: ti.i32):
        for i, j in self.color_buffer:
            u = 1.0 * i / self.image_res[0]
            v = 1.0 * j / self.image_res[1]

            darken = 1.0 - self.vignette_strength * max((ti.sqrt(
                (u - self.vignette_center[0])**2 +
                (v - self.vignette_center[1])**2) - self.vignette_radius), 0)

            for c in ti.static(range(3)):
                self._rendered_image[i, j][c] = ti.sqrt(
                    self.color_buffer[i, j][c] * darken * self.exposure /
                    samples)

    @ti.kernel
    def recompute_bbox(self):
        for d in ti.static(range(3)):
            self.bbox[0][d] = inf
            self.bbox[1][d] = -inf
        
        for i in range(self.num_particles[None]):
            pos = self.particle_pos[i]
            radius = self.particle_radius[i]
            for d_ax in ti.static(range(3)):
                ti.atomic_min(self.bbox[0][d_ax], pos[d_ax] - radius)
                ti.atomic_max(self.bbox[1][d_ax], pos[d_ax] + radius)
        
        # Ensure bbox is not inf if no particles are present
        if self.num_particles[None] == 0:
            for d_ax in ti.static(range(3)):
                self.bbox[0][d_ax] = 0.0
                self.bbox[1][d_ax] = 0.0

    def reset_framebuffer(self):
        self.current_spp = 0
        self.color_buffer.fill(0)

    def accumulate(self):
        self.render()
        self.current_spp += 1

    def fetch_image(self):
        self._render_to_image(self.current_spp)
        return self._rendered_image

    @staticmethod
    @ti.func
    def to_vec3u(c):
        c = ti.math.clamp(c, 0.0, 1.0)
        r = ti.Vector([ti.u8(0), ti.u8(0), ti.u8(0)])
        for i in ti.static(range(3)):
            r[i] = ti.cast(c[i] * 255, ti.u8)
        return r

    @staticmethod
    @ti.func
    def to_vec3(c):
        r = ti.Vector([0.0, 0.0, 0.0])
        for i in ti.static(range(3)):
            r[i] = ti.cast(c[i], ti.f32) / 255.0
        return r