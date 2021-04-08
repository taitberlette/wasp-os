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
    b'?\xff\x10\x86?\x1a\x88?\x02@\xdfK\x0b\x80\x97\x8b'
    b'\nK*K\x08\x91\x07K*J\x06\x97\x05J*I'
    b'\x05\x9b\x04I*H\x05\x9d\x04H*H\x03\xa1\x02H'
    b'*I\x01\x8d\xc9\x8dI*I\x8a\xd1\x89I*D\x02'
    b'B\x89\xd5\x88B\x02D*C\x04\x89\xd7\x89\x03C*'
    b'B\x04\x88\xdb\x88\x03B/\x88\xdd\x883\x87\xdf\x872'
    b'\x87\xe1\x870\x87\xe3\x87/\x87\xdb\xc0\xdb\xc2@\xd7F'
    b'\x87.\x87[\xc3G\x87-\x86[\xc3I\x86-\x86Z'
    b'\xc3J\x86,\x86Z\xc3L\x86+\x86Y\xc3M\x84\x82'
    b'+\x86I\x80\xfe\x83L\xc3N\xc0\x97\xc2\xc4*\xc7I'
    b'\x85I@\xdbC\x80\xd7\x8f\xc7)\xc6\x8b\xc0\xfe\xc5\x87'
    b'C\x91@\x97F)F\x8d\xc6\x83\x80\xdb\x83\xc0\xd7\xd2'
    b'F)F\xcf@\xfeD\x80+\x84\xc0\xdb\xc1@\xd7S'
    b'\x80\x97\x86)\x86P\xc0\xfe\xc3@+D\x80\xd7\x94\xc0'
    b'\x97\xc6)\xc6\x92@\xfeA\x80+\x84\xc0\xd7\xd4@\x97'
    b'F)F\xd3\x84\xd4F)F\xd4B\xd5F)F\xd4'
    b'B\xd5F)F\xd4B\xd5F)DC\xd3B\xd4G'
    b'*AE\xd3B\xd4F+F\xd3B\xd4F+F\xd3'
    b'B\xd4F,F\xd2B\xd3F-F\xd2B\xd3F-'
    b'G\xd1B\xd2G.G\xd0B\xd1G/G\xd0B\xd1'
    b'G0G\xcfB\xd0G2G\xceB\xcfG3H\xdd'
    b'H4H\xdbH6I\xd7I8I\xd5I:J\xd1'
    b'J<M\xc9M>a?\x02]?\x05[?\x08W'
    b'?\rQ?\x13K?\xffk'
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
