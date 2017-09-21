import sys
import os
sys.argv = sys.argv[sys.argv.index("--"):]
os.chdir(os.path.dirname(__file__))
