class LibCoveOCDSError(Exception):
    """Base class for exceptions from within this package."""


class OCDSVersionError(LibCoveOCDSError):
    """Raised if the major.minor version matches no supported version."""
