import argparse
import sys
import os

from utils import convert_arg_line_to_args, load_scene
import shutil

BOOT_MSG = '''
====================================================
Welcome to the PyParticle Renderer!
====================================================
Author: Sven Pfiffner
Source: -
License: MIT License

====================================================
Controls:
* Drag with your left mouse button to rotate
* Press W/A/S/D/Q/E to move
* Press P to save a screenshot of the current view
* Press C to get the current camera position and look-at direction
====================================================
'''

def main(args):

    print(BOOT_MSG)

    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')

    if args.capture and not os.path.exists('video'):
        os.makedirs('video')

    Scene = load_scene(args.scene_name)
    scene = Scene(args)
    
    scene.initialize_particles()
    scene.finish()

    if args.capture:
        # Clean up video/frames
        if os.path.exists('video/frames'):
            shutil.rmtree('video/frames')

if __name__ == "__main__":

    # Command line argument parsing
    parser = argparse.ArgumentParser(description="Run the specified rendering scene.",
                                     fromfile_prefix_chars='@',
                                     conflict_handler='resolve')
    parser.convert_arg_line_to_args = convert_arg_line_to_args

    parser.add_argument('--scene_name', type=str, required=True,
                        help='Name of the scene to render (e.g., HelloWorld to run SceneHelloWorld).')
    parser.add_argument('--exposure', type=float, default=10.0,
                        help='Exposure level for the scene rendering.')
    parser.add_argument('--resolution', type=int, nargs=2, default=(800, 600),
                        help='Resolution of the rendering window (width height).')
    parser.add_argument('--render_device', type=str, default='cpu',
                        help='Device to use for rendering (cpu or gpu).')
    parser.add_argument('--target_fps', type=int, default=30,
                        help='Target frames per second for the rendering loop.')
    parser.add_argument('--camera_pos', type=float, nargs=3, default=(0.0, 0.0, 1.0),
                        help='Initial camera position (x y z).')
    parser.add_argument('--camera_lookat_pos', type=float, nargs=3, default=(0.0, 0.0, 0.0),
                        help='Initial camera look-at position (x y z).')
    parser.add_argument('--max_particles', type=int, default=500,
                        help='Maximum number of particles the renderer allows.')
    parser.add_argument('--capture', type=bool, default=False,
                        help='Whether to capture a video of the rendering session.')

    args = parser.parse_args()

    main(args)
    