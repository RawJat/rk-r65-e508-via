# rk-r65-e508-via

A working [VIA](https://usevia.app) definition for the **Royal Kludge R65 (wired, ANSI)** revision that reports USB ID **`342D:E508`**.

RK's official R65 JSON is for product ID `E481`, and the community firmware repos target `E453`. On this revision VIA either can't find the board or maps keys to the wrong places. The stock firmware already supports VIA, so **you don't need to flash anything**. You only need the right definition file.

## Is this your keyboard?

The USB product string should be `RK-R65`, the manufacturer `Hangsheng`, and the ID `342D:E508`.

- **Windows:** Device Manager → Keyboards → HID Keyboard Device → Properties → Details → Hardware Ids. Look for `VID_342D&PID_E508`.
- **Or** run `python tools/via-probe.py` (see [Tools](#tools)).

If your ID is different, this file won't work for you.

## Usage

1. Download [`rk-r65-e508-via.json`](rk-r65-e508-via.json).
2. Open https://usevia.app in a Chromium browser such as Chrome or Edge.
3. Open Settings (gear icon) and turn on **Show Design tab**.
4. On the **Design** tab, click **Load Draft Definition** and select the JSON.
5. On the **Configure** tab, click **Authorize device** and choose **RK-R65**.

The definition is saved in that browser. If you switch browsers or clear site data, load it again.

## What's different from RK's JSON

Your board's key grid is **5 rows × 16 columns**, not 5 × 15. These keys sit at different positions:

| Key | RK JSON (`E481`) | This board (`E508`) |
|---|---|---|
| Knob press (Mute) | 0,14 | **0,15** |
| Enter | 2,13 | **2,12** |
| Right Alt | 4,8 | **4,9** |
| Fn | 4,9 | **4,10** |

All 67 key positions in the definition were checked against the live keymap read from the board. The knob (turn left/right on every layer) and the Lighting menu (brightness, effect, speed, color) also work.

## Firmware facts (stock, release `0x000E`)

- VIA protocol 12 (VIA v3), **9 layers**, **16 macros** (386-byte buffer), 1 encoder.
- **Layers come in pairs, one pair per mode:** Windows uses 0/1, Mac uses 2/3, and 4/5 and 6/7 are alternate F-key and media modes. **Fn+S** and **Fn+A** switch modes. If an edit seems to do nothing, check that you're editing the layer for the mode you're in.
- Some keys use RK-only keycodes that VIA shows as hex: `0x7E07` (Fn+Enter), `0x7E55` (Fn+Z), `0x7E58` (Fn+LCtrl), plus `0x7E08`/`0x7E09` on layer 8. RK doesn't document them, so leave them alone unless you want to replace them.
- **Fn+Space clears all saved settings (`EE_CLR`)**, including your VIA changes. Remap it on layers 1/3/5/7 if you don't want that, and save a copy from VIA's Save + Load tab.
- **Fn+RShift+Esc** enters the bootloader.

[`stock-keymap.json`](stock-keymap.json) is a raw dump of the factory keymap on all 9 layers, plus the knob and lighting settings.

## Troubleshooting

**"VIA could not find a V3 definition for RK-R65"**
The definition isn't loaded yet. Do steps 3–4 above with *this* file, not RK's `R65 Wired Windows QMK.json`.

**Console shows "Receiving incorrect response for command" and the keymap never loads**
Each reply VIA receives belongs to an earlier command. This happens in the browser, not the keyboard (`tools/via-reply-check.py` shows one correct reply per command). To fix it:
1. Close **all** usevia.app tabs.
2. Unplug the keyboard and plug it back in.
3. Open a single new tab and authorize the keyboard again.

If it still fails, try Chrome or Edge instead of Brave.

## Tools

Read-only Python scripts that talk to the keyboard using VIA's own protocol. They only *read*; nothing is written to the board. Close usevia.app before running them.

```sh
pip install -r requirements.txt
python tools/via-probe.py         # device info, protocol, layer/macro counts, layer-0 grid
python tools/via-dump.py out.json # back up every layer, knob, macros and lighting
python tools/via-reply-check.py   # confirm one reply per command
```

## Firmware warning

The public R65 QMK sources ([RK/hangshengkeji](https://github.com/hangshengkeji/qmk_firmware/tree/master/keyboards/rk/R65), [irfanjmdn/r65](https://github.com/irfanjmdn/r65), [iamdanielv/kb_rk_r65](https://github.com/iamdanielv/kb_rk_r65), [jmkl/rk65](https://github.com/jmkl/rk65)) are for the 2024 `E453` board. There is no public source for `E508`. Flashing those builds on this revision could stop the keyboard working, and you don't need to: the stock firmware already gives you full VIA support.

## Credits

The lighting menu and effect list come from Royal Kludge's official R65 VIA definition. The key grid was mapped from the live `E508` firmware.
