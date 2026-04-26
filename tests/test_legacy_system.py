# -*- coding: utf-8 -*-
"""
tests/test_legacy_system.py

Legacy system-level tests originally from new_tests/system_test.py.

The original file used ``dnastorage.system.header`` and ``dnastorage.system.dnafile``
which have been superseded by ``dnastorage.system.header_class`` and
``dnastorage.system.pipeline_dnafile``.  Tests that can be migrated to the new API
are kept active; others are skipped.
"""

import pytest
import unittest


@pytest.mark.skip(
    reason=(
        "dnastorage.system.header and dnastorage.system.dnafile have been "
        "removed; use dnastorage.system.header_class and "
        "dnastorage.system.pipeline_dnafile instead."
    )
)
class header_py_test(unittest.TestCase):
    """encode_file_header / decode_file_header tests – module removed."""
    def test_header(self):
        pass


@pytest.mark.skip(
    reason="dnastorage.system.formats API partially changed; formats tests live in test_codec_components.py"
)
class formats_py_test(unittest.TestCase):
    """formats tests – covered by TestFormatsRegistry in test_codec_components.py."""
    def test_formats(self):
        pass

    def test_format_by_abbrev(self):
        pass


@pytest.mark.skip(
    reason=(
        "dnastorage.system.dnafile (DNAFile, SegmentedWriteDNAFile) has been "
        "removed; pipeline-based API lives in dnastorage.system.pipeline_dnafile."
    )
)
class dnafile_py_test(unittest.TestCase):
    """DNAFile roundtrip tests – module removed."""
    def test_dnafile(self):
        pass


@pytest.mark.skip(
    reason="SegmentedWriteDNAFile / SegmentedReadDNAFile have been removed from the codebase."
)
class segmentedfile_py_test(unittest.TestCase):
    """Segmented DNA file tests – module removed."""
    def test_dnafile(self):
        pass


if __name__ == "__main__":
    unittest.main()
