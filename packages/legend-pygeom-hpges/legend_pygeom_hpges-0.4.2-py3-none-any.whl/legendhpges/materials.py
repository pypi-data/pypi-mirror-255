"""LEGEND HPGe material descriptions for use in geometries."""

from __future__ import annotations

import math

from pint import Quantity
from pyg4ometry import geant4 as g4

from .registry import default_g4_registry
from .registry import default_units_registry as u

# source: NIST
ge70 = g4.Isotope("Ge70", 32, 70, 69.924)
ge72 = g4.Isotope("Ge72", 32, 72, 71.922)
ge73 = g4.Isotope("Ge73", 32, 73, 72.923)
ge74 = g4.Isotope("Ge74", 32, 74, 73.921)
ge76 = g4.Isotope("Ge76", 32, 76, 75.921)

natge_isotopes: dict = {
    ge70: 0.2057,
    ge72: 0.2745,
    ge73: 0.0775,
    ge74: 0.3650,
    ge76: 0.0773,
}
"""Isotopic composition of natural germanium.

Source: `NIST <https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Ge>`_.
"""

n_avogadro: Quantity = 6.02214076e23 * u("1/mol")
natge_density_meas: Quantity = 5.3234 * u("g/cm^3")
"""Measured density of natural germanium at room temperature."""


def _number_density_theo() -> Quantity:
    """Calculate the theoretical number density of germanium.

    At room temperature, starting from the measured atomic radius.
    """
    r_ge = 0.122 * u("nm")
    a = 8 * r_ge / math.sqrt(3)
    return (8 / a**3).to("cm^-3")


def _number_density_meas() -> Quantity:
    """Calculate the measured number density of germanium.

    At room temperature, starting from the measured mass density of natural
    germanium.
    """
    a_eff = 0
    for iso, frac in natge_isotopes.items():
        a_eff += iso.a * u("g/mol") * frac
    return n_avogadro * natge_density_meas / a_eff


def _make_natural_germanium() -> g4.MaterialCompound:
    """Natural germanium material builder."""
    enrge_name = "NaturalGermanium"

    if enrge_name not in default_g4_registry.materialDict:
        enrge = g4.ElementIsotopeMixture(enrge_name, "NatGe", len(natge_isotopes))

        for iso, frac in natge_isotopes.items():
            enrge.add_isotope(iso, frac)

        matenrge = g4.MaterialCompound(
            enrge_name, natge_density_meas.m, 1, default_g4_registry
        )
        matenrge.add_element_massfraction(enrge, 1)
    else:
        matenrge = default_g4_registry.materialDict[enrge_name]
    return matenrge


def enriched_germanium_density(ge76_fraction: float = 0.92) -> float:
    """Calculate the density of enriched germanium.

    Parameters
    ----------
    ge76_fraction
        fraction of Ge76 atoms.

    Starting from the measured density of natural germanium at room
    temperature.
    """
    m_eff = (ge76.a * ge76_fraction + ge74.a * (1 - ge76_fraction)) * u("g/mol")
    return (_number_density_meas() * m_eff / n_avogadro).to("g/cm^3")


def make_enriched_germanium(ge76_fraction: float = 0.92) -> g4.MaterialCompound:
    """Enriched germanium material builder.

    Note
    ----
    The isotopic composition is approximated as a mixture of Ge76 and Ge74.

    Parameters
    ----------
    ge76_fraction
        fraction of Ge76 atoms.
    """
    enrge_name = f"EnrichedGermanium{ge76_fraction:.3f}"

    if enrge_name not in default_g4_registry.materialDict:
        enrge = g4.ElementIsotopeMixture(enrge_name, "EnrGe", 2)
        enrge.add_isotope(ge74, 1 - ge76_fraction)
        enrge.add_isotope(ge76, ge76_fraction)

        matenrge = g4.MaterialCompound(
            enrge_name,
            enriched_germanium_density(ge76_fraction).to("g/cm^3").m,
            1,
            default_g4_registry,
        )
        matenrge.add_element_massfraction(enrge, 1)
    else:
        matenrge = default_g4_registry.materialDict[enrge_name]
    return matenrge


natural_germanium: g4.MaterialCompound = _make_natural_germanium()
enriched_germanium: g4.MaterialCompound = make_enriched_germanium()
