from seeq.sdk import *
from seeq.spy import _login


def is_continuation_token_used() -> bool:
    """
    Check if compute API endpoints should use the continuation_token field for pagination. On false, should use the
    old start key increment and deduplicate capsules scheme.

    Returns
    -------
    True if the SDK version is equal to or greater than 63.
    """
    return _login.is_sdk_module_version_at_least(63)


def is_force_calculated_scalars_available() -> bool:
    """
    Check if the force_calculated_scalars parameter is available on the PutScalars endpoint.

    Returns
    -------
    True if the force_calculated_scalars parameter is available on the PutScalars endpoint.
    """
    return 'force_calculated_scalars' in PutScalarsInputV1.attribute_map
