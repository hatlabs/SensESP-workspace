# Generic ESP32 Board Reference

For ESP32, ESP32-C3, ESP32-S3, and other Espressif development boards.

## What You Need to Know

When using a generic ESP32 board (DevKitC, NodeMCU, Wemos D1 Mini, etc.), you are responsible for understanding your board's specific pinout and capabilities. Hat Labs boards have documented pin assignments and built-in protection -- generic boards typically do not.

## Common ESP32 DevKitC Pinout

This is for the standard ESP32-DevKitC with ESP32-WROOM-32 module. Other boards may differ.

| GPIO | Usable | Notes |
|------|--------|-------|
| 0 | Caution | Boot mode pin. Has internal pull-up. |
| 1 | No | UART0 TX (serial output) |
| 2 | Yes | Often connected to on-board LED |
| 3 | No | UART0 RX (serial input) |
| 4 | Yes | Common choice for 1-Wire |
| 5 | Yes | Default SPI SS |
| 12 | Caution | Boot strapping pin (must be LOW at boot) |
| 13-15 | Yes | General purpose |
| 16-17 | Yes | Good for I2C |
| 18-19 | Yes | Default SPI |
| 21-23 | Yes | GPIO 21/22 common for I2C |
| 25-27 | Yes | DAC outputs available |
| 32-33 | Yes | ADC1, touch |
| 34-39 | Input only | ADC1, no pull-up/down, no output |

**Pins to avoid**: 6-11 (connected to internal flash), 1 and 3 (UART0).

## PlatformIO Configuration

Copy `ref/SensESP-project-template` and keep its environments rather than writing an ini from scratch. The template already carries the two-environment layout, `sdkconfig.defaults`, and the `esp_websocket_client` sourcing that a hand-written `[env:esp32dev]` block gets wrong.

| Generic board | Flash this | Compile check only |
|---------------|------------|--------------------|
| ESP32 | `esp32dev_espidf` | `pioarduino_esp32` |
| ESP32-C3 | `esp32c3_espidf` | `pioarduino_esp32c3` |

Set `default_envs` to match your board. Flash the `_espidf` environment on any device that talks to a TLS Signal K server: it builds ESP-IDF from source, which is what makes `sdkconfig.defaults` authoritative and enables the dynamic mbedTLS buffers the connection needs. The plain environment ignores `sdkconfig.defaults`, so against a TLS server the device boots, joins WiFi, and Signal K stays Disconnected with `mbedtls_ssl_setup` failing at `-0x7F00`.

The template's board sections carry the board-specific parts already -- for the C3, `board = esp32-c3-devkitm-1` with `-D ARDUINO_USB_MODE=1` and `-D ARDUINO_USB_CDC_ON_BOOT=1` for the CDC USB port. Add your sensor libraries to the shared `[env]` `lib_deps`; the per-board sections need nothing.

**The template has no ESP32-S3 environment.** For an S3, add a board section modelled on the ESP32 one with `board = esp32-s3-devkitc-1`, and an `esp32s3_espidf` environment alongside the others. Note that the S3's PWM channel numbering differs from the ESP32's ([template issue 9](https://github.com/SensESP/SensESP-project-template/issues/9)).

## What Generic Boards Lack

Compared to Hat Labs boards, generic ESP32 boards typically lack:

- **Galvanic isolation** -- your inputs share ground with the ESP32. Be careful with voltage levels.
- **Input protection** -- no TVS diodes, fuses, or reverse polarity protection. A wiring mistake can damage the board.
- **CAN transceiver** -- you need an external CAN transceiver module (e.g., SN65HVD230 or MCP2551) for NMEA 2000.
- **Regulated marine power input** -- most dev boards accept 5V USB or 3.3V only. You need a separate DC-DC converter for 12V/24V systems.
- **EMC design** -- not designed for electrically noisy marine environments.

## Adding NMEA 2000 to a Generic Board

You need an external CAN transceiver module. Connect:
- CAN TX from ESP32 to the transceiver's TX input
- CAN RX from the transceiver's RX output to an ESP32 input
- 3.3V and GND to power the transceiver
- CAN H and CAN L from the transceiver to the NMEA 2000 bus

Choose any two free GPIOs for CAN TX and RX. Common choice: GPIO 16 (TX) and GPIO 17 (RX).

```cpp
// In your SensESP project, set the CAN pins:
#define CAN_TX_PIN GPIO_NUM_16
#define CAN_RX_PIN GPIO_NUM_17
```

## Adding Analog Inputs

The ESP32's built-in ADC is 12-bit and has poor linearity. For accurate analog measurements, use an external **ADS1115** I2C ADC (16-bit, same as HALMET uses).

Connect:
- SDA to your I2C SDA pin (e.g., GPIO 21)
- SCL to your I2C SCL pin (e.g., GPIO 22)
- VCC to 3.3V
- GND to GND
- Analog inputs to the ADS1115 channels (A0-A3)

**Important**: The ADS1115 input range is 0-3.3V by default. For higher voltages, add a resistive voltage divider.

## Gotchas

- **No isolation**: A ground loop or voltage spike can destroy your board and potentially your computer. Be very careful with marine electrical systems.
- **ADC quality**: The ESP32's internal ADC is noisy and non-linear. Use an external ADC for any serious measurement.
- **Power from USB only**: Most dev boards can't be powered from 12V/24V directly. You need a buck converter.
- **Pin boot strapping**: GPIO 0 and GPIO 12 affect boot behavior. Be careful what you connect to them.
- **WiFi antenna**: Built-in PCB antennas have limited range. Consider a board with U.FL connector for an external antenna in marine installations.
