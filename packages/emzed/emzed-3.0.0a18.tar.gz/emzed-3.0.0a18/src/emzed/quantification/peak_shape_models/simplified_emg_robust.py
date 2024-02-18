# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import warnings

import numpy as np
import scipy.optimize as opt
from numpy import trapz

from emzed.utils.numpy import ignore_overflow

from .base import PeakShapeModelBase
from .simplified_emg import FAC1, SQRT2_PI, SimplifiedEmgModel


class SimplifiedEmgModelRobust(SimplifiedEmgModel, PeakShapeModelBase):
    model_name = "emg_robust"

    @staticmethod
    def _apply(rt_values, height, center, width, symmetry):
        rt_values = np.atleast_1d(rt_values)

        # avoid zero division
        if symmetry * symmetry == 0.0:
            symmetry = 1e-6

        inner = (
            width * width / 2.0 / symmetry / symmetry - (rt_values - center) / symmetry
        )
        nominator = np.exp(inner)

        # avoid overflow: may happen if _fun_eval is called with full rtrange and
        # symmetry is small:
        # avoid zero division
        if width == 0:
            width = 1e-6

        denominator = 1 + np.exp(
            FAC1 * ((rt_values - center) / width - width / symmetry)
        )

        # inf / inf results in None, we prefer max_float / inf which is 0:
        t1 = height * width / symmetry * SQRT2_PI * nominator
        t1[np.isinf(t1)] = np.finfo(t1.dtype).max
        return t1 / denominator

    @classmethod
    @ignore_overflow
    def _fit(cls, rts, intensities, extra_args):
        if len(rts) < 4:
            return cls((None,) * 4, None, None, None, None)

        imax = np.max(intensities)
        center_est = rts[np.argmax(intensities)]
        # folloing estimates by experimental exploration of symmetric gaussians in
        # different configurations
        height_est = imax * 1.4
        width_est = 0.3
        symmetry_est = width_est / 0.85

        start_parameters = (height_est, center_est, width_est, symmetry_est)

        def err(parameters, rts, intensities):
            return cls._apply(rts, *parameters) - intensities

        # first guess with relatively high rel error on estimated params:
        parameters, _cov, _info_dict, msg, ierr = opt.leastsq(
            err,
            start_parameters,
            xtol=1e-3,
            gtol=1e-6,
            args=(rts, intensities),
            full_output=True,
        )

        # Now tighter fit with lower sensitivity to outliers by using IRLS
        # https://en.wikipedia.org/wiki/Iteratively_reweighted_least_squares
        p = 1.1
        residuals = err(parameters, rts, intensities)
        residuals[np.abs(residuals < 1e-10)] = 1e-10
        w = np.abs(residuals) ** ((p - 2) / 2)

        # relative error on parameters:
        xtol = extra_args.pop("xtol", 1e-8)

        # error on gradient orthogonality:
        gtol = extra_args.pop("gtol", 1e-10)

        has_maxfev = "maxfev" in extra_args
        maxfev = extra_args.pop("maxfev", 200 * 5)  # default according to scipy doc

        # ignore:
        extra_args.pop("full_output", None)

        (height, center, width, symmetry), _cov, _info_dict, msg, ierr = opt.leastsq(
            err,
            start_parameters,
            xtol=xtol,
            gtol=gtol,
            args=(rts, intensities),
            full_output=True,
            maxfev=maxfev,
            diag=w,
            **extra_args,
        )

        if (
            height < 0
            or width < 0
            or symmetry < 0
            or center < -100
            or (ierr == 5 and not has_maxfev)
        ):
            # optimizer did not converge
            return cls((None,) * 4, None, None, None, None)

        if np.any(np.isnan((height, width, symmetry, center))):
            # optimizer did not converge
            return cls((None,) * 4, None, None, None, None)

        if ierr == 0 or (ierr == 5 and not has_maxfev):
            warnings.warn(msg)
            return cls((None,) * 4, None, None, None, None)

        rtmin, rtmax = cls._detect_eic_limits(
            height, center, width, symmetry, min(rts), max(rts)
        )

        rt_full = np.linspace(rtmin, rtmax, cls.NPOINTS_INTEGRAL)
        ii_full = cls._apply(rt_full, height, center, width, symmetry)
        area = trapz(ii_full, rt_full)

        ii_smoothed = cls._apply(rts, height, center, width, symmetry)
        rmse = np.sqrt(np.sum((ii_smoothed - intensities) ** 2) / len(rts))

        parameters = (height, center, width, symmetry)
        return cls(parameters, area, rmse, rtmin, rtmax)
