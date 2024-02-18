"""Thin OS compatability helper."""
import os
import platform

EX_OK = os.EX_OK if platform.system() in ["Linux"] else 0
EX_DATAERR = os.EX_DATAERR if platform.system() in ["Linux"] else 65
EX_SOFTWARE = os.EX_SOFTWARE if platform.system() in ["Linux"] else 70
