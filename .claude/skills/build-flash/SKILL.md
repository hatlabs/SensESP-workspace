---
name: build-flash
description: >
  Build firmware, flash to device, and monitor serial output. Use when
  user wants to test, upload, flash, or "try it on the device".
argument-hint: "[optional: project name]"
---

# Build, Flash, and Monitor

Build the firmware, upload it to the connected device, and read serial output to verify it's working.

## Phase 0: Detect Project

- If a project name was provided, use `projects/<name>/`.
- Otherwise, list projects in `projects/` and ask which one (or use the only one if there's just one).
- Read the project's `platformio.ini` to identify the board. The env to build and flash is its `default_envs`, the `<board>_espidf` variant; never pass `-e <board>`, which selects the arduino compile-check build (see `AGENTS.md`, "Build, Flash, and Monitor").

## Phase 1: Build

1. Run `pio run` from the project directory.
2. **If it succeeds**: Report the binary size and move to Phase 2.
3. **If it fails**: Read the error output carefully.
   - Translate the error into plain language: "The code has a typo on line 42" not "undefined reference to `foo`."
   - Fix the issue and rebuild.
   - Repeat until the build succeeds.

## Phase 2: Flash

1. Check for a connected device by looking for serial ports:
   - macOS: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
   - Linux: `/dev/ttyUSB*`, `/dev/ttyACM*`
2. If no device found:
   - Ask the user to connect the device via USB.
   - On WSL, explain usbipd-win passthrough.
3. Run `pio run -t upload`.
4. **If upload fails**:
   - "Device not responding" → Ask user to hold the BOOT button while pressing RESET, then try again.
   - "Wrong port" → Try specifying the port with `--upload-port`.
   - Explain what's happening in plain terms.

## Phase 3: Monitor and Configure

1. Run `python3 serial_monitor.py -t 30` to capture 30 seconds of device output.
2. Read the output and interpret it:
   - **SensESP boot messages**: WiFi connection status, Signal K server connection, sensor initialization.
   - **Sensor readings**: Are values plausible? (temperature in expected range, pressure not zero, etc.)
   - **Errors**: Stack traces, assertion failures, watchdog resets.
3. **For SensESP projects**: Guide the user through initial device setup:
   - Connect to the device's WiFi access point (SensESP creates one on first boot).
   - Open the web UI and configure WiFi credentials for the boat's network.
   - Review the web UI configuration settings (sensor paths, update intervals, etc.).
   - Verify the device connects to WiFi (check serial output).
4. **End-to-end check**: Ask the user to verify data arrives where expected:
   - Signal K server: can they see the data in the dashboard?
   - NMEA 2000 chart plotter: do the values show up?
   - Guide them based on their setup in `system-profile.md`.
5. Present a summary to the user: "Your device is running. It's reading a temperature of 23.4C from the engine sensor and sending it to Signal K."

## Phase 4: Evaluate

Based on the serial output and user feedback:

- **Everything looks good**: Celebrate! Ask if they want to adjust anything or move to review.
- **Sensor readings look wrong**: Suggest checking wiring, pull-ups, scaling factors. Read the hardware doc again.
- **Device crashes or reboots**: Look for stack traces, fix the code, rebuild (go to Phase 1).
- **WiFi not connecting**: Walk them through the SensESP web configuration portal step by step -- connect to the device's AP, configure credentials, verify connection.
- **Data not showing on Signal K / chart plotter**: Check the output configuration, Signal K paths, N2K PGNs. Verify the device is on the same network or bus.
- **No sensor output**: Check that the sensor initialization code matches the actual wiring.

If changes are needed, fix the code and loop back to Phase 1.
