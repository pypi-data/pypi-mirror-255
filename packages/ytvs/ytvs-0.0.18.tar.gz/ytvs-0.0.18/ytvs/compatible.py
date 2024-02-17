import re

try:
    import urllib.error as compat_urllib_error
except ImportError:  # Python 2
    import urllib2 as compat_urllib_error


# Pythons disagree on the type of a pattern (RegexObject, _sre.SRE_Pattern, Pattern, ...?)
COMPATIBLE_RE_PATTERN = type(re.compile(''))
# and on the type of a match
COMPATIBLE_RE_MATCH = type(re.match('a', 'a'))


__all__ = [
    compat_urllib_error,
    COMPATIBLE_RE_PATTERN,
    COMPATIBLE_RE_MATCH
]