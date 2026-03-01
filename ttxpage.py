from __future__ import annotations

from tkinter import Tk
from typing import Optional

import screeninfo

from ttxline import TTXline


class TTXpage:
    # Teletext layout constants
    MIN_ROW: int = 0
    MAX_ROW: int = 24
    FASTEXT_LINK_COUNT: int = 4

    # Packet parsing constants (packet 27 / fastext)
    _FASTEXT_OFFSET: int = 2
    _FASTEXT_DESIGNATION_CODE_INDEX: int = 6

    # UI constants
    _BACKGROUND: str = "black"
    _FULLSCREEN: bool = True

    def __init__(self) -> None:
        print("TTXPage created")

        self.root = Tk()

        current_monitor = self.get_monitor_from_coord(self.root.winfo_x(), self.root.winfo_y())
        self.screen_width = current_monitor.width
        self.screen_height = current_monitor.height

        self._apply_root_geometry()

        # Lines
        self.lines = TTXline(self.root, self.screen_height)
        self.lines.text.pack()

        self.root.update_idletasks()
        self.root.update()

        # Fastext links
        self.mag: list[Optional[int]] = [None] * self.FASTEXT_LINK_COUNT
        self.page: list[Optional[int]] = [None] * self.FASTEXT_LINK_COUNT

        # Key handling
        self.root.bind("<KeyPress>", self.on_key_press)
        self.buffer: list[str] = []

        # Level 1.5 character replacement state (kept as-is)
        self.rowAddr = 0
        self.colAddr = 0

        print("ttxpage constructor exits")

    def _apply_root_geometry(self) -> None:
        """Configure the root window appearance and size."""
        self.root.configure(background=self._BACKGROUND, borderwidth=0, highlightthickness=0)

        geometry = f"{self.screen_width}x{self.screen_height}+0+0"
        print(f"[ttxpage::__init__] geometry = {geometry}")
        self.root.geometry(geometry)

        if self._FULLSCREEN:
            # Make it full screen (Comment it out if you want to run in a window)
            self.root.wm_attributes("-fullscreen", "true")

        self.root.wait_visibility(self.root)

    def get_monitor_from_coord(self, x: int, y: int):
        monitors = screeninfo.get_monitors()
        for monitor in reversed(monitors):
            if monitor.x <= x <= monitor.width + monitor.x and monitor.y <= y <= monitor.height + monitor.y:
                return monitor
        return monitors[0]

    # ... existing code ...

    # Backwards-compatible wrappers (avoid breaking existing call sites)
    def getPage(self, index):
        return self.get_page(index)

    def getMag(self, index):
        return self.get_mag(index)

    def get_page(self, index: int) -> Optional[int]:
        """Return the page number for the fastext link selected by index."""
        return self.page[index]

    def get_mag(self, index: int) -> Optional[int]:
        """Return the magazine number for the fastext link selected by index."""
        return self.mag[index]

    @staticmethod
    def deham(value: int) -> int:
        """Decode a Hamming(8,4) nibble with no parity/error correction."""
        b0 = (value & 0x02) >> 1
        b1 = (value & 0x08) >> 2
        b2 = (value & 0x20) >> 3
        b3 = (value & 0x80) >> 4
        return b0 + b1 + b2 + b3

    def printRow(self, packet, row):
        return self.print_row(packet, row)

    def print_row(self, packet, row: int) -> bool:
        """Return True if the packet contained double height."""
        if row < self.MIN_ROW or row > self.MAX_ROW:
            return False
        return self.lines.printRow(packet, row)

    def printHeader(self, packet, page, seeking, suppress=False):
        self.print_header(packet, page, seeking, suppress)

    def print_header(self, packet, page, seeking: bool, suppress: bool = False) -> None:
        self.lines.printHeader(packet, page, seeking, suppress)

    def mainLoop(self):
        self.main_loop()

    def main_loop(self) -> None:
        """Actually draw the stuff."""
        self.root.update_idletasks()
        self.root.update()

    def toggleReveal(self):
        self.toggle_reveal()

    def toggle_reveal(self) -> None:
        self.lines.toggleReveal()

    # ... existing code ...

    def decodeLinks(self, packet):
        self.decode_links(packet)

    def decode_links(self, packet) -> None:
        """Decode packet 27 fastext links."""
        offset = self._FASTEXT_OFFSET
        _dc = self.deham(packet[self._FASTEXT_DESIGNATION_CODE_INDEX + offset])  # designation code (unused for now)

        mag = self.deham(packet[0]) & 0x07  # Magazine of this packet
        for i in range(self.FASTEXT_LINK_COUNT):
            addr = (i - 1) * 6 + 7 + offset

            b1 = self.deham(packet[addr])
            b2 = self.deham(packet[addr + 1])

            # Relative magazine bits of target link M1, M2, M3
            m1 = self.deham(packet[addr + 3]) & 0x08
            m2 = self.deham(packet[addr + 5]) & 0x04
            m3 = self.deham(packet[addr + 5]) & 0x08

            target_mag = mag
            if m1:
                target_mag ^= 0x01
            if m2:
                target_mag ^= 0x02
            if m3:
                target_mag ^= 0x04
            if target_mag == 0:
                target_mag = 8

            target_page = b2 * 0x10 + b1
            self.mag[i] = target_mag
            self.page[i] = target_page

    @staticmethod
    def reverse(x: int) -> int:
        """Reverse the bit order in a byte."""
        x &= 0xFF
        x = ((x & 0xF0) >> 4) | ((x & 0x0F) << 4)
        x = ((x & 0xCC) >> 2) | ((x & 0x33) << 2)
        x = ((x & 0xAA) >> 1) | ((x & 0x55) << 1)
        return x

    def onKeyPress(self, event):
        self.on_key_press(event)

    def on_key_press(self, event) -> None:
        # Tkinter uses event.char as a string; it may be '' for non-character keys.
        self.buffer.append(event.char)
        self._key_debug("[ttxpage::on_key_press]", event.char)

    @staticmethod
    def _key_debug(prefix: str, ch: str) -> None:
        if ch != "":
            print(f"{prefix} You pressed {ord(ch)}")

    def getKey(self):
        return self.get_key()

    def get_key(self) -> str:
        """
        Return the next buffered key as a character, or a single space if none.

        Note: original code attempted `key == 105` (int) while `key` is a string.
        """
        if not self.buffer:
            return " "

        ch = self.buffer.pop(0)
        if ch == "":
            return " "

        print(f"[ttxpage::get_key] key == {ord(ch)}")

        # Preserve original behaviour: map 'i' (105) to 'P' (F1 mapping in caller)
        if ch == "i":
            return "P"

        return ch

    def dumpPacket(self, pkt):
        for i in range(8):
            print(str(i) + ":" + hex(pkt[i]) + " ", end="")
        print()

    # ... existing code ...

    def decodeRow26(self, pkt):
        return  # This is moved to packet

    # Set a flag to clear down when starting the next page
    def clear(self):
        self.lines.clear("new page")