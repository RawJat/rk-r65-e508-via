"""Read-only check that the keyboard sends exactly one reply per VIA command.

Useful when usevia.app logs "Receiving incorrect response for command": if every
command below gets exactly one matching reply, the keyboard is fine and the
problem is on the browser side (usually a second VIA tab). Close usevia.app
before running this, or its traffic will show up here too.

    python tools/via-reply-check.py
"""
import sys
import time

import hid

VID, PID = 0x342D, 0xE508

dev = next((d for d in hid.enumerate(VID, PID) if d["usage_page"] == 0xFF60 and d["usage"] == 0x61), None)
if dev is None:
    sys.exit(f"No VIA raw HID interface found for {VID:04X}:{PID:04X}.")
h = hid.device()
h.open_path(dev["path"])

stale = []
while (r := h.read(32, 200)):
    stale.append(bytes(r[:4]).hex(" "))
print(f"stale reports before test: {len(stale)} {stale[:10]}")

ok = True
for c in [(0x01,), (0x11,), (0x0D,), (0x08, 3, 1), (0x12, 0, 0, 28)]:
    h.write(b"\x00" + bytes(c) + bytes(32 - len(c)))
    got, t0 = [], time.time()
    while (r := h.read(32, 400)):
        got.append((round((time.time() - t0) * 1000), bytes(r[:6]).hex(" ")))
    good = len(got) == 1 and bytes.fromhex(got[0][1])[0] == c[0]
    ok &= good
    print(f"cmd {bytes(c).hex(' '):12s} -> {len(got)} reply(s) {'OK' if good else 'UNEXPECTED'}: {got}")
print("\nkeyboard replies look correct" if ok else "\nkeyboard replies look wrong")
h.close()
