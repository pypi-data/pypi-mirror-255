from __future__ import annotations

import math

from .base import HPGe


class V07646A(HPGe):
    """An inverted-coaxial point contact germanium detector V07646A with a special geometry."""

    def _decode_polycone_coord(self) -> tuple[list[float], list[float]]:
        c = self.metadata.geometry

        def _tan(a):
            return math.tan(math.pi * a / 180)

        r = []
        z = []

        if c.pp_contact.depth_in_mm > 0:
            r += [
                0,
                c.pp_contact.radius_in_mm,
                c.pp_contact.radius_in_mm,
            ]
            z += [
                c.pp_contact.depth_in_mm,
                c.pp_contact.depth_in_mm,
                0,
            ]
        else:
            r += [0]
            z += [0]

        r += [
            c.groove.radius_in_mm.inner,
            c.groove.radius_in_mm.inner,
            c.groove.radius_in_mm.outer,
            c.groove.radius_in_mm.outer,
        ]

        z += [
            0,
            c.groove.depth_in_mm,
            c.groove.depth_in_mm,
            0,
        ]

        bottom_cylinder = c.extra.bottom_cylinder

        if c.taper.bottom.height_in_mm > 0:
            r += [
                bottom_cylinder.radius_in_mm
                - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
                bottom_cylinder.radius_in_mm,
            ]

            z += [
                0,
                c.taper.bottom.height_in_mm,
            ]
        else:
            r += [bottom_cylinder.radius_in_mm]
            z += [0]

        r += [bottom_cylinder.radius_in_mm, c.radius_in_mm]
        z += [
            bottom_cylinder.height_in_mm,
            bottom_cylinder.height_in_mm + bottom_cylinder.transition_in_mm,
        ]

        if c.taper.top.height_in_mm > 0:
            r += [
                c.radius_in_mm,
                c.radius_in_mm
                - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
            ]

            z += [
                c.height_in_mm - c.taper.top.height_in_mm,
                c.height_in_mm,
            ]
        else:
            r += [c.radius_in_mm]
            z += [c.height_in_mm]

        if c.taper.borehole.height_in_mm > 0:
            r += [
                c.borehole.radius_in_mm
                + c.taper.borehole.height_in_mm * _tan(c.taper.borehole.angle_in_deg),
                c.borehole.radius_in_mm,
            ]

            z += [c.height_in_mm, c.height_in_mm - c.taper.borehole.height_in_mm]
        else:
            r += [c.borehole.radius_in_mm]
            z += [c.height_in_mm]

        if c.taper.borehole.height_in_mm != c.borehole.depth_in_mm:
            r += [
                c.borehole.radius_in_mm,
                0,
            ]

            z += [
                c.height_in_mm - c.borehole.depth_in_mm,
                c.height_in_mm - c.borehole.depth_in_mm,
            ]
        else:
            r += [0]

            z += [c.height_in_mm - c.borehole.depth_in_mm]

        return r, z
