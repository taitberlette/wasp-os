# SPDX-License-Identifier: MY-LICENSE
# Copyright (C) YEAR(S), AUTHOR

import wasp

class HelloApp():
    """A hello world application for wasp-os."""
    NAME = "Hello"

    def __init__(self):
        self.index = 0
        self.tabs = wasp.widgets.MetroTab(["Hello", "World", "Test"], self.index)

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.BUTTON)

    def press(self, button, state):
        self.index += 1
        self._draw()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        self.tabs.index = self.index
        self.tabs.draw()
