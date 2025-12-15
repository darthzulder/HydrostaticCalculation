import bpy
from . import physics_engine
from . import utils

class OBS_OT_SolveEquilibrium(bpy.types.Operator):
    """Calculate and apply hydrostatic equilibrium"""
    bl_idname = "obs.solve_equilibrium"
    bl_label = "Calculate Equilibrium"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target = context.scene.obs_target_object
        water_dens = context.scene.obs_water_density
        obj_dens = context.scene.obs_object_density
        extra_col = context.scene.obs_extra_objects_collection
        
        if not target:
            self.report({'ERROR'}, "No Target Object selected")
            return {'CANCELLED'}
        
        solver = physics_engine.BuoyancySolver(target, water_dens, obj_dens, extra_col)
        solver.solve()
        
        return {'FINISHED'}

class OBS_OT_AddWaterPlane(bpy.types.Operator):
    """Add a visual representation of the water plane"""
    bl_idname = "obs.add_water_plane"
    bl_label = "Add Water Plane"
    
    def execute(self, context):
        utils.create_water_plane()
        return {'FINISHED'}
