# -*- coding: utf-8 -*-
"""
tests/test_legacy_codec.py

Legacy codec tests originally from new_tests/codec_test.py.

Several modules these tests relied on (dense, huffman, commafreecodec, LayeredCodec)
have been removed from the current codebase.  Tests for surviving modules are kept
active; tests for removed modules are preserved as documentation but skipped.
"""

from io import BytesIO
from random import randint
import unittest
import pytest

from dnastorage.codec.base_conversion import *


class base_conversion_py_test(unittest.TestCase):
    """conversion test cases."""
    def test_encoding(self):
        for i in range(2**8):
            x = convertFromBase(2, convertBase(2, i, 8))
            assert x == i
            x = convertFromBase(3, convertBase(3, i, 8))
            assert x == i


class binary_py_test(unittest.TestCase):
    """binary codec test cases."""

    def test_rotated_encoding(self):
        from dnastorage.codec.binary import binary_unrotate_decode, binary_rotate_encode
        for i in range(2**8):
            assert binary_unrotate_decode(
                binary_rotate_encode(convertToAnyBase(2, i, 8, symbols=['A', 'C']))
            ) == convertToAnyBase(2, i, 8, symbols=['A', 'C'])


@pytest.mark.skip(reason="dnastorage.codec.dense has been removed from current codebase")
class dense_py_test(unittest.TestCase):
    """dense codec test cases – module removed."""
    def test_dense(self):
        pass


@pytest.mark.skip(reason="dnastorage.codec.huffman has been removed from current codebase")
class huffman_py_test(unittest.TestCase):
    """Huffman table test – module removed."""
    def test_tables_match(self):
        pass


@pytest.mark.skip(reason="dnastorage.codec.huffman_table has been removed from current codebase")
class huffman_table_py_tests(unittest.TestCase):
    """Huffman table creation tests – module removed."""
    def test_dense_16(self):
        pass


class phys_py_tests(unittest.TestCase):
    """Check the logic for adding primers to strands and inserting mid-sequence cut sites."""
    import random

    def test_append_prepend_and_cut(self):
        import random
        from dnastorage.codec.phys import (
            InsertMidSequence, PrependSequence, AppendSequence, AllowAll,
        )
        cut = InsertMidSequence('AGATATAGGG', Policy=AllowAll())
        pre = PrependSequence('TAAAGGAAAAAG', CodecObj=cut, Policy=AllowAll())
        app = AppendSequence('CAAAATATAAAA', CodecObj=pre, Policy=AllowAll())

        match = 0
        for _ in range(10000):
            while True:
                strand = [random.choice('AGCT') for _ in range(100)]
                strand = "".join(strand)
                if 'AGATATAGGG' not in strand:
                    break

            original = strand
            strand = app.encode(strand)

            copy = (
                [random.choice('AGCT') for _ in range(10)]
                + [_ for _ in strand]
                + [random.choice('AGCT') for _ in range(10)]
            )
            copy[random.randint(0, 20)] = random.choice('AGCT')
            copy[random.randint(140, 150)] = random.choice('AGCT')
            copy[random.randint(75, 78)] = random.choice('AGCT')
            copy = "".join(copy)
            new = app.decode(copy)
            if new == original:
                match += 1

        assert match / 10000 * 100 > 70.0


@pytest.mark.skip(reason="dnastorage.codec.commafreecodec has been removed from current codebase")
class commafreecodec_py_tests(unittest.TestCase):
    """Comma-free coding tests – module removed."""
    def test_commafreecodec_no_faults(self):
        pass


@pytest.mark.skip(reason="BlockToStrand has been removed from dnastorage.codec.block in the current codebase")
class block_py_tests(unittest.TestCase):
    """Check the logic for breaking blocks into strands for the inner code."""
    def test_BlockToStrand(self):
        from dnastorage.codec.block import BlockToStrand
        from dnastorage.codec.phys import AllowAll
        b2s = BlockToStrand(20, 80, Policy=AllowAll())
        x = [randint(0, 255) for _ in range(4 * 20)]
        r = b2s.encode([2323, x])
        index, y = b2s.decode([2323, r])
        assert index == 2323
        assert x == y


@pytest.mark.skip(reason="dnastorage.codec.LayeredCodec has been removed from current codebase")
class LayeredCodec_py_tests(unittest.TestCase):
    """LayeredCodec encode/decode test – module removed."""
    def test_layered_encoder(self):
        pass


if __name__ == "__main__":
    unittest.main()
