import bpy

class OBS_PT_MainPanel(bpy.types.Panel):
    """Creates a Panel in the View3D UI"""
    bl_label = "Organic Buoyancy"
    bl_idname = "OBS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hydrostatics"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "obs_target_object")
        
        box = layout.box()
        box.label(text="Physical Properties")
        box.prop(scene, "obs_water_density")
        box.prop(scene, "obs_object_density")
        
        layout.separator()
        layout.prop(scene, "obs_extra_objects_collection")
        
        layout.separator()
        layout.operator("obs.add_water_plane", text="Add Water Plane")
        
        layout.separator()
        row = layout.row()
        row.scale_y = 2.0
        row.operator("obs.solve_equilibrium", text="Calculate Equilibrium")
