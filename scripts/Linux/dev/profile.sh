#!/bin/bash
blender/blender --background --python Writing3D/samples/performance.py
gprof2dot -f pstats Writing3D/samples/profile.out | dot -Tpng -o profile.png
feh profile.png
