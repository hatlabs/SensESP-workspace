# Getting Started with SensESP Workspace

## Prerequisites

Before using this workspace, you need:

1. **Claude Code** -- the AI coding assistant that drives the development process.
   Install from: https://code.claude.com/docs/en/quickstart

2. **A computer** running macOS, Linux, or Windows (with WSL).

3. **An ESP32 device** -- either a Hat Labs board (HALMET, HALSER, SH-ESP32) or any generic ESP32 development board.

4. **A USB cable** to connect your device to your computer.

## Setup

### 1. Clone the Workspace

Open a terminal and run:

```
git clone https://github.com/hatlabs/SensESP-workspace.git
cd SensESP-workspace
```

### 2. Run the Setup Script

```
./run init
```

This will:
- Install required tools (uv, PlatformIO, pyserial)
- Download reference code and examples

The setup takes a few minutes on the first run.

### 3. Start Claude Code

Open Claude Code in the workspace directory. Then describe what you want to build. For example:

- "I want to monitor my engine temperature using HALMET"
- "I have a DevKitC and a BMP280 pressure sensor"
- "Help me create a tank level monitor for my boat"

Claude will guide you through the entire process.

## What Happens Next

Claude will:

1. **Ask you questions** about what you want to build, which sensors you have, and how you want the data to flow.
2. **Show you how to wire** your sensors to the board, with specific pin numbers and connection diagrams.
3. **Write the firmware** based on your requirements.
4. **Help you upload** the code to your device.
5. **Test with you** that everything is working correctly.

## Supported Hardware

### Hat Labs Boards
- **HALMET** -- Marine Engine and Tank Interface. 4 analog inputs (16-bit, 0-33V), 4 digital inputs, NMEA 2000, 1-Wire, I2C.
- **HALSER** -- Serial Interface. RS-485 (NMEA 0183), RS-232, UART, NMEA 2000, 1-Wire, I2C.
- **SH-ESP32** -- Sailor Hat for ESP32. General-purpose with optoisolated CAN/NMEA 2000 and I/O.

### Generic ESP32 Boards
Any ESP32, ESP32-C3, or ESP32-S3 development board. You'll need to provide details about your board's pinout and features.

## Windows Users

This workspace works on Windows through WSL (Windows Subsystem for Linux). To set it up:

1. Install WSL: https://learn.microsoft.com/en-us/windows/wsl/install
2. Open a WSL terminal and follow the setup instructions above.
3. For USB device access, you'll need usbipd-win: https://learn.microsoft.com/en-us/windows/wsl/connect-usb

## Troubleshooting

**"./run: Permission denied"** -- Run `chmod +x run` to make the script executable.

**"git: command not found"** -- Install git. On macOS, install Xcode Command Line Tools: `xcode-select --install`. On Linux: `sudo apt install git`.

**Setup takes too long** -- The first run downloads several code repositories. This is normal and only happens once.

**Serial port not found** -- Make sure your device is connected via USB. On Linux, you may need: `sudo usermod -a -G dialout $USER` (then log out and back in).
