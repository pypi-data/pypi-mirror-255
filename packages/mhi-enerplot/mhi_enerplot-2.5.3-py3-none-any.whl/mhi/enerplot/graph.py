from .command import Command
from .component import Component
from .remote import Remotable, rmi, rmi_property
from .trace import Trace

#===============================================================================
# Enerplot Graph Frames
#===============================================================================

class ZFrame(Component):

    """
    A ZFrame
    """

    @property
    def title(self):
        """The title of the frame"""
        return self.properties()["title"]

    @title.setter
    def title(self, title):
        self.properties(title=title)


    #-----------------------------------------------------------------------
    # Link/Unlink
    #-----------------------------------------------------------------------

    @rmi
    def delink_all(self):
        """
        Delink all channel data from the frame
        """

    @rmi
    def relink_all(self, datafile):
        """
        Relink the channel data to the given datafile

        Parameters:
            datafile (DataFile): the datafile to link channel data to.
        """


class GraphMixin:

    def reset_extents(self):
        """
        Reset the graph's extents
        """

        self._generic_command(Command.RESET_EXTENTS)

    def reset_limits(self):
        """
        Reset the graph's limits
        """

        self._generic_command(Command.RESET_LIMITS)

    def zoom_extents(self, x_extents=True, y_extents=True):
        """
        Reset the graph's zoom to the X and/or Y extents.
        By default, both X and Y axis zoom is affected.

        Parameters:
            x_extents (bool): set to False to not affect X-axis
            y_extents (bool): set to False to not affect Y-axis
        """

        if x_extents:
            self.zoom_x_extents()
        if y_extents:
            self.zoom_y_extents()

    def zoom_limits(self, x_limits=True, y_limits=True):
        """
        Reset the graph's zoom to the X and/or Y limits.
        By default, both X and Y axis zoom is affected.

        Parameters:
            x_limits (bool): set to False to not affect X-axis
            y_limits (bool): set to False to not affect Y-axis
        """

        if x_limits:
            self.zoom_x_limits()
        if y_limits:
            self.zoom_y_limits()

    def zoom_x_extents(self):
        """
        Reset the graph's zoom for the X-axis to the X extents.
        """

        self._generic_command(Command.RESET_EXTENTS_X)

    def zoom_x_limits(self):
        """
        Reset the graph's zoom for the X-axis to the X limits.
        """

        self._generic_command(Command.RESET_LIMITS_X)

    def zoom_y_extents(self):
        """
        Reset the graph's zoom for the Y-axis to the Y extents.
        """

        self._generic_command(Command.RESET_EXTENTS_Y)

    def zoom_y_limits(self):
        """
        Reset the graph's zoom for the Y-axis to the Y limits.
        """

        self._generic_command(Command.RESET_LIMITS_Y)

    @rmi
    def zoom(self, xmin=None, xmax=None, ymin=None, ymax=None, *, compute_x_grid=True, compute_y_grid=True):
        """
        Alter the graph's viewport
        """

    def toggle_grid_lines(self):
        """
        Toggle grid lines on or off
        """

        self._generic_command(Command.TOGGLE_GRID_LINES)

    def show_grid(self, show=True):
        """
        Set the grid's visibility.

        Parameters:
            show (bool): Set to ``False`` to turn off the grid.
        """

        self['grid'] = show

    def toggle_tick_marks(self):
        """
        Toggle tick marks on or off
        """

        self._generic_command(Command.TOGGLE_TICK_MARKS)

    def show_ticks(self, show=True):
        """
        Set the tick visibility.

        Parameters:
            show (bool): Set to ``False`` to turn off the tick markers.
        """

        self['ticks'] = show

    def toggle_curve_glyphs(self):
        """
        Toggle curve glyphs on or off
        """

        self._generic_command(Command.TOGGLE_CURVE_GLYPHS)

    def show_glyphs(self, show=True):
        """
        Set the curve glyph visibility.

        Parameters:
            show (bool): Set to ``False`` to turn off the curve glyphs.
        """

        self['glyphs'] = show

    def toggle_x_intercept(self):
        """
        Toggle X intercept on or off
        """

        self._generic_command(Command.TOGGLE_X_INTERCEPT)

    def show_x_intercept(self, show=True):
        """
        Set the X intercept visibility on or off
        """

        self['xinter'] = show

    def toggle_y_intercept(self):
        """
        Toggle Y intercept on or off
        """

        self._generic_command(Command.TOGGLE_Y_INTERCENT)

    def show_y_intercept(self, show=True):
        """
        Set the Y intercept visibility on or off
        """

        self['yinter'] = show

class MarkerMixin:

    def toggle_markers(self):
        """
        Toggle X/O markers
        """

        self._generic_command(Command.TOGGLE_MARKERS)

    def show_markers(self, show=True):
        """
        Show (or hide) the X/O markers
        """

        self['markers'] = show

    def set_markers(self, x=None, o=None, *, delta=None):
        """
        Set the X and/or O marker positions.

        If both ``x`` and ``o`` are specified, ``delta`` cannot be given.

        If ``delta`` is given, the O-marker is positioned the specified
        distance after the X-marker, unless the ``o`` value is specified
        in which case the X-marker is positioned the specified distance
        before the O-marker.

        If the markers were hidden, they will automatically be shown.

        If the markers are "locked together", they will remain locked together,
        but with their relative offset defined by their new positions.

        Parameters:
            x (float): new x-marker position
            o (float): new o-marker position
            delta (float): distance between x & o markers

        Examples:

            The following are equivalent, and set the markers 1 cycle apart,
            assuming a 60Hz waveform::

                graph_frame.set_markers(0.1, 0.11666667)
                graph_frame.set_markers(0.1, delta=0.01666667)
                graph_frame.set_markers(0.1, delta=1/60)
                graph_frame.set_markers(delta=1/60, x=0.1)
                graph_frame.set_markers(delta=1/60, o=0.11666667)
        """

        if x is not None and o is not None and delta is not None:
            raise ValueError("Cannot specify delta if both x & o are given")

        props = dict(markers=True)

        if delta is not None:
            if o is None:
                o = (x if x is not None else float(self['xmarker'])) + delta
            else:
                x = o - delta

        if x is not None:
            props['xmarker'] = x
        if o is not None:
            props['omarker'] = o

        self.properties(**props)

    def lock_markers(self, lock=True, *, delta=None):
        """
        Lock (or unlock) markers to a fixed offset from each other.

        Parameters:
            lock (bool): set to ``False`` to unlock the marker
            delta (float): used to specify lock offset (optional)

        Examples::

            fft.lock_markers()
            fft.lock_markers(delta=1/50)
            fft.lock_markers(False)
        """

        props = { 'lockmarkers': lock }

        if lock:
            props['markers'] = 'true'
            if delta is not None:
                props['omarker'] = float(self['xmarker']) + delta
        elif delta is not None:
            raise ValueError("Cannot specify delta when unlocking")

        self.properties(**props)

class SubGraphsMixin:

    def panels(self):
        return len(self.list())

    def panel(self, index):
        return self.list()[index]


class GraphFrame(ZFrame, GraphMixin, SubGraphsMixin, MarkerMixin):
    """
    Graph Frame

    A container which can hold one or more Graph Panels, stacked vertically,
    with a common x-axis.
    """

    def add_overlay_graph(self):
        """
        Add a new overly graph panel to the Graph Frame.

        Returns:
            GraphPanel: the newly added graph panel.
        """

        num_panels = len(self.list())

        self._generic_command(Command.ADD_OVERLAY_GRAPH)

        panels = self.list()
        if num_panels == len(panels):
            raise common.remote.RemoteException("Too many graph panels")

        return panels[-1]

    def add_poly_graph(self):
        """
        Add a new poly-graph panel to the Graph Frame.

        Returns:
            GraphPanel: the newly added graph panel.
        """

        num_panels = len(self.list())

        self._generic_command(Command.ADD_POLY_GRAPH)

        panels = self.list()
        if num_panels == len(panels):
            raise common.remote.RemoteException("Too many graph panels")

        return panels[-1]

    @rmi
    def remove(self, *graphs):
        """
        Remove graphs from the Graph Frame
        """

    def zoom(self, xmin=None, xmax=None, *, compute_x_grid=True):
        """
        Alter the x-axis viewport for all graph panels in this graph frame

        .. versionadded:: 2.2.1
        """

        self.panel(0).zoom(xmin=xmin, xmax=xmax, compute_x_grid=compute_x_grid)


class PlotFrame(ZFrame, GraphMixin):
    """
    Plot Frame

    A container which holds a X-Y plot graph containing 1 or more curves.
    """

    def add_curves(self, *channels):
        """
        Add one or more channels to the X-Y plot.

        For every pair of channels added, one X-Y curve is created.

        Parameters:
            *channels (Channel): curves to add to X-Y plot frame
        """

        if not channels:
            raise ValueError("Expected one or more channels")

        for channel in channels:
            channel.copy()
            self.paste_curve()

    def paste_curve(self):
        """
        Paste a curve from the clipboard into the graph
        """

        self._generic_command(Command.IDZ_CMP_PASTE)

    def polar(self):
        """
        Switch the plot to Polar mode (magnitude & phase)
        """

        self.properties(mode=1)
        return self

    def rectangular(self):
        """
        Switch the plot to Rectangular mode (X-Y)
        """

        self.properties(mode=0)
        return self


class FFTFrame(ZFrame, GraphMixin, SubGraphsMixin, MarkerMixin):
    """
    FFT Graph Frame

    A container which holds an overlay graph, as well as a magnitude and
    phase graph for automatic harmonic analysis of the curve(s) in the
    overlay graph.
    """

    def add_curves(self, *channels):
        """
        Add one or more channels to the FFT Graph

        Parameters:
            *channels (Channel): curves to add to graph
        """

        self.panel(0).add_curves(*channels)


    def paste_curve(self):
        """
        Paste a curve from the clipboard into the top graph
        """

        self.panel(0).paste_curve()



#===============================================================================
# Enerplot Graphs
#===============================================================================

class GraphPanel(Component, GraphMixin):
    """
    Graph Panel
    """

    def add_curves(self, *channels):
        """
        Add one or more channels to a graph

        Parameters:
            *channels (Channel): curves to add to graph
        """

        if not channels:
            raise ValueError("Expected one or more channels")

        for channel in channels:
            channel.copy()
            self.paste_curve()

    def paste_curve(self):
        """
        Paste a curve from the clipboard into the graph
        """
        self._generic_command(Command.IDZ_CMP_PASTE)

    @rmi
    def remove(self, *curves):
        """
        Remove curves from the Graph Panel
        """

#===============================================================================
# Enerplot Curves
#===============================================================================

class Curve(Component, Trace):
    """
    Graph Curve
    """

    @rmi
    def channel(self):
        """
        Retrieve the channel associated with a curve
        """

    @property
    def data(self):
        return self.channel().data

    def extents(self):
        """
        The domain and range of this Curve

        Returns:
            Tuple[Tuple]: (minimum x, maximum x), (minimum y, maximum y)
        """
        return self.channel().extents()

    def generate_new_record(self):
        """
        Your description here
        """

        self._generic_command(Command.ID_CURVE_GENERATENEWRECORD)

    @rmi
    def properties(self, **kwargs):
        pass
