"""Read-only backup of an RK R65 (342D:E508): every layer, the knob, macros and lighting.

    python tools/via-dump.py [output.json]     (default: backup.json)

Sends only GET commands; nothing is written to the keyboard.
"""
import json
import sys

import hid

VID, PID = 0x342D, 0xE508
ROWS, COLS = 5, 16

out_path = sys.argv[1] if len(sys.argv) > 1 else "backup.json"

dev = next((d for d in hid.enumerate(VID, PID) if d["usage_page"] == 0xFF60 and d["usage"] == 0x61), None)
if dev is None:
    sys.exit(f"No VIA raw HID interface found for {VID:04X}:{PID:04X}.")
h = hid.device()
h.open_path(dev["path"])


def cmd(*data):
    h.write(b"\x00" + bytes(data) + bytes(32 - len(data)))
    return bytes(h.read(32, 1000))


def read_buffer(command, size):
    buf = b""
    for off in range(0, size, 28):
        n = min(28, size - off)
        buf += cmd(command, off >> 8, off & 0xFF, n)[4:4 + n]
    return buf


layers = cmd(0x11)[1]
size = layers * ROWS * COLS * 2
raw = read_buffer(0x12, size)
words = [(raw[i] << 8) | raw[i + 1] for i in range(0, size, 2)]
keymap = [[[words[(l * ROWS + r) * COLS + c] for c in range(COLS)] for r in range(ROWS)] for l in range(layers)]

encoders = []
for l in range(layers):
    ccw, cw = cmd(0x14, l, 0, 0), cmd(0x14, l, 0, 1)
    encoders.append([(ccw[4] << 8) | ccw[5], (cw[4] << 8) | cw[5]])

r = cmd(0x0D)
macro_size = (r[1] << 8) | r[2]
macros = read_buffer(0x0E, macro_size)

rgb = {name: list(cmd(0x08, 3, vid)[:6]) for name, vid in
       [("brightness", 1), ("effect", 2), ("speed", 3), ("color", 4)]}

json.dump({"vid": hex(VID), "pid": hex(PID), "rows": ROWS, "cols": COLS, "layers": layers,
           "keymap": keymap, "encoders": encoders, "macro_buffer_hex": macros.hex(),
           "rgb_raw": rgb}, open(out_path, "w"), indent=1)
print(f"saved {layers} layers, {len(encoders)} encoder maps and {macro_size}-byte macro buffer to {out_path}")
h.close()
