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
            json.dump(data, f)
        print(f"\nSaved to {MAPPING_FILE}")
    except Exception as e:
        print(f"\nError saving: {e}")

def get_mapping_name(data, grid, bit):
    for name, val in data.get("icons", {}).items():
        if val == [grid, bit]:
            return f"Icon: {name}"
    char_pos = data.get("char_positions", [])
    for idx, char_map in enumerate(char_pos):
        digit_name = f"d{idx}"
        for seg, val in char_map.items():
            if val == [grid, bit]:
                return f"{digit_name}_{seg}"
    return ""

def update_mapping(data, grid, bit, name):
    # Remove existing
    keys_to_del = []
    for k, v in data["icons"].items():
        if v == [grid, bit]:
            keys_to_del.append(k)
    for k in keys_to_del:
        del data["icons"][k]
    
    for char_map in data["char_positions"]:
        keys_to_del = []
        for k, v in char_map.items():
            if v == [grid, bit]:
                keys_to_del.append(k)
        for k in keys_to_del:
            del char_map[k]
            
    # Add new
    if "_" in name and name.startswith("d") and name[1:2].isdigit():
        parts = name.split("_")
        if len(parts) == 2:
            d_idx = int(parts[0][1:])
            seg = parts[1]
            while len(data["char_positions"]) <= d_idx:
                data["char_positions"].append({})
            data["char_positions"][d_idx][seg] = [grid, bit]
            return True
    else:
        data["icons"][name] = [grid, bit]
        return True
    return False

def draw_ui(grid, bit, mapping_name):
    # ANSI clear screen
    print("\x1b[2J\x1b[H", end="") 
    
    line = ""
    for b in range(12):
        if b == bit:
            line += "[*]"
        else:
            line += "[ ]"
    
    print(f"=== VFD MAPPING TOOL ===")
    print(f"GRID: {grid:02d} (Addr 0x{grid*2:02X})")
    print(line)
    print(" 0  1  2  3  4  5  6  7  8  9 10 11")
    print("-" * 30)
    print(f"Current: Grid {grid}, Bit {bit}")
    print(f"Mapped:  {mapping_name if mapping_name else '---'}")
    print("-" * 30)
    print("Controls:")
    print("  <Enter> / n  : Next Bit")
    print("  p            : Prev Bit")
    print("  N            : Next Grid")
    print("  P            : Prev Grid")
    print("  map <name>   : Map (e.g. 'd1_a')")
    print("  jump <g> <b> : Jump to grid/bit")
    print("  save         : Save to JSON")
    print("  q            : Quit")
    print("-" * 30)

def main():
    print("Initializing...")
    try:
        display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
        # Clear buffer manually to avoid flush
        display.buffer = bytearray(48)
        display.flush()
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
        # Update Display only if changed
        if grid != last_grid or bit != last_bit:
            # FIX: Do not call display.clear() which flushes zeros!
            # Instead, manipulate buffer directly.
            display.buffer = bytearray(48) 
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
        elif cmd == 'N': # Uppercase N -> Next Grid
            grid += 1
            bit = 0
            if grid > 15: grid = 0
        elif cmd == 'P': # Uppercase P -> Prev Grid
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
