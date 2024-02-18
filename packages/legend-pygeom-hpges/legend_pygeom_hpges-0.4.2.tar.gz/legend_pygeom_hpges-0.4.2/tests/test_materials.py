from __future__ import annotations

import pytest

from legendhpges import materials


def test_number_density_meas():
    assert materials._number_density_meas().to("1/cm^3").m == pytest.approx(
        4.41752e22, rel=1e-3
    )


def test_enriched_ge_density():
    assert materials.enriched_germanium_density(1).to("g/cm^3").m == pytest.approx(
        5.569, rel=1e-3
    )
    assert materials.enriched_germanium_density(0).to("g/cm^3").m == pytest.approx(
        5.422, rel=1e-3
    )


def test_g4_materials():
    assert (
        materials.make_enriched_germanium(0.92).density
        == materials.enriched_germanium_density(0.92).to("g/cm^3").m
    )
    assert (
        materials.natural_germanium.density
        == materials.natge_density_meas.to("g/cm^3").m
    )
