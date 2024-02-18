from __future__ import annotations

import json
from pathlib import Path

from legendmeta import AttrsDict
from pyg4ometry import geant4

from .bege import BEGe
from .invcoax import InvertedCoax
from .materials import make_enriched_germanium
from .p00664b import P00664B
from .ppc import PPC
from .registry import default_g4_registry
from .semicoax import SemiCoax
from .v02160a import V02160A
from .v02162b import V02162B
from .v07646a import V07646A


def make_hpge(
    metadata: str | dict | AttrsDict,
    registry: geant4.Registry = default_g4_registry,
    **kwargs,
) -> geant4.LogicalVolume:
    """Construct an HPGe detector logical volume based on the detector metadata.

    Parameters
    ----------
    metadata
        LEGEND HPGe configuration metadata file containing
        detector static properties.
    registry
        pyg4ometry Geant4 registry instance.

    Other Parameters
    ----------------
    **kwargs
        Additionally, the following arguments are allowed for
        overriding the name and the material from the metadata:

        name
            name to attach to the detector. Used to name
            solid and logical volume.
        material
            pyg4ometry Geant4 material for the detector.

    Examples
    --------
        >>> gedet = make_hpge(metadata, registry)

        >>> gedet = make_hpge(metadata, registry, name = "my_det", material = my_material)

    """
    if not isinstance(metadata, (dict, AttrsDict)):
        with Path(metadata).open() as jfile:
            gedet_meta = AttrsDict(json.load(jfile))
    else:
        gedet_meta = AttrsDict(metadata)

    material = kwargs.get("material")
    name = kwargs.get("name")

    if material is None:
        if gedet_meta.production.enrichment is None:
            msg = "The enrichment argument in the metadata is None."
            raise ValueError(msg)
        kwargs["material"] = make_enriched_germanium(gedet_meta.production.enrichment)

    if name is None:
        if gedet_meta.name is None:
            msg = "The name of the detector in the metadata is None."
            raise ValueError(msg)
        kwargs["name"] = gedet_meta.name

    if gedet_meta.type == "ppc":
        if gedet_meta.name == "P00664B":
            gedet = P00664B(gedet_meta, registry=registry, **kwargs)
        else:
            gedet = PPC(gedet_meta, registry=registry, **kwargs)

    elif gedet_meta.type == "bege":
        gedet = BEGe(gedet_meta, registry=registry, **kwargs)

    elif gedet_meta.type == "icpc":
        if gedet_meta.name == "V07646A":
            gedet = V07646A(gedet_meta, registry=registry, **kwargs)
        elif gedet_meta.name == "V02160A":
            gedet = V02160A(gedet_meta, registry=registry, **kwargs)
        elif gedet_meta.name == "V02162B":
            gedet = V02162B(gedet_meta, registry=registry, **kwargs)
        else:
            gedet = InvertedCoax(gedet_meta, registry=registry, **kwargs)

    elif gedet_meta.type == "coax":
        gedet = SemiCoax(gedet_meta, registry=registry, **kwargs)

    return gedet
