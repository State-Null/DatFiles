# 🥋 Cross-Engine & Topological FFXI Equipment Modding Guide
**Authoritative Architectural Runbook for Foreign Mesh Porting, Skeletal Weighting, and Texture Ingestion in Final Fantasy XI.**

---

## Table of Contents
1. [The 4 Fundamental Laws of FFXI Equipment Porting](#1-the-4-fundamental-laws-of-ffxi-equipment-porting)
2. [Topological Island Partitioning vs. Procedural Bisection](#2-topological-island-partitioning-vs-procedural-bisection)
3. [The 5-Joint Leg & Foot Kinematics Architecture](#3-the-5-joint-leg--foot-kinematics-architecture)
4. [Waist Interface Clearance & The Moving Belt Artifact](#4-waist-interface-clearance--the-moving-belt-artifact)
5. [Racial Anatomy & Neck Seam Alignment](#5-racial-anatomy--neck-seam-alignment)
6. [Cross-Engine Texture Ingestion Traps (FFXIV vs. FFXI Direct3D 8)](#6-cross-engine-texture-ingestion-traps-ffxiv-vs-ffxi-direct3d-8)
7. [Comprehensive Pre-Flight Verification Checklist](#7-comprehensive-pre-flight-verification-checklist)

---

## 1. The 4 Fundamental Laws of FFXI Equipment Porting

When adapting 3D models from modern games (FFXIV, Genshin Impact, Dragon Ball, Dark Souls) into Final Fantasy XI, four immutable constraints govern the pipeline:

1. **Hardware Bone Skinning Limit**: Strictly $\le 2$ joints per vertex ($w_1 + w_2 = 1.000$). Modern models have 4, 8, or unlimited bone influences per vertex. Every vertex must be pruned and normalized to exactly 2 influences.
2. **Fixed-Function Direct3D 8 Shading**: FFXI has **no programmable pixel shaders and no PBR engine**. There are no metallic, roughness, or normal maps in the game client. All visual depth, occlusion, and fabric sheen must be baked directly into a single diffuse texture.
3. **Engine Submesh Occlusion Layers**: Submesh tags (`hf_b`, `hh_b`, `hh_l`, `hl_l`) are **dynamic occlusion zones**, not anatomical bone fences. `hf_b` can contain upper arms, clavicles, and neck, while `hh_l` can contain pelvis and thighs.
4. **Mannequin-First Conforming**: Foreign clothing must be conformed organically over authentic race mannequins (`ROM/335/6.DAT` for Elvaan Male) rather than deformed with procedural mathematical angle formulas.

---

## 2. Topological Island Partitioning vs. Procedural Bisection

### The Disaster of Planar Coordinate Slicing
In early modding attempts, clothing was often divided between equipment slots (e.g., Body vs. Legs) by slicing the mesh along an arbitrary horizontal coordinate plane (e.g., `Z = -1.157m`).

```
[PLANAR BISECTION FAILURE]
   Top Half (Body 579) --->  [  Upper Butt Cheeks  ]  <--- Weighted to joint-3 (Waist)
============================= HORIZONTAL CUT PLANE =================================
   Bottom Half (Legs 579) -> [  Lower Butt Cheeks  ]  <--- Weighted to joint-11/5 (Thighs)
```

**Why this breaks in-game:**
- Slicing through continuous geometric manifolds (like buttocks, groin, sleeves, or sashes) splits adjacent triangles onto different submeshes.
- The top half gets weighted to the spine/waist (`joint-3`), while the bottom half gets weighted to the thighs (`joint-11` / `joint-5`).
- When the character moves or engages in combat, the lower butt triangles swing outward with the leg bones, creating massive **flaring "butt wings"** and opening wide hollow gaps into the torso.

### The Topological Island Partitioning Rule
Never cut through a continuous clothing manifold. Instead, treat the mesh as a collection of independent connected-component **topological islands**:

```python
# Topological Island Traversal
unvisited = set(bm.faces)
islands = []
while unvisited:
    seed = unvisited.pop()
    island = [seed]
    queue = [seed]
    while queue:
        curr = queue.pop(0)
        for edge in curr.edges:
            for linked_face in edge.link_faces:
                if linked_face in unvisited:
                    unvisited.remove(linked_face)
                    island.append(linked_face)
                    queue.append(linked_face)
    islands.append(island)
```

- **Keep the pelvis and buttocks 100% whole in `Legs 579`**: The entire buttocks island (from waistband down through the crotch and thighs) must remain an unbroken single piece.
- **Bridge the equipment gap with an internal tucked waistband**: Rather than cutting the mesh at the belt line, extrude the top boundary loop of the pants upward by $+32\,\text{mm}$ *inside* the body's blue sash, locking its vertex weights 100% to `joint-3` (Waist).

---

## 3. The 5-Joint Leg & Foot Kinematics Architecture

FFXI's character skeleton uses 5 distinct joints per leg, running from hip to toe:

| Joint Name (Left / Right) | Anatomical Region | Coordinate Span (Elvaan Male) | Modding Function |
|---|---|---|---|
| **`joint-11` / `joint-5`** | Thigh | $Z \in [-1.126, -0.649]\,\text{m}$ | Upper pants, hips, groin flex. |
| **`joint-12` / `joint-6`** | Knee Joint Center | $Z \in [-0.649, -0.578]\,\text{m}$ | Knee hinge pivot. |
| **`joint-13` / `joint-7`** | **Shin / Calf** | $Z \in [-0.578, -0.107]\,\text{m}$ | **Lower pants & upper boot shaft!** |
| **`joint-14` / `joint-8`** | Ankle / Heel / Mid-Foot | $Z \in [-0.107, -0.032]\,\text{m}$ | Ankle flex, heel, and arch. |
| **`joint-15` / `joint-9`** | Toe / Ball of Foot | $X \ge 0.05\,\text{m}$ | Metatarsal flex & toe dorsiflexion. |

### The Two Traps That Break the `/heal` Kneeling Animation

#### Trap 1: The Missing Shin Bone
- **What goes wrong**: In many custom presets, vertex groups for the lower leg are mapped directly from Knee to Ankle, skipping the Shin bone (`joint-13` / `joint-7`).
- **The symptom**: When kneeling (`/heal`), the knee bends $95^\circ$. Because the boot shaft is weighted to the knee joint rather than the shin, the upper half of the boot rotates upward with the knee while the foot ankle stays on the floor, ripping the boot shaft open.
- **The rule**: The entire upper boot shaft ($Z \le -0.22\,\text{m}$) and the lower baggy pants cuffs ($Z \in [-0.58, -0.306]\,\text{m}$) **must be weighted to the Shin (`joint-13`/`joint-7`)**, never to the Knee!

#### Trap 2: Rigid 100% Toe Assignment (The Severed Toe Cap)
- **What goes wrong**: Assigning vertices at $X \le 0.15\,\text{m}$ rigidly to Ankle (`joint-14`) and vertices at $X > 0.15\,\text{m}$ rigidly to Toe (`joint-15`) with zero transition.
- **The symptom**: When kneeling, the character's toes dorsiflex upward by $75^\circ$ flat against the floor. Without weight blending, the front toe cap severs completely across the unblended edge loop and floats detached in midair.
- **The rule**: Apply a **Smoothstep Hermite curve** across the ball of the foot ($0.05 < X < 0.15\,\text{m}$):
  $$\begin{aligned}
  t &= \frac{X - 0.05}{0.15 - 0.05} \\
  t_s &= t^2 (3 - 2t) \\
  w_{\text{toe}} &= t_s, \quad w_{\text{ankle}} = 1.0 - t_s
  \end{aligned}$$
  This allows the rubber/leather sole to curve naturally like real flexible footwear without tearing.

---

## 4. Waist Interface Clearance & The Moving Belt Artifact

### Why Does an Orange Patch Appear on the Belt When Walking?

```
[CO-PLANAR Z-FIGHTING AT THE WAIST]
   Body 579 Blue Sash:       Radius = 0.1242m  (Ends at Z = -1.3348m)
   Legs 579 Waistband:       Radius = 0.1242m  (Extrudes up to Z = -1.3628m)
   Radial Clearance:         0.00mm (PERFECTLY CO-PLANAR!)
```

1. **Shared Spatial Coordinates**: If the bottom boundary loop of the torso sash and the top boundary loop of the pants share the exact same spatial vertices, they are co-planar ($0.00\,\text{mm}$ clearance).
2. **Contrasting Waistband Texture**: If the internal bridge waistband is textured orange (matching the pants) rather than blue (matching the belt), an orange cylinder is placed directly inside the blue belt.
3. **Walking Spine Sway**: As the player walks, the hips and lower spine sway side-to-side. Because the two surfaces are co-planar, Direct3D 8's 16/24-bit depth buffer suffers **Z-fighting**. On alternating frames, the orange quad on the swaying side pops in front of the blue belt, appearing as a moving orange rectangle sliding across the belt!

### The 3-Rule Waist Interface Protocol

1. **Flared Outer Sash Overlap (`Body 579`)**:
   Expand the blue sash bottom boundary loop outward by $+1.5\%$ ($1.015 \times R$) and extend it downward by $+4\,\text{mm}$ to $+8\,\text{mm}$. It forms a physical outer lip that wraps *over* the pants.
2. **Tucked Inner Waistband (`Legs 579`)**:
   Tuck the top boundary loop of the pants inward by $-3.0\%$ ($0.970 \times R$) and extrude the waistband upward by $+32\,\text{mm}$ into the belt interior at $-3.5\%$ ($0.965 \times R$). This guarantees a **$6.5\,\text{mm}$ radial safety air-gap** between the sash and the pants.
3. **Waistband Color Synchronization**:
   **Always texture internal bridge geometry with the color of the OUTER covering piece.** Texture the pants waistband in **Royal Blue** (`UV = (0.950, 0.640)`). Even during extreme skeletal twisting, any exposed waistband is solid blue matching the belt!

---

## 5. Racial Anatomy & Neck Seam Alignment

### Matching Authentic Race Collar Lines
Every FFXI player race and gender has unique head and neck collar heights. For Elvaan Male (Face 10 / Model 404):
- **Throat (Front)**: $Z = -1.8980\,\text{m}$
- **Nape (Rear Hair Seam)**: $Z = -1.8880\,\text{m}$
- **Seam Neck Circumference**: $R \approx 0.060\,\text{m} \pm 0.008\,\text{m}$

If a custom body mesh stops at $Z = -1.8650\,\text{m}$, it leaves a $20\,\text{mm}$ dark gap beneath the rear hair tips. The parametric neck rim must be elevated at the rear nape to slide cleanly under the hair geometry.

### Specular Compression for Direct3D 8 Fixed-Function Shading
- Anime models (and modern PBR exports) often have raw texture highlights with RGB values reaching $245-255$ on chest muscles and deltoids.
- In modern game engines, these are modulated by PBR roughness and tone mappers.
- In FFXI's fixed-function engine, daytime Vana'diel sunlight multiplies directly against the diffuse texture:
  $$C_{\text{final}} = C_{\text{texture}} \times (I_{\text{ambient}} + I_{\text{sun}} \cdot \max(0, \vec{N} \cdot \vec{L}))$$
  Uncompressed bright anime highlights blow out into blinding white or pale peach patches.
- **The Compression Rule**: Clamp relative diffuse shading on skin:
  ```python
  rel_shade = np.clip(skin_lum / max(skin_median_lum, 1.0), 0.78, 1.18)
  rel_shade = np.where(is_chest_uv, np.clip(rel_shade, 0.80, 1.04), rel_shade)
  ```
  This preserves muscle definition without blowing out in sunlight.

---

## 6. Cross-Engine Texture Ingestion Traps (FFXIV vs. FFXI Direct3D 8)

Importing assets from modern engines like **Final Fantasy XIV (Dawntrail/Endwalker)** into FFXI is a minefield of format and architectural mismatches:

```
+---------------------------------------------------------------------------------------------------+
| COMPARISON: FFXIV (DirectX 11/12 PBR) vs. FFXI (DirectX 8.1 Fixed-Function)                      |
|                                                                                                   |
| Feature                  FFXIV Engine                       FFXI Client                           |
| :----------------------- | :------------------------------- | :---------------------------------- |
| Texture Format           DDS BC7 (Linear), BC5 (Normals)    32-bit RGBA PNG / DXT1 / 16-Color PAL |
| Shader Pipeline          PBR (Metallic, Roughness, AO)      Fixed-Function Diffuse + Ambient      |
| Normal Maps              Yes (Tangent-space BC5)            NO (Vertex normals only)              |
| UV Space                 Multi-tile / UDIM / Tiling UVs     Single [0.0, 1.0] atlas per submesh   |
| Alpha Channel            8-bit Smooth Alpha Blending        1-bit Binary Alpha Testing (Punchout) |
| Color Gamma              Linear sRGB + ACES Tonemapping     Uncorrected standard sRGB             |
+---------------------------------------------------------------------------------------------------+
```

### Trap 1: The BC7 / Modern DDS Black Hole
- **What happens**: FFXIV textures extracted via TexTools or Penumbra are encoded in DirectX 11/12 **BC7 (DXGI_FORMAT_BC7_UNORM)** or **BC5** (for tangent normal maps).
- **The failure**: Blender's native glTF importer and FFXI's `ximtool.jar` **cannot decode BC7 textures**.
  - In Blender: You get console warnings:
    `WARNING DDS image '' failed to load data from file, falling back to uncompressed`
    The mesh imports, but renders with a blank white or flat grey material!
  - In XimTool: XimTool will fail to palette the image, corrupt the DAT resource table, or silently revert to an old cached texture in the output folder.
- **The rule**: **Never pass raw FFXIV `.dds` files directly to Blender or XimTool.**
  Always decompress and convert them into clean uncompressed **32-bit PNG (`RGBA`)** using `texconv.exe` or Pillow before referencing them in Blender materials:
  ```powershell
  # Convert modern DXGI DDS to clean 32-bit PNG
  texconv.exe -ft png -f R8G8B8A8_UNORM source_model.dds
  ```

### Trap 2: The Missing PBR Shading Trap (The "Flat Plastic" Look)
- **What happens**: FFXIV splits visual fidelity across multiple maps:
  1. Base Color (`_d`): Often flat and desaturated because lighting is handled dynamically.
  2. Normal Map (`_n`): Contains all the folds, seams, buttons, and cloth weave.
  3. Multi Map (`_m`): Contains Ambient Occlusion in Red, Roughness in Green, Metalness in Blue.
- **The failure**: If you only import FFXIV's Base Color into FFXI, the armor looks like flat, washed-out plastic with zero depth, seams, or folds.
- **The rule**: You must perform a **Bake-to-Diffuse Composite**:
  1. Load the model with its Normal and Multi maps into Blender.
  2. Set up a standard PBR shader.
  3. **Bake the combined Diffuse/Shading result** (Base Color $\times$ AO $\times$ Normal cavity lighting) into a single 32-bit diffuse texture (`tim em_*`).
  4. Ensure the baked texture has self-shadowing in crevices and soft cloth highlights pre-rendered into the pixel colors.

### Trap 3: UDIM & Tiling UV Wrap Collapse
- **What happens**: FFXIV armors frequently repeat small fabric patterns by setting UV coordinates far outside $[0, 1]$ (e.g. $U \in [0, 8]$) or spreading submeshes across multiple UV tiles (UDIMs).
- **The failure**: FFXI DAT textures must be self-contained in a single $[0, 1]$ coordinate space per material. Tiled UVs will either stretch out of bounds or wrap erratically across unrelated texture regions.
- **The rule**: In Blender, inspect UV bounds before export. If UVs exceed $[0, 1]$:
  - Run **UV -> Pack Islands** or manually bake tiled textures down to a unique $512 \times 512$ texture atlas.

### Trap 4: Alpha Fringe & Dithering Collapse
- **What happens**: FFXIV clothing uses 8-bit alpha channels for transparent lace, semi-translucent scarves, and hair ends.
- **The failure**: FFXI hardware skinning with Direct3D 8 does not support sorting multi-layer 8-bit alpha blending on equipment. FFXI uses **1-bit binary alpha testing** (a pixel is either 100% opaque or 100% invisible). Smooth alpha gradients become noisy, harsh black halos or blocky white fringes.
- **The rule**: In Photoshop or Python/Pillow, run an alpha threshold pass:
  ```python
  # Binary alpha threshold for FFXI 1-bit punch-through
  alpha = arr[:, :, 3]
  binary_alpha = np.where(alpha > 128, 255, 0).astype(np.uint8)
  arr[:, :, 3] = binary_alpha
  ```
  Dilate the color borders by 2-3 pixels outward into the transparent areas to prevent black outline bleed.

---

## 7. Comprehensive Pre-Flight Verification Checklist

Before compiling or deploying any custom equipment DAT:

- [ ] **1. Topological Integrity**: All continuous body parts (buttocks, groin, sleeves) belong to single undivided submesh islands. No planar slicing.
- [ ] **2. 2-Bone Hardware Rigging**: Run `vertex_group_limit_total(limit=2)` and `vertex_group_normalize_all()`. Zero vertices have $> 2$ bones.
- [ ] **3. Strict Joint Naming**: Vertex groups are named exactly `joint-<N>`. Zero `.001` or duplicate group names.
- [ ] **4. 5-Joint Leg Architecture**:
  - Upper boot shaft & lower pants cuffs weighted to Shin (`joint-13` / `joint-7`).
  - Metatarsal ball of foot ($0.05 < X < 0.15\,\text{m}$) has Smoothstep Hermite blend between Ankle and Toe.
- [ ] **5. Dynamic Motion Gate**: Mesh tested under deep kneeling ($95^\circ$ knee, $60^\circ$ toe dorsiflexion) with zero severing or torn soles.
- [ ] **6. Waist Interface Clearance**:
  - Outer sash flared $+1.5\% R$ and extended downward $+4\,\text{mm}$.
  - Inner waistband tucked $-3.0\% R$ and extruded upward $+32\,\text{mm}$ ($6.5\,\text{mm}$ clearance).
  - Waistband textured with outer belt color (e.g. Royal Blue on Royal Blue).
- [ ] **7. Texture Ingestion**:
  - Modern DDS formats (BC7/BC5) converted to uncompressed 32-bit PNG.
  - Normal and AO maps pre-baked into diffuse.
  - Specular highlights compressed for Direct3D 8 sunlight.
- [ ] **8. Clean-Room Directory**: Output folder purged of stale `.dds` and `.png` files before XimTool compilation.
- [ ] **9. String Extras**: Submesh custom properties exported as strings (`"datId": "hh_l"`, `"occludeType": "33"`).
