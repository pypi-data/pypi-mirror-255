#===============================================================================
# Trace
#-------------------------------------------------------------------------------
# A trace is an array of values, representing a quantity that changes over some
# domain.
#-------------------------------------------------------------------------------
# Arithmetic operations (+ - * /) on two traces will produce a new trace.
# If the traces are of different lengths, the new trace will be the length of
# the shorter trace; the extra values in the longer trace are discarded.
#===============================================================================

import array
import math as mth

class Trace:

    """
    A trace is an array of numbers which hold the value of a signal as it
    changes over some domain.  For instance, a trace may contain a voltage
    value as it changes over time.

    :class:`Channels <.Channel>` and :class:`Curves <.Curve>` both extend
    from the ``Trace`` class.
    """

    def __init__(self, initializer=None, domain=None):

        self._domain = domain
        self._data = None
        self._read_only = False

        if initializer is not None:

            try:
                if isinstance(initializer, int):
                    initializer = [0] * initializer
                elif isinstance(initializer, bytes):
                    initializer = memoryview(initializer)
                    self._read_only = True
                elif isinstance(initializer, bytearray):
                    initializer = memoryview(initializer)
                elif isinstance(initializer, map):
                    initializer = list(initializer)

                if isinstance(initializer, memoryview):
                    initializer = initializer.cast('d')

                self._data = array.array('d', initializer)

            except TypeError:
                print("Initializer?", type(initializer), initializer)
                pass

    @property
    def data(self):
        return self._data

    @property
    def domain(self):
        return self._domain

    @property
    def read_only(self):
        return self._read_only

    #-----------------------------------------------------------------------
    # Conversion to bytes for pickling
    #-----------------------------------------------------------------------

    def __bytes__(self):

        return bytes(self.data)


    #-----------------------------------------------------------------------
    # A trace is a container of values
    #-----------------------------------------------------------------------

    def __len__(self):
        """
        Return the number of points in a trace

        Returns:
            int: the number of points in the trace
        """

        return len(self.data)


    def __getitem__(self, key):
        """
        Return the value of a trace at a certain point, or a slice of the
        trace over a range of points

        Returns:
            The value at one point, or a new trace over the given slice.
        """

        if isinstance(key, slice):
            return Trace(self.data[key])
        else:
            return self.data[key]


    def __setitem__(self, key, item):
        """
        Update the contents of the trace, if the trace is not read-only.
        """

        if self.read_only:
            raise TypeError("cannot modify read-only trace")

        if isinstance(key, slice):
            if not isinstance(item, array.array):
                item = array.array('d', item)

        self.data[key] = item


    def __contains__(self, item):
        """
        Test if the trace contains the given value

        Returns:
            bool: ``True`` if the value is found, ``False`` otherwise.
        """

        return item in self.data


    def __iter__(self):
        """
        Return an iterator over the contents of the trace.
        """

        return iter(self.data)


    #-----------------------------------------------------------------------
    # Monotonic
    #-----------------------------------------------------------------------

    def increasing(self):
        """
        Test if a trace contains strictly increasing values.

        A strictly increasing trace is suitable to use as the domain of a
        dataset.

        Returns:
            bool: ``True`` if every value is larger than the previous one.
        """

        data = self.data

        return all(data[i-1] < data[i] for i in range(1, len(data)))


    def decreasing(self):
        """
        Test if a trace contains strictly decreasing values.

        Returns:
            bool: ``True`` if every value is smaller than the previous one.
        """

        data = self.data

        return all(data[i-1] > data[i] for i in range(1, len(data)))


    #-----------------------------------------------------------------------
    # Equality / Inequality
    #-----------------------------------------------------------------------

    def __eq__(self, other):
        if isinstance(other, Trace):
            return self.data == other.data
        return False

    def __ne__(self, other):
        if isinstance(other, Trace):
            return self.data != other.data
        return True


    #-----------------------------------------------------------------------
    # Trace = op Trace, where op is one of: + - abs trunc floor ceil
    #-----------------------------------------------------------------------

    def __pos__(self):
        """
        Return a positive (unary +) version of the trace ... as in, return
        a copy of the trace, unmodified.

        Returns:
            Trace: a new trace
        """

        return Trace((+x for x in self), self.domain)


    def __neg__(self):
        """
        Return a negative (unary -) version of the trace.

        Returns:
            Trace: a new trace
        """

        return Trace((-x for x in self), self.domain)


    def __abs__(self):
        """
        Return the absolute value of the trace.

        Returns:
            Trace: a new trace
        """

        return Trace((abs(x) for x in self), self.domain)


    def __trunc__(self):
        """
        Return a trace with each value truncated towards zero.

        Returns:
            Trace: a new trace
        """

        return Trace(map(mth.trunc, self), self.domain)


    def __floor__(self):
        """
        Return a trace with each value rounded down to an integer value.

        Returns:
            Trace: a new trace
        """

        return Trace(map(mth.floor, self), self.domain)

    def __ceil__(self):
        """
        Return a trace with each value rounded up to an integer value.

        Returns:
            Trace: a new trace
        """

        return Trace(map(mth.ceil, self), self.domain)


    #-----------------------------------------------------------------------
    # Trace = Trace op Trace, where op is one of: + - * / **
    #-----------------------------------------------------------------------

    def __add__(self, other):
        """
        Add two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(a + b for a, b in zip(self, other) )
        else:
            return Trace(a + other for a in self)

    def __radd__(self, other):
        """
        Add two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(b + a for a, b in zip(self, other) )
        else:
            return Trace(other + a for a in self)

    def __sub__(self, other):
        """
        Subtract two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(a - b for a, b in zip(self, other) )
        else:
            return Trace(a - other for a in self)

    def __rsub__(self, other):
        """
        Subtract two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(b - a for a, b in zip(self, other) )
        else:
            return Trace(other - a for a in self)

    def __mul__(self, other):
        """
        Multiply two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(a * b for a, b in zip(self, other) )
        else:
            return Trace(a * other for a in self)

    def __rmul__(self, other):
        """
        Multiply two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(b * a for a, b in zip(self, other) )
        else:
            return Trace(other * a for a in self)

    @staticmethod
    def div(a, b, inf = float('inf'), nan = float('nan')):
        if b == 0:
            if a > 0:
                return inf
            elif a < 0:
                return -inf
            else:
                return nan
        return a / b

    def __truediv__(self, other):
        """
        Divide two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(Trace.div(a, b) for a, b in zip(self, other))
        else:
            return Trace(a / other for a in self)

    def __rtruediv__(self, other):
        """
        Divide two traces, or a trace and a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(Trace.div(b, a) for a, b in zip(self, other))
        else:
            return Trace(Trace.div(other, a) for a in self)

    def __pow__(self, other):
        """
        Raise a trace to the power of another trace or a scalar value

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(a ** b for a, b in zip(self, other) )
        else:
            return Trace(a ** other for a in self)

    def __rpow__(self, other):
        """
        Raise a trace or scalar to the power of another trace

        Returns:
            Trace: a new trace
        """

        if isinstance(other, Trace):
            return Trace(b ** a for a, b in zip(self, other) )
        else:
            return Trace(other ** a for a in self)


    #-----------------------------------------------------------------------
    # Trace = Trace @ Trace, Convolution of two traces
    #-----------------------------------------------------------------------

    def __matmul__(self, other):
        """
        Return the convolution of two traces.

        (f♦g)[n] = Σ f[m] g[n-m], over all m

        The traces do not need to be equal length.  The length of the returned
        trace will be 1 point shorter than the length of both traces combined.

        Returns:
            Trace: a new trace
        """

        f = self.data
        g = other.data
        N = len(f)
        M = len(g)

        fg = lambda n: sum(f[n - m] * g[m]
                           for m in range(max(0, n - N + 1), min(n + 1, M)))

        return Trace(fg(i) for i in range(M + N - 1))
