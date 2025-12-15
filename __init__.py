bl_info = {
    "name": "Organic Buoyancy Solver",
    "author": "Antigravity",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Hydrostatics",
    "description": "Simulates hydrostatic stability for irregular 3D bodies.",
    "warning": "",
    "wiki_url": "",
    "category": "Physics",
}

import bpy
import importlib

# Import submodules
from . import operators
from . import panels
from . import physics_engine
from . import utils

# Force reload of submodules to ensure updates are picked up without restart
importlib.reload(operators)
importlib.reload(panels)
importlib.reload(physics_engine)
importlib.reload(utils)

classes = (
    operators.OBS_OT_SolveEquilibrium,
    operators.OBS_OT_AddWaterPlane,
    panels.OBS_PT_MainPanel,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass # Already registered
    
    # Register Scene Properties
    bpy.types.Scene.obs_target_object = bpy.props.PointerProperty(type=bpy.types.Object, name="Target Island")
    bpy.types.Scene.obs_water_density = bpy.props.FloatProperty(name="Water Density", default=1025.0, description="kg/m3", min=1.0)
    bpy.types.Scene.obs_object_density = bpy.props.FloatProperty(name="Object Density", default=30.0, description="kg/m3 (e.g. EPS)", min=1.0)
    bpy.types.Scene.obs_extra_objects_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Extra Objects", description="Collection containing extra weights")

def unregister():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    
    del bpy.types.Scene.obs_target_object
    del bpy.types.Scene.obs_water_density
    del bpy.types.Scene.obs_object_density
    del bpy.types.Scene.obs_extra_objects_collection

if __name__ == "__main__":
    register()
