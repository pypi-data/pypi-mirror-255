# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2024 Bryant E. McDonnell (See AUTHORS)
#
# Licensed under the terms of the BSD2 License
# See LICENSE.txt for details
# -----------------------------------------------------------------------------
"""Base class for a SWMM Simulation."""


class Config(object):
    """"""

    def __init__(self):
        self._display_progress_bar = False

    @property
    def display_progress_bar(self) -> bool:
        """
        Configure Simulation Properties.

        Examples:

        .. code-block:: python

            from pyswmm import Simulation, Config

            C


        """
        return self._display_progress_bar

    @display_progress_bar.setter
    def display_progress_bar(self, v: bool) -> None:
        self._display_progress_bar = v
    
     