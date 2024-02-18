# read version from installed package
from importlib.metadata import version
__version__ = version("crockode")

from .crockode import encode_string, decode_dna