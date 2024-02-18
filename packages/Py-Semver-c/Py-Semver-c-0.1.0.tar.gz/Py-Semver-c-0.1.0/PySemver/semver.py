import re
from typing import Any, Optional, Self

from . import exceptions
from . import semver_utils


class SemabticVersion:
    r"""
    Senabtic Version 2.0.0
    https://semver.org/

    This class can be used to represent version numbers or compare two versions.

    An valid version is shown below:
    0.1.0-0p0.0+date-20240207.commit-0000000.publisher-char46
    x.y.z-prerelease+buildmetadata

    An valid version must be matched with these regular expression:
    These two RegEx is equivalent.
        This RegEx with named groups, can used on PCRE, Python and Go:
          r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        This RegEx with numbered capture groups, can used on ECMA Script, PCRE, Python and Go:
          r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'

    The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC 2119.
    See also: https://tools.ietf.org/html/rfc2119
    """

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        pre_release: Optional[str] = None,
        build_matedata: Optional[str] = None,
    ) -> None:
        """
        This method is used to create a new version.

        Parameters
        ----------
        major : int
            The major version number, it MUST be a non-negative integer and MUST NOT contain leading zeros.
        minor : int
            The minor version number, it MUST be a non-negative integer and MUST NOT contain leading zeros.
        patch : int
            The patch version number, it MUST be a non-negative integer and MUST NOT contain leading zeros.
        pre_release : Optional[str] = None
            The pre-release version.
        build_matedata : Optional[str] = None
            The build metadata.
            The two versions are equal if only the build metadata is different.
        """
        self.major: int = semver_utils.version_core_check(major, "Major")
        self.minor: int = semver_utils.version_core_check(minor, "Minor")
        self.patch: int = semver_utils.version_core_check(patch, "Patch")
        self.pre_release: Optional[__PreRelease] = (
            _ if (_ := __PreRelease(pre_release)) else None
        )
        self.build_matedata: Optional[str] = (
            _ if (_ := semver_utils.build_matedata_check(build_matedata)) else None
        )

    @classmethod
    def init(cls, version: Any) -> Self:
        """
        This method is used to create a new version from a string.

        Parameters
        ----------
        version : Any
            The version as a string.

        Returns
        -------
        Self
            A new version.

        Raises
        ------
        VersionValueError:
            If the version is empty.
            If the version is not a string.
            The version is not valid.
        """
        if not version:
            raise exceptions.VersionValueError("Version is empty")
        if isinstance(version, str):
            raise exceptions.VersionValueError("Version is not a string")
        pattern = re.compile(
            r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        )
        groups = pattern.match(version)
        if not groups:
            raise exceptions.VersionValueError("Version is not valid")
        SemVer = cls(
            major=int(groups["major"]),
            minor=int(groups["minor"]),
            patch=int(groups["patch"]),
            pre_release=groups["prerelease"],
            build_matedata=groups["buildmetadata"],
        )
        return SemVer

    def __repr__(self) -> str:
        return f"<Senabtic Version 2.0.0 [{self.major}.{self.minor}.{self.patch}-{repr(self.pre_release)}+{self.build_matedata}>"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}-{str(self.pre_release)}+{self.build_matedata}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return False
        if (self.pre_release is not None) and (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        ):
            return True
        return False

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return False
        if self.major < other.major:
            return True
        if self.major == other.major and self.minor < other.minor:
            return True
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch < other.patch
        ):
            return True
        if (self.pre_release is not None) and (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release < other.pre_release
        ):
            return True
        return False

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return False
        if self.major > other.major:
            return True
        if self.major == other.major and self.minor > other.minor:
            return True
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch > other.patch
        ):
            return True
        if (self.pre_release is not None) and (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release > other.pre_release
        ):
            return True
        return False

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return True
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        ):
            return False
        return True

    def __le__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return False
        if self.__lt__(other) or self.__eq__(other):
            return True
        return False

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, SemabticVersion):
            return False
        if self.__gt__(other) or self.__eq__(other):
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __bool__(self) -> bool:
        if (
            self.major == 0
            and self.minor == 0
            and self.patch == 0
            and (self.pre_release == "" or self.pre_release is None)
            and (self.build_matedata == "" or self.build_matedata is None)
        ):
            return False
        return True


class __PreRelease:

    def __init__(self, pre_release: Optional[str]) -> None:
        self.pre_version = semver_utils.pre_release_check(pre_release)

    def __repr__(self) -> str:
        return self.pre_version

    def __str__(self) -> str:
        return self.pre_version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return False
        if self.pre_version == other.pre_version:
            return True
        return False

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return False
        if self.pre_version < other.pre_version:
            return True
        return False

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return False
        if self.pre_version > other.pre_version:
            return True
        return False

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return True
        if self.pre_version == other.pre_version:
            return False
        return True

    def __le__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return False
        if self.__lt__(other) or self.__eq__(other):
            return True
        return False

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, __PreRelease):
            return False
        if self.__gt__(other) or self.__eq__(other):
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __bool__(self) -> bool:
        if self.pre_version == "":
            return False
        return True
