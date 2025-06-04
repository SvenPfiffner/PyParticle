<p align="center" width="100%">
    <img width="50%" src="https://github.com/SvenPfiffner/PyParticle/blob/main/assets/pyparticle_logo.png">
</p>

[![Python 3.10.17](https://img.shields.io/badge/python-3.10.17-green.svg)](https://www.python.org/downloads/release/python-360/) [![Python 3.10.17](https://img.shields.io/badge/License-MIT-blue.svg)](https://www.python.org/downloads/release/python-360/)


ℹ️**Notice: This repository is in pre-alpha and in active development. The main functionality is usable but expect errors, bugs or unexpected behavior.**

🌠 PyParticle Renderer
======================

PyParticle is a python based particle simulation framework that allows easy experimentation with particle physics. Built with Taichi and powered by GPU-accelerated ray tracing, PyParticle is designed for students, educators, researchers, and curious minds who want to explore physical simulations without touching a graphics pipeline.

🎯 You focus on particles. PyParticle handles the pixels.

What is PyParticle?
-------------------

PyParticle is an educational rendering framework that:
- 💡 Renders particle-based simulations in real-time using path tracing
- 🎮 Lets you explore scenes interactively (mouse + WASD controlled camera)
- 🧪 Allows you to create custom simulations just by overwriting particle initialization and update logic
- 🎥 Captures screenshots and videos at the press of a button

Features
--------

- 🧱 Real-time ray-traced particle renderer
- 🔧 CPU or GPU rendering support via Taichi
- 🖱️ Interactive camera (mouse + keyboard)
- 💡 Directional lighting, floor plane, and material shading
- 📷 Screenshot + video capture
- 🎓 Clean architecture - ideal for teaching or experimentation

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

🛣️ Roadmap
-------

- [x] Raytraced rendering of spherical particles 
- [x] Modular system to overwrite particle behavior and initialization  
- [x] Simulation on GPU, CUDA, Vulkan  
- [ ] Improve particle API  
  - [ ] Define volumes filled with particles for initialization
  - [ ] Support multiple particle types per scene
  - [ ] Allow other particle shapes  
  - [ ] API to add static colliders to scene
  - [ ] Provide acceleration data structures for particle neighbor search
- [ ] Improve Rendering
    - [ ] Add more materials (Parameterizable for diffusion, scattering etc.)
    - [ ] Improve efficiency
    - [ ] Mitigate video capture overhead
    - [ ] Support for headless rendering
    - [ ] Add variable render quality options
- [ ] Testing & QA  
  - [ ] Unit tests  
  - [ ] CI Setup  
- [ ] Documentation  
  - [ ] API Reference  
  - [ ] Setup Guide  
- [ ] Deployment    
  - [ ] Deploy to PyPi

License
-------

Free and licenced under the MIT License

Acknowledgments
---------------

Built with ❤️ and Taichi.
