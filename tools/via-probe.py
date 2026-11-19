"""Read-only check that an RK R65 (342D:E508) speaks the VIA protocol.

Prints the USB strings, VIA protocol version, layer/macro counts and the
layer-0 keymap as a 5x16 grid. Sends only GET commands; nothing is written.

    python tools/via-probe.py
"""
import sys

import hid

VID, PID = 0x342D, 0xE508
ROWS, COLS = 5, 16


def open_raw_hid():
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == 0xFF60 and d["usage"] == 0x61:
            h = hid.device()
            h.open_path(d["path"])
            return h, d
    sys.exit(f"No VIA raw HID interface found for {VID:04X}:{PID:04X}. Is the keyboard plugged in by USB?")


h, info = open_raw_hid()


def cmd(*data):
    h.write(b"\x00" + bytes(data) + bytes(32 - len(data)))
    return bytes(h.read(32, 1000))


print(f"device            : {info['manufacturer_string']} {info['product_string']} "
      f"({VID:04X}:{PID:04X}, release 0x{info['release_number']:04X})")
r = cmd(0x01)
print(f"protocol version  : {(r[1] << 8) | r[2]} (12 = VIA v3)")
print(f"layers            : {cmd(0x11)[1]}")
print(f"macros            : {cmd(0x0C)[1]}")
r = cmd(0x0D)
print(f"macro buffer      : {(r[1] << 8) | r[2]} bytes")
r = cmd(0x14, 0, 0, 0), cmd(0x14, 0, 0, 1)
print(f"encoder 0 ccw/cw  : 0x{(r[0][4] << 8) | r[0][5]:04x} / 0x{(r[1][4] << 8) | r[1][5]:04x}")

print("\nlayer 0 keymap (row x col, 0000 = no switch):")
print("      " + " ".join(f"c{c:<3}" for c in range(COLS)))
for row in range(ROWS):
    codes = []
    for col in range(COLS):
        r = cmd(0x04, 0, row, col)
        codes.append(f"{(r[4] << 8) | r[5]:04x}")
    print(f"r{row}    " + " ".join(codes))
h.close()
