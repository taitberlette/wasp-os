# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache
"""Calculator
~~~~~~~~~~~~~

This is a simple calculator app that uses the build-in eval() function to
compute the solution.

.. figure:: res/CalcApp.png
    :width: 179
"""

import wasp, fonts

# 2-bit RLE, generated from res/calc.png, 413 bytes
calc = (
    b'\x02'
    b'`@'
    b'?\xff\xc1\xe2<\xe69\xe87\xea6\xea5\xc6\x1f\xc7'
    b'4\xc6 \xc64\xc5"\xc54\xc5"\xc54\xc5\x05\xd8'
    b'\x05\xc54\xc5\x04\xda\x04\xc54\xc5\x03\xdc\x03\xc54\xc5'
    b'\x03\xdc\x03\xc54\xc5\x03\xdc\x03\xc54\xc5\x03\xc5\x12\xc5'
    b'\x03\xc54\xc5\x03\xc5\x12\xc5\x03\xc54\xc5\x03\xc5\x12\xc5'
    b'\x03\xc54\xc5\x03\xc5\x12\xc5\x03\xc54\xc5\x03\xc5\x12\xc5'
    b'\x03\xc54\xc5\x03\xc5\x12\xc5\x03\xc54\xc5\x03\xdc\x03\xc5'
    b'4\xc5\x03\xdc\x03\xc54\xc5\x03\xdc\x03\xc54\xc5\x04\xda'
    b'\x04\xc54\xc5\x05\xd8\x05\xc54\xc5"\xc54\xc5"\xc5'
    b'4\xc5"\xc54\xc5\x05\xc4\x06\xc4\x06\xc4\x05\xc54\xc5'
    b'\x04\xc6\x04\xc6\x04\xc6\x04\xc54\xc5\x03\xc8\x02\xc8\x02\xc8'
    b'\x03\xc54\xc5\x03\xc8\x02\xc8\x02\xc8\x03\xc54\xc5\x03\xc8'
    b'\x02\xc8\x02\xc8\x03\xc54\xc5\x04\xc6\x04\xc6\x03\xc8\x03\xc5'
    b'4\xc5\x04\xc6\x04\xc6\x03\xc8\x03\xc54\xc5\x17\xc8\x03\xc5'
    b'4\xc5\x17\xc8\x03\xc54\xc5\x05\xc4\x06\xc4\x04\xc8\x03\xc5'
    b'4\xc5\x04\xc6\x04\xc6\x03\xc8\x03\xc54\xc5\x03\xc8\x02\xc8'
    b'\x02\xc8\x03\xc54\xc5\x03\xc8\x02\xc8\x02\xc8\x03\xc54\xc5'
    b'\x03\xc8\x02\xc8\x02\xc8\x03\xc54\xc5\x03\xc8\x02\xc8\x02\xc8'
    b'\x03\xc54\xc5\x04\xc6\x04\xc6\x04\xc6\x04\xc54\xc5\x05\xc4'
    b'\x06\xc4\x06\xc4\x05\xc54\xc5"\xc54\xc5"\xc54\xc6'
    b' \xc64\xc7\x1e\xc75\xea6\xea7\xe89\xe6<\xe2'
    b'?\xff\xc1'
)

fields = ( '789+('
           '456-)'
           '123*^'
           'C0./=' )

class CalculatorApp():
    NAME = 'Calc'
    ICON = calc

    def __init__(self):
        self.output = ""

    def foreground(self):
        self._draw()
        self._update()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def touch(self, event):
        if (event[2] < 48):
            if (event[1] > 200): # undo button pressed
                if (self.output != ""):
                    self.output = self.output[:-1]
        else:
            x = event[1] // 47
            y = (event[2] // 48) - 1

            # Error handling for touching at the border
            if x > 4:
                x = 4
            if y > 3:
                y = 3
            button_pressed = fields[x + 5*y]
            if (button_pressed == "C"):
                self.output = ""
            elif (button_pressed == "="):
                try:
                    self.output = str(eval(self.output.replace('^', '**')))[:12]
                except:
                    wasp.watch.vibrator.pulse()
            else:
                self.output +=  button_pressed
        self._update()

    def _draw(self):
        draw = wasp.watch.drawable

        hi = wasp.system.theme('bright')
        lo = wasp.system.theme('mid')
        mid = draw.lighten(lo, 2)
        bg = draw.darken(wasp.system.theme('ui'), wasp.system.theme('contrast'))
        bg2 = draw.darken(bg, 2)

        # Draw the background
        draw.fill(0, 0, 0, 239, 47)
        draw.fill(0, 236, 239, 3)
        draw.fill(bg, 141, 48, 239-141, 235-48)
        draw.fill(bg2, 0, 48, 140, 235-48)

        # Make grid:
        draw.set_color(lo)
        for i in range(4):
            # horizontal lines
            draw.line(x0=0,y0=(i+1)*47,x1=239,y1=(i+1)*47)
            # vertical lines
            draw.line(x0=(i+1)*47,y0=47,x1=(i+1)*47,y1=235)
        draw.line(x0=0, y0=47, x1=0, y1=236)
        draw.line(x0=239, y0=47, x1=239, y1=236)
        draw.line(x0=0, y0=236, x1=239, y1=236)

        # Draw button labels
        draw.set_color(hi, bg2)
        for x in range(5):
            if x == 3:
                draw.set_color(mid, bg)
            for y in range(4):
                label = fields[x + 5*y]
                if (x == 0):
                    draw.string(label, x*47+14, y*47+60)
                else:
                    draw.string(label, x*47+16, y*47+60)
        draw.set_color(hi)
        draw.string("<", 215, 10)
    
    def _update(self):
        output = self.output if len(self.output) < 12 else self.output[len(self.output)-12:]
        wasp.watch.drawable.string(output, 0, 14, width=200, right=True)
