from __future__ import annotations

import pint
from pyg4ometry import geant4

default_g4_registry = geant4.Registry()
"""Default Geant4 GDML registry."""

default_units_registry = pint.get_application_registry()
"""Default Pint physical units registry."""

default_units_registry.default_format = "~P"
