import importlib

def convert_arg_line_to_args(arg_line):
    """Convert a line from a file to a list of arguments."""
    for arg in arg_line.split():
        if not arg.strip():
            continue
        yield str(arg)

def load_scene(scene_name):
    """
    Dynamically import and return a scene class based on the provided name

    Assumes the class is named Scene<scene_name> and is located in scenes/scene_<scene_name>.
    """

    try:
        module_name = f'scenes.scene_{scene_name.lower()}'
        class_name = f'Scene{scene_name}'

        module = importlib.import_module(module_name)
        scene_class = getattr(module, class_name)
        return scene_class
    
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load scene '{scene_name}': {e}")