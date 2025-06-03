<p align="center" width="100%">
    <img width="33%" src="https://github.com/SvenPfiffner/PyParticle/blob/main/pyparticle_logo.png">
</p>

[![Python 3.10.17](https://img.shields.io/badge/python-3.10.17-green.svg)](https://www.python.org/downloads/release/python-360/) [![Python 3.10.17](https://img.shields.io/badge/License-MIT-blue.svg)](https://www.python.org/downloads/release/python-360/)


🌠 PyParticle Renderer
======================

PyParticle is python based particle simulation framework that allows easy experimentation with particle physics. Built with Taichi and powered by GPU-accelerated ray tracing, PyParticle is designed for students, educators, researchers, and curious minds who want to explore physical simulations without touching a graphics pipeline.

🎯 You focus on particles. PyParticle handles the pixels.

What is PyParticle?
-------------------

PyParticle is an educational rendering framework that:
- 💡 Renders particle-based simulations in real-time using path tracing
- 🎮 Lets you explore scenes interactively (mouse + WASD camera)
- 🧪 Allows you to create custom simulations just by overwriting particle initialization and update logic
- 🎥 Captures screenshots and videos at the press of a button

All you need to do is subclass the Scene class and define:
- How your particles should be initialized
- How their properties should change with time

Features
--------

- 🧱 Real-time ray-traced particle renderer
- 🔧 CPU or GPU rendering support via Taichi
- 🖱️ Interactive camera (mouse + keyboard)
- 💡 Directional lighting, floor plane, and material shading
- 📷 Screenshot + video capture
- 🎓 Clean architecture ideal for teaching or experimentation

Getting Started
---------------

### Prerequisites
Install Taichi and NumPy:

    pip install taichi numpy

### Run the Example Scene

    python main.py --scene_name HelloWorld

This runs SceneHelloWorld, which drops a grid of red particles into a simulated gravity field with floor collisions.

Create Your Own Scene
---------------------

Define a new class in scene_youridea.py like this:

```python
from rendering.scene import Scene

class SceneYourIdea(Scene):
def initialize_particles(self):
  # Initialize particles however you like
  pass

  def update_particles(self, dt):
    # Animate or simulate particles here
    pass
```

Then run it with:

    python main.py --scene_name YourIdea

Controls
--------

| Action           | Key/Mouse        |
|------------------|------------------|
| Rotate camera    | Left mouse drag  |
| Move camera      | W / A / S / D / Q / E |
| Save screenshot  | P                |

Folder Structure
----------------

    ├── main.py              # Entry point
    ├── renderer.py          # Rendering engine (ray tracer)
    ├── camera.py            # Interactive camera logic
    ├── scene.py             # Abstract Scene class
    ├── scene_helloworld.py  # Sample implementation
    ├── renderutils.py       # Math & ray helpers
    └── utils/               # Utility functions

Why PyParticle?
---------------

- No need to write rendering code
- Learn by doing — focus on physics, not pixels
- Make your first graphics project without OpenGL/Vulkan headaches
- Ideal for computer graphics or simulation coursework

License
-------

MIT License — free for education, experimentation, and even mischief.

Acknowledgments
---------------

Built with ❤️ and Taichi.
