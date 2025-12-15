import bpy
import bmesh
import mathutils
from mathutils import Vector

GRAVITY = 9.81

class PhysicsUtils:
    @staticmethod
    def calculate_mesh_properties(obj):
        """Calculates volume and center of mass (centroid) of a mesh object."""
        bm = bmesh.new()
        # Use dependency graph to get the evaluated mesh (modifiers applied)
        depsgraph = bpy.context.view_layer.depsgraph
        bm.from_object(obj, depsgraph)
        
        bmesh.ops.triangulate(bm, faces=bm.faces)
        
        vol = bm.calc_volume()
        
        # Calculate approximate centroid
        cog = Vector((0,0,0))
        if len(bm.verts) > 0:
            cog = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            
        bm.free()
        
        # Scale volume by object scale
        scale = obj.matrix_world.to_scale()
        vol *= (scale.x * scale.y * scale.z)
        
        # Transform local COG to world
        cog = obj.matrix_world @ cog
        
        return vol, cog

    @staticmethod
    def get_submerged_properties(bm_base, matrix):
        """
        Returns volume, centroid (COB), and water plane area (WPA) at Z=0.
        Works on a copy of the base bmesh transformed by matrix.
        """
        bm = bm_base.copy()
        bm.transform(matrix)
        
        # Bisect at Z=0
        # Result returns geometry that was cut/created
        result = bmesh.ops.bisect_plane(
            bm, 
            geom=bm.verts[:]+bm.edges[:]+bm.faces[:], 
            plane_co=Vector((0,0,0)), 
            plane_no=Vector((0,0,1)), 
            clear_outer=True, 
            clear_inner=False
        )
        
        wpa = 0.0
        
        # Calculate Water Plane Area (WPA)
        # The bisect operation leaves edges on the boundary where the cut happened.
        # We can fill these edges to form the "waterplane" faces and calculate their area.
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            try:
                ret = bmesh.ops.contextual_create(bm, geom=edges)
                if 'faces' in ret:
                    wpa = sum(f.calc_area() for f in ret['faces'])
            except:
                pass

        bmesh.ops.triangulate(bm, faces=bm.faces)
        vol = bm.calc_volume()
        
        cob = Vector((0,0,0))
        if len(bm.verts) > 0:
            cob = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
        
        bm.free()
        return vol, cob, wpa

class BuoyancySolver:
    def __init__(self, target_obj, water_density, object_density, extra_objs_collection):
        self.target_obj = target_obj
        self.water_density = water_density
        self.object_density = object_density
        self.extra_objs_collection = extra_objs_collection
        
        self.precision_force = 1.0 # Newtons
        self.precision_torque = 0.01 # Meters
        self.max_iterations = 100 

        # Heuristics for stability
        # Start with conservative damping
        self.damping_heave = 0.2 
        self.damping_rot = 0.1 
        
    def calculate_total_mass_and_cog(self):
        """Calculates the combined Mass and COG of the island + extra objects."""
        vol_base, cog_base_world = PhysicsUtils.calculate_mesh_properties(self.target_obj)
        mass_base = vol_base * self.object_density
        
        total_mass = mass_base
        total_moment = cog_base_world * mass_base
        
        if self.extra_objs_collection:
            for obj in self.extra_objs_collection.objects:
                if "mass" in obj:
                    obj_mass = obj["mass"]
                    obj_cog = obj.matrix_world.translation
                else:
                    obj_vol, obj_cog = PhysicsUtils.calculate_mesh_properties(obj)
                    obj_mass = obj_vol * 700 # Default density for extras
                
                total_mass += obj_mass
                total_moment += obj_cog * obj_mass
        
        final_cog = total_moment / total_mass if total_mass > 0 else Vector((0,0,0))
        return total_mass, final_cog

    def solve(self):
        print("Starting Hydrostatic Solver (Robust)...")
        
        total_mass, total_cog = self.calculate_total_mass_and_cog()
        weight_force = total_mass * GRAVITY
        print(f"Total Mass: {total_mass:.2f} kg, COG: {total_cog}")
        
        # Pre-capture mesh data in local space
        bm_base = bmesh.new()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = self.target_obj.evaluated_get(depsgraph)
        bm_base.from_mesh(obj_eval.data)
        
        # Initialize Decomposition
        current_matrix = self.target_obj.matrix_world.copy()
        loc, rot, scale = current_matrix.decompose()
        
        step_reducer = 1.0
        
        for i in range(getattr(self, 'max_iterations', 100)):
            # 1. Construct current transformation matrix
            mat_loc = mathutils.Matrix.Translation(loc)
            mat_rot = rot.to_matrix().to_4x4()
            mat_scale = mathutils.Matrix.Scale(scale.x, 4, (1,0,0)) @ \
                        mathutils.Matrix.Scale(scale.y, 4, (0,1,0)) @ \
                        mathutils.Matrix.Scale(scale.z, 4, (0,0,1))
            
            current_matrix = mat_loc @ mat_rot @ mat_scale
            
            # 2. Physics Calculation (in memory)
            submerged_vol, cob, wpa = PhysicsUtils.get_submerged_properties(bm_base, current_matrix)
            buoyancy_force = submerged_vol * self.water_density * GRAVITY
            
            # 3. Forces & Moments
            net_force_z = buoyancy_force - weight_force
            
            # Transform COG to current location to check alignment
            # (Assuming Rigid Body: global COG moves with the body)
            # Local COG is constant. Global COG = Current_Matrix * Local_COG_Inverse
            mat_inv_init = self.target_obj.matrix_world.inverted()
            cog_local = mat_inv_init @ total_cog
            current_cog = current_matrix @ cog_local
            
            dx = current_cog.x - cob.x
            dy = current_cog.y - cob.y
            
            # Adaptive dampening
            if i > 50: step_reducer = 0.5
            if i > 80: step_reducer = 0.2
            
            # Check Convergence
            if abs(net_force_z) < self.precision_force and abs(dx) < self.precision_torque and abs(dy) < self.precision_torque:
                print(f"Converged in {i} iterations.")
                break
            
            # 4. Apply Corrections
            
            # Heave (Stiffness based on Water Plane Area)
            k_stiffness_heave = self.water_density * GRAVITY * wpa
            if k_stiffness_heave < 1.0: 
                # Fallback if WPA is near zero (e.g. fully submerged or in air)
                if submerged_vol > 0:
                    k_stiffness_heave = self.water_density * GRAVITY * (submerged_vol**(2/3))
                else:
                    k_stiffness_heave = 100.0
            
            dz = net_force_z / k_stiffness_heave
            dz = max(min(dz, 1.0), -1.0) # Clamp step
            
            loc.z += dz * self.damping_heave * step_reducer
            
            # Rotation (Simple proportional control for aligning centers)
            # COG needs to be above COB? 
            # Stable equilibrium: COB is vertically aligned with COG.
            # If COG is X+, COB is X-, we tilt to sink X+ side. 
            # Sink X+ => Rotate +Y (around Y axis).
            # Torque ~ Force * MomentArm.
            # Rot = Error * Gain
            
            rot_y = dx * self.damping_rot * step_reducer
            rot_x = -dy * self.damping_rot * step_reducer
            
            # Clamp rotation step
            max_rot = 0.05 # radians
            rot_y = max(min(rot_y, max_rot), -max_rot)
            rot_x = max(min(rot_x, max_rot), -max_rot)

            q_rot = mathutils.Euler((rot_x, rot_y, 0), 'XYZ').to_quaternion()
            rot = q_rot @ rot 
            
            if i % 10 == 0:
                print(f"Iter {i}: F_net={net_force_z:.1f}N, dXY=({dx:.3f}, {dy:.3f}), WPA={wpa:.2f}")

        bm_base.free()
        
        # Apply Final Transform
        self.target_obj.location = loc
        if self.target_obj.rotation_mode == 'QUATERNION':
            self.target_obj.rotation_quaternion = rot
        else:
            self.target_obj.rotation_euler = rot.to_euler(self.target_obj.rotation_mode)
        
        bpy.context.view_layer.update()
        
        if i == self.max_iterations - 1:
            print("Warning: Solver did not fully converge.")
