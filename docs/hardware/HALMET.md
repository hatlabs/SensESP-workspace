# HALMET Hardware Reference

**Hat Labs Marine Engine and Tank Interface**

Online docs: https://docs.hatlabs.fi/halmet/

## Microcontroller

- **MCU**: ESP32-WROOM-32E
- **Flash**: 16 MB
- **WiFi**: 802.11 b/g/n (2.4 GHz)
- **Bluetooth**: BLE 4.2

## Power

- **Input**: 5-32V DC via NMEA 2000 connector
- **Protection**: 500 mA self-resetting fuse, reverse polarity diode, TVS overvoltage/ESD protection, two-stage noise filtering
- **Isolation**: Galvanic isolation between inputs and ESP32 (isolated DC/DC converter + digital isolators). Safe to power from NMEA 2000 without ground loops.

## Pin Assignments

| GPIO | Function | Notes |
|------|----------|-------|
| 18 | CAN RX | NMEA 2000 receive |
| 19 | CAN TX | NMEA 2000 transmit |
| 21 | I2C SDA | Shared bus |
| 22 | I2C SCL | Shared bus |
| 4 | 1-Wire | DS18B20 temperature sensors |
| 23 | Digital Input 1 | Optoisolated, Schmitt trigger |
| 25 | Digital Input 2 | Optoisolated, Schmitt trigger |
| 27 | Digital Input 3 | Optoisolated, Schmitt trigger |
| 26 | Digital Input 4 | Optoisolated, Schmitt trigger |

## GPIO Expansion Header

**J201**, a 2x10 pin header, breaks out the 13 GPIOs the product page counts as available. The signals below were read from [`ESP32.kicad_sch` at `e8bffda`](https://github.com/hatlabs/HALMET-hardware/blob/e8bffda7a83aede84c1d496083c84866a5130c25/ESP32.kicad_sch), which is the canonical source; the online docs give the count but no pinout. The remaining header pins carry power and ground. Re-read the schematic at a newer revision before trusting this table against a later board.

| Signal | GPIO | Usable as an output |
|--------|------|---------------------|
| IO5 | 5 | Yes, but it is a strapping pin |
| SENSOR_VP | 36 | No, input only |
| SENSOR_VN | 39 | No, input only |
| IO16 | 16 | Yes |
| IO17 | 17 | Yes |
| IO32 | 32 | Yes |
| IO33 | 33 | Yes |
| IO34 | 34 | No, input only |
| IO35 | 35 | No, input only |
| TDI | 12 | Yes, but it is a strapping pin (flash voltage) |
| TCK | 13 | Yes |
| TMS | 14 | Yes |
| TDO | 15 | Yes, but it is a strapping pin |

GPIO 13, 14, 16, 17, 32 and 33 are the pins with no strapping or input-only caveat. `ref/HALMET-example-firmware` drives GPIO 33 as its test output.

Driving a digital input from one of these pins is possible -- a 3.3 V swing is enough for the input stage -- and a test rig wired that way reads a tacho signal generated on the header. The wiring is not documented here: the digital inputs sit on their own ground domain behind the isolation barrier, so the signal and its return both have to be accounted for, and this page has not traced that path. Check the schematic before wiring one up.

## Analog Inputs

4 channels via **ADS1115** 16-bit ADC on I2C (address **0x4b**).

- **Voltage range**: 0-33V per channel
- **Resolution**: 16-bit
- **Isolation**: Galvanically isolated from ESP32
- **Filtering**: Low-pass at 160 Hz to reduce noise
- **Protection**: Under-voltage and over-voltage protection on each input
- **Constant-current source**: Optional 10 mA source per channel for resistance measurement (enable via CCS jumper headers). Max measurable resistance: 320 ohm.

## Digital Inputs

4 optoisolated inputs with Schmitt trigger for noise immunity.

- **Voltage range**: +/- 30V max
- **Active**: Input is considered active when voltage is applied (polarity independent due to optoisolation)
- **Use cases**: RPM/tacho signals, alarm switches, bilge pump status, ignition detection

## CAN / NMEA 2000

- **Pins**: GPIO 18 (RX), GPIO 19 (TX)
- **LEDs**: RX and TX activity LEDs on board
- **Connector**: NMEA 2000 compatible terminal block (also provides power)
- **Protocol**: NMEA 2000 at 250 kbps

## I2C

- **Pins**: GPIO 21 (SDA), GPIO 22 (SCL)
- **On-board devices**: ADS1115 ADC at address 0x4b
- **External**: 4-pin header for additional I2C sensors or OLED display

## 1-Wire

- **Pin**: GPIO 4
- **Connector**: 3-pin header (GND, 3V3, DQ)
- **Use**: DS18B20 temperature sensors (supports multiple sensors on one bus)

## User Interface

- **Reset button**: Resets the ESP32
- **Boot/user button**: Hold during reset to enter programming mode; available as general-purpose button in firmware
- **Red LED**: Power indicator
- **Blue LED**: User-programmable

## USB

- **Connector**: USB 2.0 (Micro-B or USB-C depending on revision)
- **Function**: Programming and serial debug output

## PlatformIO Configuration

Flash `halmet_espidf` on any device that talks to a TLS Signal K server. The `halmet` env builds faster and is fine for compile checks, but its precompiled libraries ignore `sdkconfig.defaults`, so the device runs out of memory against a TLS server.

```ini
; Arduino compile-check env (fast build, no TLS support)
[env:halmet]
extends = pioarduino, esp32
build_flags =
    ${pioarduino.build_flags}
    ${esp32.build_flags}

; Flash this one (ESP-IDF from source, TLS works)
[env:halmet_espidf]
extends = env:halmet
framework = espidf, arduino
lib_deps =
    ${env.lib_deps}
board_build.embed_txtfiles =
    managed_components/espressif__esp_insights/server_certs/https_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_mqtt_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_claim_service_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_ota_server.crt
```

The shared `[env]`, `[pioarduino]`, and `[esp32]` sections come from the project template. See `ref/SensESP-project-template/platformio.ini` for the full layout.

## Wiring Guide

### Temperature Sender (Resistive, e.g., VDO/Faria)
Connect the sender between an analog input and the isolated ground. Enable the CCS jumper for the channel to use constant-current resistance measurement.

### Pressure Sender (Resistive)
Same wiring as temperature sender. The resistance-to-pressure mapping depends on the specific sender model.

### Tank Level Sender (Resistive)
Same wiring pattern. Enable CCS jumper. Calibrate using known empty and full resistance values.

### RPM / Tacho Signal
Connect the tacho signal wire to a digital input. The signal ground connects to the isolated input ground. Use the `DigitalInputCounter` class in SensESP for pulse counting.

### NMEA 2000
Connect CAN H and CAN L from the NMEA 2000 backbone. Power is also supplied through this connector.

### DS18B20 Temperature Sensor
Connect to the 1-Wire header. Multiple sensors can share the same bus. Each sensor has a unique address that SensESP discovers automatically.

## Gotchas

- The ADS1115 raw values need voltage divider compensation for correct voltage readings. Check `ref/HALMET-example-firmware` for scaling factors.
- When using constant-current source (CCS), the analog input reads the voltage across the resistance, not the resistance directly. Conversion formula is in the reference firmware.
- The isolation barrier means the input ground is separate from the ESP32 ground. Don't bridge them.
- Two partition layouts are in use, and the one you hold depends on where the project started. `ref/HALMET-example-firmware` uses `default_8MB.csv` with `board_upload.flash_size = 8MB` and a matching `sdkconfig.defaults`, which gives two large app partitions for OTA. The template's `halmet` and `halmet_espidf` envs build at 4 MB with `min_spiffs.csv`, like every other board in the template; that is safe on the 16 MB part (the builder only warns about the size mismatch) but leaves less room per app. Moving a device between the two layouts relocates the settings partition, so it loses its saved WiFi and Signal K settings once.
