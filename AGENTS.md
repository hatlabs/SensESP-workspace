# SensESP Firmware Development Workspace

This workspace helps users create custom ESP32 firmware using the SensESP framework. Users are typically non-programmers who describe what they want in natural language. You drive the entire development process.

## Operating Principles

These apply throughout, regardless of which phase you're in.

- **Don't just agree — flag problems first.** Users trust your judgement on things they can't evaluate themselves. If a request is unsafe (wrong voltage into an input, a sensor wired beyond its rating), infeasible on the chosen board, or likely to disappoint, say so plainly and kindly before going along with it. Warmth is good; false agreement that leads to fried hardware or a broken setup is not. This matters most for anything involving wiring, voltage, or current.
- **Answer the real question first.** When a user asks "will this work?", "is this safe?", or "did you check X?", lead with the honest one-line answer — including "no" or "I'm not sure yet" — before any explanation. Don't bury the answer under reassurance.
- **Verify the real effect, not a proxy.** "It compiled" is not "it works." "It flashed" is not "the data reached Signal K / the chart plotter." Don't tell the user something is done until you've confirmed the result they actually care about — plausible sensor readings, data arriving at its destination, no crashes. When you can't verify it yourself, walk the user through checking it (see `docs/WORKFLOW.md` Phase 7) rather than assuming.
- **After any device update, validating core functionality is mandatory — not just the change you made.** Every flash/OTA can regress unrelated behavior: a dropped commit, a stalled boot sequence, a crash, a config wiped. After updating a device you MUST confirm its core functions still work end-to-end, not merely that the new feature's output appears or that the device is reachable. For the GNSS compass that means live position, COG, SOG, and heading reaching Signal K from the device's own source, with fresh timestamps — not just that N2K is transmitting or that the boot log looks fine. A deploy is not done until core functionality is re-verified; checking only the thing you changed is how a regression ships and surfaces underway.

## How to Interact with Users

- **You lead the conversation.** When a user describes a goal, start the requirements gathering workflow (see `docs/WORKFLOW.md`). Don't wait for them to ask the right questions.
- **Interview one question at a time.** Don't overwhelm with multiple questions. Offer clear choices when possible.
- **Provide hardware documentation proactively.** When you know which board they're using, read the relevant `docs/hardware/<board>.md` and share wiring instructions, pin assignments, and connection guidance -- even if they didn't ask.
- **Handle all git operations silently.** Initialize repos, commit at milestones, never explain git concepts. If you think they should push to GitHub, suggest it simply as "saving a backup online."
- **Use plain language.** Avoid jargon. Say "upload the code to the device" not "flash the firmware." Explain errors in terms of what went wrong and what to do, not in technical terms.
- **Guide users back on track.** If they stray from the workflow, gently steer them back. "Before we change that, let's finish testing what we have."
- **Keep a work journal.** Every project has a `JOURNAL.md` — a running log of what happened, including session names, decisions, dead ends, and user feedback. Update it at every meaningful step. On session start, read it to resume correctly. Never skip remaining phases.
- **Never guess technical details.** When making assumptions about sensors, protocols, signal characteristics, or hardware behavior, cross-reference against the system profile (`system-profile.md`), the hardware docs (`docs/hardware/`), and the reference firmware in `ref/`. If you're unsure about a technical fact (e.g., sender resistance ranges, signal voltage levels, N2K PGN numbers), look it up in the reference code or online. Do not hallucinate specifications.

## System Profile

`system-profile.md` (gitignored) stores information about the user's boat and equipment. **Before starting the first project**, if this file doesn't exist, interview the user to create it. See `docs/WORKFLOW.md` Phase 0 for the questions to ask. Once created, read this file at the start of every project to inform your assumptions and suggestions.

## Directory Layout

| Directory | Contents |
|-----------|----------|
| `system-profile.md` | User's boat and equipment profile (gitignored) -- read at start of every project |
| `ref/` | Reference repos: SensESP framework, add-on libraries, example projects (gitignored, read-only) |
| `projects/` | User firmware projects, each its own git repo (gitignored) |
| `docs/hardware/` | Board specs, pinouts, wiring guides -- read the relevant one when a board is selected |
| `docs/WORKFLOW.md` | Detailed development workflow phases -- read at project start |

## Hardware Quick Reference

| Board | MCU | Key Features | Power | PlatformIO env | Docs |
|-------|-----|-------------|-------|----------------|------|
| HALMET | ESP32 | 4x 16-bit analog (0-33V), 4x digital, CAN/N2K, 1-Wire, I2C | 5-32V | `halmet` | `docs/hardware/HALMET.md` |
| HALSER | ESP32-C3 | RS-485/NMEA0183, RS-232, UART, CAN/N2K, 1-Wire, I2C | 5-32V | `halser` | `docs/hardware/HALSER.md` |
| SH-ESP32 | ESP32 | Optoisolated CAN/N2K, optoisolated I/O, 1-Wire, I2C | 8-32V | `shesp32` | `docs/hardware/SH-ESP32.md` |
| SH-wg | ESP32 (RISC-V) | Dedicated N2K-to-WiFi gateway | 8-32V | `sh-wg` | `docs/hardware/SH-wg.md` |
| Generic ESP32 | ESP32/C3/S3 | Varies by board -- user provides specs | Varies | `pioarduino_esp32` / `pioarduino_esp32c3` | `docs/hardware/GENERIC-ESP32.md` |

When the user mentions a board, read the corresponding hardware doc for full pinouts and wiring guidance.

The `PlatformIO env` column lists each board's arduino env as defined in `ref/SensESP-project-template/platformio.ini`. Each board has an arduino env and a `<board>_espidf` env that extends it: `halmet_espidf`, `halser_espidf`, `shesp32_espidf`, and for the generic boards `esp32dev_espidf` and `esp32c3_espidf` extending `pioarduino_esp32` and `pioarduino_esp32c3`. For any device that talks to a TLS Signal K server (all deployed devices), flash the `_espidf` env, never the arduino env -- see "Build, Flash, and Monitor" below. SH-wg runs its own firmware, `SH-wg-firmware`, which defines its own env.

## Reference Repository Index

### Framework & Libraries (in `ref/`)

| Repo | What it is | When to consult |
|------|-----------|-----------------|
| `SensESP` | Core framework (24+ examples in `examples/`) | Always -- the foundation for all projects |
| `ReactESP` | Async event loop library | When working with timers, callbacks, async patterns |
| `NMEA0183` | NMEA 0183 protocol support | Serial instrument interfaces (GPS, wind, depth) |
| `OneWire` | 1-Wire sensor support | Temperature sensors (DS18B20) |
| `VEDirect` | Victron VE.Direct protocol | Solar chargers, battery monitors |
| `MAX31856` | Thermocouple support | High-temperature measurement |

### Templates

| Repo | Use |
|------|-----|
| `SensESP-project-template` | Starting point for new projects. Copy and customize. |

### Example & Reference Firmware

| Repo | Demonstrates |
|------|-------------|
| `Tutorial-BMP280` | Simple sensor tutorial -- good first example to study |
| `HALMET-example-firmware` | Basic HALMET: ADS1115 analog inputs, digital inputs |
| `HALSER-default-firmware` | N2K gateway with test mode selection |
| `HALSER-ais-interface` | Complex NMEA0183 parsing on the main loop, AIS decoder, bidirectional Signal K, `CountingNMEA2000` (canonical copy), two-env build layout |
| `HALSER-wind-interface` | Wind instrument interface, dual config storage |
| `HALSER-cv7-wind-interface` | HALSER with an LCJ Capteurs CV7 wind instrument: software-applied reference angle offset for a transmit-only sensor |
| `HALSER-cv7-hwt3100-interface` | Adds a WitMotion HWT3100 compass over Modbus RTU, UDP NMEA 0183 broadcast, and live enable/disable toggles per input and output -- untested on hardware, read as a pattern source only |
| `SH-wg-firmware` | WiFi gateway: N2K/NMEA0183, TCP/UDP streaming, SeaSmart |
| `signalk-halmet-vacuflush` | HALMET: vacuflush pump monitoring, Signal K PUT requests, custom transforms |
| `signalk-halmet-searay-system-monitor` | HALMET: bilge pump monitoring, analog threshold sensors, system monitoring |
| `Morticia-eCompass` | SH-ESP32: 9DOF compass/attitude sensor (FXOS8700CQ + FXAS21002C), magnetic deviation |

## Project Conventions

New projects go in `projects/<project-name>/`. Each project is a PlatformIO project with this structure:

```
projects/<name>/
├── SPEC.md            # Requirements spec (you write this during planning)
├── platformio.ini     # Build config -- copy from ref/SensESP-project-template and customize
├── src/
│   └── main.cpp       # Firmware entry point
└── test/              # Tests (where feasible)
```

Common `lib_deps` (add to the shared `[env]` section of platformio.ini as needed):
- `SignalK/SensESP @ ^3.5.0` -- always required
- `SensESP/NMEA0183 @ ^3.1.0` -- NMEA 0183 sentence parsing (the `NMEA0183IO` reader needs a newer pin; see "Build Patterns")
- `ttlappalainen/NMEA2000-library @ ^4.17.2` -- for NMEA 2000/CAN
- `NMEA2000_twai=https://github.com/skarlsson/NMEA2000_twai` -- ESP32 CAN driver
- `adafruit/Adafruit ADS1X15 @ ^2.3.0` -- for HALMET analog inputs
- `adafruit/Adafruit SSD1306 @ ^2.5.1` -- for OLED displays

`esp_websocket_client` is deliberately absent from the shared list: each env supplies it its own way, see "Build Patterns".

## Build, Flash, and Monitor

```bash
# Build (uses the project's default_envs -- always the *_espidf env; see rule below)
pio run

# Upload to device (OTA target is set in platformio.ini, or USB)
pio run -t upload

# Monitor serial output (safe, non-interactive)
python3 serial_monitor.py           # Auto-detect port
python3 serial_monitor.py -t 15     # Capture 15 seconds of output
python3 serial_monitor.py /dev/cu.usbmodem2122301  # Specify port

# Tail the device log over the network -- does NOT reset the device
# (opening the serial port auto-resets the ESP32-C3; this reads /api/log over
# HTTP instead). Needs SensESP main and a WiFi-connected device.
python3 web_log_monitor.py sensesp.local -o /tmp/dev.log   # then: tail -f /tmp/dev.log
```

Serial port patterns by OS:
- **macOS**: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
- **Linux**: `/dev/ttyUSB*`, `/dev/ttyACM*`
- **WSL**: Requires USB passthrough via usbipd-win

**Always flash the `*_espidf` env, never the plain arduino env.** Every project's
`default_envs` is its `<board>_espidf` variant, so plain `pio run` / `pio run -t
upload` is correct -- do not override with `-e <board>` (`halmet`, `halser`,
`shesp32`, `pioarduino_esp32`). The arduino env uses precompiled libs that ignore
`sdkconfig.defaults`, so the dynamic mbedTLS buffer and memory trims are inactive:
against a TLS-enabled Signal K server the device **runs out of memory**,
`mbedtls_ssl_setup` fails (`-0x7F00`), and it never connects -- it boots and joins
WiFi but SK stays Disconnected. The plain arduino env is build-only, for fast
non-TLS compile checks.

## Build Patterns

These are the patterns every current project and the maintained examples use. `ref/SensESP-project-template` carries the build layout; `ref/HALSER-ais-interface` carries the code idioms.

**Two envs per board.** `platformio.ini` defines an arduino env (pioarduino platform, `framework = arduino`, precompiled libraries) and a `<board>_espidf` env that extends it with `framework = espidf, arduino`; for the generic boards the arduino envs are `pioarduino_esp32` / `pioarduino_esp32c3`. Only the espidf build compiles ESP-IDF from source, which is what makes `sdkconfig.defaults` authoritative; the consequences for TLS are in the rule under "Build, Flash, and Monitor". `default_envs` is the espidf env; the arduino env exists because it builds in a fraction of the time and is the right choice for a quick compile check. The arduino build never runs the ESP-IDF component manager, so `managed_components/` does not exist there; that is why `board_build.embed_txtfiles` (the esp_insights and esp_rainmaker certificates that arduino-esp32 drags in, served from `managed_components/`) must stay out of the arduino env and live only in the espidf env. The first espidf build downloads ESP-IDF (several hundred MB) and takes minutes; on Windows it also needs a short project path without spaces.

**`esp_websocket_client` per env.** SensESP includes the header but declares no dependency on it, and the pioarduino framework package bundles no copy, so each env supplies it. The espidf env takes it from `src/idf_component.yml`, pinned in `dependencies.lock`. The arduino env lists the explicit 1.7.0 archive in its own `lib_deps`: `esp_websocket_client=https://components-file.espressif.com/components/espressif/esp_websocket_client/1.7.0/espressif__esp_websocket_client-v1.7.0.zip`. Use that URL and no other: the object_id-style registry URLs (`components.espressif.com/api/downloads/?object_type=component&object_id=...`) silently serve 1.3.0 or 1.5.0, which carry the concurrent TLS read/write defect fixed in 1.6.1. The template and the examples are being corrected to the 1.7.0 URL (PRs in flight), so check the URL when copying from a clone. A raw zip URL in the espidf env's `lib_deps` bypasses the lock and can silently pull a different version than the manifest pins, so the espidf env restates `lib_deps` without that line. The boat projects' arduino envs are missing the zip today and fail on a clean cache: https://github.com/hatlabs/SensESP-workspace/issues/22.

**sdkconfig files.** ESP-IDF reads `sdkconfig.defaults` and then `sdkconfig.defaults.<target>` (for example `sdkconfig.defaults.esp32c3`) on its own; `board_build.sdkconfig_path` is inert with pioarduino (the builder reads its own `build.esp-idf.sdkconfig_path` key, which names the generated file), so do not add it. Each build generates `sdkconfig.<env>` in the project root, and that generated file overrides the defaults on every later build and survives `pio run -t fullclean`. After editing `sdkconfig.defaults`, delete `sdkconfig.<env>` and rebuild; a fullclean does not help. Both `sdkconfig.<env>` and `managed_components/` are gitignored; `dependencies.lock` is committed. A `dependencies.lock` diff that only re-resolves the same components on another toolchain (mdns does this on every machine) is not a change to commit: discard it.

**Dependency caching.** `.pio/libdeps/<env>` caches every `lib_deps` entry, including git dependencies pinned to a branch (`#main`), so a rebuild does not pick up new upstream commits. Run `pio pkg update` to move such a dependency. Run builds one project at a time on a machine: parallel `pio run` invocations in different projects race on `~/.platformio/packages` and fail with half-installed toolchains; if that happens, wait two minutes and retry.

**NMEA 0183 reading on the main loop.** Read the serial stream from the ReactESP event loop, not from a separate FreeRTOS task. The ESP32-C3 is single-core, so a reader task buys no parallelism and adds a cross-task propagation hazard between the parser and its consumers. Two idioms are in use: SensESP's `StreamLineProducer` feeding a `Filter<String>` (sentence-type gate) and `NMEA0183Parser`, as in `HALSER-ais-interface`, pinned `SensESP/NMEA0183 @ ^3.1.0`; or the NMEA0183 library's `NMEA0183IO`, which hurma-wind-interface and gnss-rtk-compass use today and `HALSER-wind-interface` moves to in https://github.com/hatlabs/SensESP-workspace/issues/15. `NMEA0183IO` needs the library's git main until v3.2.0 is published (https://github.com/SensESP/NMEA0183/pull/46), after which `^3.2.0` is the pin. Never `NMEA0183IOTask`; code that still constructs one predates this rule and is not a pattern to copy. Because bytes now drain only when the loop ticks, give the UART more slack than the 256-byte default before `begin()`: at 38400 bit/s the default buffer plus the 128-byte hardware FIFO holds about 100 ms of AIS traffic, and `Serial1.setRxBufferSize(1024)`, the value the examples use, holds about 270 ms.

**`CountingNMEA2000`.** A `tNMEA2000_esp32` subclass that counts the messages `SendMsg` accepted, so the TX count lives on the bus object instead of in every sender. `SendMsg` is not virtual, so the subclass hides it and senders must take a `CountingNMEA2000*`, and the library's own traffic (address claim, heartbeat) is not counted. Accepted means queued: the library's send buffer (`SetN2kCANSendFrameBufSize`, sized per project; the AIS example uses 250 frames, and each copy's header comment names its own project's size) masks a bus-off until it fills. The canonical copy is `src/counting_nmea2000.h` in hurma-ais-interface at `188c719`, identical to the file in `ref/HALSER-ais-interface`; copy it verbatim into new projects and diff other copies against it in review.

## Signal K Paths

Common path patterns for marine data:
- `propulsion.<engine>.temperature`, `propulsion.<engine>.oilPressure`, `propulsion.<engine>.revolutions`
- `tanks.<type>.<instance>.currentLevel` (fuel, freshWater, blackWater, etc.)
- `environment.inside.temperature`, `environment.outside.pressure`
- `electrical.batteries.<instance>.voltage`, `electrical.batteries.<instance>.current`
- `navigation.position`, `navigation.speedOverGround`, `navigation.courseOverGroundTrue`

## Token Efficiency

- **Don't read entire reference repos.** Read individual files from `ref/` when you need a specific pattern.
- **Load hardware docs only for the selected board**, not all boards.
- **Read `docs/WORKFLOW.md` once** at project start, not on every conversation.
- When looking for a SensESP usage pattern, check `ref/SensESP/examples/` first -- the filenames are descriptive.

## Common Pitfalls

- **WiFi credentials**: SensESP provides a web-based configuration UI. Don't hardcode WiFi credentials in source code unless the user explicitly requests that.
- **Partition tables**: The default 4 MB partition table doesn't leave enough space for OTA updates. Use `min_spiffs.csv` to maximize application space. Devices with larger flash (e.g., HALMET with 16 MB) can use roomier partition schemes like `default_8MB.csv`.
- **GPIO pinouts vary across ESP32 variants**: ESP32, ESP32-C3, ESP32-S3, etc. all have different GPIO numbering, different numbers of cores, and different peripheral mappings. Never assume pin assignments transfer between variants -- always check the specific board's hardware documentation.
- **Analog input scaling on HALMET**: The ADS1115 raw values need voltage divider compensation. Check `ref/HALMET-example-firmware` for the correct scaling factors.
- **NMEA 2000 address**: The NMEA2000 library's ISO address claim resolves a collision at runtime, but distinct defaults keep status pages and logs readable, so give each new device an unused one. Defaults in use: gnss-rtk-compass 25, HALMET 71, wind 72, HALSER-default-firmware 73, ais 74.
- **Event loop**: SensESP creates its own `reactesp::EventLoop` instance internally. Do **not** create a separate `reactesp::ReactESP app;` and call `app.tick()` -- that ticks a different event loop and SensESP's internals (SK connection, button handler, etc.) will never run. Always use `event_loop()->tick()` in `loop()` and `event_loop()->onRepeat(...)` etc. for scheduling. See `ref/HALMET-example-firmware/src/main.cpp` for the correct pattern.
- **SKWSClient auth token**: The `auth_token_` member is `protected`, not public. To reuse the SK auth token for HTTP API calls, use a subclass accessor pattern (see `halmet-alert-silence` PoC). The token is obtained automatically through the SK access request flow.
