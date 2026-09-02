# DatFiles - High-Fidelity FFXI Zone & Asset Overhauls

A collection of curated, crash-proof, high-resolution DAT overhauls and visual enhancements for Final Fantasy XI, optimized for **XIPivot**.

---

## ⚡ Featured Pack: Tronmenos (Zone 37 - Temenos)

**Tronmenos** is a complete, retro-futuristic cybernetic overhaul for **Temenos** (ROM3/3/82.DAT). It eliminates the harsh, blinding white floor glare of vanilla and replaces the entire zone architecture with high-tech matte obsidian surfaces, glowing neon cyan energy conduits, and digital circuit freeways.

### 📸 In-Game Screenshots

| Central Chamber & Energy Rings | Hallway Freeways & Carbon Weave |
|:---:|:---:|
| ![Tronmenos Chamber](docs/screenshots/tronmenos_chamber.jpg) | ![Tronmenos Hallway](docs/screenshots/tronmenos_hallway.jpg) |

---

### ✨ Architectural Features
* **Zero Floor Glare**: The blinding white floor is replaced by high-contrast, dark obsidian cyber-flooring with radiant cyan circuit traces.
* **Direct3D DXT1 Compression**: Encoded with hardware-accelerated Direct3D DXT1 blocks ( \times 2048$ Ultra HD) for locked 60 FPS performance.
* **Expanded Container Architecture**: Built upon isolated multi-megabyte memory buffers with 100% boundary safety.
* **Full Zone Cohesion**: Covers floors (yuka, 	ile, sin_tile), walls (kabe2, kabe3, sin_kabe), and pillars (piller).
* **Protected Interactivity**: Doors, Zilart teleporters, sprite lighting, and collision walkmeshes remain 100% retail-exact.

---

## 📦 Installation (XIPivot)

1. Copy the Tronmenos folder directly into your XIPivot DATs directory:
   `	ext
   C:\windower4\addons\XIPivot\data\DATs\Tronmenos
   `
2. Open your XIPivot settings.xml (C:\windower4\addons\XIPivot\data\settings.xml) and add Tronmenos to your overlays:
   `xml
   <overlays>Tronmenos,zones,objects,test,remapster,mithra,NextHD</overlays>
   `
3. In your Windower console, reload XIPivot:
   `	ext
   //pivot reload
   `

---

## 📜 License & Credits
* Original Zone Meshes: Square Enix
* Container Architecture: NextHD / Amelila
* Cybernetic Textures & DXT1 Mastering: State-Null
