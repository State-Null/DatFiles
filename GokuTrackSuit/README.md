# GokuTrackSuit (Track Shirt & Track Pants - Elvaan Male)

Complete Son Goku Gi costume override for Elvaan Male in Final Fantasy XI. Replaces the **Track Shirt** and **Track Pants** lockstyle items.

| In-Game Front Stance | In-Game Back (Turtle / Kai Emblem) | In-Game Kneeling Flex (`/heal`) |
|:---:|:---:|:---:|
| ![Goku Front Stance](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/gokutracksuit_front.png) | ![Goku Back Emblem](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/gokutracksuit_back.png) | ![Goku Kneeling Flex](https://github.com/State-Null/DatFiles/raw/main/.github/screenshots/gokutracksuit_kneel.png) |

---

## Installation

Drop the `GokuTrackSuit` folder directly into your XIPivot directory:

```text
Windower4/addons/XIPivot/data/DATs/
└── GokuTrackSuit/
    └── ROM/
        └── 339/
            ├── 25.DAT   # Body 579 (Track Shirt / Track Shirt +1)
            └── 26.DAT   # Legs 579 (Track Pants / Track Pants +1)
```

Enable in XIPivot via in-game Windower console or script:
```text
//pivot add GokuTrackSuit
```

---

## Targeted Files & In-Game Items

| Equipment Slot | Model ID | Target DAT Path | In-Game Lockstyle Item |
| :--- | :--- | :--- | :--- |
| **Body** | `Body 579` | `ROM/339/25.DAT` | **Track Shirt** (`#25713`) / **Track Shirt +1** (`#25714`) |
| **Legs / Feet** | `Legs 579` | `ROM/339/26.DAT` | **Track Pants** (`#27325`) / **Track Pants +1** (`#27326`) |

*Note: The pants mesh includes Goku's boots integrated directly into `Legs 579`, ensuring full kinematic synchronization with the shin and pants cuffs during movement.*

---

## Technical Highlights (Build v8.3)

* **5-Joint Leg & Foot Kinematics**:
  - Restores authentic FFXI skeletal hierarchy (`joint-13`/`joint-7` Shin, `joint-14`/`joint-8` Ankle, `joint-15`/`joint-9` Toe).
  - Smoothstep Hermite sole curvature across the metatarsals ($0.05 < X < 0.15\text{ m}$) prevents sole tearing or severed toe caps during the `/heal` kneeling animation.
  - Lower pants cuffs and upper boot shafts follow the shin without unhinging from the knee.
* **Zero-Z-Fighting Waist Interface**:
  - Flared outer blue sash ($+1.5\%$) with $+4\text{ mm}$ lower wrap overlap.
  - Inset inner waistband ($-3.0\%$) extruded $+32\text{ mm}$ into belt cavity ($6.5\text{ mm}$ radial safety gap).
  - Internal waistband textured Royal Blue (`UV = 0.950, 0.640`) matching the sash, eliminating walking spine sway flicker.
* **Racial Anatomy Alignment**:
  - Elevated collar rim eliminates the dark nape notch beneath Elvaan Male Face 10 hair.
  - Calibrated skin tone with compressed sunlight specular highlights tailored for Direct3D 8 fixed-function shading.
* **Hardware Skinning Compliance**:
  - Strict $\le 2$ bone influences per vertex, $100\%$ normalized totals. Clean compilation through `ximtool`.
