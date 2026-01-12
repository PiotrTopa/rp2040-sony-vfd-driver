from vfd import PT6315
import time
from font import CHAR_POSITIONS, FONT_14SEG

# Pin Configuration (RP2040-Zero)
PIN_CLK = 4
PIN_DAT = 3
PIN_STB = 5

def main():
    print("Initializing Sony VFD Driver (PT6315)...")
    
    display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
    display.set_brightness(7)
    display.clear()
    
    print(f"Loaded {len(CHAR_POSITIONS)} digits (d0-d{len(CHAR_POSITIONS)-1})")
    
    # 1. All Segments Test
    print("Test 1: All Segments On")
    display.write_string("88888888")
    display.flush()
    time.sleep(1)
    
    # 2. Cycling Digits
    print("Test 2: Cycling Digits")
    for i in range(len(CHAR_POSITIONS)):
        display.clear()
        display.write_char(i, '8')
        display.flush()
        print(f"Digit d{i} ON")
        time.sleep(0.5)
        
    # 3. Text Demo
    print("Test 3: Text Demo (Slower)")
    texts = ["HELLO", "SONY", "VFD", "RP2040", "GOOD", "BYTE"]
    for t in texts:
        display.clear()
        print(f"Displaying: {t}")
        
        # Simulate what is being written to console
        # Text writes backwards from d0 (Right)
        # "SONY" -> Y(d0), N(d1), O(d2), S(d3)
        
        debug_str = []
        target_pos = 0
        for i in range(len(t) - 1, -1, -1):
            char = t[i]
            segs = FONT_14SEG.get(char.upper(), [])
            debug_str.append(f"d{target_pos}='{char}' {segs}")
            target_pos += 1
        print("  Mapping: " + " | ".join(debug_str))
        
        display.write_string(t)
        time.sleep(2.0) # Slower
        
    # 4. Icon Test
    print("Test 4: Icons")
    display.clear()
    from font import ICONS
    for icon_name in ICONS.keys():
        print(f"Icon: {icon_name}")
        display.set_icon(icon_name, 1)
        display.flush()
        time.sleep(0.1)
        
    time.sleep(1)
    display.clear()
    
    # 5. Counter
    print("Test 5: Counter")
    for i in range(1000):
        s = f"{i:>8}"
        display.write_string(s)
        time.sleep(0.05)
        
    print("Done.")

if __name__ == "__main__":
    main()
