import time
import os
from datetime import datetime
import numpy as np
import taichi as ti
from .renderer import Renderer
from .camera import Camera
import __main__
from taichi.math import *


UP_DIR = (0, 1, 0)


@ti.data_oriented
class Scene:
    def __init__(self, args):
        

        if args.render_device == 'cpu':
            ti.init(arch=ti.cpu)
        elif args.render_device == 'gpu':
            ti.init(arch=ti.gpu)
        else:
            raise ValueError("Unsupported render device. Use 'cpu' or 'gpu'.")
        
        self.target_fps = args.target_fps
        self.resolution = (args.resolution[0], args.resolution[1])
        self.capture_video = args.capture

        self.window = ti.ui.Window("PyParticle Renderer",
                                   self.resolution,
                                   vsync=True)
        
        camera_pos = np.array(args.camera_pos, dtype=np.float32)
        camera_lookat_pos = np.array(args.camera_lookat_pos, dtype=np.float32)
        self.camera = Camera(self.window,
                             camera_pos=camera_pos,
                             lookat_pos=camera_lookat_pos,
                             up_dir=UP_DIR)
        self.renderer = Renderer(image_res=self.resolution,
                                 up=UP_DIR,
                                 exposure=args.exposure,
                                 max_particles=args.max_particles)

        self.renderer.set_camera_pos(*self.camera.position)


    @ti.func
    def add_particle(self, position, material, color, radius, velocity=vec3(0.0, 0.0, 0.0)):
        self.renderer.add_particle(position, color, material, radius, velocity)

    def set_floor(self, height, color):
        self.renderer.floor_height[None] = height
        self.renderer.floor_color[None] = color

    def set_directional_light(self, direction, direction_noise, color):
        self.renderer.set_directional_light(direction, direction_noise, color)

    def set_background_color(self, color):
        self.renderer.background_color[None] = color

    def finish(self):
        self.renderer.recompute_bbox()
        canvas = self.window.get_canvas()
        spp = 1

        if self.capture_video:
            video_manager = ti.tools.VideoManager(
                output_dir='video',
                width=self.resolution[0],
                height=self.resolution[1],
                framerate=self.target_fps,
                automatic_build=False
            )

        while self.window.running:
            
            dt = 1.0 / self.target_fps

            should_reset_framebuffer = False

            if self.camera.update_camera():
                self.renderer.set_camera_pos(*self.camera.position)
                look_at = self.camera.look_at
                self.renderer.set_look_at(*look_at)
                should_reset_framebuffer = True

            if self.renderer.num_particles[None] > 0:
                self.update_particles(dt)
                self.renderer.recompute_bbox()
                should_reset_framebuffer = True

            if should_reset_framebuffer:
                self.renderer.reset_framebuffer()

            t = time.time()
            for _ in range(spp):
                self.renderer.accumulate()

            img = self.renderer.fetch_image()

            if self.capture_video:
                video_manager.write_frame(img)

            if self.window.is_pressed('c'):
                camera_pos = self.camera.position
                look_at = self.camera.look_at
                print(f"Camera Position: {camera_pos}, Look At: {look_at}")

            if self.window.is_pressed('p'):
                timestamp = datetime.today().strftime('%Y-%m-%d-%H%M%S')
                dirpath = os.getcwd()
                main_filename = os.path.split(__main__.__file__)[1]
                fname = os.path.join(dirpath, 'screenshot', f"{main_filename}-{timestamp}.jpg")
                ti.tools.image.imwrite(img, fname)
                print(f"Screenshot has been saved to {fname}")
            canvas.set_image(img)
            elapsed_time = time.time() - t
            if elapsed_time * self.target_fps > 1:
                spp = int(spp / (elapsed_time * self.target_fps) - 1)
                spp = max(spp, 1)
            else:
                spp += 1
            self.window.show()

        if self.capture_video:
            video_manager.make_video(gif=True, mp4=True)
            print(f"Video has been saved")

    @ti.kernel
    def initialize_particles(self):
        """
        Initialize the particles in the scene.
        This method should be implemented by child classes to define how particles are initialized.
        """
        raise NotImplementedError("initialize_particles should be implemented by a child class.")
    
    @ti.kernel
    def update_particles(self, dt: ti.f32):
        """
        Update the particles in the scene.
        This method should be implemented by child classes to define how particles are updated.
        """
        raise NotImplementedError("update_particles should be implemented by a child class.")