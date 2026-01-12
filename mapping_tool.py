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
                return f"{category}: {name}"
    return ""

def update_mapping(data, grid, bit, name):
    if "_" not in name:
        return False
        
    parts = name.split("_", 1) 
    category = parts[0]
    item_name = parts[1]
    
    mappings = data.setdefault("mappings", {})
    
    # Remove existing mapping for this grid/bit
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

def draw_ui(grid, bit, mapping_name, mode, brightness):
    # ANSI clear screen
    print("\x1b[2J\x1b[H", end="") 
    
    line = ""
    for b in range(16):
        if b == bit:
            line += "[*]"
        else:
            line += "[ ]"
    
    print(f"=== VFD MAPPING TOOL ===")
    print(f"GRID: {grid:02d} (Addr 0x{grid*2:02X}) | Mode: 0x{mode:02X} | Bright: {brightness}")
    print(line)
    print(" 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15")
    print("-" * 40)
    print(f"Current: Grid {grid}, Bit {bit}")
    print(f"Mapped:  {mapping_name if mapping_name else '---'}")
    print("-" * 40)
    print("Controls:")
    print("  <Enter> / n  : Next Bit")
    print("  p            : Prev Bit")
    print("  N / P        : Next / Prev Grid")
    print("  map <name>   : Map (category_name)")
    print("  jump <g> <b> : Jump to grid/bit")
    print("  mode <val>   : Set Mode (8=12G, C=16G)")
    print("  bright <val> : Set Brightness (0-7)")
    print("  led <val>    : Set LEDs (0-15)")
    print("  save         : Save to JSON")
    print("  q            : Quit")
    print("-" * 40)

def main():
    print("Initializing...")
    try:
        display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
        # Clear buffer manually
        for i in range(len(display.buffer)): display.buffer[i] = 0
        display.flush()
    except Exception as e:
        print(f"Display Init Failed: {e}")
        return

    data = load_data()
    
    grid = 0
    bit = 0
    last_grid = -1
    last_bit = -1
    
    current_mode = 0x08 # Default 12G
    current_brightness = 7
    
    while True:
        # Update Display only if changed (or forced by logic update)
        if grid != last_grid or bit != last_bit:
            # FIX: Manually clear buffer (in place)
            for i in range(len(display.buffer)): display.buffer[i] = 0
            
            display.set_pixel(grid, bit, 1)
            display.flush()
            
            mapping_name = get_mapping_name(data, grid, bit)
            draw_ui(grid, bit, mapping_name, current_mode, current_brightness)
            
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
                if grid > 31: grid = 0 # Extended to 31 (32 Grids)
        elif cmd == 'p':
            bit -= 1
            if bit < 0:
                bit = 15
                grid -= 1
                if grid < 0: grid = 31
        elif cmd == 'nn': # Next Grid
            grid += 1
            bit = 0
            if grid > 31: grid = 0
        elif cmd == 'pp': # Prev Grid
            grid -= 1
            bit = 0
            if grid < 0: grid = 31
        elif cmd == 'jump':
            if len(parts) >= 2:
                try:
                    grid = int(parts[1])
                    if len(parts) >= 3:
                        bit = int(parts[2])
                    else:
                        bit = 0
                    if grid > 31: grid = 31
                    if bit > 15: bit = 15
                except:
                    pass
        elif cmd == 'mode':
            if len(parts) >= 2:
                try:
                    val = int(parts[1], 16) # Hex
                    current_mode = val
                    display.set_mode(current_mode)
                    display.set_brightness(current_brightness) # Re-enable display
                    print(f"Mode set to 0x{val:02X}")
                    last_grid = -1 # Force redraw
                except:
                    print("Invalid mode (use hex)")
        elif cmd == 'bright':
            if len(parts) >= 2:
                try:
                    val = int(parts[1])
                    if 0 <= val <= 7:
                        current_brightness = val
                        display.set_brightness(current_brightness)
                        print(f"Brightness set to {val}")
                        last_grid = -1
                except:
                    pass
        elif cmd == 'led':
            if len(parts) >= 2:
                try:
                    val = int(parts[1])
                    display.write_leds(val)
                    print(f"LEDs set to {val}")
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
            
    print("Exiting.")

if __name__ == "__main__":
    main()
