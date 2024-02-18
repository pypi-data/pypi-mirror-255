
import warnings

__author__ = ["Benjamin Fuchs"]
__copyright__ = "Copyright 2022, German Aerospace Center (DLR)"
__credits__ = [
    "Felix Nitsch",
    "Jan Buschmann",
]

__license__ = "MIT"
__maintainer__ = "Benjamin Fuchs"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

HAS_IOPROVENANCE = True
try:
    import ioprovenance
except ImportError:
    HAS_IOPROVENANCE = False

ALLOWED_ATTRS = ['requested_metadata_format', 'error_msg']


class MissingMetaFormatProxy:
    def __init__(self, requested_metadata_format):
        self.error_msg = []
        if not HAS_IOPROVENANCE:
            self.error_msg.append("ioProvenance is not installed. This library is needed to process meta information. Please install ioprovenance.")
        if requested_metadata_format is not None:
            self.error_msg.append(f'Unknown meta format "{requested_metadata_format}" requested. Please specify a meta data format supported by ioprovenance via the command line parameter "-m".')
        self.error_msg = '\n    '+'\n    Also:\n    '.join(self.error_msg)

    def __setattr__(self, k, v):
        if k in ALLOWED_ATTRS:
            super().__setattr__(k, v)
        else:
            warnings.warn(self.error_msg)
    
    def __getattribute__(self, k):
        if k in ALLOWED_ATTRS:
            return super().__getattribute__(k)

        raise AttributeError(self.error_msg)

    def type(self):
        return 'missing'
