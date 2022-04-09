import os
import subprocess


def git_suffix(fname):
    """
    :returns: `<short git hash>` if Git repository found
    """
    try:
        gh = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=open(os.devnull, 'w')).strip()
        gh = "-git" + gh.decode() if gh else ''
    except Exception:
        # trapping everything on purpose; git may not be installed or it
        # may not work properly
        gh = ''

    return gh


__version__ = '0.0.1'
__version__ += git_suffix(__file__)
