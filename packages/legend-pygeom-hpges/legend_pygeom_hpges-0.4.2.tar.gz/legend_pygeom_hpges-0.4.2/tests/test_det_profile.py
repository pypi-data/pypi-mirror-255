from __future__ import annotations

import pathlib

import pytest
from legendmeta import TextDB
from legendtestdata import LegendTestData
from pyg4ometry import geant4

from legendhpges import (
    P00664B,
    PPC,
    V02160A,
    V02162B,
    V07646A,
    BEGe,
    InvertedCoax,
    SemiCoax,
    make_hpge,
)
from legendhpges.materials import natural_germanium

reg = geant4.Registry()
configs = TextDB(pathlib.Path(__file__).parent.resolve() / "configs")


@pytest.fixture(scope="session")
def test_data_configs():
    ldata = LegendTestData()
    ldata.checkout("5f9b368")
    return ldata.get_path("legend/metadata/hardware/detectors/germanium/diodes")


def test_icpc(test_data_configs):
    InvertedCoax(
        test_data_configs + "/V99000A.json", material=natural_germanium, registry=reg
    )


def test_bege(test_data_configs):
    BEGe(test_data_configs + "/B99000A.json", material=natural_germanium, registry=reg)


def test_ppc(test_data_configs):
    PPC(test_data_configs + "/P99000A.json", material=natural_germanium, registry=reg)


def test_semicoax(test_data_configs):
    SemiCoax(
        test_data_configs + "/C99000A.json", material=natural_germanium, registry=reg
    )


def test_v07646a():
    V07646A(configs.V07646A, material=natural_germanium, registry=reg)


def test_p00664p():
    P00664B(configs.P00664B, material=natural_germanium, registry=reg)


def test_v02162b():
    V02162B(configs.V02162B, material=natural_germanium, registry=reg)


def test_v02160a():
    V02160A(configs.V02160A, material=natural_germanium, registry=reg)


def test_make_icpc(test_data_configs):
    gedet = make_hpge(test_data_configs + "/V99000A.json")
    assert isinstance(gedet, InvertedCoax)


def test_make_bege(test_data_configs):
    gedet = make_hpge(test_data_configs + "/B99000A.json")
    assert isinstance(gedet, BEGe)


def test_make_ppc(test_data_configs):
    gedet = make_hpge(test_data_configs + "/P99000A.json")
    assert isinstance(gedet, PPC)


def test_make_semicoax(test_data_configs):
    gedet = make_hpge(test_data_configs + "/C99000A.json")
    assert isinstance(gedet, SemiCoax)


def make_v07646a():
    gedet = make_hpge(configs.V07646A)
    assert isinstance(gedet, V07646A)


def test_make_p00664b():
    gedet = make_hpge(configs.P00664B)
    assert gedet.mass
    assert isinstance(gedet, P00664B)


def test_make_v02162b():
    gedet = make_hpge(configs.V02162B)
    assert gedet.mass
    assert isinstance(gedet, V02162B)


def test_make_v02160a():
    gedet = make_hpge(configs.V02160A)
    assert gedet.mass
    assert isinstance(gedet, V02160A)


def test_null_enrichment():
    metadata = configs.V07646A
    metadata.production.enrichment = None
    make_hpge(metadata, registry=reg, material=natural_germanium, name="my_gedet")
