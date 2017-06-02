/* -*- c++ -*-
 * Copyright (c) 2012-2016 by the GalSim developers team on GitHub
 * https://github.com/GalSim-developers
 *
 * This file is part of GalSim: The modular galaxy image simulation toolkit.
 * https://github.com/GalSim-developers/GalSim
 *
 * GalSim is free software: redistribution and use in source and binary forms,
 * with or without modification, are permitted provided that the following
 * conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions, and the disclaimer given in the accompanying LICENSE
 *    file.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions, and the disclaimer given in the documentation
 *    and/or other materials provided with the distribution.
 */

//#define DEBUGLOGGING

#include "SBDeltaFunction.h"
#include "SBDeltaFunctionImpl.h"

// Define this variable to find azimuth (and sometimes radius within a unit disc) of 2d photons by
// drawing a uniform deviate for theta, instead of drawing 2 deviates for a point on the unit
// circle and rejecting corner photons.
// The relative speed of the two methods was tested as part of issue #163, and the results
// are collated in devutils/external/time_photon_shooting.
// The conclusion was that using sin/cos was faster for icpc, but not g++ or clang++.

namespace galsim {

    SBDeltaFunction::SBDeltaFunction(double flux, const GSParamsPtr& gsparams) :
        SBProfile(new SBDeltaFunctionImpl(flux, gsparams)) {}

    SBDeltaFunction::SBDeltaFunction(const SBDeltaFunction& rhs) : SBProfile(rhs) {}

    SBDeltaFunction::~SBDeltaFunction() {}

    std::string SBDeltaFunction::SBDeltaFunctionImpl::serialize() const
    {
        std::ostringstream oss(" ");
        oss.precision(std::numeric_limits<double>::digits10 + 4);
        oss << "galsim._galsim.SBDeltaFunction("<<getFlux();
        oss << ", galsim.GSParams("<<*gsparams<<"))";
        return oss.str();
    }

    SBDeltaFunction::SBDeltaFunctionImpl::SBDeltaFunctionImpl(double flux,
                                               const GSParamsPtr& gsparams) :
        SBProfileImpl(gsparams),
        _flux(flux)
    {
        dbg<<"DeltaFunction:\n";
        dbg<<"_flux = "<<_flux<<std::endl;
        dbg<<"maxK() = "<<maxK()<<std::endl;
        dbg<<"stepK() = "<<stepK()<<std::endl;
    }

    // Set maxK to the value where the FT is down to maxk_threshold
    double SBDeltaFunction::SBDeltaFunctionImpl::maxK() const
    {
        // This is essentially infinite since the delta function
        // is constant over k space
        return MOCK_INF;
    }

    // The amount of flux missed in a circle of radius pi/stepk should be at
    // most folding_threshold of the flux.
    double SBDeltaFunction::SBDeltaFunctionImpl::stepK() const
    {
        // This is essentially infinite since the delta function
        // is constant over k space
        return MOCK_INF;
    }

    double SBDeltaFunction::SBDeltaFunctionImpl::xValue(const Position<double>& p) const
    {
        return (p.x == 0 && p.y == 0) ? MOCK_INF : 0.;
    }

    std::complex<double>
    SBDeltaFunction::SBDeltaFunctionImpl::kValue(const Position<double>& k) const
    {
        std::complex<double> result(_flux,0);
        return result;
    }

    boost::shared_ptr<PhotonArray> SBDeltaFunction::SBDeltaFunctionImpl::shoot(int N, UniformDeviate u) const
    {
        dbg<<"Delta Function shoot: N = "<<N<<std::endl;
        dbg<<"Target flux = "<<getFlux()<<std::endl;
        boost::shared_ptr<PhotonArray> result(new PhotonArray(N));

        double fluxPerPhoton = _flux/N;
        for (int i=0; i<N; i++) {
            result->setPhoton(i, 0.0, 0.0, fluxPerPhoton);
        }
        dbg<<"Realized flux = "<<result->getTotalFlux()<<std::endl;

        return result;
    }
}
