from .command import Command
from .remote import Remotable, rmi, rmi_property

#===============================================================================
# Enerplot Component
#===============================================================================

class Component(Remotable):

    """
    The base type for all Enerplot components.

    Include graph frames, dividers, and sticky notes
    """

    #---------------------------------------------------------------------------
    # Identity
    #---------------------------------------------------------------------------

    @property
    def id(self):
        """The id of the component (read-only)"""
        return self._identity['id']

    @property
    def book_name(self):
        """The book the component belongs to (read-only)"""
        return self._identity['book']

    @property
    def book(self):
        """The book the component belongs to (read-only)"""
        return self.main.book(self.book_name)

    @rmi_property
    def classid(self):
        """The classid of the component (read-only)"""

    #---------------------------------------------------------------------------
    # Hierarchy
    #---------------------------------------------------------------------------

    @rmi
    def parent(self):
        """Retrieve the owner of this component"""

    #---------------------------------------------------------------------------
    # Attributes
    #---------------------------------------------------------------------------

    @rmi
    def attributes(self, **kwargs):
        """
        Set or get a component's attributes

        A component's attributes are used to describe the component's
        location and size relative to its parent.

        Parameters:
            **kwargs: key=value arguments

        Returns:
            dict: The component's current attributes.

        See also:
            :meth:`properties`

        """

    def _extents(self, **kwargs):
        args = sum(v is not None for v in kwargs.values())
        if args == 0:
            attr = self.attributes()
            return tuple(attr[key] for key in kwargs)
        elif args != len(kwargs):
            raise ValueError("Specify all arguments, or no arguments")
        elif any(v <= 0 for v in kwargs.values()):
            raise ValueError("All values must be positive")
        else:
            self.attributes(**kwargs)

    def position(self, x=None, y=None):
        """
        Get or set the component's position.

        If the x & y parameters are given, the position is set.
        If they are omitted, the current position is returned.

        Parameters:
            x (int): The component's new x location on the sheet
            y (int): The component's new y location on the sheet

        Returns:
            Tuple[x,y]: The current location of the component
        """

        return self._extents(x=x, y=y)

    def size(self, width=None, height=None):
        """
        Get or set the component's size

        If the width & height parameters are given, the size is set.
        If they are omitted, the current size is returned.

        Parameters:
            width (int): The component's new width
            height (int): The component's new height

        Returns:
            Tuple[width, height]: The current size of the component
        """

        return self._extents(w=width, h=height)

    def extents(self, x=None, y=None, width=None, height=None):
        """
        Get or set the component's position and size

        If all parameters are given, the position and size is set.
        If all parameters are omitted, the current extents are returned.

        Parameters:
            x (int): The component's new x location on the sheet
            y (int): The component's new y location on the sheet
            width (int): The component's new width
            height (int): The component's new height

        Returns:
            Tuple[x,y,width,height]: The current extents of the component
        """

        return self._extents(x=x, y=y, w=width, h=height)

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------

    @rmi
    def _properties(self, paramlist, **kwargs):
        """Set/Get parameters"""

    @staticmethod
    def _app_val(val):
        if isinstance(val, bool):
            return 'true' if val else 'false'
        return str(val)

    def properties(self, paramlist='', **kwargs):
        """
        Set or get a component's properties

        A component's properties are used to describe the component's
        appearance or control the component's behaviour.

        Parameters:
            **kwargs: key=value arguments

        Returns:
            dict: The component's current property values

        See also:
            :meth:`attributes`
        """

        codecs = self._codecs()

        if kwargs:
            kwargs = { key.replace('̵','-'): val for key, val in kwargs.items()
                       if val is not None }
            for codec in codecs:
                kwargs = codec.encode_all(kwargs)
            kwargs = { key: Component._app_val(val)
                       for key, val in kwargs.items() if val is not None }
            self._properties(paramlist, **kwargs)
        else:
            params = self._properties(paramlist)
            for codec in codecs:
                params = codec.decode_all(params)
            return params

    def __setitem__(self, key, item):
        self.properties('', **{key: item})

    def __getitem__(self, key):
        return self.properties('')[key]

    def _codecs(self):
        return ()

    #---------------------------------------------------------------------------
    # Commands
    #---------------------------------------------------------------------------

    @rmi
    def _command(self, cmd_id):
        """
        Send a generic command to the component

        Parameters:
            cmd_id (int): The command number
        """

    def _generic_command(self, command):
        """
        Send a generic command to the component

        Parameters:
            command (enum): The enumerated command identifier
        """

        self._command(command.value)

    def copy_as_metafile(self):
        """
        Copy component to clipboard as a metafile
        """

        self._generic_command(Command.COPY_AS_METAFILE)

    def copy_as_bitmap(self):
        """
        Copy component to clipboard as a bitmap
        """

        self._generic_command(Command.COPY_AS_BITMAP)


    def cut(self):
        """
        Remove the component to the clipboard
        """

        self._generic_command(Command.IDZ_CMP_CUT)

    def copy(self):
        """
        Copy the component to the clipboard
        """

        self._generic_command(Command.IDZ_CMP_COPY)

    def paste(self):
        """
        Paste the component(s) from the clipboard to this canvas
        """

        self._generic_command(Command.IDZ_CMP_PASTE)


    #---------------------------------------------------------------------------
    # Container functions
    #---------------------------------------------------------------------------

    @rmi
    def list(self, classid=None):
        """
        List all the components contained inside this object,
        possibly restricted to a certain classid.

        Parameters:
            classid (str): one of "GraphFrame", "PlotFrame", "FFTFrame",
                "Divider", "Sticky" or "GroupBox".

        Returns:
            List[Component]: the list of components
        """

    def find(self, classid=None, **properties):
        """find( [classid,] [key=value, ...])

        Find the (singular) component that matches the given criteria, or None
        if no matching component can be found.  Raises an exception if more
        than one component matches the given criteria.

        Parameters:
            classid (str): one of "GraphFrame", "PlotFrame", "FFTFrame",
                "Divider", "Sticky" or "GroupBox".
            key=value: additional parameters which must be matched.

        Returns:
            Component: the found component or None
        """

        components = self.find_all(classid, **properties)

        if len(components) > 1:
            raise Exception("Multiple components found")

        return components[0] if components else None

    def find_first(self, classid=None, **properties):
        """find_first( [classid,] [key=value, ...])

        Find a component that matches the given criteria, or None
        if no matching component can be found.

        Parameters:
            classid (str): one of "GraphFrame", "PlotFrame", "FFTFrame",
                "Divider", "Sticky" or "GroupBox".
            key=value: additional parameters which must be matched.

        Returns:
            Component: the found component or None
        """

        components = self.find_all(classid, **properties)

        return components[0] if components else None

    def find_all(self, classid=None, **properties):
        """find_all( [classid,] [key=value, ...])

        Find all components that matches the given criteria, or None
        if no matching component can be found.

        Parameters:
            classid (str): one of "GraphFrame", "PlotFrame", "FFTFrame",
                "Divider", "Sticky" or "GroupBox".
            key=value: additional parameters which must be matched.

        Returns:
            List[Component]: the list of matching components
        """

        components = self.list(classid) if classid else self.list()

        if properties:
            properties = { key: Component._app_val(val)
                           for key, val in properties.items() }
            components = [ component for component in components
                           if self._match_props(component, properties) ]

        return components

    @staticmethod
    def _match_props(cmp, properties):
        props = cmp.properties()

        return all(props.get(key) == val for key, val in properties.items())


