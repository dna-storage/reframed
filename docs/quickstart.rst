Quick Start
===========

Install
-------

Basic library use requires only Python 3.9+ and pip — no MPI, C-shell, or Julia needed:

.. code-block:: bash

   pip install -r requirements.txt
   pip install -e .

For the full simulation environment (conda + MPI), see ``config/README.md``.

Encode and decode in Python
---------------------------

.. code-block:: python

   from io import BytesIO
   from dnastorage.arch.builder import ReedSolomon_Base4_Pipeline
   from dnastorage.util.packetizedfile import ReadPacketizedFilestream, WritePacketizedFilestream

   PARAMS = dict(
       blockSizeInBytes=160, strandSizeInBytes=16,
       primer5='CGCGATCGAT', primer3='ATCGATCGCG',
       outerECCStrands=10, inner_ECC=0,
       using_DNA_consolidator=False,
   )

   data = b"Hello, DNA storage!"

   # Encode
   pf = ReadPacketizedFilestream(BytesIO(data))
   pipe = ReedSolomon_Base4_Pipeline(pf, **PARAMS)
   strands = [s for block in pipe for s in block]
   hdr = pipe.encode_header_data()

   # Decode
   buf = BytesIO()
   pf2 = WritePacketizedFilestream(buf, len(data), 0)
   pipe2 = ReedSolomon_Base4_Pipeline(pf2, **PARAMS)
   pipe2.decode_header_data(hdr)
   for s in strands:
       pipe2.decode(s)
   pipe2.final_decode()
   buf.seek(0)
   assert buf.read(len(data)) == data

A runnable version is at ``examples/quickstart/quickstart.py``.

For more usage patterns see ``tests/test_pipeline_roundtrip.py``.
For the HPC simulation workflow see ``tools/fault_injection.py``.
