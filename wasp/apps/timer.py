# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Wolfgang Ginolas
"""Timer Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration in a specified amount of time. Like a kitchen timer.

    .. figure:: res/TimerApp.png
        :width: 179

        Screenshot of the Timer Application

"""

import wasp
import fonts
import time
import widgets
import math
from micropython import const

# 2-bit RLE, generated from res/timer_icon.png, 345 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff\xde\xe68\xea6\xea8\xe6;\xc3\x1e\xc3<'
    b'\xc3\x1e\xc3<\xc3\x1e\xc3<\xc3\x1e\xc3<\xc3\x1e\xc3<'
    b'\xc3\x1e\xc3<\xc3\x1e\xc3=\xc3\x1c\xc3>\xc3\x1c\xc3>'
    b'\xc3\x1c\xc3?\x00\xc3\x06\xce\x06\xc3?\x01\xc4\x05\xce\x05'
    b'\xc4?\x02\xc3\x07\xca\x07\xc3?\x04\xc3\x08\xc6\x08\xc3?'
    b'\x06\xc3\x14\xc3?\x08\xc4\x10\xc4?\n\xc5\x0c\xc5?\x0c'
    b'\xc6\x08\xc6?\x0f\xc5\x06\xc5?\x13\xc3\x06\xc3?\x15\xc3'
    b'\x06\xc3?\x13\xc5\x06\xc5?\x0f\xc6\x08\xc6?\x0c\xc5\x0c'
    b'\xc5?\n\xc4\x10\xc4?\x08\xc3\x14\xc3?\x06\xc3\x16\xc3'
    b'?\x04\xc3\x18\xc3?\x02\xc4\x18\xc4?\x01\xc3\x08\xc9\t'
    b'\xc3?\x00\xc3\x08\xcc\x08\xc3>\xc3\x06\xd0\x06\xc3>\xc3'
    b'\x05\xd2\x05\xc3=\xc3\x05\xd4\x05\xc3<\xc3\x05\xd4\x05\xc3'
    b'<\xc3\x04\xd6\x04\xc3<\xc3\x04\xd6\x04\xc3<\xc3\x03\xd8'
    b'\x03\xc3<\xc3\x03\xd8\x03\xc3<\xc3\x03\xd8\x03\xc3;\xe6'
    b'8\xea6\xea8\xe6?\xff\xff\xe2'
)

_STOPPED = const(0)
_RUNNING = const(1)
_RINGING = const(2)

_BUTTON_Y = const(200)

class TimerApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Timer'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.minutes = widgets.Spinner(50, 60, 0, 99, 2)
        self.seconds = widgets.Spinner(130, 60, 0, 59, 2)
        self.current_alarm = None

        self.minutes.value = 10
        self.state = _STOPPED

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        if self.state == _RINGING:
            self.state = _STOPPED

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.state == _RINGING:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        self._update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.state == _RINGING:
            mute = wasp.watch.display.mute
            mute(True)
            self._stop()
            mute(False)
        elif self.state == _RUNNING:
            self._stop()
        else:  # _STOPPED
            if self.minutes.touch(event) or self.seconds.touch(event):
                pass
            else:
                y = event[2]
                if y >= _BUTTON_Y:
                    self._start()


    def _start(self):
        self.state = _RUNNING
        now = wasp.watch.rtc.time()
        self.current_alarm = now + self.minutes.value * 60 + self.seconds.value
        wasp.system.set_alarm(self.current_alarm, self._alert)
        self._draw()

    def _stop(self):
        self.state = _STOPPED
        wasp.system.cancel_alarm(self.current_alarm, self._alert)
        self._draw()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

        if self.state == _RINGING:
            draw.set_font(fonts.sans24)
            draw.string(self.NAME, 0, 150, width=240)
            draw.blit(icon, 73, 50)
        elif self.state == _RUNNING:
            self._draw_stop(104, _BUTTON_Y)
            draw.string(':', 110, 120-14, width=20)
            self._update()
        else:  # _STOPPED
            draw.set_font(fonts.sans28)
            draw.string(':', 110, 120-14, width=20)

            self.minutes.draw()
            self.seconds.draw()

            self._draw_play(114, _BUTTON_Y)

    def _update(self):
        wasp.system.bar.update()
        draw = wasp.watch.drawable
        if self.state == _RUNNING:
            now = wasp.watch.rtc.time()
            s = self.current_alarm - now
            if s<0:
                s = 0
            m = str(math.floor(s // 60))
            s = str(math.floor(s) % 60)
            if len(m) < 2:
                m = '0' + m
            if len(s) < 2:
                s = '0' + s
            draw.set_font(fonts.sans28)
            draw.string(m, 50, 120-14, width=60)
            draw.string(s, 130, 120-14, width=60)

    def _draw_play(self, x, y):
        draw = wasp.watch.drawable
        for i in range(0,20):
            draw.fill(0xffff, x+i, y+i, 1, 40 - 2*i)

    def _draw_stop(self, x, y):
        wasp.watch.drawable.fill(0xffff, x, y, 40, 40)

    def _alert(self):
        self.state = _RINGING
        wasp.system.wake()
        wasp.system.switch(self)
