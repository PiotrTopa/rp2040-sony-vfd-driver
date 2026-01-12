# VFD Grid & Segment Mapping Documentation

## Overview
The Sony 1-869-725-12 VFD panel is driven by a PT6315 controller configured in **16 Grid x 12 Segment** mode.

## Grid Allocation (Hypothesis & Findings - 12 Digits Mode)

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

The display uses a 14-segment layout for characters. The mapping in `font.py` uses the following keys:

- **Outer Ring**: `a` (top), `b` (top-right), `c` (bottom-right), `d` (bottom), `e` (bottom-left), `f` (top-left)
- **Middle**: `g1` (left-mid), `g2` (right-mid)
- **Top Inner**: `h`, `i`, `j` (Verticals/Diagonals)
- **Bottom Inner**: `k`, `l`, `m` (Verticals/Diagonals)

## Using the Mapping Tool

Run `mapping_tool.py` on the device to interactively find and record segments. The tool now features a graphical UI in the terminal and saves data to `mappings.json`.

### Controls
- **<Enter> / n**: Next Bit (0-15)
- **p**: Previous Bit
- **N**: Next Grid (0-11)
- **P**: Previous Grid
- **jump <grid> [bit]**: Jump to specific location (e.g., `jump 6 0`)
- **map <name>**: Record mapping for current segment (e.g., `map d1_d`)
- **save**: Save recorded mappings to `mappings.json`
- **q**: Quit

### Data Storage
Mappings are stored in `mappings.json`. The framework (`font.py`) loads this file automatically.

### Missing Items to Find
1.  **d1 segment 'd'**: Likely on **Grid 6** (Bits 12-15).
2.  **Digits d4 - d8**: Likely on Grids 10-11, or utilizing bits 12-15 of other grids.
