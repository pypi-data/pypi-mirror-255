class PySemverBaseException(Exception):
    """Base exception for all PySemver exceptions."""


class VersionCoreValueError(PySemverBaseException):
    """Raised when the version core value is invalid."""


class PreReleaseValueError(PySemverBaseException):
    """Raised when the pre-release value is invalid."""


class BuildMetadataValueError(PySemverBaseException):
    """Raised when the build metadata value is invalid."""


class VersionValueError(PySemverBaseException):
    """Raised when the version value is invalid."""
