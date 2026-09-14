# SH-ESP32 Hardware Reference

**Sailor Hat for ESP32**

Online docs: https://docs.hatlabs.fi/sh-esp32/

## Microcontroller

- **MCU**: ESP32-WROOM-32E (or 32U variant with U.FL antenna connector)
- **Processor**: Dual-core Tensilica Xtensa LX6, 240 MHz
- **Flash**: 4 MB
- **WiFi**: 802.11 b/g/n (2.4 GHz)
- **Bluetooth**: BLE 4.2

## Power

- **Input**: 8-32V DC
- **Protection**: 500 mA polyfuse, reverse polarity diode, TVS overvoltage/ESD protection (36-40V breakdown, >600W pulse)
- **Connector**: 2-pin terminal block (Rev 2.0.0+) or JST XH (earlier revisions)
- **Protected output**: Filtered input voltage available for external devices

## Pin Assignments

| GPIO | Function | Notes |
|------|----------|-------|
| 32 | CAN TX | NMEA 2000 transmit, optoisolated |
| 34 | CAN RX | NMEA 2000 receive, optoisolated (input only) |
| 16 | I2C SDA | Configurable via jumper |
| 17 | I2C SCL | Configurable via jumper |
| 4 | 1-Wire | DS18B20 temperature sensors, configurable via jumper |
| 33 | Opto OUT | Optoisolated digital output |
| 35 | Opto IN | Optoisolated digital input (2.5-18V range, input only) |
| 2 | Blue LED | User-programmable |
| 0 | Boot button | Also GPIO; Ethernet REF_CLK option |
| 1 | Serial TX | Default UART0 |
| 3 | Serial RX | Default UART0 |

**Free GPIOs** (directly available on header): 5, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 27, 36, 39

## CAN / NMEA 2000

- **Pins**: GPIO 32 (TX), GPIO 34 (RX)
- **Isolation**: Optoisolated CAN transceiver (ISO1050DUB or separate digital isolator + TJA1050)
- **Termination**: Available via solder jumper (enable if this is the last device on the bus)
- **Connector**: Phoenix MC 3.81mm terminal block (Rev 2.0.0+) or JST XH (earlier)

## Optoisolated I/O

- **Input (Opto IN)**: GPIO 35, accepts 2.5-18V signal. Input only pin.
- **Output (Opto OUT)**: GPIO 33, can drive slow-speed single-sided NMEA 0183 or control relays.

## I2C

- **Pins**: GPIO 16 (SDA), GPIO 17 (SCL), configurable via jumpers
- **Connectors**: 4-pin 2.54mm header + unpopulated Qwiic-compatible JST SH footprint
- **ESD protection and noise filtering**: Yes

## 1-Wire

- **Pin**: GPIO 4, configurable via jumper
- **Connector**: 3-pin 2.54mm header (GND, 3V3, DQ)
- **ESD and RF filtering**: Yes

## User Interface

- **Reset button**: Resets ESP32
- **Boot button**: GPIO 0; hold during reset for programming mode
- **Red LED**: Power indicator (hardwired to 3.3V)
- **Blue LED**: GPIO 2, user-controllable

## USB

- **Connector**: Micro-B USB
- **USB-to-serial**: CH340C (supports up to 2 Mbps)

## Proto Board Area

Central perforated area for custom modifications. Isolated and non-isolated sections available. Useful for adding custom circuitry, voltage dividers, or additional connectors.

## Ethernet Provisions

The board has pin assignments compatible with optional Ethernet PHY modules, but no Ethernet hardware is populated by default. GPIOs 0, 5, 18, 19, 21, 22, 23, 25, 26, 27 have Ethernet function options.

## PlatformIO Configuration

Flash `shesp32_espidf` on any device that talks to a TLS Signal K server. The `shesp32` env builds faster and is fine for compile checks, but its precompiled libraries ignore `sdkconfig.defaults`, so the device runs out of memory against a TLS server.

```ini
; Arduino compile-check env (fast build, no TLS support)
[env:shesp32]
extends = pioarduino, esp32
build_flags =
    ${pioarduino.build_flags}
    ${esp32.build_flags}

; Flash this one (ESP-IDF from source, TLS works)
[env:shesp32_espidf]
extends = env:shesp32
framework = espidf, arduino
lib_deps =
    ${env.lib_deps}
board_build.embed_txtfiles =
    managed_components/espressif__esp_insights/server_certs/https_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_mqtt_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_claim_service_server.crt
    managed_components/espressif__esp_rainmaker/server_certs/rmaker_ota_server.crt
```

The shared `[env]`, `[pioarduino]`, and `[esp32]` sections come from the project template. See `ref/SensESP-project-template/platformio.ini` for the full layout. Add `adafruit/Adafruit ADS1X15` to the shared `[env]` `lib_deps` if using an external ADC, or `adafruit/Adafruit SSD1306` for an OLED display.

## Common Use Cases

### Engine Monitor with Add-on Board
Pair with an ADS1115 ADC breakout on I2C for analog inputs (oil pressure, temperature, fuel level). Add digital inputs for RPM/tacho via the opto input or GPIO header. Start from the template's `shesp32_espidf` env; `ref/HALMET-example-firmware` shows the ADS1115 scaling and tacho counting code, with HALMET's pin numbers.

### Temperature Monitoring
Connect DS18B20 sensors to the 1-Wire bus. Multiple sensors supported on the same wire. Simple and reliable for engine room, exhaust, and water temperature.

### NMEA 2000 Interface
General-purpose device on the NMEA 2000 network. Read or write PGNs. Combine with WiFi for Signal K server connectivity.

## Gotchas

- **GPIO 34 and 35 are input only.** These are used for CAN RX and Opto IN respectively. Don't try to drive them as outputs.
- **CAN termination**: Only enable the solder jumper if this is at the end of the NMEA 2000 backbone. Most installations should leave it open.
- **I2C address conflicts**: If connecting multiple I2C devices, verify they don't share addresses. Common conflict: two ADS1115 at default address.
- **Many free GPIOs**: This board has many free pins on the header. Good for custom builds, but you need to track which pins you're using.
- **Board revisions**: Pin assignments are the same across revisions, but connector types differ (JST XH vs Phoenix MC terminals). Code is compatible.
