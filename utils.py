import bpy

def create_water_plane():
    """Creates a large blue transparent plane at Z=0 to represent water."""
    
    # Check if exists
    name = "Water_Plane"
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        # Ensure it's visible and at Z=0
        obj.location.z = 0
        obj.hide_viewport = False
        return obj

    # Create Plane
    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    
    # Create Material
    mat_name = "Water_Material"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default
        nodes.clear()
        
        # Shader
        shader = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader.location = (0,0)
        shader.inputs['Base Color'].default_value = (0.0, 0.4, 0.8, 1.0) # Blue
        shader.inputs['Alpha'].default_value = 0.5
        shader.inputs['Roughness'].default_value = 0.1
        shader.inputs['Transmission Weight'].default_value = 0.8 # Glass-like
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300,0)
        
        links.new(shader.outputs['BSDF'], output.inputs['Surface'])
        
        # Settings for transparency in Viewport (Eevee/Workbench)
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE' # Water doesn't cast dark shadows usually in simple viz
    
    # Assign Material
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    # Lock transform
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    
    return obj
