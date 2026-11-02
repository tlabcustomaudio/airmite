<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo/airmite-wordmark-dark.svg">
    <img alt="AirMite" src="docs/logo/airmite-wordmark-light.svg" width="420">
  </picture>
</h1>

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-support-yellow?logo=buymeacoffee)](https://buymeacoffee.com/tlabcustom)

Tiny temperature + humidity sensors for **Home Assistant**, built on an ESP32-C3 and a
Sensirion SHT40/41 (or a Bosch BME280 outdoors, with pressure, or an SCD41 with CO2 on a 2.8" touch display). You don't need to write any code or edit any files:

1. flash the firmware from the browser,
2. type in your Wi-Fi,
3. pick the room in Home Assistant,
4. set the calibration offsets from Home Assistant.

**Compatible with [CapillAir](https://github.com/tlabcustomaudio/CapillAir).** Every AirMite reports
temperature, relative humidity and **absolute humidity** (g/m³), the readings CapillAir uses to
compare each room with the outdoor air. Name the device after the room (step 3) and its entities
match: `sensor.<room>_temperature`, `sensor.<room>_absolute_humidity`.

## The variants

| | Board | Power | Firmware |
|---|---|---|---|
| **AirMite USB** | ESP32-C3 SuperMini | USB-C, always on, updates every 30 s | [airmite-usb.factory.bin](https://github.com/tlabcustomaudio/airmite/releases/latest/download/airmite-usb.factory.bin) |
| **AirMite USB Plus** | ESP32-C3 SuperMini **Plus** | USB-C, always on, updates every 30 s | [airmite-usb-plus.factory.bin](https://github.com/tlabcustomaudio/airmite/releases/latest/download/airmite-usb-plus.factory.bin) |
| **AirMite Outdoor** | ESP32-C3 SuperMini **Plus** + **BME280** | USB-C, always on, updates every 30 s, adds **Pressure** | [airmite-outdoor.factory.bin](https://github.com/tlabcustomaudio/airmite/releases/latest/download/airmite-outdoor.factory.bin) |
| **AirMite CYD** | Guition ESP32-2432S028R (CYD 2.8" touch) + **SCD41** | USB, 5 V / 1 A, always on, adds **CO2**, screen and HEAT/COOL buttons | [airmite-cyd.factory.bin](https://github.com/tlabcustomaudio/airmite/releases/latest/download/airmite-cyd.factory.bin) |
| **AirMite Battery** | Seeed Studio XIAO ESP32-C3 | 1S LiPo, wakes every 15 min (months per charge), charges from USB-C | [airmite-battery.factory.bin](https://github.com/tlabcustomaudio/airmite/releases/latest/download/airmite-battery.factory.bin) |

Every variant shows these entities in Home Assistant:
- **Temperature**, **Humidity**, **Absolute humidity**.
- **Temperature offset** and **Humidity offset** (settings).
- The outdoor variant also has **Pressure** (hPa).
- The CYD variant also has **CO2**, a **Calibrate CO2** button, CO2 offset, alert thresholds, screen settings (brightness, night window, skin, rotation, alternate clock) and **Room cold** / **Stale air** / **High humidity** alerts.
- The battery variant also has **Battery** (%), **Battery Voltage**, **USB Power**, **Battery divider factor** and **Prevent Deep Sleep**. Turn Prevent Deep Sleep on to keep it awake for an update; turning it off sends it back to sleep.

## Shopping list

**AirMite USB / USB Plus**
- 1× ESP32-C3 SuperMini (or SuperMini Plus)
- 1× SHT40 or SHT41 breakout (I2C, with pull-ups)
- 4 short wires (~10 cm)
- 1× USB-C cable + 5 V USB power supply

**AirMite Outdoor**
- 1× ESP32-C3 SuperMini Plus
- 1× BME280 breakout (I2C, 3.3 V, address 0x76; not the BMP280, which has no humidity)
- 4 wires (~10 cm)
- 1× USB-C cable long enough for outdoors + 5 V USB power supply
- 1× radiation shield (Stevenson screen)

**AirMite CYD**
- 1× Guition ESP32-2432S028R ("Cheap Yellow Display" 2.8", ILI9341; the board usually comes with its CN1 cable)
- 1× Sensirion SCD41 breakout (I2C)
- 1× 4-pin cable for CN1 (JST 1.25 mm), or 4 wires
- 1× USB cable (micro-USB or USB-C, depending on the board revision) + 5 V / 1 A power supply

**AirMite Battery**
- 1× Seeed Studio XIAO ESP32-C3 (with its IPEX antenna)
- 1× SHT40 or SHT41 breakout (I2C, with pull-ups)
- 1× LiPo 3.7 V 1S, ~300–1000 mAh (with protection PCB preferred)
- Resistors (1/4 W): 2× 220k, 1× 100k, 1× 150k
- Wire; a USB-C cable to charge

3D-printable enclosures for every variant are coming on MakerWorld; the link will be here.

## Wiring

All ESP32-C3 variants use the same sensor wiring: **SDA → GPIO5**, **SCL → GPIO6**, **VIN → 3V3**
(never 5V), **GND → GND**.

### AirMite USB / USB Plus

![Wiring, USB](docs/wiring-usb.png)

![Schematic, USB](docs/schematic-usb.png)

### AirMite Outdoor

Same four wires as the USB picture, with a BME280 in place of the SHT41. Not GPIO8/9: on the
Plus, GPIO8 drives the RGB LED, and I2C traffic there lights it up and warms the sensor.
The firmware expects address 0x76 (most breakouts); a board with SDO tied high is 0x77.

### AirMite CYD

The SCD41 goes on the board's **CN1** connector: **3V3 → VIN**, **GND → GND**, **IO27 → SDA**,
**IO22 → SCL** (the only free I2C on this board). Keep the sensor below the screen, not against the board:
the display heats it (the firmware already corrects for the backlight).

- **HEAT** and **COOL** toggle `switch.heat` and `switch.cool` (any entity that `homeassistant.toggle` handles:
  switch, input_boolean, light, climate...). **Hold 0.8 s**: a short tap only shows a hint. Give your entities
  those ids, or build it yourself with `heat_entity` / `cool_entity` set.
- In HA: **Settings → Devices → ESPHome → the device → Configure → Allow the device to perform Home Assistant
  actions**. Without it the buttons do nothing.
- Wi-Fi can also be set on the screen: gear → **WIFI** (scans the networks, on-screen keyboard).
- CO2: automatic self-calibration is off (lived-in rooms never reach 420 ppm). Calibrate it outdoors after 5
  minutes in fresh air: hold the button on **CALIB.** or press **Calibrate CO2** in HA. It stays in the
  sensor. Repeat every 6–12 months.
- Some boards ship an ST7789 instead of the ILI9341: if the screen stays white, change `model:`.

### AirMite Battery

![Wiring, battery](docs/wiring-battery.png)

![Schematic, battery](docs/schematic-battery.png)

Besides the sensor, it needs:
- **R1/R2**, 220k + 220k, from BAT+ to GND, middle to **D1/GPIO3**: this measures the battery.
- **R3/R4**, 100k + 150k, from 5V to GND, middle to **D2/GPIO4**: this tells the board USB is plugged in. With USB plugged in it stays awake.

## 1. Flash the firmware

1. Download the `.factory.bin` for your board (table above, or [Releases](https://github.com/tlabcustomaudio/airmite/releases)).
2. Open **<https://web.esphome.io>** in Chrome or Edge and plug the board in by USB.
3. **Connect** → choose the port → **Install** → pick the file you downloaded.
4. When it's done, the page asks for your **Wi-Fi** name and password. Type them in.

If the board isn't detected, hold **BOOT** while plugging it in.

If you skipped the Wi-Fi step, or later change your Wi-Fi: when the sensor can't connect, it opens its own
**"AirMite setup"** hotspot. Join it from a phone and choose your network.

## 2. Add it to Home Assistant

You need the **ESPHome** integration; Home Assistant offers it by itself.

1. Go to **Settings → Devices & services**. The sensor appears under **Discovered** as *AirMite*.
2. Click **Add**, then choose the **room (area)**.
3. Open the device and rename it after the room with ✏️ (e.g. *Kitchen*). When Home Assistant asks
   whether to rename the entity IDs too, say **yes**. The entities become
   `sensor.kitchen_temperature` and so on; this is what CapillAir looks for.

To move the sensor to another room later: open the device → ✏️ → **Area**.

## 3. Calibrate

No sensor is perfect, and a board that is always on warms its own sensor a little. To correct it:

1. Put the AirMite next to a thermometer/hygrometer you trust for **about an hour**.
2. Open the device in Home Assistant. Under **Configuration**, set:
   - **Temperature offset** = reference − AirMite. AirMite 22.5 °C, reference 21.0 °C → **−1.5**.
   - **Humidity offset** = reference − AirMite. AirMite 52 %, reference 55 % → **+3**.

The sensor stores the offsets itself, so they survive reboots, power cuts and firmware updates.

**USB Plus** starts at −1.7 °C / +3.8 %, measured on one board. Check yours anyway.

**Outdoor:** calibrate it indoors next to the reference, before you mount it outside. The
humidity reading follows the temperature offset by itself (same water content at the corrected
temperature), so the humidity offset is only what is left after that.

**Battery:** the board is awake only a few seconds every 15 minutes. To change a setting, plug
USB in (it then stays awake), change it, and unplug.

**Battery divider factor:** leave it at 2.0 if you used 220k + 220k. To check it, charge the
cell full with USB plugged in; the cell is then at 4.20 V. If **Battery Voltage** shows something
else, set factor = old factor × 4.20 ÷ the reading.

## Updates

Firmware updates go over Wi-Fi. If you use the **ESPHome Device Builder** add-on, the discovered AirMite shows
**Take control**: it then compiles and updates it for you, with your own Wi-Fi in `secrets.yaml`.
Without it, flash the new `.factory.bin` over USB as in step 1. The stored offsets stay.

## Build it yourself

`firmware/` holds plain ESPHome configs. `common.yaml` is the shared part, `sht4x.yaml` / `bme280.yaml` the
sensor, and each board file adds only what is different:

```bash
esphome run firmware/airmite-usb.yaml
```

No `secrets.yaml` needed. `tools/drawings.py` redraws the pictures in `docs/` and `tools/logo.py`
the wordmark (matplotlib + fontTools).

Using AirMite for your own sensors with your own keys and fixed IPs: write a small config that
includes the variant as a package and adds `api: encryption`, an OTA password and `wifi: manual_ip`.
Set `name_add_mac_suffix: false` to keep a fixed hostname. Firmware substitutions you can set:
`name`, `friendly_name`, `t_offset`, `rh_offset` (starting offsets), on the battery variant
`bat_factor`, on the CYD `heat_entity`, `cool_entity`, `altitude`, `co2_good`, `co2_bad`, `notify_action`.

**Security note:** shared firmware cannot carry your keys, so the API has no encryption key and
OTA has no password. Anyone on your local network could read or reflash the sensor. If that
matters to you, add `api: encryption: key:` and an OTA password in your own copy.

## License

MIT. Made by [T Lab](https://github.com/tlabcustomaudio). The wordmark uses
[Outfit](https://fonts.google.com/specimen/Outfit) (SIL Open Font License), converted to outlines.

If AirMite saves you time, you can support it on [Buy Me a Coffee](https://buymeacoffee.com/tlabcustom).
