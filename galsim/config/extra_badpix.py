# Copyright (c) 2012-2015 by the GalSim developers team on GitHub
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

import numpy
import galsim

# The badpix extra output type is currently just a placeholder for when we eventually add 
# defects, saturation, etc.  Now it always just builds an Image with all 0's.

# The function to call at the end of building each stamp
def ProcessBadPixStamp(images, scratch, config, base, obj_num, logger=None):
    # Note: This is just a placeholder for now.  Once we implement defects, saturation, etc.,
    # these features should be marked in the badpix mask.  For now though, all pixels = 0.
    if base['do_noise_in_stamps']:
        badpix_im = galsim.ImageS(base['current_stamp'].bounds, wcs=base['wcs'], init_value=0)
        scratch[obj_num] = badpix_im

# The function to call at the end of building each image
def ProcessBadPixImage(images, scratch, config, base, logger=None):
    image = galsim.ImageS(base['image_bounds'], wcs=base['wcs'], init_value=0)
    if len(scratch) > 0.:
        # If we have been accumulating the variance on the stamps, build the total from them.
        for stamp in scratch.values():
            b = stamp.bounds & image.getBounds()
            if b.isDefined():
                # This next line is equivalent to:
                #    image[b] |= stamp[b]
                # except that this doesn't work through the proxy.  We can only call methods
                # that don't start with _.  Hence using the more verbose form here.
                image.setSubImage(b, image.subImage(b) | stamp[b])
    else:
        # Otherwise, build the bad pixel mask here.
        # Again, nothing here yet.
        pass
    k = base['image_num'] - base['start_image_num']
    images[k] = image

# For the hdu, just return the first element
def HDUBadPix(images):
    n = len(images)
    if n == 0:
        raise RuntimeError("No badpix images were created.")
    elif n > 1:
        raise RuntimeError("%d badpix images were created, but expecting only 1."%n)
    return images[0]


# Register this as a valid extra output
from .extra import RegisterExtraOutput
RegisterExtraOutput('badpix',
                    stamp_func = ProcessBadPixStamp,
                    image_func = ProcessBadPixImage,
                    write_func = galsim.fits.writeMulti,
                    hdu_func = HDUBadPix)
