#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Version Module Utils
"""

import re
from typing import Any

from . import exceptions


def version_core_check(value: Any, desc: str = "Version Core") -> int:
    """
    Version Core Check function

    See also: https://semver.org/#spec-item-2
    > A normal version number MUST take the form X.Y.Z where X, Y, and Z are non-negative integers, and MUST NOT contain leading zeroes. X is the major version, Y is the minor version, and Z is the patch version. Each element MUST increase numerically. For instance: 1.9.0 -> 1.10.0 -> 1.11.0.

    Parameters
    ----------
    value: Any
        This parameter from major, minor, patch.
    desc: str, optional
        This parameter is description to build error message.
        Default is 'Version Core', suggested to use 'major', 'minor', 'patch'.

    Returns
    -------
    Literal[0]:
        If value is valid, return itself.

    Raises
    ------
    VersionCoreValueError:
        If value is negative or not integer, raise VersionCoreValueError.
    """
    if isinstance(value, int) or value < 0:
        raise exceptions.VersionCoreValueError(f"{desc} must be non-negative integer")
    return value


def pre_release_check(value: Any) -> str:
    """
    Pre Release Check function

    See also: https://semver.org/#spec-item-9
    > A pre-release version MAY be denoted by appending a hyphen and a series of dot separated identifiers immediately following the patch version. Identifiers MUST comprise only ASCII alphanumerics and hyphens [0-9A-Za-z-]. Identifiers MUST NOT be empty. Numeric identifiers MUST NOT include leading zeroes. Pre-release versions have a lower precedence than the associated normal version. A pre-release version indicates that the version is unstable and might not satisfy the intended compatibility requirements as denoted by its associated normal version. Examples: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7, 1.0.0-x.7.z.92, 1.0.0-x-y-z.--.

    Parameters
    ----------
    value: Any
        This parameter from pre_release.

    Returns
    -------
    str:
        If value is valid, return itself.

    Raises
    ------
    PreReleaseValueError:
        If value is not string.
        If value is not valid.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        raise exceptions.PreReleaseValueError("pre_release must be string")
    pattern = re.compile(
        r"^(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)$"
    )
    if not re.match(pattern, value):
        raise exceptions.PreReleaseValueError("pre_release must be valid")
    return value


def build_matedata_check(value: Any) -> str:
    """
    Build Metadata Check function

    See also: https://semver.org/#spec-item-10
    > Build metadata MAY be denoted by appending a plus sign and a series of dot separated identifiers immediately following the patch or pre-release version. Identifiers MUST comprise only ASCII alphanumerics and hyphens [0-9A-Za-z-]. Identifiers MUST NOT be empty. Build metadata MUST be ignored when determining version precedence. Thus two versions that differ only in the build metadata, have the same precedence. Examples: 1.0.0-alpha+001, 1.0.0+20130313144700, 1.0.0-beta+exp.sha.5114f85, 1.0.0+21AF26D3----117B344092BD.

    Parameters
    ----------
    value: Any
        This parameter from build_metadata.

    Returns
    -------
    str:
        If value is valid, return itself.

    Raises
    ------
    BuildMetadataValueError:
        If value is not string.
        If value is not valid.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        raise exceptions.BuildMetadataValueError("build_metadata must be string")
    pattern = re.compile(r"^(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)$")
    if not re.match(pattern, value):
        raise exceptions.BuildMetadataValueError("build_metadata must be valid")
    return value
