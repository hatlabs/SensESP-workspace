---
name: new-project
description: >
  Guide the user through requirements gathering and create a new SensESP
  firmware project. Use when user wants to start a new project, describes
  a sensor/hardware goal, or says "new project".
argument-hint: "[optional: brief project description]"
---

# New SensESP Project

Guide the user through creating a new firmware project. Follow each phase in order. Ask one question at a time. Never skip the hardware documentation phase.

## Phase 0: Assess

- Check if `system-profile.md` exists. If not, run the system profiling interview first (see `docs/WORKFLOW.md` Phase 0). This captures the user's boat, engines, electrical system, existing electronics, and goals. This step is essential -- do not skip it for the first project.
- If `system-profile.md` exists, read it to inform all subsequent decisions.
- Check if there's already a project in progress in `projects/`. If so, ask if they want to continue that or start fresh.
- If the user provided a description in the argument, use it as the starting point for Phase 1.

## Phase 1: Requirements Gathering

Interview the user to understand what they want to build. Ask **one question at a time** and offer clear choices where possible. Cross-reference all assumptions against `system-profile.md` -- don't ask questions the profile already answers, and don't suggest things that contradict the user's setup.

**Never guess technical specifications.** If you need to know sender resistance ranges, signal types, PGN numbers, or protocol details, look them up in the reference firmware (`ref/`) or online. Say "I'm not sure about X, let me check" rather than confidently stating something wrong.

**Questions to cover** (adapt order to the conversation):

1. **Goal**: What do you want your device to do? (monitor engine, measure tank levels, gateway between protocols, alarm system, etc.)
2. **Hardware**: Which board are you using? Offer choices based on what the system profile says they own:
   - HALMET (analog/digital inputs, engine monitoring, tank levels)
   - HALSER (serial interfaces, NMEA 0183, AIS)
   - SH-ESP32 (general purpose with CAN/N2K)
   - SH-wg (WiFi gateway)
   - Generic ESP32 board (ask them to describe it)
3. **Sensors**: What sensors or inputs will you connect? (temperature senders, pressure senders, tank level senders, GPS, wind instruments, etc.)
4. **Outputs**: Where should the data go? (Signal K server via WiFi, NMEA 2000 network, both, display, alarms)
5. **Environment**: Where will this run? (boat, vehicle, indoor, outdoor)

**Handling "I don't know"**: Suggest sensible defaults based on their goal. For example, if they want engine monitoring on HALMET, suggest temperature + oil pressure + RPM as a starting point.

## Phase 2: Hardware Documentation

Once you know which board they're using:

1. Read the relevant `docs/hardware/<board>.md` file.
2. **Present wiring instructions** for their specific sensors. Include pin numbers, connector positions, and any jumper settings.
3. **Warn about gotchas** (voltage limits, isolation boundaries, required pull-ups).
4. If using a generic board, ask for a link to the board's documentation or have them describe the pinout.

This phase is mandatory even if the user didn't ask about wiring.

## Phase 3: Specification

Write a `SPEC.md` file in the project directory summarizing:

```markdown
# <Project Name> Specification

## Goal
<What this firmware does, in plain language>

## Hardware
- **Board**: <board name and model>
- **Sensors/Inputs**: <list with connection details>
- **Outputs**: <Signal K paths, N2K PGNs, display, alarms>

## Connections
<Pin-by-pin wiring table>

## Expected Behavior
<What happens when the device is running>

## Dependencies
<PlatformIO libraries needed>
```

Present the spec to the user and ask for confirmation before proceeding.

## Phase 4: Project Creation

1. Create the project directory: `projects/<name>/`
2. Copy `ref/SensESP-project-template/` (`platformio.ini`, `sdkconfig.defaults`, `sdkconfig.defaults.esp32c3`, `min_spiffs.csv`, `CMakeLists.txt`, `src/CMakeLists.txt`, `src/idf_component.yml`) and set `default_envs` to the board's `<board>_espidf` env. See `docs/WORKFLOW.md` Phase 5.
3. Create `src/main.cpp` with a basic SensESP skeleton appropriate for their use case. Study the relevant reference examples in `ref/` for patterns.
4. Create `JOURNAL.md` work journal (see `docs/WORKFLOW.md` "Work Journal" section for format). Record the current session name and log completed phases.
5. Initialize a git repo: `git init` in the project directory.
6. Commit the initial structure.

## Phase 5: Handoff

Present what was created and offer next steps:

- "Ready to start building the firmware?" (proceeds to implementation)
- "Want to adjust the specification?"
- "Want to see how similar projects are built?" (show relevant reference code)
