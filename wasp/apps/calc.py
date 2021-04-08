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
    b'?\xff\xff!@Wf9h8h8h8F\x80'
    b'e\x9cF8E\x9eE8E\x9eE8E\x9eE8'
    b'E\x9eE8E\x9eE8E\x9eE8E\x9eE8'
    b'E\x9eE8F\x9cF8h8h8h8h8'
    b'G\xc0\xdf\xc6D\xc6D\xc6G8F\xc8B\xc8B\xc8'
    b'F8F\xc8B\xc8B\xc8F8F\xc8B\xc8B\xc8'
    b'F8F\xc8B\xc8B\xc8F8F\xc8B\xc8B\xc8'
    b'F8F\xc8B\xc8B\xc8F8G\xc6D\xc6D\xc6'
    b'G8h8h8[@\x0fG\x80W\x868\x87\xc6'
    b'\x84\xc6\x83I\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8'
    b'\x82\xc8\x82I\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8'
    b'\x82\xc8\x82I\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8'
    b'\x82\xc8\x82I\x858\x87\xc6\x84\xc6\x83I\x858\x9aI'
    b'\x858\x9aI\x858\x9aI\x858\x87\xc6\x84\xc6\x83I'
    b'\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8\x82\xc8\x82I'
    b'\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8\x82\xc8\x82I'
    b'\x858\x86\xc8\x82\xc8\x82I\x858\x86\xc8\x82\xc8\x82I'
    b'\x858\x87\xc6\x84\xc6\x84G\x868\xa88\xa88\xa89'
    b'\xa6?\xff\xff\x1f'
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
