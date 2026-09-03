# 🛠️ FFXI DAT Engineering Technical Knowledge Dump
**Document Purpose:** Raw, high-density reference sheet for binary DAT manipulation, offsets, bitmasks, and engine quirks. Zero fluff.

---

## 1. Section Type IDs (Shipped Retail Zones)

| Section Code | Type / Purpose | Data Layout & Key Fields |
|---|---|---|
| `0x2E` | **ZoneMesh** | Local-space 3D vertices, normals, UVs, vertex colors (`BGRA`). Indexed triangles / strips. |
| `0x1C` | **ZoneDef** | Object placement table. Instances `0x2E` meshes with Pos/Rot/Scale. Contains space-tree & collision grid. |
| `0x20` | **3TXD (Texture)** | Bitmap headers + palette/DXT data. Standard marker `3TXD`. |
| `0x2F` | **Environment** | Global lighting (Sun/Moon/Ambient), Fog distances, Clear color, 8-ring skydome elevations. |
| `0x05` | **Particles / Emitters** | Particle emitters (`smok`, `bsmk`, `effe`, `sk00`..`sk20`). |
| `0x36` | **ZoneInteraction** | Trigger volumes, zone boundary lines, door interactors. |
| `0x3D` | **Sound** | Pointers to ambient music / sound effect streams. |

---

## 2. Binary Offsets & Byte Layouts

### 2.1 Texture Chunk (`3TXD`)
```text
[pos - 40..pos]: BITMAPINFOHEADER (40 bytes)
  +0x00: biSize (uint32 = 0x28)
  +0x04: biWidth (uint32)
  +0x08: biHeight (uint32)
  +0x0C: biPlanes (uint16 = 1)
  +0x0E: biBitCount (uint16: 8 for CLUT, 16 for DXT/Direct)
  +0x10: biCompression (uint32: 0 for DXT/uncompressed)

[pos + 0x00]: Magic b'3TXD'
[pos + 0x04]: Data Length (uint32)
[pos + 0x08]: Palette Length (uint32)
  - In CLUT8: Palette starts at (pos + 12), length = 1024, 2048, or 4096 bytes.
  - In NextHD DXT1: Raw DXT1 byte stream starts at (pos + 12).
```

### 2.2 Particle Emitter (`0x05`) — 1-Bit Auto-Run Toggle
* **Valid Emitter Tags**: `smok`, `bsmk`, `effe`, `sk00`..`sk20` (4 bytes ASCII).
* **Auto-Run Flag Offset**: `emitter_pos + 0x79`
* **Mask**: Bit 4 (`0x10`)
* **Silence Code**:
  ```python
  data[emitter_pos + 0x79] &= ~0x10
  ```

### 2.3 Environment (`0x2F`) Lighting & Fog Offsets
All offsets relative to section `data_start` (after header):
* `+0x00` (uint32): Indoors flag (`1` = indoor, `0` = outdoor)
* `+0x0C` (4B RGBA): Sun color (model)
* `+0x14` (4B RGBA): Ambient color (model)
* `+0x18` (4B RGBA): Fog color (model)
* `+0x1C` (float32): **Fog Far distance (model)** *(Far is before Near)*
* `+0x20` (float32): **Fog Near distance (model)**
* `+0x24` (float32): Diffuse multiplier (model)
* `+0x2C` (4B RGBA): Sun color (terrain)
* `+0x34` (4B RGBA): Ambient color (terrain)
* `+0x38` (4B RGBA): Fog color (terrain)
* `+0x3C` (float32): **Fog Far distance (terrain)**
* `+0x40` (float32): **Fog Near distance (terrain)**
* `+0x4C` (4B RGBA): Clear color
* `+0x58` (float32): Draw distance
* `+0x6C` (8 $\times$ 4B RGBA): Skydome 8-ring colors (horizon $\rightarrow$ zenith)
* `+0x8C` (8 $\times$ float32): Skydome 8-ring elevations ($0.0 \rightarrow 1.0$)

---

## 3. Formulas & Engine Equations

### 3.1 Terrain Lighting Equation
$$\text{litColor} = \text{vColor} \cdot \text{ambient} + \sum \text{vColor} \cdot \max(0, \mathbf{N} \cdot \mathbf{L}) \cdot \text{lightColor}$$
$$\text{out.rgb} = 2 \cdot \text{litColor} \cdot \text{texture.rgb} \quad (\text{framebuffer-clamped})$$
$$\text{out.a} = 4 \cdot \text{vColor.a} \cdot \text{texture.a}$$

* **Neutral Vertex Color**: `vColor = 128` (`0x80`). ($2 \times \frac{128}{255} \approx 1.0$)
* **Color Order**: Per-vertex color in `0x2E` is **BGRA**; `0x2F` packed color is **RGBA**.

### 3.2 DXT1 Compression Math ($4 \times 4$ Texel Block = 8 Bytes)
* **Byte 0–1 ($C_0$, uint16)**: Max luma 16-bit RGB565 (`(R5 << 11) | (G6 << 5) | B5`)
* **Byte 2–3 ($C_1$, uint16)**: Min luma 16-bit RGB565
* **Byte 4–7 ($Indices$, uint32)**: 16 texels $\times$ 2 bits:
  * `00` = $C_0$
  * `01` = $C_1$
  * `10` = $\frac{2}{3}C_0 + \frac{1}{3}C_1$
  * `11` = $\frac{1}{3}C_0 + \frac{2}{3}C_1$

### 3.3 FTABLE File ID Formulas (Zone DAT Types)
| DAT Type | Zone ID < 256 | Zone ID $\ge$ 256 |
|---|---|---|
| **Model** | `100 + zone_id` | `83891 + (zone_id - 256)` |
| **Event** | `5820 + zone_id` | `Model + 1100` |
| **Dialog** | `6420 + zone_id` | `Model + 1700` |
| **NPC** | `6720 + zone_id` | `Model + 2600` |

---

## 4. Hard Engine Rules & Quirks

1. **The Non-Renormalized Normal Constraint**:
   * FFXI vertex shader does **not** renormalize normals.
   * If $\|\mathbf{N}\| \ne 1.0$, the diffuse dot product $(\mathbf{N} \cdot \mathbf{L})$ saturates $\rightarrow$ **mesh glows fullbright white**.
2. **The Leading Underscore (`_`) Foliage Alpha Rule**:
   * `ZoneRenderer` enables `D3DRS_ALPHATESTENABLE` (discard threshold $0.375$) **only if mesh name starts with `_`** (e.g. `_kusa`).
   * `#` selects opaque-clamp. The `0x2000` mesh flag is double-sided rendering (back-face cull disable).
3. **The 'ef' Trap**:
   * Never match emitters via `tag.startswith(b'ef')`.
   * Floating-point 3D vertex coordinates contain binary `0x65 0x66` (`ef`). Must use strict 4-byte match `['smok', 'bsmk', 'effe', 'sk00'..'sk20']`.
4. **Alpha Overdraw Rules**:
   * **Physical Solids (Grass/Leaves)**: Convert palette alphas to binary cutouts ($A=0$ or $A=0x80$) to switch Direct3D from multi-pass blending to instant 1-pass testing.
   * **Fluid Waves/Foam (`unhu`, `shn1`)**: Keep soft gradients ($A \le 18 \implies A=0$, else keep $A$). Hard $0x80$ cutouts create scrolling Z-fighting slabs over sand.
5. **Collision Grid Bounds**:
   * The spatial hashing collision grid in `0x1C` has fixed coordinate bounds. Scaling geometry outside this bounding box breaks player collision (rubberbanding / falling through floor).

---

## 5. Working Reference Code Snippets

### 5.1 Native Python DXT1 Block Encoder (Zero External Dependencies)
```python
import struct

def encode_dxt1_block(block_pixels):
    def luma(p): return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    sorted_p = sorted(block_pixels, key=luma)
    p_min, p_max = sorted_p[0], sorted_p[-1]

    def to_rgb565(p):
        r = (p[0] >> 3) & 0x1F
        g = (p[1] >> 2) & 0x3F
        b = (p[2] >> 3) & 0x1F
        return (r << 11) | (g << 5) | b

    c0, c1 = to_rgb565(p_max), to_rgb565(p_min)
    if c0 == c1:
        return struct.pack('<HHI', c0, c1, 0)

    r0, g0, b0 = (p_max[0] >> 3) << 3, (p_max[1] >> 2) << 2, (p_max[2] >> 3) << 3
    r1, g1, b1 = (p_min[0] >> 3) << 3, (p_min[1] >> 2) << 2, (p_min[2] >> 3) << 3

    pal = [
        (r0, g0, b0),
        (r1, g1, b1),
        (int((2*r0 + r1)/3), int((2*g0 + g1)/3), int((2*b0 + b1)/3)),
        (int((r0 + 2*r1)/3), int((g0 + 2*g1)/3), int((b0 + 2*b1)/3))
    ]

    indices = 0
    for idx, p in enumerate(block_pixels):
        best_d, best_idx = 1e9, 0
        for p_idx, c in enumerate(pal):
            d = (p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2
            if d < best_d:
                best_d, best_idx = d, p_idx
        indices |= (best_idx << (idx * 2))

    return struct.pack('<HHI', c0, c1, indices)

def encode_dxt1(image):
    w, h = image.size
    pix = image.load()
    out = bytearray()
    for by in range(0, h, 4):
        for bx in range(0, w, 4):
            blk = [pix[min(w-1, bx+x), min(h-1, by+y)] for y in range(4) for x in range(4)]
            out.extend(encode_dxt1_block(blk))
    return bytes(out)
```

### 5.2 1-Bit Emitter Silence Routine
```python
def silence_emitters(dat_bytes, emitter_tags=[b'smok', b'bsmk', b'effe']):
    data = bytearray(dat_bytes)
    silenced = 0
    for tag in emitter_tags:
        start = 0
        while True:
            pos = data.find(tag, start)
            if pos == -1: break
            start = pos + 4
            flag_offset = pos + 0x79
            if flag_offset < len(data) and (data[flag_offset] & 0x10):
                data[flag_offset] &= ~0x10
                silenced += 1
    return bytes(data), silenced
```
