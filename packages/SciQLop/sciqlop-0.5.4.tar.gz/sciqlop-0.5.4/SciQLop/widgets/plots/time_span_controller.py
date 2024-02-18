from typing import List

from PySide6.QtCore import QObject

from .time_span import TimeSpan
from .time_sync_panel import TimeSyncPanel
from ...backend import TimeRange
from ...backend.property import SciQLopProperty


class TimeSpanController(QObject):
    def __init__(self, plot_panel: TimeSyncPanel, parent=None):
        QObject.__init__(self, parent)
        self._ranges: List[TimeSpan] = []
        self._visible_ranges: List[TimeSpan] = []
        self._plot_panel = plot_panel
        self._plot_panel.time_range_changed.connect(self._range_changed)

    def _range_changed(self, new_range: TimeRange):
        visible_ranges = self.visible_spans()
        list(map(lambda r: r.hide(), list(set(self._visible_ranges) - set(visible_ranges))))
        list(map(lambda r: r.show(), list(set(visible_ranges) - set(self._visible_ranges))))
        self._visible_ranges = visible_ranges

    @SciQLopProperty(list)
    def spans(self) -> List[TimeSpan]:
        return self._ranges

    @spans.setter
    def spans(self, ranges: List[TimeSpan]):
        self._ranges = ranges
        self._range_changed(self._plot_panel.time_range)

    def visible_spans(self):
        return [r for r in self._ranges if r.time_range.overlaps(self._plot_panel.time_range)]
