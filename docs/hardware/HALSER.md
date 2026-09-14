# HALSER Hardware Reference

**Hat Labs Serial Interface**

Online docs: https://docs.hatlabs.fi/halser/

## Microcontroller

- **MCU**: ESP32-C3 (RISC-V single-core, 160 MHz)
- **Flash**: 4 MB
- **WiFi**: 802.11 b/g/n (2.4 GHz)
- **Note**: Single-core RISC-V -- different architecture from ESP32. Don't use ESP32 pin numbers or dual-core assumptions.

## Power

- **Input**: 5-32V DC via NMEA 2000 terminal block
- **Protection**: 500 mA self-resetting fuse, reverse polarity diode, TVS overvoltage/ESD protection, two-stage noise filtering
- **Output**: 3.3V regulated (switching supply)

## Pin Assignments

| GPIO | Function | Notes |
|------|----------|-------|
| 4 | CAN TX | NMEA 2000 transmit (TWAI) |
| 5 | CAN RX | NMEA 2000 receive (TWAI) |
| 2 | UART TX | Serial transmit |
| 3 | UART RX | Serial receive |
| 6 | I2C SDA | I2C data |
| 7 | I2C SCL | I2C clock |
| 8 | RGB LED | SK6805 addressable LED |
| 9 | User Button | Active low, internal pull-up |
| 10 | 1-Wire | DS18B20 temperature sensors |
| 1 | Hall Sensor | Active low, on-board, magnet activation |
| 0 | Test Mode | HIGH at boot = test mode |

## Serial Interfaces

HALSER's primary feature is its serial interface versatility. All serial interfaces are **galvanically isolated** from the ESP32-C3 and the NMEA 2000 bus.

### RS-485 (NMEA 0183)
- **Connectors**: Separate 3-pin terminal blocks for TX and RX
- **Use**: Standard NMEA 0183 instruments (GPS, depth, wind, AIS)
- **Baud rate**: Depends on instrument (4800 for standard NMEA, 38400 for AIS)

### RS-232
- **Connector**: 3-pin terminal block
- **Use**: Legacy serial instruments

### UART (TTL)
- **Connector**: 3-pin terminal block
- **Voltage**: Selectable 3.3V or 5V via jumper
- **Use**: Direct connection to other microcontrollers or modern sensors

## CAN / NMEA 2000

- **Pins**: GPIO 4 (TX), GPIO 5 (RX)
- **Connector**: 4-pin terminal block (shared with power input)
- **Protocol**: NMEA 2000 at 250 kbps

## I2C

- **Pins**: GPIO 6 (SDA), GPIO 7 (SCL)
- **Connector**: 4-pin header (GND, 3V3, SCL, SDA)

## 1-Wire

- **Pin**: GPIO 10
- **Connector**: 3-pin header (GND, 3V3, DQ)
- **ESD/RF protection**: Yes (marine environment)

## Status Indicators

- **Red LED (PWR)**: Power indicator (3.3V present)
- **RGB LED (SK6805)**: GPIO 8, software-controlled
  - Rainbow cycle = device ready
  - Brief off-blink = NMEA 0183 sentence received

## User Interface

- **Reset button**: Resets ESP32-C3
- **User button**: GPIO 9, active low
- **Hall sensor**: GPIO 1, magnet activation through enclosure wall

## USB

- **Connector**: USB-C
- **Function**: Programming and serial monitor via USB CDC

## PlatformIO Configuration

Flash `halser_espidf` on any device that talks to a TLS Signal K server. The `halser` env builds faster and is fine for compile checks, but its precompiled libraries ignore `sdkconfig.defaults`, so the device runs out of memory against a TLS server.

```ini
; Arduino compile-check env (fast build, no TLS support)
[env:halser]
extends = pioarduino, esp32c3
build_flags =
    ${pioarduino.build_flags}
    ${esp32c3.build_flags}

; Flash this one (ESP-IDF from source, TLS works)
[env:halser_espidf]
extends = env:halser
framework = espidf, arduino
lib_deps =
    ${env.lib_deps}
board_build.embed_txtfiles =
    managed_components/espressif__esp_insights/server_certs/https_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_mqtt_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_claim_service_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_ota_server.crt
```

The shared `[env]`, `[pioarduino]`, and `[esp32c3]` sections come from the project template. See `ref/SensESP-project-template/platformio.ini` for the full layout.

## Common Use Cases

### NMEA 0183 to NMEA 2000 Gateway
Connect an NMEA 0183 instrument (GPS, depth sounder, wind) to the RS-485 RX port. HALSER parses the sentences and outputs corresponding NMEA 2000 PGNs. See `ref/HALSER-default-firmware`.

### AIS Receiver Interface
Connect an AIS receiver (e.g., Matsutec HA-102) to RS-485 RX at 38400 baud. HALSER decodes VDM/VDO sentences and outputs AIS data on NMEA 2000 and Signal K. See `ref/HALSER-ais-interface`.

### Wind Instrument Interface
Connect a wind instrument (e.g., Autonnic A5120) to RS-485 RX at 4800 baud. HALSER parses MWV sentences and outputs PGN 130306 (Wind Data) on NMEA 2000. See `ref/HALSER-wind-interface`.

## Gotchas

- **ESP32-C3 is NOT an ESP32.** Different GPIO numbering, single-core RISC-V, no Bluetooth Classic. Don't copy ESP32 pin numbers.
- **USB CDC**: The USB-C port uses native USB CDC, not a separate USB-to-serial chip. Build flags `ARDUINO_USB_MODE=1` and `ARDUINO_USB_CDC_ON_BOOT=1` are required.
- **Serial baud rate**: Must match the connected instrument. Standard NMEA 0183 is 4800, AIS is 38400, some instruments use 9600.
- **Boot mode**: If GPIO 0 is HIGH at boot (test jig connected), the device enters test mode instead of normal operation.
