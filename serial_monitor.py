#!/usr/bin/env python3
"""Non-interactive serial monitor that does not reset the device.

The ESP32 auto-reset circuit triggers on a DTR/RTS *edge*. This monitor opens
the port without ever driving DTR/RTS (raw termios open, HUPCL cleared), so no
edge is produced and the chip is never reset -- safe to attach to a device
that is already running, regardless of what state a prior tool (e.g. esptool
after a flash) left the modem-control lines in.

Standard baud rates use a dependency-free raw-termios path. Non-standard rates
fall back to pyserial, which drives DTR/RTS on open and may reset the device.

Supports macOS, Linux, and WSL port auto-detection.
"""

import argparse
import os
import platform
import select
import sys
import termios
import time

# Standard rates reachable with POSIX termios speed constants (no reset).
BAUD_CONSTANTS = {
    9600: termios.B9600,
    19200: termios.B19200,
    38400: termios.B38400,
    57600: termios.B57600,
    115200: termios.B115200,
    230400: termios.B230400,
    460800: getattr(termios, "B460800", None),
    921600: getattr(termios, "B921600", None),
}


def open_reset_free(port, baud):
    """Open the port raw, never touching DTR/RTS. Returns (fd, close) or None.

    Returns None if the baud rate has no termios constant (caller should fall
    back to pyserial).
    """
    speed = BAUD_CONSTANTS.get(baud)
    if speed is None:
        return None
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = termios.IGNBRK  # iflag: raw input
    attrs[1] = 0               # oflag: raw output
    # cflag: 8N1, ignore modem control (CLOCAL), enable receiver (CREAD), and
    # clear HUPCL so close() doesn't drop the lines either.
    attrs[2] = (attrs[2] & ~(termios.HUPCL | termios.PARENB | termios.CSTOPB |
                             termios.CSIZE)) | termios.CS8 | termios.CLOCAL | \
        termios.CREAD
    attrs[3] = 0               # lflag: raw (no canonical mode, echo, signals)
    attrs[4] = speed           # ispeed
    attrs[5] = speed           # ospeed
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd, lambda: os.close(fd)


def read_loop(fd, timeout):
    """Stream the fd to stdout line-buffered until timeout (0 = forever)."""
    deadline = time.time() + timeout if timeout > 0 else None
    buf = b""
    try:
        while deadline is None or time.time() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.5)
            if not ready:
                continue
            try:
                data = os.read(fd, 4096)
            except BlockingIOError:
                # select() can spuriously report readable on a non-blocking
                # tty; no data is actually available yet.
                continue
            if not data:
                continue
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                sys.stdout.write((line + b"\n").decode("utf-8", errors="replace"))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        if buf:
            sys.stdout.write(buf.decode("utf-8", errors="replace"))
            sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Read serial output without resetting the device"
    )
    parser.add_argument(
        "port",
        nargs="?",
        help="Serial port (default: auto-detect)",
    )
    parser.add_argument(
        "-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)"
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=0,
        help="Exit after N seconds (default: 0 = run until interrupted)",
    )
    args = parser.parse_args()

    port = args.port
    if port is None:
        port = auto_detect_port()
        if port is None:
            print("Error: no USB serial device found", file=sys.stderr)
            if is_wsl():
                print(
                    "\nWSL detected. USB devices require usbipd-win to pass through.",
                    file=sys.stderr,
                )
                print(
                    "See: https://learn.microsoft.com/en-us/windows/wsl/connect-usb",
                    file=sys.stderr,
                )
            sys.exit(1)
        print(f"Auto-detected port: {port}", file=sys.stderr)

    opened = open_reset_free(port, args.baud)
    if opened is not None:
        fd, close = opened
        try:
            read_loop(fd, args.timeout)
        finally:
            close()
        return

    # Non-standard baud: fall back to pyserial. This drives DTR/RTS on open and
    # may reset the device.
    print(
        f"Note: baud {args.baud} has no reset-free termios constant; "
        "falling back to pyserial (may reset the device).",
        file=sys.stderr,
    )
    import serial

    ser = serial.Serial()
    ser.port = port
    ser.baudrate = args.baud
    ser.timeout = 1
    ser.dtr = False
    ser.rts = False
    ser.dsrdtr = False
    ser.rtscts = False
    ser.open()
    try:
        read_loop(ser.fileno(), args.timeout)
    finally:
        ser.close()


def is_wsl():
    """Detect if running under Windows Subsystem for Linux."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def auto_detect_port():
    import glob

    ports = []

    system = platform.system()
    if system == "Darwin":
        # macOS
        ports = glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/cu.usbserial*")
    elif system == "Linux":
        # Linux and WSL (if USB passthrough is configured)
        ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")

    if len(ports) == 1:
        return ports[0]
    if len(ports) > 1:
        print(f"Multiple ports found: {ports}", file=sys.stderr)
        print(f"Using first: {ports[0]}", file=sys.stderr)
        return ports[0]
    return None


if __name__ == "__main__":
    main()
