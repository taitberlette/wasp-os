# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Music Player for GadgetBridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/MusicApp.png
        :width: 179

        Screenshot of the Music Player application

Music Player Controller:

* Touch: play/pause
* Swipe UPDOWN: Volume down/up
* Swipe LEFTRIGHT: next/previous
"""

import wasp

import icons
import time

from micropython import const

# 2-bit RLE, generated from res/music_icon.png, 358 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff.@2L?\x12R?\rV?\tZ'
    b'?\x05^?\x02`?\x00b=d;f9h7'
    b'j5l4l3n2n1p0T\x80\xcc\x88'
    b'T/S\x8cS.R\x8eP\xc0\xfe\xc2.Q\x90K'
    b'\xc6.P\x92G\xc9-Q\x92C\xce,P\x92@\xc6'
    b'B\xd0,\x802\x90\xc0\xcc\xceF@\xfeP,\x90\xc8'
    b'D\x80\xc6\x88P,\xc02\xd0@\xccD\x84\x80\xfe\x84'
    b'\xc0\xc6\xc8\x90,@2N\x82\xc8\x84\xc8\x90,J\x86'
    b'\xc8\x84\xc8\x90,F\x8a\xd4\x90,B\x8e\xd4\x90,\x91'
    b'\xd2\x91-\x90\xd2\x90.\x91\xd0\x91.\x92\xce\x92.\x93'
    b'\xcc\x93/\x94\xc8\x940\xb01\xae2\xae3\xac4\xac'
    b'5\xaa7\xa89\xa6;\xa4=\xa2?\x00\xa0?\x02\x9e'
    b'?\x05\x9a?\t\x96?\r\x92?\x12\x8b\x81?\xff\xff'
    b','
)

DISPLAY_WIDTH = const(240)
ICON_SIZE = const(72)
CENTER_AT = const((DISPLAY_WIDTH - ICON_SIZE) // 2)

class MusicPlayerApp(object):
    """ Music Player Controller application."""
    NAME = 'Music'
    ICON = icon

    def __init__(self):
        self._pauseplay = wasp.widgets.GfxButton(CENTER_AT, CENTER_AT, icons.play)
        self._back = wasp.widgets.GfxButton(0, 120-12, icons.back)
        self._fwd = wasp.widgets.GfxButton(240-48, 120-12, icons.fwd)
        self._play_state = False
        self._musicstate = 'pause'
        self._artist = ''
        self._track = ''
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def _send_cmd(self, cmd):
        print('\r')
        for i in range(1):
            for i in range(0, len(cmd), 20):
                print(cmd[i: i + 20], end='')
                time.sleep(0.2)
            print(' ')
        print(' ')

    def _fill_space(self, key):
        if key == 'top':
            wasp.watch.drawable.fill(
                x=0, y=0, w=DISPLAY_WIDTH, h=CENTER_AT)
        elif key == 'down':
            wasp.watch.drawable.fill(x=0, y=CENTER_AT + ICON_SIZE,
                                     w=DISPLAY_WIDTH,
                            h=DISPLAY_WIDTH - (CENTER_AT + ICON_SIZE))

    def foreground(self):
        """Activate the application."""
        state = wasp.system.musicstate.get('state')
        artist = wasp.system.musicinfo.get('artist')
        track = wasp.system.musicinfo.get('track')
        if state:
            self._musicstate = state
            if self._musicstate == 'play':
                self._play_state = True
            elif self._musicstate == 'pause':
                self._play_state = False
        if artist:
            self._artist = artist
        if track:
            self._track = track
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.TOUCH)

    def background(self):
        """De-activate the application (without losing state)."""
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        music_state_now = wasp.system.musicstate.get('state')
        music_artist_now = wasp.system.musicinfo.get('artist')
        music_track_now = wasp.system.musicinfo.get('track')
        if music_state_now:
            if music_state_now != self._musicstate:
                self._musicstate = music_state_now
                self._state_changed = True
        else:
            self._state_changed = False
        wasp.system.musicstate = {}
        if music_track_now:
            if music_track_now != self._track:
                self._track = music_track_now
                self._track_changed = True
        else:
            self._track_changed = False
        if music_artist_now:
            if music_artist_now != self._artist:
                self._artist = music_artist_now
                self._artist_changed = True
        else:
            self._artist_changed = False
        wasp.system.musicinfo = {}
        self._update()

    def swipe(self, event):
        """
        Notify the application of a touchscreen swipe event.
        """
        if event[0] == wasp.EventType.UP:
            self._send_cmd('{"t":"music", "n":"volumeup"} ')
        elif event[0] == wasp.EventType.DOWN:
            self._send_cmd('{"t":"music", "n":"volumedown"} ')

    def touch(self, event):
        if self._pauseplay.touch(event):
            self._play_state = not self._play_state
            if self._play_state:
                self._musicstate = 'play'
                self._pauseplay.gfx = icons.pause
                self._pauseplay.draw()
                self._send_cmd('{"t":"music", "n":"play"} ')
            else:
                self._musicstate = 'pause'
                self._pauseplay.gfx = icons.play
                self._pauseplay.draw()
                self._send_cmd('{"t":"music", "n":"pause"} ')
        elif self._back.touch(event):
            self._send_cmd('{"t":"music", "n":"previous"} ')
        elif self._fwd.touch(event):
            self._send_cmd('{"t":"music", "n":"next"} ')

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        if self._state_changed:
            self._pauseplay.draw()
        if self._track_changed:
            self._draw_label(self._track, 24 + 144)
        if self._artist_changed:
            self._draw_label(self._artist, 12)
        self._back.draw()
        self._fwd.draw()

    def _draw_label(self, label, pos):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            chunks = draw.wrap(label, 240)
            self._fill_space(pos)
            for i in range(len(chunks)-1):
                sub = label[chunks[i]:chunks[i+1]].rstrip()
                draw.string(sub, 0, pos + 24 * i, 240)

    def _update(self):
        if self._musicstate == 'play':
            self._play_state = True
            self._pauseplay.gfx = icons.pause
        elif self._musicstate == 'pause':
            self._play_state = False
            self._pauseplay.gfx = icons.play
        self._draw()

    def update(self):
        pass
