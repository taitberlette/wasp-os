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
    b'?\xff\xcc\xcc?\x11\xd4?\x0b\xd8?\x07\xdc?\x04\xde'
    b'?\x01\xcc\n\xcc=\xca\x10\xca;\xc9\x14\xc99\xc8\x18'
    b'\xc87\xc8\x1a\xc85\xc7\x1e\xc74\xc6 \xc63\xc6"'
    b'\xc61\xc7"\xc70\xc6$\xc6/\xc6&\xc6.\xc6\x0f'
    b'\xc8\x0f\xc6-\xc6\x0e\xcc\x0e\xc6,\xc6\r\xce\r\xc6,'
    b'\xc5\r\xd0\r\xc5,\xc5\x0c\xd2\x0c\xc5+\xc6\x0b\xc8\x04'
    b'\xc8\x0b\xc6*\xc5\x0c\xc6\x08\xc6\x0c\xc5*\xc5\x0b\xc6\n'
    b'\xc6\x0b\xc5*\xc5\x0b\xc6\x03\xc4\x03\xc6\x0b\xc5*\xc5\x0b'
    b'\xc5\x03\xc6\x03\xc5\x0b\xc5*\xc5\x0b\xc5\x03\xc6\x03\xc5\x0b'
    b'\xc5*\xc5\x0b\xc5\x03\xc6\x03\xc5\x0b\xc5*\xc5\x0b\xc5\x03'
    b'\xc6\x03\xc5\x0b\xc5*\xc5\x0b\xc6\x03\xc4\x03\xc6\x0b\xc5*'
    b'\xc5\x0b\xc6\n\xc6\x0b\xc5*\xc5\x0c\xc6\x08\xc6\x0c\xc5*'
    b'\xc6\x0b\xc8\x04\xc8\x0b\xc6+\xc5\x0c\xd2\x0c\xc5,\xc5\r'
    b'\xd0\r\xc5,\xc6\r\xce\r\xc6,\xc6\x0e\xcc\x0e\xc6-'
    b'\xc6\x0f\xc8\x0f\xc6.\xc6&\xc6/\xc6$\xc60\xc7"'
    b'\xc71\xc6"\xc63\xc6 \xc64\xc7\x1e\xc75\xc8\x1a'
    b'\xc87\xc8\x18\xc89\xc9\x14\xc9;\xca\x10\xca=\xcc\n'
    b'\xcc?\x01\xde?\x04\xdc?\x07\xd8?\x0b\xd4?\x11\xcc'
    b'?\xff\xcc'
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
