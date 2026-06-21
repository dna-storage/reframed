"""
Minimal encode -> decode round-trip example using the reFrameD library.

Run from the repo root after installing:
    pip install -e .
    python examples/quickstart/quickstart.py
"""

from io import BytesIO
from dnastorage.arch.builder import ReedSolomon_Base4_Pipeline
from dnastorage.util.packetizedfile import ReadPacketizedFilestream, WritePacketizedFilestream

PIPELINE_PARAMS = dict(
    blockSizeInBytes=160,
    strandSizeInBytes=16,
    primer5='CGCGATCGAT',
    primer3='ATCGATCGCG',
    outerECCStrands=10,
    inner_ECC=0,
    using_DNA_consolidator=False,
)


def encode(data: bytes):
    pf = ReadPacketizedFilestream(BytesIO(data))
    pipe = ReedSolomon_Base4_Pipeline(pf, **PIPELINE_PARAMS)
    strands = [s for block in pipe for s in block]
    hdr = pipe.encode_header_data()
    return strands, hdr


def decode(strands, hdr, data_len: int) -> bytes:
    buf = BytesIO()
    pf = WritePacketizedFilestream(buf, data_len, 0)
    pipe = ReedSolomon_Base4_Pipeline(pf, **PIPELINE_PARAMS)
    pipe.decode_header_data(hdr)
    for s in strands:
        pipe.decode(s)
    pipe.final_decode()
    buf.seek(0)
    return buf.read(data_len)


if __name__ == "__main__":
    data = b"Hello, DNA storage! This message is encoded into synthetic DNA strands."

    print(f"Original message ({len(data)} bytes): {data.decode()}\n")

    strands, hdr = encode(data)
    print(f"Encoded to {len(strands)} DNA strand(s). First 3 strands:")
    for s in strands[:3]:
        print(f"  index={s.index_ints}  seq={s.dna_strand[:40]}...")

    recovered = decode(strands, hdr, len(data))
    assert recovered == data, "Decoded data does not match original!"
    print(f"\nDecoded successfully: {recovered.decode()}")
