import json
import time
import sys
import uselect
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
    # ANSI clear screen usually works in serial terminals
    # \x1b[2J clears screen, \x1b[H moves cursor to home
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
    print("  Right / Enter : Next Bit")
    print("  Left / p      : Prev Bit")
    print("  Up / P        : Prev Grid")
    print("  Down / N      : Next Grid")
    print("  m             : Map (type name)")
    print("  j             : Jump (type grid [bit])")
    print("  s             : Save")
    print("  q             : Quit")
    print("-" * 30)

def read_key():
    # Blocking read of one key
    k = sys.stdin.read(1)
    if k == '\x1b':
        # Check for escape sequence
        poll = uselect.poll()
        poll.register(sys.stdin, uselect.POLLIN)
        if poll.poll(50): # 50ms timeout
            k2 = sys.stdin.read(1)
            if k2 == '[':
                if poll.poll(50):
                    k3 = sys.stdin.read(1)
                    if k3 == 'A': return 'UP'
                    if k3 == 'B': return 'DOWN'
                    if k3 == 'C': return 'RIGHT'
                    if k3 == 'D': return 'LEFT'
    return k

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

        # Read Input
        try:
            key = read_key()
        except KeyboardInterrupt:
            break
        
        # Parse Key
        cmd = ''
        if key in ['\n', '\r', 'n', 'RIGHT']:
            cmd = 'next_bit'
        elif key in ['p', 'LEFT']:
            cmd = 'prev_bit'
        elif key in ['N', 'DOWN']: # Down arrow goes to next grid (visual flow)
            cmd = 'next_grid'
        elif key in ['P', 'UP']:   # Up arrow goes to prev grid
            cmd = 'prev_grid'
        elif key == 'q':
            break
        elif key == 'm':
            # Map command
            print("\nType mapping name (e.g. d1_a): ", end="")
            name = sys.stdin.readline().strip()
            if name:
                if update_mapping(data, grid, bit, name):
                    print(f"Mapped {name}")
                else:
                    print("Invalid format")
                time.sleep(1)
                last_grid = -1 # Force redraw
        elif key == 'j':
            print("\nJump to (grid [bit]): ", end="")
            line = sys.stdin.readline().strip()
            parts = line.split()
            if len(parts) >= 1:
                try:
                    grid = int(parts[0])
                    if len(parts) >= 2:
                        bit = int(parts[1])
                    else:
                        bit = 0
                    if grid > 15: grid = 15
                    if grid < 0: grid = 0
                    if bit > 11: bit = 11
                    if bit < 0: bit = 0
                except:
                    pass
            last_grid = -1
        elif key == 's':
            save_data(data)
            time.sleep(1)
            last_grid = -1
            
        # Process Movement
        if cmd == 'next_bit':
            bit += 1
            if bit > 11:
                bit = 0
                grid += 1
                if grid > 15: grid = 0
        elif cmd == 'prev_bit':
            bit -= 1
            if bit < 0:
                bit = 11
                grid -= 1
                if grid < 0: grid = 15
        elif cmd == 'next_grid':
            grid += 1
            if grid > 15: grid = 0
            bit = 0
        elif cmd == 'prev_grid':
            grid -= 1
            if grid < 0: grid = 15
            bit = 0

    display.clear()
    print("\nExiting.")

if __name__ == "__main__":
    main()
