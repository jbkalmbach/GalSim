# Copyright (c) 2012-2016 by the GalSim developers team on GitHub
# https://github.com/GalSim-developers
#
# This file is part of GalSim: The modular galaxy image simulation toolkit.
# https://github.com/GalSim-developers/GalSim
#
# GalSim is free software: redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the disclaimer given in the documentation
#    and/or other materials provided with the distribution.
#
"""@file photon_array.py
Implements the PhotonArray class describing a collection of photons incident on a detector.
Also includes classes that modify PhotonArray objects in a number of ways.
"""

# Most of the functionality comes from the C++ layer
from ._galsim import PhotonArray
import numpy as np

# Add on more methods in the python layer

PhotonArray.__doc__ = """
The PhotonArray class encapsulates the concept of a collection of photons incident on
a detector.

A PhotonArray object is not typically constructed directly by the user.  Rather, it is
typically constructed as the return value of the `GSObject.shoot` method.
At this point, the photons only have x,y,flux values.  Then there are a number of classes
that perform various modifications to the photons such as giving them wavelenghts or
inclination angles or remove some due to fringing or vignetting.

TODO: fringing, vignetting, and angles are not implemented yet, but we expect them to
be implemented soon, so the above paragraph is a bit aspirational atm.

Attributes
----------

A PhotonArray instance has the following attributes, each of which is a numpy array:

- x,y           the incidence positions at the top of the detector
- flux          the flux of the photons
- dxdz, dydz    the tangent of the inclination angles in each direction
- wavelength    the wavelength of the photons

Unlike most GalSim objects (but like Images), PhotonArrays are mutable.  It is permissible
to write values to the above attributes with code like

    >>> photon_array.x += numpy.random.random(1000) * 0.01
    >>> photon_array.flux *= 20.
    >>> photon_array.wavelength = sed.sampleWavelength(photonarray.size(), bandpass)
    etc.

All of these will update the existing numpy arrays being used by the photon_array instance.

Note about the flux attribute
-----------------------------

Normal photons have flux=1, but we allow for "fat" photons that combine the effect of several
photons at once for efficiency.  Also, some profiles need to use negative flux photons to properly
implement photon shooting (e.g. InterpolateImage, which uses negative flux photons to get the
interpolation correct).  Finally, when we "remove" photons, for better efficiency, we actually
just set the flux to 0 rather than recreate new numpy arrays.

Initialization
--------------

The initialization constructs a PhotonArray to hold N photons, but does not set the values of
anything yet.  The constructor allocates space for the x,y,flux arrays, since those are always
needed.  The other arrays are only allocated on demand if the user accesses these attributes.

@param N            The number of photons to store in this PhotonArray.  This value cannot be
                    changed.
@param x            Optionally, the inital x values. [default: None]
@param y            Optionally, the inital y values. [default: None]
@param flux         Optionally, the inital flux values. [default: None]
@param dxdz         Optionally, the inital dxdz values. [default: None]
@param dydz         Optionally, the inital dydz values. [default: None]
@param wavelength   Optionally, the inital wavelength values. [default: None]
"""

# In python we want the init function to be a bit more functional so we can serialize properly.
# Save the C++-layer constructor as _PhotonArray_empty_init.
_PhotonArray_empty_init = PhotonArray.__init__

# Now make the one we want as the python-layer init function.
def PhotonArray_init(self, N, x=None, y=None, flux=None, dxdz=None, dydz=None, wavelength=None):
    _PhotonArray_empty_init(self, N)
    if x is not None: self.x[:] = x
    if y is not None: self.y[:] = y
    if flux is not None: self.flux[:] = flux
    if dxdz is not None: self.dxdz[:] = dxdz
    if dydz is not None: self.dydz[:] = dydz
    if wavelength is not None: self.wavelength[:] = wavelength
PhotonArray.__init__ = PhotonArray_init

PhotonArray.__getinitargs__ = lambda self: (
        self.size(), self.x, self.y, self.flux,
        self.dxdz if self.hasAllocatedAngles() else None,
        self.dydz if self.hasAllocatedAngles() else None,
        self.wavelength if self.hasAllocatedWavelengths() else None)

def PhotonArray_repr(self):
    s = "galsim.PhotonArray(%d, x=array(%r), y=array(%r), flux=array(%r)"%(
            self.size(), self.x.tolist(), self.y.tolist(), self.flux.tolist())
    if self.hasAllocatedAngles():
        s += ", dxdz=array(%r), dydz=array(%r)"%(self.dxdz.tolist(), self.dydz.tolist())
    if self.hasAllocatedWavelengths():
        s += ", wavelength=array(%r)"%(self.wavelength.tolist())
    s += ")"
    return s

def PhotonArray_str(self):
    return "galsim.PhotonArray(%d)"%self.size()

PhotonArray.__repr__ = PhotonArray_repr
PhotonArray.__str__ = PhotonArray_str
PhotonArray.__hash__ = None

PhotonArray.__eq__ = lambda self, other: (
        isinstance(other, PhotonArray) and
        np.array_equal(self.x,other.x) and
        np.array_equal(self.y,other.y) and
        np.array_equal(self.flux,other.flux) and
        self.hasAllocatedAngles() == other.hasAllocatedAngles() and
        self.hasAllocatedWavelengths() == other.hasAllocatedWavelengths() and
        (np.array_equal(self.dxdz,other.dxdz) if self.hasAllocatedAngles() else True) and
        (np.array_equal(self.dydz,other.dydz) if self.hasAllocatedAngles() else True) and
        (np.array_equal(self.wavelength,other.wavelength)
                if self.hasAllocatedWavelengths() else True) )
PhotonArray.__ne__ = lambda self, other: not self == other

# Make properties for convenient access to the various arrays
def PhotonArray_setx(self, x): self.getXArray()[:] = x
PhotonArray.x = property(PhotonArray.getXArray, PhotonArray_setx)

def PhotonArray_sety(self, y): self.getYArray()[:] = y
PhotonArray.y = property(PhotonArray.getYArray, PhotonArray_sety)

def PhotonArray_setflux(self, flux): self.getFluxArray()[:] = flux
PhotonArray.flux = property(PhotonArray.getFluxArray, PhotonArray_setflux)

def PhotonArray_setdxdz(self, dxdz): self.getDXDZArray()[:] = dxdz
PhotonArray.dxdz = property(PhotonArray.getDXDZArray, PhotonArray_setdxdz)

def PhotonArray_setdydz(self, dydz): self.getDYDZArray()[:] = dydz
PhotonArray.dydz = property(PhotonArray.getDYDZArray, PhotonArray_setdydz)

def PhotonArray_setwavelength(self, wavelength): self.getWavelengthArray()[:] = wavelength
PhotonArray.wavelength = property(PhotonArray.getWavelengthArray, PhotonArray_setwavelength)

