from .utils import np_normalize, np_rotate_matrix

import taichi as ti
import numpy as np

class Camera:

    def __init__(self, window, camera_pos, lookat_pos, up_dir):
        self._window = window
        self._camera_pos = camera_pos
        self._lookat_pos = lookat_pos
        self._up = np_normalize(np.array(up_dir))
        self._last_mouse_pos = None

    @property
    def mouse_exclusive_owner(self):
        return True
    
    def update_camera(self):
        res = self._update_by_wasd()
        res = self._update_by_mouse() or res
        return res
    
    def _update_by_wasd(self):
        win = self._window
        tgtdir = self.target_dir
        leftdir = self._compute_left_dir(tgtdir)
        lut = [
            ('w', tgtdir),
            ('a', leftdir),
            ('s', -tgtdir),
            ('d', -leftdir),
            ('e', [0, -1, 0]),
            ('q', [0, 1, 0]),
        ]

        dir = np.array([0.0, 0.0, 0.0])
        pressed = False
        for key, d in lut:
            if win.is_pressed(key):
                pressed = True
                dir += np.array(d)

        if not pressed:
            return False
        
        dir *= 0.05
        self._lookat_pos += dir
        self._camera_pos += dir
        return True
    
    def _update_by_mouse(self):
        win = self._window
        if not self.mouse_exclusive_owner or not win.is_pressed(ti.ui.LMB):
            self._last_mouse_pos = None
            return False
        mouse_pos = np.array(win.get_cursor_pos())
        if self._last_mouse_pos is None:
            self._last_mouse_pos = mouse_pos
            return False
        # Makes camera rotation feels right
        dx, dy = self._last_mouse_pos - mouse_pos
        self._last_mouse_pos = mouse_pos

        out_dir = self._lookat_pos - self._camera_pos
        leftdir = self._compute_left_dir(np_normalize(out_dir))

        scale = 3
        rotx = np_rotate_matrix(self._up, dx * scale)
        roty = np_rotate_matrix(leftdir, dy * scale)

        out_dir_homo = np.array(list(out_dir) + [0.0])
        new_out_dir = np.matmul(np.matmul(roty, rotx), out_dir_homo)[:3]
        self._lookat_pos = self._camera_pos + new_out_dir

        return True
    
    @property
    def position(self):
        return self._camera_pos
    
    @property
    def look_at(self):
        return self._lookat_pos
    
    @property
    def target_dir(self):
        return np_normalize(self.look_at - self.position)
    
    def _compute_left_dir(self, tgtdir):
        cos = np.dot(self._up, tgtdir)
        if abs(cos) > 0.999:
            return np.array([-1.0, 0.0, 0.0])
        return np.cross(self._up, tgtdir)