# Galka Mech Experiment (Tarutaru Pilot Cockpit Mod)

<p align="center">
  <img src="https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/galkamech_hero.png" alt="Galka Mech Experiment - Tarutaru Cockpit Mod" width="480" />
</p>

A custom Final Fantasy XI experiment that turns the Galka into a piloted mecha suit! A custom brass-bezel cockpit is cut directly into the Galka's chest cavity, revealing an authentic retail Tarutaru pilot steering the giant with twin flight levers.

| Galka Mech Stance | Cockpit & Pilot Close-Up | Standalone Modular Cockpit |
|:---:|:---:|:---:|
| ![Galka Mech Hero](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/galkamech_hero.png) | ![Cockpit Close](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/galkamech_pilot.png) | ![Cockpit Module](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/galkamech_module.png) |

---

## Quick Installation (XIPivot)

Drop the `GalkaMechExperiment` folder directly into your XIPivot directory:

```text
Windower4/addons/XIPivot/data/DATs/
└── GalkaMechExperiment/
    └── ROM/
        ├── 363/
        │   └── 58.DAT   # Mithkabob Shirt (Item #26545 / Galka Model 590)
        └── 372/
            └── 58.DAT   # Moogle Shirt (Item #26546 / Galka Model 591)
```

Enable in XIPivot via the in-game Windower console or your `init.txt`:
```text
//pivot add GalkaMechExperiment
```

Equip either the **Mithkabob Shirt** or **Moogle Shirt** (or set either in your lockstyle) to activate the mech suit!

---

## Targeted Files & In-Game Items

| Equipment Slot | Model ID | Target DAT Path | In-Game Lockstyle Item |
| :--- | :--- | :--- | :--- |
| **Body** | `Body 590` | `ROM/363/58.DAT` | **Mithkabob Shirt** (`#26545`) |
| **Body** | `Body 591` | `ROM/372/58.DAT` | **Moogle Shirt** (`#26546`) |

---

## Pilot & Cockpit Anatomy

* **Authentic Retail Geometry & Materials**:
  * **Tarutaru Pilot Head**: Authentic FFXI retail Tarutaru mesh (`ROM/46/98.DAT`), customized with rich anime/navy blue hair, caramel skin tone, anime specular catchlight eyes, and a black choker with a golden bell.
  * **Stars Cap**: Authentic retail Stars Cap (`ROM/156/91.DAT` / Item `#15212`) complete with floppy tail and star charms.
  * **Mithkabob Shirt**: Authentic retail Mithkabob Shirt (`ROM/363/55.DAT` / Item `#26545`) with the Yakitori meat skewer emblem.
* **Cockpit Interior**:
  * Heavy riveted brass porthole bezel with 8 3D hex bolts.
  * Vintage analog dial gauge and glowing navigation lantern.
  * Dual flight control sticks with red and amber grips.

---

## Standalone Cockpit Module (Attach to ANY Galka Armor!)

The Tarutaru pilot cockpit is completely modular. You can import and mount it onto **any** Galka body mesh or custom DAT you desire.

### Included Standalone Files
* `Galka_Cockpit_Pilot_Module.zip`: Complete bundle with 3D models, textures, sample DAT, and the automated Blender script.
* `galka_cockpit_module.glb`: Pre-rigged glTF binary module ready for DCC tools.
* `galka_cockpit_module.obj` & `galka_cockpit_module.mtl`: Universal Wavefront geometry.
* `tim_gal_cockpit_atlas.png`: 256x256 cockpit texture atlas.
* `attach_cockpit_to_galka_body.py`: Automated headless Blender script that mounts the cockpit, builds the composite texture atlas, and binds the vertices.

### Automated Mounting via Blender
To attach the cockpit module to any extracted Galka body GLB:

```bash
blender --background --python attach_cockpit_to_galka_body.py -- <galka_body.glb> <body_texture.png> [out.glb] [out_atlas.png]
```

Example:
```bash
blender -b -P attach_cockpit_to_galka_body.py -- 58.glb tim_gl_byc15.png
```

---

## Technical Specifications & Hardware Compliance

* **Strict Direct3D 8 Skinning Limit**:
  * Vertices are strictly limited to $\le 2$ bone influences per vertex (`bone0038`: 0.85 chest, `bone0037`: 0.15 spine).
  * 100% normalized weight totals prevent mesh tearing, geometry explosion, or client crashes.
* **Unified Texture Atlas**:
  * Combines the host body texture (U: `0.0..0.5`) with the cockpit atlas (U: `0.5..1.0`) into a single 256x256 Direct3D 8 surface.
