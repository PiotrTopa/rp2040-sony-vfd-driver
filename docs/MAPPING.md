# VFD Grid & Segment Mapping Documentation

## Overview
The Sony 1-869-725-12 VFD panel is driven by a PT6315 controller configured in **16 Grid x 12 Segment** mode.

## Grid Allocation (12 Digits Mode)

In **12 Digits / 16 Segments** Mode, we only have Grids 0-11. Each Grid has 16 bits (0-15).

| Grid Index | Address (Base) | Primary Usage | Notes |
|------------|----------------|---------------|-------|
| **0**      | `0x00`         | Icons         | `mp3`, `pgm`, `shuf`, `folder`, `diskS`, `disc`, `1`, `ALL`, `play`, `pause`, `DAB`, `FM` |
| **1**      | `0x02`         | Icons         | `rec`, `sync` |
| **2**      | `0x04`         | Icons         | `trk`, `L_folder` |
| **3**      | `0x06`         | Icons         | `preset`, `cat`, `ens`, `mhz`, `khz`, `play_icon` |
| **4**      | `0x08`         | **d0** (Rightmost) | Partial segments (h, i, j) |
| **5**      | `0x0A`         | **d0** / Icons | d0 segments (c, e, k, l, m, d), Icon `auto` |
| **6**      | `0x0C`         | **d1**        | Almost full digit. Missing 'd' segment (check bits 12-15). |
| **7**      | `0x0E`         | **d2**        | Partial segments (a, h, i, j) |
| **8**      | `0x10`         | **d2** / Icons | d2 segments (c, e, k, l, m, d, dot), Icon `name` |
| **9**      | `0x12`         | **d3**        | Full digit? (a-l) |
| **10**     | `0x14`         | **d4**?       | *To be mapped* |
| **11**     | `0x16`         | **d5**?       | *To be mapped* |
| **12-15**  | N/A            | N/A           | Not available in this mode. |

## Segment Layout (14-Segment)

![14-Segment Layout](images/14-segment.svg)

The display uses a 14-segment layout for characters. The mapping in `font.py` uses the following keys:

- **Outer Ring**: `a` (top), `b` (top-right), `c` (bottom-right), `d` (bottom), `e` (bottom-left), `f` (top-left)
- **Middle**: `g1` (left-mid), `g2` (right-mid)
- **Top Inner**: `h`, `i`, `j` (Verticals/Diagonals)
- **Bottom Inner**: `k`, `l`, `m` (Verticals/Diagonals)

## Using the Mapping Tool

The `mapping_tool.py` is an interactive utility to reverse-engineer the VFD's internal wiring. It allows you to light up individual segments (Grid/Bit pairs) and assign them meaningful names.

### Workflow
1.  **Run the Tool**: Execute `mapping_tool.py` on the microcontroller.
2.  **Explore**: Use `n` (Next) and `p` (Previous) to toggle through every Grid and Bit.
3.  **Identify**: Watch the VFD to see what lights up.
4.  **Map**: When a segment or icon lights up, assign it a name using the `map` command.
    *   *Example:* You are on Grid 4, Bit 8, and the top segment of the rightmost digit lights up. Type `map d0_a`.
5.  **Save**: Periodically type `save` to write changes to `mappings.json`.

### Naming Convention
The tool uses a `category_name` format. This structure allows the driver to group segments logically (e.g., all segments for Digit 0).

*   **Digits:** `d{n}_{seg}`
    *   `n`: Digit index (0 is usually rightmost).
    *   `seg`: Segment name (a-f, g1, g2, h-m).
    *   *Example:* `d0_a` (Digit 0, Segment A), `d5_g1` (Digit 5, Segment G1).
*   **Icons:** `icon_{name}`
    *   *Example:* `icon_play`, `icon_usb`.
*   **Labels:** `label_{name}`
    *   *Example:* `label_mhz`, `label_stereo`.

### Controls
| Command | Action |
| :--- | :--- |
| **`<Enter>` / `n`** | Next Bit (Toggle current off, next on) |
| **`p`** | Previous Bit |
| **`N` / `P`** | Next / Previous Grid |
| **`jump <g> [b]`** | Jump to Grid `g` (and optional Bit `b`) |
| **`map <name>`** | Assign name to current segment (e.g., `map d1_a`) |
| **`mode <hex>`** | Change Display Mode (e.g., `mode 8` for 12G/16S) |
| **`save`** | Save mappings to `mappings.json` |
| **`q`** | Quit |

### Data Storage
Mappings are saved to `mappings.json` in the following structure:
```json
{
  "mappings": {
    "d0": {
      "a": [4, 8],
      "b": [4, 12]
    },
    "icon": {
      "play": [3, 10]
    }
  }
}
```
The driver (`font.py`) automatically loads this file to configure the display.
