# Sony VFD Font & Mapping Definitions
import json

MAPPING_FILE = "mappings.json"

def load_mappings():
    try:
        with open(MAPPING_FILE, "r") as f:
            data = json.load(f)
            
        icons = {}
        for name, val in data.get("icons", {}).items():
            icons[name] = tuple(val)
            
        char_pos = []
        for char_map in data.get("char_positions", []):
            converted_map = {}
            for seg, val in char_map.items():
                converted_map[seg] = tuple(val)
            char_pos.append(converted_map)
            
        return icons, char_pos
    except Exception as e:
        print(f"Error loading {MAPPING_FILE}: {e}")
        # Return empty/default to avoid crash if file missing
        return {}, [{}, {}, {}, {}, {}, {}, {}, {}, {}]

ICONS, CHAR_POSITIONS = load_mappings()

# 14-Segment Font Definition (ASCII -> List of Segments)
FONT_14SEG = {
    ' ': [],
    '0': ['a', 'b', 'c', 'd', 'e', 'f'],
    '1': ['b', 'c'],
    '2': ['a', 'b', 'g1', 'g2', 'e', 'd'],
    '3': ['a', 'b', 'g1', 'g2', 'c', 'd'],
    '4': ['f', 'g1', 'g2', 'b', 'c'],
    '5': ['a', 'f', 'g1', 'g2', 'c', 'd'],
    '6': ['a', 'f', 'e', 'd', 'c', 'g1', 'g2'],
    '7': ['a', 'b', 'c'],
    '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g1', 'g2'],
    '9': ['a', 'b', 'c', 'd', 'f', 'g1', 'g2'],
    'A': ['a', 'b', 'c', 'e', 'f', 'g1', 'g2'],
    'B': ['a', 'b', 'c', 'd', 'e', 'f', 'g1', 'g2'], # 8-like
    'C': ['a', 'f', 'e', 'd'],
    'D': ['a', 'b', 'c', 'd', 'e', 'f'], # 0-like
    'E': ['a', 'f', 'g1', 'g2', 'e', 'd'],
    'F': ['a', 'f', 'g1', 'g2', 'e'],
    'H': ['f', 'e', 'g1', 'g2', 'b', 'c'],
    'I': ['b', 'c'], # Simple I
    'L': ['f', 'e', 'd'],
    'M': ['f', 'e', 'b', 'c', 'h', 'i'],
    'N': ['f', 'e', 'b', 'c', 'h', 'k'],
    'O': ['a', 'b', 'c', 'd', 'e', 'f'],
    'P': ['a', 'b', 'g1', 'g2', 'f', 'e'],
    'R': ['a', 'b', 'g1', 'g2', 'f', 'e', 'k'],
    'S': ['a', 'f', 'g1', 'g2', 'c', 'd'],
    'T': ['a', 'j', 'm'], 
    'Y': ['h', 'j', 'l'], 
    'U': ['f', 'e', 'd', 'c', 'b'],
    '-': ['g1', 'g2'],
    '_': ['d'],
}
