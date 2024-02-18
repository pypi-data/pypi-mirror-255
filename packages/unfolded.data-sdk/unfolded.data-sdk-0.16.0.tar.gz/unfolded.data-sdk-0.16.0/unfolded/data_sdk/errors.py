class DataSDKError(Exception):
    """Base exception class."""


class DataFrameParsingError(DataSDKError):
    """Unable to parse DataFrame"""


class UnknownMediaTypeError(DataSDKError):
    """Unknown Media Type"""


class UnknownDatasetNameError(DataSDKError):
    """Unknown Dataset Name"""


class AuthenticationError(DataSDKError):
    """AuthenticationError"""


CREDENTIALS_NOT_WRITABLE_MSG = """\
Credentials directory not writable.
Either make $HOME/.config/unfolded writable or supply another credentials_dir.
"""

REFRESH_TOKEN_SAVED_MSG = """\
Your refresh token has been successfully saved to disk.
Future interactions with the Data SDK on this machine and user via Python or
via the CLI do not need to pass in authentication parameters manually.
"""

NON_ROTATING_TOKEN_WARNING = """\
Warning: a non-rotating refresh token will never expire. Take care to keep this token safe.
"""
