#!/usr/bin/env python3

# Teletext Stream to Invision decoder
#
# Copyright (c) 2020-2026 Peter Kwan
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

from tkinter import Text, END, NORMAL, DISABLED
from tkinter.font import Font

from clut import clut
from mapper import mapchar, mapdiacritical
from packet import metaData


def deham(value):
    """Decode a Hamming(8,4) nibble with no parity/error correction."""
    bit0 = (value & 0x02) >> 1
    bit1 = (value & 0x08) >> 2
    bit2 = (value & 0x20) >> 3
    bit3 = (value & 0x80) >> 4
    return bit0 + bit1 + bit2 + bit3


class TTXline:
    """
    Represents a class for managing and displaying a teletext line.

    The `TTXline` class handles the structure and layout of teletext-based text
    components within a GUI application. It includes features such as font
    management, row and line manipulation for teletext pages, and basic rules for
    graphics and mosaic rendering. The class can also manage additional states like
    concealed text, double-height rows, and side panels for specialised components.

    :ivar root: The root GUI component to which the teletext elements are attached.
    :type root: Any
    :ivar text: The primary text widget for displaying teletext content.
    :type text: tkinter.Text
    :ivar textConceal: A secondary text widget for managing concealed or hidden text.
    :type text: tkinter.Text
    :ivar width_value: The screen width of the environment in which the application runs.
    :type width_value: int
    :ivar height_value: The height of the teletext lines or application window.
    :type height_value: int
    :ivar fontH: The font height calculated dynamically based on screen dimensions.
    :type fontH: int
    :ivar ttxfont2: Font used for standard teletext rows.
    :type ttxfont2: tkinter.font.Font
    :ivar ttxfont4: Font used for double-height teletext rows.
    :type ttxfont4: tkinter.font.Font
    :ivar rowOffset: Offset used for managing the height of rows with special properties like double-height.
    :type rowOffset: int
    :ivar pageLoaded: Indicates whether a teletext page has been successfully loaded.
    :type pageLoaded: bool
    :ivar found: Indicates certain processing states for teletext content.
    :type found: bool
    :ivar currentHeader: The header of the currently displayed teletext page, stored as a byte array.
    :type currentHeader: bytearray
    :ivar revealMode: Indicates if the concealed text is currently revealed.
    :type revealMode: bool
    :ivar natOpt: National option code for teletext regional settings.
    :type natOpt: int
    :ivar clearFlag: Denotes whether the teletext page is cleared or marked for clearing.
    :type clearFlag: bool
    :ivar offsetSplit: Specifies the split index for side panels within the teletext display.
    :type offsetSplit: int
    """

    # Map a teletext colour number to an actual colour
    # The CLUT needs to be chosen according to X26 settings so this isn't good enough
    # Probably also needs to go to CLUT instead of being in here

    # Teletext layout constants
    TEXT_COLUMNS = 40
    DISPLAY_LINES = 25 # 0 row is the header, 23 lines on page, 1 for fastext
    SIDE_PANEL_COLUMNS = 16

    # Initial filler lines (kept as-is, but named)
    _BLANK_ROW = "                                        \n"
    _SPLASH_ROW_INDEX = 11
    _SPLASH_ROW_TEXT = "     VBIT IN-VISION                     \n"
    _SPLASH_TAG = "dbl"

    def get_colour(self, colour_index: int):
        """Return the colour value for a teletext colour index."""
        return clut.clut0[colour_index % 8]

    def __init__(self, root_param, height=360):
        """
        Initializes a teletext display object that handles the rendering of text onto
        a tkinter Text widget, applying specific configurations for font size,
        multi-screen setup, and concealed text.

        :param root_param: The tkinter root or parent widget where the text will
            be displayed.
        :param height: Screen height to be used for text rendering. Defaults to 360.
        """
        print("TTXLine created")

        # this is where we define a Text object and set it up
        self.root = root_param

        # establish the maximum font size required to fill the available space
        self.width_value = self.root.winfo_screenwidth()
        self.height_value = height

        # @todo Temporary hack to cope with my own multi-screen setup
        if self.width_value < self.height_value:
            self.height_value = self.width_value / 1.77

        self.fontH = -round((-1 + self.height_value / (self.DISPLAY_LINES + 2)))
        self.ttxfont2 = Font(family="teletext2", size=round(self.fontH))
        self.ttxfont4 = Font(family="teletext4", size=round(self.fontH * 2))

        self.total_columns = self.TEXT_COLUMNS + self.SIDE_PANEL_COLUMNS

        self.text = Text(self.root, width=self.total_columns, height=self.DISPLAY_LINES)  # The normal text
        self.textConceal = Text(self.root, width=self.total_columns, height=self.DISPLAY_LINES)  # Concealed copy

        self._configure_text_widgets()

        # Build blank rows that actually match the configured width (prevents odd indexing behaviour)
        self._blank_row = (" " * self.total_columns) + "\n"

        self._populate_initial_buffer()
        self._ensure_rows_exist()

        self.rowOffset = 0  # Used to elide double height lines
        self.pageLoaded = False
        self.found = False
        self.currentHeader = bytearray()
        self.currentHeader.extend(
            b"YZ0123456789012345678901234567890123456789"
        )  # header of the page that is being displayed
        self.revealMode = False  # hidden

        # header flags
        self.natOpt = 0  # 0=EN, 1=FR, 2=SW/FI/HU, 3=CZ/SK, 4=DE, 5=PT/SP, 6=IT, 7=N/A
        self.clearFlag = False  # Set by clear(), cleared by printHeader()
        self.offsetSplit = 8  # Where the side panels are split (0..16, default 8)

    def _ensure_rows_exist(self) -> None:
        """
        Ensure both Text widgets contain at least DISPLAY_LINES + 1 lines.

        Note: tkinter.Text always maintains a trailing newline / extra line.
        If we insert DISPLAY_LINES rows with '\n', we end up with DISPLAY_LINES + 1 lines.
        """
        def line_count(widget: Text) -> int:
            end_line = int(widget.index("end").split(".")[0])
            return max(0, end_line - 1)

        def append_blank_lines(widget: Text, n: int) -> None:
            if n <= 0:
                return
            blank = (" " * self.total_columns) + "\n"
            widget.insert(END, blank * n)

        want = self.DISPLAY_LINES + 1

        have = line_count(self.text)
        if have < want:
            append_blank_lines(self.text, want - have)

        have_c = line_count(self.textConceal)
        if have_c < want:
            append_blank_lines(self.textConceal, want - have_c)

    def _replace_row_text(self, widget: Text, row0: int, text: str) -> None:
        """
        Replace a single row's content with fixed-width text without deleting the newline.

        row0 is 0-based: row0=0 -> Text line 1.
        """
        self._ensure_rows_exist()

        line1 = row0 + 1
        start = f"{line1}.0"
        end = f"{line1}.{self.total_columns}"

        fixed = (text[: self.total_columns]).ljust(self.total_columns, " ")

        widget.delete(start, end)
        widget.insert(start, fixed)

    def _configure_text_widgets(self) -> None:
        """Apply a consistent look-and-feel to both Text widgets."""
        base_cfg = dict(
            borderwidth=0,
            foreground="white",
            background="black",
            font=self.ttxfont2,
            padx=0,
            pady=0,
            autoseparators=0,
            highlightbackground="black",
        )
        self.text.config(**base_cfg, spacing1=0, spacing2=0, spacing3=-1)
        self.textConceal.config(**base_cfg)

    def _populate_initial_buffer(self) -> None:
        """Create initial blank rows and a demo double-height row (as per existing behaviour)."""
        for i in range(self.DISPLAY_LINES):
            if i == self._SPLASH_ROW_INDEX:
                self.text.insert(END, self._SPLASH_ROW_TEXT)
                self.textConceal.insert(END, self._SPLASH_ROW_TEXT)
                self.text.tag_add(self._SPLASH_TAG, "12.0", "12.end")
                self.text.tag_config(self._SPLASH_TAG, font=self.ttxfont4, offset=0, foreground="orange")
            else:
                # Use width-correct blank row (not the old 40-column constant)
                self.text.insert(END, self._blank_row)
                self.textConceal.insert(END, self._blank_row)

    # true if while in graphics mode, it is a mosaic character. False if control or upper case alpha
    def is_mosaic(self, ch):
        return bool(ch & 0x20)  # Bit 6 set?

    def dump(self, pkt):
        return
        print("Dumping row")
        for i in range(len(pkt)):
            print(str(i) + " " + pkt.hex())

    def _row_index_range(self, row: int) -> tuple[str, str, str]:
        """Return (rstr, start_index, end_index) for a given 0-based row."""
        rstr = f"{row + 1}."
        return rstr, f"{rstr}0", f"{rstr}end"

    # clear and replace the line contents
    # @param packet : packet to write
    # @param row : row number to write (starting from 0)
    def setLine(self, pkt, row):

        if row == 2:
            self.dump(pkt)

        # Keep rows stable
        self._ensure_rows_exist()
        if row < 0 or row >= self.DISPLAY_LINES:
            return False

        rstr = str(row + 1) + "."
        tag_start = str(rstr + "0")
        tag_end = str(rstr + "end")

        # wsfn remove this for testing
        for tag in self.text.tag_names():  # erase the line attributes
            attr = tag.split("-")
            if attr[0] == str(row + 1):
                self.text.tag_delete(tag)
                self.textConceal.tag_delete(tag)

        # Instead of deleting the whole line (which can remove blank rows), overwrite it safely
        self._replace_row_text(self.text, row, " " * self.total_columns)
        self._replace_row_text(self.textConceal, row, " " * self.total_columns)

        # Set the conditions at the start of the line
        graphicsMode = False
        hasDoubleHeight = False
        holdChar = 0x00
        holdMode = False
        contiguous = True
        concealed = False
        flashMode = False  # @todo

        lastMosaicChar = " "

        def _primary_charset() -> tuple[int, int]:
            """
            Primary G0 charset (region/option):
            - If X/28 is present, use its default G0 region/option
            - Else fall back to header natOpt, region 0
            """
            if metaData.defaultCharSetLanguage is not None and metaData.defaultCharSetRegion is not None:
                return metaData.defaultCharSetLanguage, metaData.defaultCharSetRegion
            return self.natOpt, 0

        def _secondary_charset() -> tuple[int, int]:
            """
            Secondary G0 charset (region/option) from X/28, if present.
            If absent, fall back to primary (so ESC becomes a harmless toggle).
            """
            if metaData.secondG0CharSetLanguage is not None and metaData.secondG0CharSetRegion is not None:
                return metaData.secondG0CharSetLanguage, metaData.secondG0CharSetRegion
            return _primary_charset()

        # Second G0 toggle state:
        # At the start of each line, we use the FIRST G0 set (primary).
        use_second_g0 = False

        #def _active_charset() -> tuple[int, int]:
        #    """
        #    Decide which (language_option, region) to use for mapchar().
        #    - Header-derived language option: self.natOpt, region forced to 0
        #    - Packet 28 override: metaData.defaultCharSetLanguage/defaultCharSetRegion
        #    """
        #    if metaData.defaultCharSetLanguage is not None and metaData.defaultCharSetRegion is not None:
        #        print ("[ttxline::_active_charset] option = " + str(metaData.defaultCharSetLanguage) + " region = " + str(metaData.defaultCharSetRegion))
        #        return metaData.defaultCharSetLanguage, metaData.defaultCharSetRegion
        #    return self.natOpt, 0

        #self.text.insert(tag_start, "        ") # This could be a big mistake
        #self.text.insert(tag_start, "        ")

        # PASS 1: put the characters in. Selects glyphs for alpha, contiguous gfx, separated gxf
        #print('[setLine] rendering row ' + str(row))
        for i in range(40):
            c = pkt[i + 2] & 0x7f # strip parity
            # Convert control code ascii

            # ESC toggles between primary and secondary G0 for subsequent characters on this line.
            # The ESC itself is not displayed.
            if c == 0x1B:
                use_second_g0 = not use_second_g0
                c = 0x20  # treat as space for rendering
            ch = chr(c)
            if c < 0x08 or c >= 0x10 and c < 0x18: # colour codes cancel conceal mode
                concealed = False
            #if c == 0x0f: # double size
             #   print("double size not implemented")  # Not the same as double height
            if c == 0x1e: # hold graphics - set at
                holdMode = True
                holdChar = lastMosaicChar # ' '
            if c == 0x18: # conceal mode - set at
                concealed = True
            if c == 0x19: # Contiguous graphics
                contiguous = True
            if c == 0x1a: # Separated graphics
                contiguous = False
            if graphicsMode:
                # If it is a mosaic, work out what character it is
                if self.is_mosaic(c):
                    if contiguous:
                        ch = chr(c + 0x0e680 - 0x20) # contiguous
                    else:
                        ch = chr(c + 0x0e680) # separate
                    if holdMode:
                        holdChar = ch # save the character for later
                    lastMosaicChar = ch
                else:
                    if ch<' ': # Unprintable?
                        if holdMode:
                            ch = holdChar # non printable and in hold
                        else:
                            ch = " " # Non printable
                    else:
                        if use_second_g0:
                            lang_opt, region = _secondary_charset()
                        else:
                            lang_opt, region = _primary_charset()
                        ch = mapchar(ch, lang_opt, region)  # text in alpha mode @todo implement
                        ch = mapdiacritical(ch, row, i, metaData.X26CharMappings)
                # if it is not a mosaic and we are in hold mode, substitute the character
            else:
                # alpha is way simpler
                if ch < ' ':
                    ch = ' '
                else:
                    if use_second_g0:
                        lang_opt, region = _secondary_charset()
                    else:
                        lang_opt, region = _primary_charset()
                    ch = mapchar(ch, lang_opt, region)  # text in alpha mode @todo implement group number
                    ch = mapdiacritical(ch, row, i, metaData.X26CharMappings)

            # Overwrite (do not insert): inserting shifts the line and can corrupt alignment over time
            col = i + self.offsetSplit
            pos0 = f"{rstr}{col}"
            pos1 = f"{rstr}{col + 1}"

            out_ch = ch if not concealed else ' '
            self.text.delete(pos0, pos1)
            self.text.insert(pos0, out_ch)

            conceal_ch = ch if concealed else ' '
            self.textConceal.delete(pos0, pos1)
            self.textConceal.insert(pos0, conceal_ch)

            # set-after
            if c == 0x1f: # release graphics - set after
                holdMode = False
            if c < 0x08: # alpha colours
                graphicsMode = False
            if c >= 0x10 and c < 0x18: # Mosaic colour
                graphicsMode = True

        # PASS 2: Add text attributes: font, colour, flash

        # Any full row colours?
        #print('[setLine] rendering pass 2')
        foreground_colour = 7 # 'white'
        background_colour = 0 # 'black'
        text_height = 'single'

        # Set the initial colour for the row
        # background_colour = metaData.rowColour(row) # X26/0 full row colour triplet
        #print('[setLine] row = ' + str(row) + " bgcol = " + background_colour)

        # Complicate things if side panels are enabled
        if metaData.leftSidePanel or metaData.rightSidePanel:
            #print('[setLine] SETTING SIDE PANELS')
            tag_id = "rowBGCol"+str(row)
            fg = clut.RemapColourTable(foreground_colour, metaData.ColourTableRemapping, True)
            bg = metaData.rowColour(row)
            self.text.tag_config(tag_id , font = self.ttxfont2, foreground = fg, background = bg)
            self.textConceal.tag_config(tag_id , font = self.ttxfont2, foreground = fg, background = bg)
            if metaData.BlackBackgroundColourSubstitution:
                self.text.tag_add(tag_id, rstr + str(0), rstr + 'end') # whole row
                self.textConceal.tag_add(tag_id, rstr + str(0), rstr + 'end') # whole row
            else:
                # Side panels only
                # @ todo Check where the actual split is, not just 8+8
                background_colour = 0 # 'black'
                if metaData.leftSidePanel:
                    self.text.tag_add(tag_id, rstr + str(0), rstr + str(8)) # left panel
                    self.textConceal.tag_add(tag_id, rstr + str(0), rstr + str(8)) # left panel
                if metaData.rightSidePanel:
                    self.text.tag_add(tag_id, rstr + str(48), rstr + 'end') # right panel
                    self.textConceal.tag_add(tag_id, rstr + str(48), rstr + 'end') # right panel


        # Set the text attributes: colour and font size
        # row
        row = str(row + 1)
        ix= 0
        attr = text_height
        for i in range(40):
            c = pkt[i+2] & 0x7f
            ch = chr(c)
            #if i==1 and c<0x20:
            #print (hex(c))
            attributeChanged =False
            if c == 0x0c: # normal height
                # This code breaks if there is a normal size but NO double height on the line
                text_height = 'single'
                #tag_id = "thc"+str(row)+"-"+str(i)
                attributeChanged = True
                #tag_id = text_height + '-' + foreground_colour + '-' + background_colour
                #self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after
                # self.text.tag_config(tag_id, font=self.ttxfont2, offset=0) # normal height too
            # @todo Doing another pass for the offset is the only way to make it work correctly, probably
            if c == 0x0d: # double height
                text_height = 'double'
                hasDoubleHeight = True
                attributeChanged = True
                #tag_id = "thd"+str(row)+"-"+str(i)
                #tag_id = text_height + '-' + foreground_colour + '-' + background_colour
                #self.text.tag_add(tag_id, rstr + str(i+1), rstr + 'end') # column + 1 - set-after
                #self.text.tag_config(tag_id, font=self.ttxfont4, offset=0) # double height

            set_at = 1 # 0 = set at, 1 = set after
            if c==0x1c: # black background - set at
                background_colour = 0x00
                attributeChanged = True
                set_at = 0
            if c==0x1d: # new background - set at
                background_colour = foreground_colour
                attributeChanged = True
                set_at = 0
            if c < 0x08 : # alpha colour - set after
                foreground_colour = c
                attributeChanged = True
                # also need to see if there is an X26/0 background colour change
                #foreground_colour = metaData.mapColourFg(int(row), i, foreground_colour)
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
            if c >= 0x10 and c < 0x18: # Mosaic colour - set after
                foreground_colour = c-0x10 # self.getcolour(c-0x10)
                attributeChanged = True
                #foreground_colour = metaData.mapColourFg(int(row), i, foreground_colour)
                #background_colour = metaData.mapColourBg(int(row), i, background_colour)
                # also need to see if there is an X26/0 foreground colour change
            fg = metaData.mapColourFg(int(row), i+1, foreground_colour) # Set after
            if fg != 'x':
                attributeChanged = True
                #foreground_colour = fg
            bg = metaData.mapColourBg(int(row), i+1, background_colour) # Set at
            if bg != 'x':
                attributeChanged = True
                #background_colour = bg
            if attributeChanged:
                if fg != 'x':
                    fgc = fg
                else:
                    fgc = clut.RemapColourTable(foreground_colour, metaData.ColourTableRemapping, True)
                if bg != 'x':
                    bgc = bg
                else:
                    bgc = clut.RemapColourTable(background_colour, metaData.ColourTableRemapping, False)
                # tag_id identifies the row
                tag_id = row + '-' + str(ix) + '-' + text_height + '-' + fgc + '-' + str(background_colour)
                ix = ix + 1
                self.text.tag_add(tag_id, rstr + str(i+set_at+self.offsetSplit), rstr + str(48)) # @todo This depends on the side panel columns
                self.textConceal.tag_add(tag_id, rstr + str(i+set_at+self.offsetSplit), rstr + str(48)) #

                if text_height == 'double':
                    textFont = self.ttxfont4
                    #print("line 325. It got here")
                else:
                    textFont = self.ttxfont2
                self.text.tag_config(tag_id , font = textFont, foreground = fgc, background = bgc)
                self.textConceal.tag_config(tag_id , font = textFont, foreground = fgc, background = bgc)

        self.text.config(state = DISABLED) # prevent editing
        return hasDoubleHeight

    def decodeFlags(self, packet):
        flags = [0,0,0,0,0,0,0,0,0]
        for i in range(8):
            flags[i] = deham(packet[i+2])
            print (hex(flags[i]) + ', ', end='')
        print()
        page = flags[1]*0x10 + flags[0]
        C4 = (flags[3] & 0x08) > 0 # clear
        C5 = (flags[5] & 0x04) > 0 # newsflash
        self.natOpt = (flags[7] >> 1) & 0x07 # C12, C13, C14
        C11 = flags[7] & 0x01 # Serial tx
        print(
            "Page = "
            + hex(page)
            + ", C4(clear) = "
            + str(C4)
            + ", C5 = "
            + str(C5)
            + " natOpt = "
            + str(self.natOpt)
        )
        return {
            "page": page,
            "clear": C4,
            "newsflash": C5,
            "natOpt": self.natOpt,
            "serial": C11,
        }

    # param page - An 8 character info string for the start of the header
    def print_header(self, packet, page ="Header..", seeking = False, suppressHeader = False):
        if self.clearFlag:
            self.clearFlag = False

        lines = self.text.index(END)
        line = int(lines.split(".")[0])

        # 'end' points one line beyond the last character; allow DISPLAY_LINES + 2 safely.
        # (DISPLAY_LINES+1 real lines => end is at (DISPLAY_LINES+2).0)
        if line > (self.DISPLAY_LINES + 2):
            print(f"[print_header] {line} Too many lines. Some bug somewhere!")

        self.text.config(state=NORMAL)
        buf = bytearray(packet)  # convert to bytearray so we can modify it
        if suppressHeader:
            for i in range(42): # blank out the header bytes
                buf[i]=0x00
            print("SUPPRESS HEADER!")
            buf[10]=ord('x')
            buf[11]=ord('y')
            self.setLine(buf,0)
            return
        for i in range(34,42): # copy the clock
            self.currentHeader[i] = buf[i]
            #print(str(type(self.currentHeader)))
            #print(str(type(buf)))

        for i in range(10): # blank out the header bytes
            buf[i]=buf[i] & 0x7f
            if buf[i]<0x20:
                buf[i]=0x20
        for i in range(2,10):
            buf[i]=ord(page[i-2])

        if seeking:
            #self.pageLoaded = False
            self.currentHeader = buf # The whole header is updating
            self.found = False
        else:
            if not self.found:
                print("[ttxline::printHeader] Calling clear")
                #self.clear("new header")
                self.currentHeader = buf # The whole header is updating
                self.found = True
                self.revealMode = False # New page starts with concealed text
                # Now that we have found the page, dump all of the tags
                # @todo Probably change this to tag_remove
                # for tag in self.text.tag_names(): # This clears all tags BUT only when moving to a new page
                #     self.text.tag_delete(tag)
                self.decodeFlags(packet)

            #if not self.pageLoaded:
            #    self.pageLoaded = True
            buf = self.currentHeader # The header stays on the loaded page

        # print(buf[:12])
        self.setLine(buf, 0)

        # Re-enable before tag operations (setLine() disables the widget)
        self.text.config(state=NORMAL)
        try:
            self.textConceal.config(state=NORMAL)
        except Exception:
            pass

        # Colour the page label where it is actually rendered (offsetSplit-based).
        page_start = f"1.{self.offsetSplit}"
        page_end = f"1.{self.offsetSplit + 8}"

        # Now that the buffer has the correct characters loaded, we can set the generated page number
        #@todo Change the colour of the page number while seeking a page
        #self.text.delete("1.0", "1.8") # strip the control bytes
        #self.text.insert("1.0", "pagexxxx") # add the page number
        #print("inserting <" + page +'>')
        # self.text.insert("1.4", "    ") # pad the remaining space
        #self.text.tag_add("pageColour", "1.0", "1.7")
        if seeking or page[0] == 'H': # Page number goes green in HOLD or while seeking
            self.text.tag_add("pagenumber", page_start, page_end)
            self.text.tag_config("pagenumber", foreground = "green1") # seeking
            self.text.tag_raise("pagenumber")

            self.textConceal.tag_add("pagenumberc", page_start, page_end)
            self.textConceal.tag_config("pagenumberc", foreground = "green1") # seeking
            self.textConceal.tag_raise("pagenumberc")
        else:
            self.text.tag_add("pagenumber", page_start, page_end)
            self.text.tag_config("pagenumber", foreground = "white") # found
            self.text.tag_raise("pagenumber")

            self.textConceal.tag_add("pagenumberc", page_start, page_end)
            self.textConceal.tag_config("pagenumberc", foreground = "white") # found
            self.textConceal.tag_raise("pagenumberc")

        self.rowOffset = 0
        self.text.config(state = DISABLED)
        try:
            self.textConceal.config(state=DISABLED)
        except Exception:
            pass

    # Return True if the row includes double height
    def printRow(self, packet, row):
        self.text.config(state = NORMAL) # allow editing
        # If the line is double height, then skip the next line
        if self.setLine(packet, row - self.rowOffset):
            self.rowOffset=self.rowOffset+1
            return True
        return False

    # show/hide concealed text
    def toggleReveal(self):
        self.revealMode = not self.revealMode
        self.text.config(state = NORMAL) # allow editing
        for row in range(24):
            for col in range(40):
                p0 = str(row + 1) + '.' + str(col)
                ch = self.textConceal.get(p0) # The revealed character
                if ch!=' ': # It might be concealed
                    if not self.revealMode:
                        ch = ' ' # or it could be hidden
                    p1 = str(row + 1) + '.' + str(col+1)
                    self.text.insert(p0, ch)
                    self.text.delete(p1)
        self.text.config(state = DISABLED)

    # Clear stuff including all the page modifiers
    def clear(self, reason):
        self.clearFlag = True
        metaData.clear()

        # A clear marks the start of a new page/subpage, so the next header
        # must be re-latched and flags re-decoded (natOpt/language, etc.).
        self.found = False
        self.currentHeader = bytearray(42)

        # Do NOT delete all widget content; that destroys the row structure.
        self.text.config(state=NORMAL)

        self._ensure_rows_exist()
        for row0 in range(self.DISPLAY_LINES):
            self._replace_row_text(self.text, row0, " " * self.total_columns)
            self._replace_row_text(self.textConceal, row0, " " * self.total_columns)

        self.text.config(state=DISABLED)
