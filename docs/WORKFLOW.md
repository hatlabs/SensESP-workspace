# SensESP Development Workflow

This document defines the phases Claude follows when helping users create firmware projects. Each phase has clear entry conditions, actions, and exit conditions.

## Phase 0: System Profile

**Entry**: User describes any goal, and `system-profile.md` does not yet exist in the workspace root.

**Skip if**: `system-profile.md` already exists. Read it instead and proceed to Phase 1.

**Purpose**: Understanding the user's overall setup prevents wrong assumptions later. A user who says "monitor my engine" might have a single-engine sailboat or a twin-engine motor yacht -- the right design is very different. This profile captures context that informs all future projects.

**Actions**:
Interview the user to build a comprehensive picture of their setup. Ask one topic at a time. It's fine if the user doesn't know some answers -- record what they do know.

Topics to cover:

1. **Vessel**: Make/model, year, name, type (sailboat, motor yacht, RIB, commercial, etc.)
2. **Engines**: Make, model, year, number of engines. Fuel type (diesel, petrol). Are there existing engine instruments?
3. **Electrical system**: 12V or 24V? Battery bank setup (starter, house, lithium/AGM/lead-acid). Charging sources (alternator, shore power, solar panels, wind generator). Inverter?
4. **Existing electronics**:
   - Chart plotter(s): make, model
   - AIS: transponder or receiver, make/model
   - VHF radio
   - Wind/speed/depth instruments: make, model, interface type (NMEA 0183, NMEA 2000, analog)
   - Autopilot: make, model
   - Radar
5. **Network**: Is there an NMEA 2000 backbone? NMEA 0183 wiring? WiFi network on board?
6. **Computers**: Raspberry Pi or other onboard computer? Signal K server running? What software?
7. **Tank senders**: Fuel, fresh water, black water, holding tank. What type of senders (resistive, capacitive, ultrasonic)? Are they already installed?
8. **Hat Labs and DIY hardware**: Which Hat Labs boards do they already own or plan to use? Any other ESP32-based devices, DIY sensors, or custom boards on the boat?
9. **Goals**: What are they most interested in achieving? (monitoring, alarms, data logging, integration with chart plotter, remote monitoring, etc.)

**Output**: Write the answers to `system-profile.md` in a clear, structured format. This file is gitignored and stays local to the workspace.

**Exit**: `system-profile.md` exists with whatever information the user could provide.

## Phase 1: Requirements Gathering

**Entry**: User describes a goal ("I want to monitor my engine temperature"). `system-profile.md` has been read.

**Actions**:
1. Ask about the goal -- what do they want to measure, control, or connect?
2. Ask about the hardware -- which board? What sensors?
3. Ask about outputs -- where should data go? (Signal K, NMEA 2000, display, alarms)
4. Ask about the environment -- marine, automotive, indoor?

**Guidelines**:
- One question at a time. Offer choices when possible.
- **Cross-reference everything against `system-profile.md`.** If the user has a 12V system, don't suggest 24V components. If they already have a Signal K server, suggest connecting to it. If they have NMEA 2000, suggest N2K output.
- **Verify technical details.** When you need to know sender resistance ranges, signal characteristics, PGN numbers, or other technical facts, look them up in the reference firmware (`ref/`) or online. Do not guess. If you're unsure, say so and ask the user or suggest looking it up together.
- If the user doesn't know what sensors they need, suggest common options for their goal based on what makes sense for their setup.
- If the user has a Hat Labs board, use the board's capabilities to guide suggestions.
- If the user has a generic ESP32, ask about its specific features.

**Exit**: You have enough information to write a specification.

## Phase 2: Hardware Documentation

**Entry**: Board is known.

**Actions**:
1. Read `docs/hardware/<board>.md` for the selected board.
2. Present wiring instructions for the user's specific sensors and connections.
3. Include pin numbers, connector positions, jumper settings.
4. Warn about any gotchas (voltage limits, isolation, required components).

**Guidelines**:
- This phase is mandatory even if the user didn't ask about wiring.
- For generic boards, ask the user to describe or link to their board's pinout.
- Use plain language: "Connect the temperature sensor's signal wire to pin 23" not "Wire GPIO23 to the NTC output."

**Exit**: User understands how to physically connect their sensors.

## Phase 3: Specification

**Entry**: Requirements gathered, hardware documented.

**Actions**:
1. Create the project directory: `projects/<project-name>/`
2. Write `SPEC.md` summarizing: goal, hardware, sensors, connections, Signal K paths, expected behavior, dependencies.
3. Present the spec to the user for review.

**Guidelines**:
- The spec is the contract. Don't proceed until the user confirms it.
- Keep it readable by non-technical users.
- Include a connections table with physical pin numbers.

**Exit**: User confirms the specification.

## Phase 4: Architecture

**Entry**: Specification confirmed.

**Actions**:
1. Study relevant reference examples in `ref/` for patterns that match the use case.
2. Design the SensESP signal flow: sensor → transform → output.
3. Identify required libraries (lib_deps for platformio.ini).
4. Plan the main.cpp structure.

**Guidelines**:
- Check `ref/SensESP/examples/` for matching patterns first.
- Then check the product-specific examples (HALMET-example-firmware, etc.).
- Prefer simple, linear pipelines. Avoid unnecessary complexity.
- Note which example files you're drawing from so you can reference them during implementation.

**Exit**: You have a clear plan for the code structure.

## Phase 5: Implementation

**Entry**: Architecture planned.

**Actions**:
1. Copy `ref/SensESP-project-template/` as the starting point, including `sdkconfig.defaults`, `sdkconfig.defaults.esp32c3`, `min_spiffs.csv`, `CMakeLists.txt`, `src/CMakeLists.txt` and `src/idf_component.yml` -- the `<board>_espidf` builds need all of them.
2. In `platformio.ini`, set `default_envs` to the board's `<board>_espidf` env (`halmet_espidf`, `halser_espidf`, `shesp32_espidf`, `esp32dev_espidf`, `esp32c3_espidf`) and add the project's dependencies to the shared `[env]` `lib_deps`. The plain `<board>` env stays as it is: it is the fast compile check, never the flashed build (see `AGENTS.md`, "Build, Flash, and Monitor").
3. Write `src/main.cpp` following the planned architecture.
4. Where feasible, write tests for transforms and logic in `test/`.
5. Initialize git repo and commit the initial implementation.

**Guidelines**:
- Follow test-driven development where practical. SensESP transforms and custom logic can be unit tested.
- Keep the code simple. A non-programmer should be able to read it and roughly understand what's happening.
- Add brief comments explaining what each section does (for the user's benefit).
- Commit at meaningful milestones, not after every line.

**Exit**: Code compiles and is ready to flash.

## Phase 6: Build and Flash

**Entry**: Code written or modified.

**Actions**:
1. Build with plain `pio run`. The project's `default_envs` is its `<board>_espidf` env; do not pass `-e <board>`, which selects the arduino compile-check build that cannot hold a TLS Signal K connection. The first `<board>_espidf` build downloads and compiles ESP-IDF and takes several minutes; later builds are incremental.
2. Fix any compilation errors (explain them in plain language).
3. Upload with `pio run -t upload`.
4. Handle upload failures (device not found, bootloader mode, wrong port).

**Guidelines**:
- If the build fails, fix the code -- don't ask the user to fix it.
- If the upload fails, guide the user through the physical steps (press BOOT, reconnect USB).
- Report binary size so the user knows if they're close to limits.
- **Build failures often reveal issues in the implementation.** After fixing, return to Phase 5 if the fix requires rethinking the approach, or stay in Phase 6 if it's a simple correction.

**Exit**: Firmware is running on the device.

## Phase 7: Hardware Testing

**Entry**: Firmware uploaded.

**Actions**:
1. Monitor serial output with `python3 serial_monitor.py -t 30`.
2. Interpret the output:
   - Boot messages (WiFi, Signal K connection, sensor init)
   - Sensor readings (are values plausible?)
   - Error messages (stack traces, watchdog resets)
3. Report findings in plain language.
4. **SensESP device setup** (for SensESP projects):
   - Guide the user to connect to the device's WiFi access point (SensESP creates one on first boot).
   - Walk them through the web UI to configure WiFi credentials for the boat's network.
   - Ask them to review the web UI configuration: are the sensor paths, update intervals, and other settings correct?
   - Once WiFi is configured, verify the device connects to the network (check serial output for connection confirmation).
5. **End-to-end verification**: Based on how the project is configured, ask the user to verify data arrives at its destination:
   - **Signal K server**: Can they see the sensor data in the Signal K dashboard or data browser?
   - **NMEA 2000**: Do the values appear on their chart plotter or MFD?
   - **Both**: Check each output path separately.
   - If the user isn't sure how to check, guide them through it based on what's in `system-profile.md` (e.g., which chart plotter they have).
6. **Ask the user for feedback.** Does the device behave as they expected? Is the data meaningful to them? Is anything missing, surprising, or wrong? Encourage them to describe what they see and how it compares to what they had in mind.
7. If issues are found -- technical or expectation-based -- diagnose and address them.

**Guidelines**:
- Plausibility checks: room temperature should be 15-30°C, not 0 or 1000. Oil pressure at idle should be non-zero.
- If sensor reads zero or constant, likely a wiring issue.
- If device reboots, look for stack traces.
- WiFi configuration happens through SensESP's built-in web portal, not in code.

**User feedback is the most valuable signal in this phase.** Users often can't fully express what they want until they see something working. It's common and perfectly fine for the user to say things like "this works, but actually I also need..." or "I thought I wanted X but now I realize I need Y." This isn't a problem -- it's the normal process of discovering real requirements through hands-on experience. Encourage it.

**Iteration**: Testing and user feedback frequently reveal issues that require going back to earlier phases:
- **Wiring or sensor issues** → return to Phase 2 (Hardware Documentation) to re-check connections.
- **"This isn't quite what I wanted"** or **missing features** → return to Phase 3 (Specification) to update requirements based on what the user has learned, then Phase 4-5 to redesign and reimplement.
- **Code bugs** → return to Phase 5, fix, then Phase 6 to rebuild and reflash.
- **Plausible readings but wrong values** → may need scaling or calibration adjustments in Phase 5.
- **"Can we also add..."** → welcome it. Update SPEC.md, return to the appropriate phase.

This iteration is normal and expected. Don't treat it as failure -- it's how firmware development works. Each cycle narrows the gap between intended and actual behavior. When updating SPEC.md based on feedback, note what changed and why so the evolution of requirements is visible.

**Exit**: The user confirms the device works as they expect -- sensor readings are plausible, data flows to the intended outputs, no crashes or errors, and the user is satisfied with the behavior.

## Phase 8: Review

**Entry**: Hardware testing passed.

**Actions**:
1. Review code for correctness, hardware compatibility, SensESP best practices.
2. Check Signal K path naming against conventions.
3. Verify pin assignments match the hardware doc.
4. Ensure no hardcoded WiFi credentials (unless user explicitly requested them).
5. Fix any issues found.

**Guidelines**:
- Keep the review proportional to the project size.
- **If the review reveals significant issues**, return to Phase 5 (Implementation) to fix them, then Phase 6-7 to rebuild and retest. Don't ship code with known problems.

**Exit**: Code is correct and follows best practices.

## Phase 9: Cleanup and Documentation

**Entry**: Review passed.

**Actions**:
1. Clean up: remove debug prints, organize code, ensure comments are helpful.
2. Final commit.
3. **Capture learnings**: Write down anything surprising, non-obvious, or useful for future projects:
   - Hardware quirks discovered during testing (e.g., "this sensor needs a 4.7k pull-up to work reliably")
   - Workarounds for framework limitations
   - Calibration values or scaling factors that were hard to find
   - Save these to `CLAUDE.local.md` (project-specific notes) or to Claude Code memory (for cross-project learnings).
4. Suggest pushing to GitHub as a backup.

**Guidelines**:
- Learnings are valuable. Even small observations ("HALMET analog input 3 has slightly higher noise than the others") can save hours on future projects.
- Don't write learnings that merely restate what the code does. Focus on what was surprising or non-obvious.

**Exit**: Project is complete, clean, and learnings are preserved.

## Work Journal

**Every project must have a `JOURNAL.md` file** in the project directory. This is a running work journal -- the raw, unpolished record of what happened, including dead ends, user feedback, direction changes, and session references. It survives session restarts and allows Claude to resume work correctly.

The journal is deliberately different from git history. Git commits are the cleaned-up narrative of what was built. The journal is the messy reality of how it got built -- the context that makes future sessions productive.

**Update `JOURNAL.md` at every meaningful step**: phase transitions, user feedback, decisions, problems encountered, direction changes. Include the Claude Code session name so future sessions can access the original conversation if needed.

**Format**:

```markdown
# Work Journal

## 2026-04-09 — Initial development
Session: determined-blue-fox

### Engine temperature monitoring
- Phase 1: User wants to monitor engine coolant temp on their Yanmar 3YM30.
  Checked system-profile.md — 12V system, has Signal K server on RPi.
- Phase 2: HALMET board, using analog input 1 with CCS enabled.
  VDO sender 120-10 ohm. Looked up resistance curve in VDO catalog.
- Phase 3: Wrote SPEC.md. User confirmed.
- Phase 4-5: Based design on ref/HALMET-example-firmware analog temp pattern.
  Implemented with linear interpolation transform.
- Phase 6: Built and flashed OK. Binary size 1.2MB.

## 2026-04-10 — Testing and iteration
Session: gentle-morning-rain

- Phase 7: Serial output shows temperature reading but value seems high (95°C
  at cold engine). User confirms engine is cold.
  → Problem: resistance-to-temperature mapping was inverted. VDO senders have
    HIGH resistance when cold, LOW when hot. Fixed the interpolation table.
- Rebuilt, reflashed. Now reads 22°C at cold engine. User confirms plausible.
- Walked user through SensESP WiFi setup. Connected to boat network.
- User confirms data visible on Signal K dashboard. Values match engine gauge.
- **Still TODO**: Review (Phase 8) and cleanup (Phase 9).

## 2026-04-10 — Adding oil pressure
Session: gentle-morning-rain (continued)

- User wants to add oil pressure as second feature.
- Phase 1: VDO 0-10 bar sender, 10-184 ohm. Using HALMET analog input 2.
- Phase 5: Implementation in progress...
```

The journal grows over the life of the project. It's committed to git along with everything else — it's part of the project's history.

## Resuming Work

When a user returns to an existing project or starts a new session:
1. Check `projects/` for their project(s).
2. **Read `JOURNAL.md`** to understand the current state -- what's been done, what's in progress, what's pending.
3. Read SPEC.md and source code to recall technical context.
4. Resume from where the journal left off. Tell the user where things stand: "Last session we got the temperature sensor working and verified it on Signal K. We still need to do code review and cleanup. Want to do that now, or work on something else first?"
5. **Do not skip remaining phases.** If the journal shows testing passed but review hasn't happened, the next step is review -- not "done."
6. Record the new session name in the journal and continue logging.
