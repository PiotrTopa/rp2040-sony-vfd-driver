import json
import time
import sys
from vfd import PT6315

# Pin Configuration
PIN_CLK = 4
PIN_DAT = 3
PIN_STB = 5

MAPPING_FILE = "mappings.json"

def load_data():
    try:
        with open(MAPPING_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {MAPPING_FILE}: {e}")
        return {"icons": {}, "char_positions": [{} for _ in range(9)]}

def save_data(data):
    try:
        with open(MAPPING_FILE, "w") as f:
            json.dump(data, f) # MicroPython json.dump might not support indent
        print(f"Saved to {MAPPING_FILE}")
    except Exception as e:
        print(f"Error saving: {e}")

def get_mapping_name(data, grid, bit):
    # Check icons
    for name, val in data.get("icons", {}).items():
        if val == [grid, bit]:
            return f"Icon: {name}"
            
    # Check chars
    char_pos = data.get("char_positions", [])
    for idx, char_map in enumerate(char_pos):
        digit_name = f"d{idx}"
        for seg, val in char_map.items():
            if val == [grid, bit]:
                return f"{digit_name}_{seg}"
    return ""

def update_mapping(data, grid, bit, name):
    # Name format: "d1_a" or "icon_name"
    # Remove old mapping for this grid/bit if exists? 
    # Actually, one segment can be used for multiple things? Unlikely for VFD.
    # We should probably remove any existing mapping for this (grid, bit) first.
    
    # 1. Remove existing from icons
    keys_to_del = []
    for k, v in data["icons"].items():
        if v == [grid, bit]:
            keys_to_del.append(k)
    for k in keys_to_del:
        del data["icons"][k]
        
    # 2. Remove existing from chars
    for char_map in data["char_positions"]:
        keys_to_del = []
        for k, v in char_map.items():
            if v == [grid, bit]:
                keys_to_del.append(k)
        for k in keys_to_del:
            del char_map[k]
            
    # 3. Add new
    if "_" in name and name.startswith("d") and name[1:2].isdigit():
        # Character segment: d1_a
        parts = name.split("_")
        if len(parts) == 2:
            d_idx = int(parts[0][1:])
            seg = parts[1]
            
            # Ensure char_positions has enough slots
            while len(data["char_positions"]) <= d_idx:
                data["char_positions"].append({})
                
            data["char_positions"][d_idx][seg] = [grid, bit]
            return True
    else:
        # Icon
        data["icons"][name] = [grid, bit]
        return True
    return False

def draw_ui(grid, bit, mapping_name):
    # ANSI clear screen? Maybe just newlines
    print("\n" * 5)
    
    # Grid visualization
    line = ""
    nums = ""
    for b in range(12):
        if b == bit:
            line += "[*]"
        else:
            line += "[ ]"
        nums += f"{b:3}"
        
    print(f"=== VFD MAPPING TOOL ===")
    print(f"GRID: {grid:02d} (Addr 0x{grid*2:02X})")
    print(line)
    print(" 0  1  2  3  4  5  6  7  8  9 10 11")
    print("-" * 30)
    print(f"Current: Grid {grid}, Bit {bit}")
    print(f"Mapped:  {mapping_name if mapping_name else '---'}")
    print("-" * 30)
    print("Controls:")
    print("  <Enter>      : Next Bit")
    print("  p            : Prev Bit")
    print("  N / P        : Next / Prev Grid")
    print("  map <name>   : Map (e.g. 'd1_a', 'play')")
    print("  save         : Save to JSON")
    print("  jump <g> <b> : Jump to grid/bit")
    print("  q            : Quit")
    print("-" * 30)

def main():
    print("Initializing...")
    try:
        display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
        display.clear()
        display.set_brightness(7)
    except Exception as e:
        print(f"Display Init Failed: {e}")
        return

    data = load_data()
    
    grid = 0
    bit = 0
    last_grid = -1
    last_bit = -1
    
    while True:
        # Refresh Display and UI
        if grid != last_grid or bit != last_bit:
            display.clear()
            display.set_pixel(grid, bit, 1)
            display.flush()
            
            mapping_name = get_mapping_name(data, grid, bit)
            draw_ui(grid, bit, mapping_name)
            
            last_grid = grid
            last_bit = bit

        # Input
        try:
            inp = input("> ").strip()
        except KeyboardInterrupt:
            break
            
        parts = inp.split()
        cmd = parts[0].lower() if parts else "n" # Default to 'n' (Next)
        
        if cmd == 'q':
            break
        elif cmd == 'n':
            bit += 1
            if bit > 11:
                bit = 0
                grid += 1
                if grid > 15: grid = 0
        elif cmd == 'p':
            bit -= 1
            if bit < 0:
                bit = 11
                grid -= 1
                if grid < 0: grid = 15
        elif cmd == 'N': # Uppercase N
            grid += 1
            bit = 0
            if grid > 15: grid = 0
        elif cmd == 'P': # Uppercase P
            grid -= 1
            bit = 0
            if grid < 0: grid = 15
        elif cmd == 'jump':
            if len(parts) >= 2:
                try:
                    grid = int(parts[1])
                    if len(parts) >= 3:
                        bit = int(parts[2])
                    else:
                        bit = 0
                except:
                    pass
        elif cmd == 'map':
            if len(parts) > 1:
                name = parts[1]
                if update_mapping(data, grid, bit, name):
                    print(f"Mapped {name}")
                    last_grid = -1 # Force redraw
                else:
                    print("Invalid mapping name format")
            else:
                print("Usage: map <name>")
        elif cmd == 'save':
            save_data(data)
            
    display.clear()
    print("Exiting.")

if __name__ == "__main__":
    main()
