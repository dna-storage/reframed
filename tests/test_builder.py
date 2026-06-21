"""Tests for dnastorage.arch.builder — check_required() and pipeline construction."""

import pytest
from io import BytesIO

from dnastorage.arch.builder import (
    ReedSolomon_Base4_Pipeline,
    Basic_Hedges_Pipeline,
    Fountain_Base4_Pipeline,
    Fountain_Hedges_Pipeline,
)
from dnastorage.exceptions import PipeLineConstructionError
from dnastorage.util.packetizedfile import ReadPacketizedFilestream

_BASE_PARAMS = dict(
    blockSizeInBytes=160,
    strandSizeInBytes=16,
    primer5='CGCGATCGAT',
    primer3='ATCGATCGCG',
    outerECCStrands=10,
    inner_ECC=0,
    using_DNA_consolidator=False,
)

_HEDGES_PARAMS = dict(
    blockSizeInBytes=160,
    strandSizeInBytes=16,
    hedges_rate=0.5,
    dna_length=300,
    crc_type='strand',
    reverse_payload=False,
    primer5='CGCGATCGAT',
    primer3='ATCGATCGCG',
    outerECCStrands=10,
    using_DNA_consolidator=False,
)


def _pf(size=160):
    return ReadPacketizedFilestream(BytesIO(b'x' * size))


class TestCheckRequired:
    def test_rs_base4_raises_on_missing_block_size(self):
        params = {k: v for k, v in _BASE_PARAMS.items() if k != 'blockSizeInBytes'}
        with pytest.raises(PipeLineConstructionError, match='blockSizeInBytes'):
            ReedSolomon_Base4_Pipeline(_pf(), **params)

    def test_rs_base4_raises_on_missing_strand_size(self):
        params = {k: v for k, v in _BASE_PARAMS.items() if k != 'strandSizeInBytes'}
        with pytest.raises(PipeLineConstructionError, match='strandSizeInBytes'):
            ReedSolomon_Base4_Pipeline(_pf(), **params)

    def test_rs_base4_raises_on_no_kwargs(self):
        with pytest.raises(PipeLineConstructionError):
            ReedSolomon_Base4_Pipeline(_pf())

    def test_fountain_base4_raises_on_missing_required(self):
        with pytest.raises(PipeLineConstructionError):
            Fountain_Base4_Pipeline(_pf())

    def test_hedges_raises_on_missing_hedges_rate(self):
        params = {k: v for k, v in _HEDGES_PARAMS.items() if k != 'hedges_rate'}
        with pytest.raises(PipeLineConstructionError, match='hedges_rate'):
            Basic_Hedges_Pipeline(_pf(), **params)

    def test_hedges_raises_on_missing_crc_type(self):
        params = {k: v for k, v in _HEDGES_PARAMS.items() if k != 'crc_type'}
        with pytest.raises(PipeLineConstructionError, match='crc_type'):
            Basic_Hedges_Pipeline(_pf(), **params)

    def test_rs_base4_accepts_valid_params(self):
        # Should not raise
        pipe = ReedSolomon_Base4_Pipeline(_pf(), **_BASE_PARAMS)
        assert pipe is not None

    def test_fountain_base4_accepts_valid_params(self):
        params = dict(_BASE_PARAMS)
        params.pop('inner_ECC', None)
        params['outerECCStrands'] = 20
        pipe = Fountain_Base4_Pipeline(_pf(), **params)
        assert pipe is not None
