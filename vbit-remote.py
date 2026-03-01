#!/usr/bin/env python3

# Copyright (c) 2021 Peter Kwan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#   Remote control client
#   Connects REQ socket to tcp://localhost:5558
#   Sends remote control commands to vbit-vi

# pip3 install readchar
# pip3 install pyzmq
#
"""
Remote control client for vbit-iv.

Connects a REQ socket to the remote control port and sends key presses.
"""

import zmq

DEFAULT_HOST = "tcp://127.0.0.1:7777"
EXIT_KEYS = {"q"}  # Ctrl+C is handled via KeyboardInterrupt


def _read_key() -> str:
    """
    Read a single character.

    Prefers `readchar` (if installed); otherwise falls back to a very small
    cross-platform-ish stdin reader.
    """
    try:
        import readchar  # type: ignore
    except ModuleNotFoundError:
        # Fallback: read a single character from stdin.
        # On Windows this may require Enter in some terminals; still better than crashing.
        return input()[:1] or ""
    else:
        return readchar.readchar()


def _create_socket(context: zmq.Context, host: str) -> zmq.Socket:
    socket = context.socket(zmq.REQ)
    socket.connect(host)
    return socket


def main(host: str = DEFAULT_HOST) -> None:
    print("Connecting to vbit-iv")
    with zmq.Context() as context:
        socket = _create_socket(context, host)

        try:
            while True:
                ch = _read_key()

                if not ch:
                    continue

                # Ctrl+C is handled by KeyboardInterrupt; keep 'q' for convenience.
                if ch in EXIT_KEYS:
                    socket.send_string(ch)
                    return

                socket.send_string(ch)
                socket.recv()  # reply is not used; keep the REQ/REP handshake happy
        except KeyboardInterrupt:
            # Send 'q' to request a clean shutdown on the server side, then exit.
            try:
                socket.send_string("q")
            except Exception:
                pass


if __name__ == "__main__":
    main()