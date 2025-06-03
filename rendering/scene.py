import time
import os
from datetime import datetime
import numpy as np
import taichi as ti
from .renderer import Renderer
from .utils import np_normalize, np_rotate_matrix
from .camera import Camera
import __main__
from taichi.math import *

VOXEL_DX = 1 / 64
SCREEN_RES = (1280, 720)
UP_DIR = (0, 1, 0)

MAT_LAMBERTIAN = 1
MAT_LIGHT = 2

@ti.data_oriented
class Scene:
    def __init__(self, args):
        
        voxel_edges = 0.06

        if args.render_device == 'cpu':
            ti.init(arch=ti.cpu)
        elif args.render_device == 'gpu':
            ti.init(arch=ti.gpu)
        else:
            raise ValueError("Unsupported render device. Use 'cpu' or 'gpu'.")
        
        self.target_fps = args.target_fps

        self.window = ti.ui.Window("PyParticle Renderer",
                                   (args.resolution[0], args.resolution[1]),
                                   vsync=True)
        
        camera_pos = np.array(args.camera_pos, dtype=np.float32)
        camera_lookat_pos = np.array(args.camera_lookat_pos, dtype=np.float32)
        self.camera = Camera(self.window,
                             camera_pos=camera_pos,
                             lookat_pos=camera_lookat_pos,
                             up_dir=UP_DIR)
        self.renderer = Renderer(dx=VOXEL_DX,
                                 image_res=(args.resolution[0], args.resolution[1]),
                                 up=UP_DIR,
                                 voxel_edges=voxel_edges,
                                 exposure=args.exposure)

        self.renderer.set_camera_pos(*self.camera.position)
        if not os.path.exists('screenshot'):
            os.makedirs('screenshot')

    @staticmethod
    @ti.func
    def round_idx(idx_):
        idx = ti.cast(idx_, ti.f32)
        return ti.Vector(
            [ti.round(idx[0]),
             ti.round(idx[1]),
             ti.round(idx[2])]).cast(ti.i32)

    @ti.func
    def set_voxel(self, idx, mat, color):
        self.renderer.set_voxel(self.round_idx(idx), mat, color)

    @ti.func
    def get_voxel(self, idx):
        mat, color = self.renderer.get_voxel(self.round_idx(idx))
        return mat, color

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
        while self.window.running:
            should_reset_framebuffer = False

            if self.camera.update_camera():
                self.renderer.set_camera_pos(*self.camera.position)
                look_at = self.camera.look_at
                self.renderer.set_look_at(*look_at)
                should_reset_framebuffer = True

            if should_reset_framebuffer:
                self.renderer.reset_framebuffer()

            t = time.time()
            for _ in range(spp):
                self.renderer.accumulate()
            img = self.renderer.fetch_image()
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

    @ti.kernel
    def initialize_particles(self):
        raise NotImplementedError("initialize_particles should be implemented by a child class.")