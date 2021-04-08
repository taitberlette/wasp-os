# SPDX-License-Identifier: MY-LICENSE
# Copyright (C) YEAR(S), AUTHOR

import wasp

class HelloApp():
    """A hello world application for wasp-os."""
    NAME = "Hello"

    def __init__(self, msg="Hello, world!"):
        self.msg = msg
        self.index = 0
        self.tabs = wasp.widgets.MetroTab(["Hello", "World", "Test"], self.index)
        wasp.system.request_event(wasp.EventMask.BUTTON)

    def foreground(self):
        self._draw()

    def press(self, button, state):
        self.index += 1

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        tabs.index = self.index
        tabs.draw()
        draw.string(self.msg, 0, 108, width=240)
