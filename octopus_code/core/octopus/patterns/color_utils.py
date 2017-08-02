#!/usr/bin/env python

"""Helper functions to make color manipulations easier."""

from __future__ import division
import math
import numpy as np

pi_16 = np.float16(np.pi)

lookup_len = 256
two = np.float16(2)
cos_rescale = np.float16((lookup_len-1) / (two*pi_16))
cos_lookup_table = np.zeros(lookup_len, dtype=np.float16)
for i in range(lookup_len):
    cos_lookup_table[i] = np.float16(np.cos(2*np.pi*i/lookup_len))

def remap(x, oldmin, oldmax, newmin, newmax):
    """Remap the float x from the range oldmin-oldmax to the range newmin-newmax

    Does not clamp values that exceed min or max.
    For example, to make a sine wave that goes between 0 and 256:
        remap(math.sin(time.time()), -1, 1, 0, 256)

    """
    zero_to_one = (x-oldmin) / (oldmax-oldmin)
    return zero_to_one*(newmax-newmin) + newmin

def clamp(x, minn, maxx):
    """Restrict the float x to the range minn-maxx."""
    y = np.copy(x)
    y[y<minn] = minn
    y[y>maxx] = maxx
    return y

def cos_lookup(x, offset=0, period=6.28318, minn=-1, maxx=1):
    maxx=np.float16(maxx)
    minn=np.float16(minn)

    cos_arg = (cos_rescale*(((x/np.float16(period) - np.float16(offset)) * pi_16 * two) % (two*pi_16)))

    if type(cos_arg).__module__ == np.__name__:
        cos_arg = cos_arg.astype(int)
    else:
        cos_arg = int(cos_arg)
        
    return minn + np.float16(0.5) * (maxx-minn) * (np.float16(1) + cos_lookup_table[cos_arg])

def cos(x, offset=0, period=1, minn=0, maxx=1):
    """A cosine curve scaled to fit in a 0-1 range and 0-1 domain by default.

    offset: how much to slide the curve across the domain (should be 0-1)
    period: the length of one wave
    minn, maxx: the output range

    """
    return minn + 0.5 * (maxx-minn) * (1 + np.cos((x/period - offset) * np.pi * 2))

def contrast(color, center, mult):
    """Expand the color values by a factor of mult around the pivot value of center.

    color: an (r, g, b) tuple
    center: a float -- the fixed point
    mult: a float -- expand or contract the values around the center point

    """
    r, g, b = color
    r = (r - center) * mult + center
    g = (g - center) * mult + center
    b = (b - center) * mult + center
    return (r, g, b)

def contrast_np(arr, center, mult):
    return (arr - center)*mult + center

def clip_black_by_luminance(color, threshold):
    """If the color's luminance is less than threshold, replace it with black.
    
    color: an (r, g, b) tuple
    threshold: a float

    """
    r, g, b = color
    if r+g+b < threshold*3:
        return (0, 0, 0)
    return (r, g, b)

def clip_black_by_channels(color, threshold):
    """Replace any individual r, g, or b value less than threshold with 0.

    color: an (r, g, b) tuple
    threshold: a float

    """
    r, g, b = color
    if r < threshold: r = 0
    if g < threshold: g = 0
    if b < threshold: b = 0
    return (r, g, b)

def mod_dist(a, b, n):
    """Return the distance between floats a and b, modulo n.

    The result is always non-negative.
    For example, thinking of a clock:
    mod_dist(11, 1, 12) == 2 because you can "wrap around".

    """
    return min((a-b) % n, (b-a) % n)

def gamma(color, gamma):
    """Apply a gamma curve to the color.  The color values should be in the range 0-1."""
    r, g, b = color
    return (max(r, 0) ** gamma, max(g, 0) ** gamma, max(b, 0) ** gamma)

def linspace_16(start, stop, npts):
    start = np.float16(start)
    npts = np.float16(npts)
    stop = np.float16(stop)
    length = np.float16(stop - start)
    return start + np.arange(npts, dtype=np.float16)*length/(npts-1)