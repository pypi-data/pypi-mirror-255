import pglive.examples_pyqt6 as examples
import signal
from threading import Thread
import pyqtgraph as pg  # type: ignore

from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_axis_range import LiveAxisRange
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget

"""
Live plot range is used to increase plotting performance in this example.
"""

layout = pg.LayoutWidget()
layout.layout.setSpacing(0)
args = []
args2 = []

'''
Move view to the right on every 300 ticks (data update).
Y range is automatically adjudicating every tick.
'''
widget = LivePlotWidget(title=f"Roll_on_tick = 50 @ 10Hz",
                        x_range_controller=LiveAxisRange(roll_on_tick=50))
plot = LiveLinePlot(pen="green")
widget.addItem(plot)
layout.addWidget(widget)
args.append(DataConnector(plot, max_points=300, update_rate=100))


layout.show()
Thread(target=examples.sin_wave_generator, args=args).start()
examples.app.exec()
examples.stop()
