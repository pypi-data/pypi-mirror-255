#/bin/bash
rm pyrt_lib_rasmusklitgaard/helpers.py
rm pyrt_lib_rasmusklitgaard/patient.py
rm pyrt_lib_rasmusklitgaard/lkb_ntcp.py
rm pyrt_lib_rasmusklitgaard/select_structures.py
rm dist/*
cp ../helpers.py ../patient.py ../lkb_ntcp.py ../select_structures.py pyrt_lib_rasmusklitgaard
/usr/bin/python3.10 -m build
