# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Joris Warmbier
"""Alarm Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration alarm. All settings can be accessed from the Watch UI.

    .. figure:: res/AlarmApp.png
        :width: 179

        Screenshot of the Alarm Application

"""

import wasp
import fonts
import time
import widgets

# 2-bit RLE, generated from res/alarm_icon.png, 390 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\x9e\xc3 \xc38\xc6\x1e\xc65\xc7\x1e\xc73\xc8\t'
    b'\xcc\t\xc81\xc8\x06\xd4\x06\xc8/\xc8\x05\xd8\x05\xc8-'
    b'\xc7\x05\xdc\x05\xc7+\xc7\x05\xde\x05\xc7)\xc7\x04\xcc\n'
    b"\xcc\x04\xc7'\xc7\x04\xca\x10\xca\x04\xc7&\xc6\x04\xc9\x14"
    b'\xc9\x04\xc6%\xc6\x04\xc8\x18\xc8\x04\xc6$\xc6\x03\xc8\x1a'
    b'\xc8\x03\xc6$\xc5\x03\xc7\x1e\xc7\x03\xc5%\xc3\x04\xc6\x0c'
    b'\xc4\x10\xc6\x04\xc3,\xc6\r\xc4\x11\xc61\xc7\r\xc4\x11'
    b'\xc70\xc6\x0e\xc4\x12\xc6/\xc6\x0f\xc4\x13\xc6.\xc6\x0f'
    b'\xc4\x13\xc6-\xc6\x10\xc4\x14\xc6,\xc6\x10\xc4\x14\xc6,'
    b'\xc5\x11\xc4\x15\xc5,\xc5\x11\xc4\x15\xc5+\xc6\x11\xc4\x15'
    b'\xc6*\xc5\x12\xc4\x16\xc5*\xc5\x12\xc4\x16\xc5*\xc5\x12'
    b'\xc4\x16\xc5*\xc5\x12\xc4\x16\xc5*\xc5\x12\xc4\x16\xc5*'
    b'\xc5\x12\xcf\x0b\xc5*\xc5\x12\xcf\x0b\xc5*\xc5\x12\xcf\x0b'
    b'\xc5*\xc5\x12\xcf\x0b\xc5*\xc5,\xc5*\xc6*\xc6+'
    b'\xc5*\xc5,\xc5*\xc5,\xc6(\xc6,\xc6(\xc6-'
    b'\xc6&\xc6.\xc6&\xc6/\xc6$\xc60\xc7"\xc71'
    b'\xc6"\xc63\xc6 \xc64\xc7\x1e\xc75\xc8\x1a\xc87'
    b'\xc8\x18\xc89\xc9\x14\xc9:\xcb\x10\xcb9\xcf\n\xcf7'
    b'\xea5\xec4\xc7\x03\xd8\x03\xc74\xc6\x07\xd2\x07\xc65'
    b'\xc4\x0b\xcc\x0b\xc4?\xff\xbd'
)

class AlarmApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Alarm'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.active = widgets.Checkbox(104, 200)
        self.hours = widgets.Spinner(50, 60, 0, 23, 2)
        self.minutes = widgets.Spinner(130, 60, 0, 59, 2)

        self.hours.value = 7
        self.ringing = False

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)
        if self.active.state:
            wasp.system.cancel_alarm(self.current_alarm, self._alert)

    def background(self):
        """De-activate the application."""
        if self.active.state:
            self._set_current_alarm()
            wasp.system.set_alarm(self.current_alarm, self._alert)
            if self.ringing:
                self.ringing = False

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.ringing:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        else:
            wasp.system.bar.update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.ringing:
            mute = wasp.watch.display.mute
            self.ringing = False
            mute(True)
            self._draw()
            mute(False)
        elif self.hours.touch(event) or self.minutes.touch(event) or \
             self.active.touch(event):
            pass

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        if not self.ringing:
            draw.fill()

            sbar = wasp.system.bar
            sbar.clock = True
            sbar.draw()

            draw.set_font(fonts.sans28)
            draw.string(':', 110, 120-14, width=20)

            self.active.draw()
            self.hours.draw()
            self.minutes.draw()
        else:
            draw.fill()
            draw.set_font(fonts.sans24)
            draw.string("Alarm", 0, 150, width=240)
            draw.blit(icon, 73, 50)

    def _alert(self):
        self.ringing = True
        wasp.system.wake()
        wasp.system.switch(self)

    def _set_current_alarm(self):
        now = wasp.watch.rtc.get_localtime()
        yyyy = now[0]
        mm = now[1]
        dd = now[2]
        HH = self.hours.value
        MM = self.minutes.value
        if HH < now[3] or (HH == now[3] and MM <= now[4]):
            dd += 1
        self.current_alarm = (time.mktime((yyyy, mm, dd, HH, MM, 0, 0, 0, 0)))
