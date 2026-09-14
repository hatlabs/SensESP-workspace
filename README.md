# SensESP Workspace

Create custom ESP32 firmware for marine and IoT applications using natural language. This workspace provides [Claude Code](https://code.claude.com/docs/en/quickstart) with the context and tools to guide you through the entire process -- from describing what you want to build, to flashing working firmware onto your device.

Supports [Hat Labs](https://hatlabs.fi/) hardware (HALMET, HALSER, SH-ESP32) and generic ESP32 boards.

## What You Need

- **Claude Code** -- install from https://code.claude.com/docs/en/quickstart
- **A Claude Pro subscription** (or higher) -- Claude Code requires at least a Pro plan. An API key with usage-based billing also works but is significantly more expensive.
- **A USB cable** to connect your ESP32 device
- **Your ESP32 device** -- a Hat Labs board or any ESP32 dev board

**Note:** This workspace is built specifically for Claude Code. It does not work with ChatGPT, Gemini, the Claude app, or other AI assistants.

## Quick Start

1. Clone this workspace:
   ```
   git clone https://github.com/hatlabs/SensESP-workspace.git
   cd SensESP-workspace
   ```

2. Run the setup script (installs tools and downloads reference code):
   ```
   ./run init
   ```

3. Open Claude Code in the workspace directory and describe what you want to build.

## Example First Messages

Once Claude Code is open, try something like:

- "I want to monitor my engine temperature using HALMET"
- "I have a DevKitC and a BMP280 pressure sensor"
- "I want to build an NMEA 0183 to NMEA 2000 gateway with HALSER"
- "Help me create a tank level monitor for my boat"

Claude will interview you about the details, show you how to wire things up, write the firmware, and help you flash it to your device.

## Available Commands

```
./run init            # First-time setup
./run repos:clone     # Clone missing reference repos
./run repos:pull      # Update reference repos
./run repos:status    # Check what's cloned
./run help            # Show all commands
```

## Project Structure

After setup, your workspace looks like this:

```
SensESP-workspace/
├── ref/          # Reference code (examples, libraries, templates)
├── projects/     # Your firmware projects (created by Claude)
├── docs/         # Hardware docs, workflow guides
└── ...           # Workspace tools and configuration
```

Each project Claude creates for you goes into `projects/` as its own folder.

## License

Copyright 2026 Hat Labs Oy.
