# SPDX-FileCopyrightText: Copyright 2016, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
from .._plots._plot_utilities import show_or_save_plot, plt, matplotlib, \
        get_theme
from mpl_toolkits.axes_grid1 import make_axes_locatable

__all__ = ['plot_cor_cov']


# ============
# Plot cor cov
# ============

@matplotlib.rc_context(get_theme(font_scale=1.2))
def plot_cor_cov(
        cor,
        cov,
        vel_component,
        save=True,
        verbose=True):
    """
    Plot correlation and covariance matrices.
    """

    cmap = plt.cm.YlGnBu
    interp = 'none'
    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(121)
    # ax1.set_rasterization_zorder(0)
    divider1 = make_axes_locatable(ax1)
    cax1 = divider1.append_axes("right", size="5%", pad=0.09)
    mat1 = ax1.matshow(cor, vmin=0, vmax=1, cmap=cmap, rasterized=True,
                       zorder=-1, interpolation=interp)
    cb1 = fig.colorbar(mat1, cax=cax1, ticks=numpy.array([0, 0.5, 1]))
    cb1.solids.set_rasterized(True)

    if vel_component == 'east':
        title_cor = '(a) Correlation'
        label_cor = 'East Velocity Data'
    else:
        title_cor = '(c) Correlation'
        label_cor = 'North Velocity Data'
    ax1.set_title(title_cor)
    ax1.set_ylabel(label_cor)
    ax1.tick_params(bottom=False)

    ax2 = fig.add_subplot(122)
    # ax2.set_rasterization_zorder(0)
    divider2 = make_axes_locatable(ax2)
    cax2 = divider2.append_axes("right", size="5%", pad=0.09)
    mat2 = ax2.matshow(cov, vmin=0, cmap=cmap, rasterized=True, zorder=-1,
                       interpolation=interp)
    cb2 = fig.colorbar(mat2, cax=cax2)
    cb2.solids.set_rasterized(True)
    ax2.tick_params(bottom=False)

    if vel_component == 'east':
        title_cov = '(b) Covariance'
    else:
        title_cov = '(d) Covariance'
    ax2.set_title(title_cov)

    fig.set_tight_layout(True)
    fig.patch.set_alpha(0)

    # Save plot
    if save:
        filename = 'cor_cov_' + vel_component
        show_or_save_plot(plt, filename=filename, transparent_background=False,
                          bbox_extra_artists=None, verbose=verbose)
