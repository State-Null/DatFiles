import bpy
import bmesh
import math
import os
import sys
from PIL import Image, ImageDraw
from mathutils import Vector, Matrix

"""
Galka Cockpit Module Attacher
Attaches the 3D Cockpit Module & Tarutaru Pilot to ANY FFXI Galka Body Mesh.
Strictly Direct3D 8 compliant (<= 2 bones per vertex, normalized).
"""

def attach_cockpit(body_glb_path, body_tex_path, cockpit_glb_path, cockpit_atlas_path, out_glb_path, out_atlas_path, is_white_shirt=False, kebab_logo_path=None):
    print(f"\n=======================================================")
    print(f" Attaching Cockpit Module to: {os.path.basename(body_glb_path)}")
    print(f"=======================================================\n")
    
    # 1. BUILD MERGED 256x256 TEXTURE ATLAS
    # Left Half  (U: 0.0..0.5) -> Galka Body Texture
    # Right Half (U: 0.5..1.0) -> Cockpit & Pilot Texture Atlas
    body_img = Image.open(body_tex_path).convert("RGBA")
    
    if is_white_shirt:
        # Recolor/brighten body to white cotton
        w_body = Image.new("RGBA", (128, 256), (245, 245, 248, 255))
        draw_b = ImageDraw.Draw(w_body)
        # Black choker collar at neck (X: 15..110, Y: 0..16)
        draw_b.rectangle([15, 0, 112, 16], fill=(28, 28, 32))
        draw_b.ellipse([60, 4, 68, 12], fill=(255, 215, 30), outline=(160, 110, 0))
        # Paste kebab logo above the cockpit (X: 38..92, Y: 46..112)
        if kebab_logo_path and os.path.exists(kebab_logo_path):
            k_img = Image.open(kebab_logo_path).convert("RGBA")
            k_resized = k_img.resize((52, 68), Image.Resampling.LANCZOS)
            w_body.paste(k_resized, (38, 46), k_resized if "A" in k_resized.getbands() else None)
        body_half = w_body
    else:
        body_half = body_img.resize((128, 256), Image.Resampling.LANCZOS)
        
    cockpit_img = Image.open(cockpit_atlas_path).convert("RGBA")
    cockpit_half = cockpit_img.resize((128, 256), Image.Resampling.LANCZOS)
    
    master_atlas = Image.new("RGBA", (256, 256), (0, 0, 0, 255))
    master_atlas.paste(body_half, (0, 0))
    master_atlas.paste(cockpit_half, (128, 0))
    master_atlas.save(out_atlas_path)
    print(f"[1] Built combined texture atlas: {out_atlas_path} (256x256)")
    
    # 2. BLENDER GEOMETRY MERGE
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import Galka Body
    bpy.ops.import_scene.gltf(filepath=body_glb_path)
    galka_arm = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
    galka_mesh = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
    print(f"[2] Imported Galka Body: {galka_mesh.name} ({len(galka_mesh.data.vertices)} verts)")
    
    # Remap Galka Body UVs to left half (u = u * 0.5)
    for uv_loop in galka_mesh.data.uv_layers.active.data:
        uv_loop.uv.x = uv_loop.uv.x * 0.5
        
    # Chest center in Galka World Space:
    cx_w, cy_w, cz_w = 0.293, 0.0, 1.602
    
    # Cut precise circular hole using Boolean Cylinder (radius 0.120)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.120,
        depth=0.5,
        vertices=32,
        location=(cx_w, cy_w, cz_w),
        rotation=(0, math.radians(90), 0)
    )
    cutter = bpy.context.active_object
    
    mod = galka_mesh.modifiers.new(name='Cutter', type='BOOLEAN')
    mod.object = cutter
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    
    bpy.context.view_layer.objects.active = galka_mesh
    bpy.ops.object.modifier_apply(modifier='Cutter')
    bpy.data.objects.remove(cutter, do_unlink=True)
    print(f"[3] Excised circular cockpit aperture (r=0.120m) with Boolean Difference")
    
    # Import Standalone Cockpit Module
    bpy.ops.import_scene.gltf(filepath=cockpit_glb_path)
    mod_mesh = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o != galka_mesh and o.name != 'Icosphere'][0]
    
    # Unparent and clean imported module
    for v in mod_mesh.data.vertices:
        v.co = mod_mesh.matrix_world @ v.co
    mod_mesh.parent = None
    mod_mesh.matrix_world = Matrix.Identity(4)
    mod_mesh.modifiers.clear()
    
    for o in list(bpy.context.scene.objects):
        if o.type == 'EMPTY' or (o.type == 'ARMATURE' and o != galka_arm) or o.name == 'Icosphere':
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Remap Cockpit Module UVs to right half (u = 0.5 + u * 0.5)
    for uv_loop in mod_mesh.data.uv_layers.active.data:
        uv_loop.uv.x = 0.5 + uv_loop.uv.x * 0.5
        
    # Transform Cockpit Module into Galka Mesh local coordinate space
    inv_mat = galka_mesh.matrix_world.inverted()
    mod_mesh.data.transform(inv_mat)
    mod_mesh.matrix_world = galka_mesh.matrix_world
    
    # Ensure vertex groups exist on both meshes
    vg38 = mod_mesh.vertex_groups.get("bone0038") or mod_mesh.vertex_groups.new(name="bone0038")
    vg37 = mod_mesh.vertex_groups.get("bone0037") or mod_mesh.vertex_groups.new(name="bone0037")
    vg38.add(range(len(mod_mesh.data.vertices)), 0.85, 'REPLACE')
    vg37.add(range(len(mod_mesh.data.vertices)), 0.15, 'REPLACE')
    
    for vg in galka_mesh.vertex_groups:
        if vg.name not in mod_mesh.vertex_groups:
            mod_mesh.vertex_groups.new(name=vg.name)
            
    # Join into Galka mesh
    mat = galka_mesh.data.materials[0] if galka_mesh.data.materials else None
    if mat:
        mod_mesh.data.materials.clear()
        mod_mesh.data.materials.append(mat)
        if mat.use_nodes:
            tex_node = mat.node_tree.nodes.get('Image Texture')
            if tex_node:
                new_img = bpy.data.images.load(out_atlas_path, check_existing=False)
                tex_node.image = new_img
                
    bpy.ops.object.select_all(action='DESELECT')
    mod_mesh.select_set(True)
    galka_mesh.select_set(True)
    bpy.context.view_layer.objects.active = galka_mesh
    bpy.ops.object.join()
    
    # 3. DIRECT3D 8 RIGGING CEILING ENFORCEMENT (<= 2 BONES)
    bpy.ops.object.vertex_group_limit_total(limit=2)
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.005)
    bpy.ops.object.vertex_group_normalize_all()
    print(f"[4] Enforced D3D8 <= 2 bones ceiling & 100% normalization")
    
    # 4. EXPORT FINAL GLB
    bpy.ops.object.select_all(action='DESELECT')
    galka_mesh.select_set(True)
    galka_arm.select_set(True)
    bpy.context.view_layer.objects.active = galka_arm
    
    bpy.ops.export_scene.gltf(
        filepath=out_glb_path,
        use_selection=True,
        export_format='GLB',
        export_skins=True,
        export_all_influences=False,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"[5] Exported complete merged Galka Mech GLB: {out_glb_path} ({len(galka_mesh.data.vertices)} vertices)")
    print(f"\nSUCCESS! Ready for 'xi gear import' and 'xi tex import'!\n")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for CLI arguments after '--'
    args = []
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        args = sys.argv[1:]
        
    c_glb = os.path.join(script_dir, "galka_cockpit_module.glb")
    c_atlas = os.path.join(script_dir, "tim_gal_cockpit_atlas.png")
    
    if len(args) >= 2:
        b_glb = os.path.abspath(args[0])
        b_tex = os.path.abspath(args[1])
        base_name = os.path.splitext(os.path.basename(b_glb))[0]
        o_glb = args[2] if len(args) > 2 else os.path.join(script_dir, f"{base_name}_with_cockpit.glb")
        o_atlas = args[3] if len(args) > 3 else os.path.join(script_dir, f"{base_name}_atlas.png")
        attach_cockpit(b_glb, b_tex, c_glb, c_atlas, o_glb, o_atlas)
    else:
        print("\n=======================================================")
        print(" Galka Cockpit Module Attacher - Usage Instructions")
        print("=======================================================")
        print("Run via Blender command line:")
        print("  blender --background --python attach_cockpit_to_galka_body.py -- <body.glb> <body_texture.png> [out.glb] [out_atlas.png]")
        print("\nExample:")
        print("  blender -b -P attach_cockpit_to_galka_body.py -- 58.glb tim_gl_bp18m.png\n")
