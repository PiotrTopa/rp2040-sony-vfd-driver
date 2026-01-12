# Wiring Documentation

## Hardware Specification
- **Display:** Sony VFD Model 1-869-725-12
- **Controller:** PT6315 (NEC/Renesas compatible)
- **MCU:** RP2040-Zero
- **Power Supply:** Dual Rail (12V Input)

## Connection Diagram (Pinout)

### RP2040 <-> VFD (PT6315)

| RP2040 Pin | GPIO | Function | VFD Pin | Description |
|------------|------|---------|---------|------|
| 3.3V Out   | -    | Logic Power | 1 | PT6315 Logic Power (+3.3V) |
| GND        | -    | Ground  | 2, 9    | Common Ground (Logic & Power GND) |
| GP5        | 5    | SPI CS  | 3       | Chip Select / Strobe (FL STB) |
| GP4        | 4    | SPI CLK | 4       | Clock (FL CLK) |
| GP3        | 3    | SPI DATA| 5       | Data Input (FL DATA) |

### Power Supply Section
**Main Input:** 12V-14V DC

1.  **Rail A (MCU):**
    -   12V -> Mini-360 DC-DC (#2) -> **5.0V**
    -   5.0V -> RP2040 `5V` Pin (LDO drops it to 3.3V for logic)

2.  **Rail B (VFD Power):**
    -   12V -> Mini-360 DC-DC (#1) -> **6.2V**
    -   6.2V -> VFD Pin 8 (Filament/Anodes)
    -   *Note:* The VFD PCB generates the negative anode voltage internally.

### Other (RS485 - Currently Unused)
| RP2040 GPIO | Function | Connection |
|-------------|---------|------------|
| GP0         | UART TX | MAX3485 DI |
| GP1         | UART RX | MAX3485 RO |
| GP2         | DIR     | MAX3485 RE/DE |

### Additional Notes
-   Pins 6 (LED DIRECT) and 7 (LED OSOK) control transistors for Standby/On LEDs - left unconnected for now.
-   **Important:** Ensure 5V (MCU logic) is stable before applying 6.2V to the VFD to avoid latch-up, although with a common 12V source they start simultaneously which is fine.
