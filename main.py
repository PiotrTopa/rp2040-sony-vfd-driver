from vfd import PT6315
import time

# Pin Configuration (RP2040-Zero)
PIN_CLK = 4
PIN_DAT = 3
PIN_STB = 5

def main():
    print("Initializing Sony VFD Driver (PT6315)...")
    
    # Initialize Driver
    display = PT6315(clk_pin=PIN_CLK, din_pin=PIN_DAT, stb_pin=PIN_STB)
    
    print("Display Initialized.")
    # Reduce brightness to test if it's a power issue
    display.set_brightness(1) 
    
    # Test Icons
    print("Testing Icons...")
    display.set_icon('icon_mp3', 1)
    display.flush()
    time.sleep(0.5)
    display.set_icon('icon_pgm', 1)
    display.flush()
    time.sleep(0.5)
    
    # Keep Icons ON to see if they persist
    print("Icons ON. Waiting...")
    time.sleep(2)
    
    display.clear()
    
    # Test Strings
    print("Testing Strings...")
    
    # "SONY" - S(d3), O(d2), N(d1), Y(d0)
    display.write_string("SONY")
    
    # Debug: Re-send display control periodically to see if it fixes degradation
    print("SONY Displayed. Loop check...")
    for i in range(20):
        time.sleep(0.1)
        # Optional: Force re-flush or brightness set to keep it alive
        # display.flush() 
        # display.set_brightness(1)
    
    display.write_string("PLAY")
    display.set_icon('icon_play', 1)
    display.flush()
    time.sleep(2)
    
    # Counter
    for i in range(100):
        display.write_string(f"{i:4}") # Padded to 4 chars
        time.sleep(0.1)
        
    print("Done.")

if __name__ == "__main__":
    main()
