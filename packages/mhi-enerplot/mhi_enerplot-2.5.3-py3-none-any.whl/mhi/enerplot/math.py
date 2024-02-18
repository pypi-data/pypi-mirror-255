#===============================================================================
# Manitoba Hydro Internation / Power Technology Center
# Enerplot Automation Library - Trace math functions
#===============================================================================
"""
Manitoba Hydro International

MHI Enerplot Trace Math Library

Enables advanced calculations on traces (arrays of double precision values)
"""

#===============================================================================
# Imports
#===============================================================================

import math, array
from math import e, pi
from .trace import Trace


#===============================================================================
# Map function
#    returns NaN for any points where the map function breaks down
#===============================================================================

def _map(func, *traces, nan=float('nan')):
    def f(*args):
        try:
            return func(*args)
        except ValueError:
            return nan
    return Trace(f(*args) for args in zip(*traces))


#===============================================================================
# Logarithmic Functions
#===============================================================================

def exp(trace):
    """
    Return a new trace where every value is transformed as: x → e^x.
    """
    
    return Trace(map(math.exp, trace))

def ln(trace):
    """
    Return a new trace where every value is transformed as: x → logₑ(x).

    All values less than or equal to zero are replaced with ``NaN``
    """
    
    return _map(math.log, trace)

def log(trace, base=math.e):
    """
    Return a new trace where every value is transformed as: x → logₐ(x).
    The default base is "e", for the natural logarithm.

    All values less than or equal to zero are transformed to ``NaN``
    """

    if base <= 0 or base == 1:
        raise ValueError("Invalid base")

    f = lambda x: math.log(x, base)
    return _map(f, trace)

def log10(trace):
    """
    Return a new trace where every value is transformed as: x → log₁₀(x).

    All values less than or equal to zero are transformed to ``NaN``
    """
    
    return _map(math.log10, trace)


def sqrt(trace):
    """
    Return a new trace where every value is transformed as: x → √x.

    All values less than or equal to zero are transformed to ``NaN``
    """
    
    return _map(math.sqrt, trace)


#===============================================================================
# Circular Functions
#===============================================================================

def degrees(trace):
    """
    Return a new trace where every value is transformed from radians
    to degrees.
    """
    
    return Trace(map(math.degrees, trace))

def radians(trace):
    """
    Return a new trace where every value is transformed from degrees
    to radians.
    """
    
    return Trace(map(math.radians, trace))


def sin(trace):
    """
    Return a new trace where every value is transformed as: x → sin(x).

    The input to the sin(x) function is intrepeted as being in radians.
    """
    
    return Trace(map(math.sin, trace))

def cos(trace):
    """
    Return a new trace where every value is transformed as: x → cos(x).

    The input to the cos(x) function is intrepeted as being in radians.
    """
    
    return Trace(map(math.cos, trace))

def tan(trace):
    """
    Return a new trace where every value is transformed as: x → tan(x).

    The input to the tan(x) function is intrepeted as being in radians.
    """
    
    return Trace(map(math.tan, trace))


def asin(trace):
    """
    Return a new trace where every value is transformed as: x → sin⁻¹(x).

    The output of the sin⁻¹(x) function is in radians.

    ``NaN`` is returned for all values greater than 1, or less than -1.
    """
    
    return _map(math.asin, trace)

def acos(trace):
    """
    Return a new trace where every value is transformed as: x → cos⁻¹(x).

    The output of the cos⁻¹(x) function is in radians.

    ``NaN`` is returned for all values greater than 1, or less than -1.
    """
    
    return _map(math.acos, trace)

def atan(trace):
    """
    Return a new trace where every value is transformed as: x → tan⁻¹(x).

    The output of the tan⁻¹(x) function is in radians.
    """
    
    return Trace(map(math.atan, trace))


def hypot(x, y):
    """
    Compute a new trace, returning the Euclidean distance, sqrt(x*x + y*y),
    for each pair of values from the two input traces.

    The follow two statements produce equivalent output::

        from mhi.enerplot.math import hypot, sqrt

        c = hypot(a, b)
        c = sqrt(a ** 2 + b ** 2)

    The first statement is significantly faster since the second statement
    requires allocating several temporary traces for holding the intermediate
    results.
    """

    return _map(math.hypot, x, y)

def atan2(y, x):
    """
    Compute a new trace, returning the arc tangent (measured in radians) of y/x,
    for each pair of values from the two input traces.
    Unlike atan(y/x), the signs of both x and y are considered.

    When used in conjunction with the :func:`.hypot`, two traces representing
    real and imaginary values may be converted into two traces representing
    polar coordinates: magnitude and angle.
    """
    
    return _map(math.atan2, y, x)


#===============================================================================
# Selection: max/min
#===============================================================================

def maximum(*traces):
    """
    Return a new trace where the maximum value from each trace, at each point,
    is selected.
    """

    if len(traces) < 2:
        raise ValueError("At least two traces are required")

    return _map(max, *traces)

def minimum(*traces):
    """
    Return a new trace where the minimum value from each trace, at each point,
    is selected.
    """

    if len(traces) < 2:
        raise ValueError("At least two traces are required")

    return _map(min, *traces)


#===============================================================================
# Processing
#===============================================================================

def smooth(trace, time_constant, domain=None):

    """
    Return a smoothed version of the input trace.

    This function simulates a lag or 'real pole' function.
    The time domain solution algorithm is based on the trapezoidal rule.
    The solution method for this function is as follows:

    Parameters:
        trace (Trace): the input to be smoothed.
        time_constant (float): the time-constant to be used for smoothing
        domain (float or trace): the time-step, or the signal domain

    Examples:

        If ``input`` represents a :class:`.Curve` from a :class:`.DataFile`
        with a 50µs timestep, the following statements would produce the same
        output::

            from mhi.enerplot.math import smooth
            
            output = smooth(input, 0.001, 50e-6)
            output = smooth(input, 0.001, input.domain)
    """

    def const_dt(dt):

        a = math.exp(-dt / time_constant)
        b = 1 - a

        y = trace[0]
        yield y

        for x in trace.data[1:]:
            y = y * a + x * b

            yield y

    def variable_dt():

        t0 = domain[0]
        y = trace[0]

        yield y

        for x, t in zip(trace.data[1:], domain.data[1:]):
            a = math.exp((t0 - t) / time_constant)
            y = y * a + x * (1 - a)

            yield y

            t0 = t

    if domain is None:
        domain = trace.domain

    if hasattr(domain, '__len__'):

        dt = domain[-1] - domain[0] / (len(domain) - 1)

        if not math.isclose(domain[1] - domain[0], dt):
            return Trace(variable_dt())
    else:
        dt = float(domain)

    return Trace(const_dt(dt))



