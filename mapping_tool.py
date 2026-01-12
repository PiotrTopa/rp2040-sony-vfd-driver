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
        return {"mappings": {}}

def save_data(data):
    try:
        with open(MAPPING_FILE, "w") as f:
            json.dump(data, f)
        print(f"\nSaved to {MAPPING_FILE}")
        print("\n--- JSON DUMP (Copy below) ---")
        # MicroPython json.dumps might not support indent, but we print raw for easy copy
        print(json.dumps(data))
        print("------------------------------")
    except Exception as e:
        print(f"\nError saving: {e}")

def get_mapping_name(data, grid, bit):
    mappings = data.get("mappings", {})
    # Search all categories
    for category, items in mappings.items():
        for name, val in items.items():
            if val == [grid, bit]:
                # e.g. "d1: a" or "icon: play"
                return f"{category}: {name}"
    return ""

def update_mapping(data, grid, bit, name):
    # Name format: "category_name"
    if "_" not in name:
        return False
        
    parts = name.split("_", 1) # Split on first underscore
    category = parts[0]
    item_name = parts[1]
    
    mappings = data.setdefault("mappings", {})
    
    # Remove existing mapping for this grid/bit across ALL categories
    # Because one bit usually controls one segment/icon
    for cat, items in mappings.items():
        keys_to_del = []
        for k, v in items.items():
            if v == [grid, bit]:
                keys_to_del.append(k)
        for k in keys_to_del:
            del items[k]
            
    # Add new mapping
    cat_dict = mappings.setdefault(category, {})
    cat_dict[item_name] = [grid, bit]
    return True

def draw_ui(grid, bit, mapping_name):
    # ANSI clear screen
    print("\x1b[2J\x1b[H", end="") 
    
    line = ""
    for b in range(16):
        if b == bit:
            line += "[*]"
        else:
            line += "[ ]"
    
    print(f"=== VFD MAPPING TOOL (12G x 16S Mode) ===")
    print(f"GRID: {grid:02d} (Addr 0x{grid*2:02X})")
    print(line)
    print(" 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15")
    print("-" * 30)
    print(f"Current: Grid {grid}, Bit {bit}")
    print(f"Mapped:  {mapping_name if mapping_name else '---'}")
    print("-" * 30)
    print("Controls:")
    print("  <Enter> / n  : Next Bit")
    print("  p            : Prev Bit")
    print("  N            : Next Grid")
    print("  P            : Prev Grid")
    print("  map <name>   : Map (Format: category_name e.g. d1_a, icon_play)")
    print("  jump <g> <b> : Jump to grid/bit")
    print("  save         : Save to JSON")
    print("  q            : Quit")
    print("-" * 30)

def main():
    print("Initializing...")
    try:
        display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
        # Clear buffer manually to avoid flush
        for i in range(len(display.buffer)): display.buffer[i] = 0
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
            # FIX: Manually clear buffer (in place)
            for i in range(len(display.buffer)): display.buffer[i] = 0
            
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
            if bit > 15:
                bit = 0
                grid += 1
                if grid > 11: grid = 0
        elif cmd == 'p':
            bit -= 1
            if bit < 0:
                bit = 15
                grid -= 1
                if grid < 0: grid = 11
        elif cmd == 'N': # Uppercase N -> Next Grid
            grid += 1
            bit = 0
            if grid > 11: grid = 0
        elif cmd == 'P': # Uppercase P -> Prev Grid
            grid -= 1
            bit = 0
            if grid < 0: grid = 11
        elif cmd == 'jump':
            if len(parts) >= 2:
                try:
                    grid = int(parts[1])
                    if len(parts) >= 3:
                        bit = int(parts[2])
                    else:
                        bit = 0
                    if grid > 11: grid = 11
                    if bit > 15: bit = 15
                except:
                    pass
        elif cmd == 'map':
            if len(parts) > 1:
                name = parts[1]
                if update_mapping(data, grid, bit, name):
                    print(f"Mapped {name}")
                    last_grid = -1 # Force redraw
                else:
                    print("Invalid format. Use: category_name (e.g. icon_play)")
            else:
                print("Usage: map category_name")
        elif cmd == 'save':
            save_data(data)
            
    #display.clear()
    print("Exiting.")

if __name__ == "__main__":
    main()
