from machine import Pin
import time
from font import ICONS, CHAR_POSITIONS, FONT_14SEG

class PT6315:
    """
    Driver for PT6315 VFD Controller using MicroPython.
    Sony 1-869-725-12 Panel.
    Standard 12G/16S Mode.
    """
    
    # Command Definitions
    CMD_MODE_SET     = 0x00
    CMD_DATA_SET     = 0x40
    CMD_ADDR_SET     = 0xC0
    CMD_DISPLAY_CTRL = 0x80

    # Display Modes (Grid / Segment)
    MODE_12_DIG_16_SEG = 0x08 # Standard PT6315 12-Digit Mode

    # Display Control
    DISP_OFF = 0x00
    DISP_ON  = 0x08
    DIMMING_MAX = 0x07

    def __init__(self, clk_pin, din_pin, stb_pin):
        self.clk = Pin(clk_pin, Pin.OUT)
        self.din = Pin(din_pin, Pin.OUT)
        self.stb = Pin(stb_pin, Pin.OUT)
        
        # Idle State
        self.clk.value(1)
        self.stb.value(1)
        self.din.value(0)
        
        # Buffer: 63 Bytes (Avoid 0x3F which crashes VFD)
        self.buffer = bytearray(63) 
        
        time.sleep_ms(100)
        self.init_display()

    def _write_byte(self, data):
        # LSB First
        for i in range(8):
            self.clk.value(0)
            self.din.value((data >> i) & 0x01)
            time.sleep_us(1)
            self.clk.value(1)
            time.sleep_us(1)

    def send_command(self, cmd):
        self.stb.value(0)
        time.sleep_us(1)
        self._write_byte(cmd)
        time.sleep_us(1)
        self.stb.value(1)
        time.sleep_us(1)

    def send_data(self, addr, data_bytes):
        # 1. Set Data Write Mode
        self.stb.value(0)
        time.sleep_us(1)
        self._write_byte(self.CMD_DATA_SET)
        time.sleep_us(1)
        self.stb.value(1)
        time.sleep_us(1)

        # 2. Set Address and Write Data
        self.stb.value(0)
        time.sleep_us(1)
        self._write_byte(self.CMD_ADDR_SET | (addr & 0x3F))
        for b in data_bytes:
            self._write_byte(b)
        time.sleep_us(1)
        self.stb.value(1)
        time.sleep_us(1)

    def init_display(self):
        self.stb.value(1)
        self.clk.value(1)
        time.sleep_ms(10)
        
        self.send_command(self.CMD_MODE_SET | self.MODE_12_DIG_16_SEG)
        self.clear()
        self.send_command(self.CMD_DISPLAY_CTRL | self.DISP_ON | self.DIMMING_MAX)

    def clear(self):
        for i in range(len(self.buffer)):
            self.buffer[i] = 0x00
        self.flush()

    def flush(self):
        """Send entire buffer to display."""
        self.send_data(0x00, self.buffer)

    def set_brightness(self, level):
        if level < 0: level = 0
        if level > 7: level = 7
        self.send_command(self.CMD_DISPLAY_CTRL | self.DISP_ON | level)

    def set_mode(self, mode):
        self.send_command(self.CMD_MODE_SET | mode)

    def write_leds(self, bitmap):
        # 0x41 = Write LED Port
        self.stb.value(0)
        time.sleep_us(1)
        self._write_byte(0x41)
        time.sleep_us(1)
        self._write_byte(bitmap & 0x0F)
        time.sleep_us(1)
        self.stb.value(1)
        time.sleep_us(1)

    def set_pixel(self, grid, bit, state):
        """Set a specific Grid/Bit in the buffer."""
        addr_base = grid * 2
        if bit < 8:
            byte_idx = addr_base
            bit_mask = 1 << bit
        else:
            byte_idx = addr_base + 1
            bit_mask = 1 << (bit - 8)
            
        if byte_idx < len(self.buffer):
            if state:
                self.buffer[byte_idx] |= bit_mask
            else:
                self.buffer[byte_idx] &= ~bit_mask

    def set_icon(self, name, state):
        if name in ICONS:
            grid, bit = ICONS[name]
            self.set_pixel(grid, bit, state)

    def write_char(self, char_pos_idx, char):
        if char_pos_idx >= len(CHAR_POSITIONS):
            return 
        
        mapping = CHAR_POSITIONS[char_pos_idx]
        segments = FONT_14SEG.get(char.upper(), [])
        
        for seg_name, (grid, bit) in mapping.items():
            self.set_pixel(grid, bit, 0)
            
        for seg in segments:
            if seg in mapping:
                grid, bit = mapping[seg]
                self.set_pixel(grid, bit, 1)

    def write_string(self, text):
        text = text[:len(CHAR_POSITIONS)]
        target_pos = 0
        for i in range(len(text) - 1, -1, -1):
            char = text[i]
            self.write_char(target_pos, char)
            target_pos += 1
        self.flush()
