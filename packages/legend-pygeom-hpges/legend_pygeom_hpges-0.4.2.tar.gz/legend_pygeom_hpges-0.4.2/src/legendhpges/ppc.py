from __future__ import annotations

import math

from .base import HPGe


class PPC(HPGe):
    """A p-type point contact germanium detector."""

    def _decode_polycone_coord(self):
        c = self.metadata.geometry

        def _tan(a):
            return math.tan(math.pi * a / 180)

        r = []
        z = []

        if c.pp_contact.depth_in_mm > 0:
            r += [0, c.pp_contact.radius_in_mm, c.pp_contact.radius_in_mm]
            z += [c.pp_contact.depth_in_mm, c.pp_contact.depth_in_mm, 0]
        else:
            r += [0]
            z += [0]

        if c.taper.bottom.height_in_mm > 0:
            r += [
                c.radius_in_mm
                - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
                c.radius_in_mm,
            ]
            z += [0, c.taper.bottom.height_in_mm]
        else:
            r += [c.radius_in_mm]
            z += [0]

        if c.taper.top.height_in_mm > 0:
            r += [
                c.radius_in_mm,
                c.radius_in_mm
                - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
            ]
            z += [c.height_in_mm - c.taper.top.height_in_mm, c.height_in_mm]
        else:
            r += [c.radius_in_mm]
            z += [c.height_in_mm]

        r += [0]
        z += [c.height_in_mm]

        return r, z
