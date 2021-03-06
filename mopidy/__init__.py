import sys
if not (2, 6) <= sys.version_info < (3,):
    sys.exit(u'Mopidy requires Python >= 2.6, < 3')

from subprocess import PIPE, Popen

VERSION = (0, 4, 0)

def get_git_version():
    process = Popen(['git', 'describe'], stdout=PIPE, stderr=PIPE)
    if process.wait() != 0:
        raise Exception('Execution of "git describe" failed')
    version = process.stdout.read().strip()
    if version.startswith('v'):
        version = version[1:]
    return version

def get_plain_version():
    return '.'.join(map(str, VERSION))

def get_version():
    try:
        return get_git_version()
    except Exception:
        return get_plain_version()

class MopidyException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(MopidyException, self).__init__(message, *args, **kwargs)
        self._message = message

    @property
    def message(self):
        """Reimplement message field that was deprecated in Python 2.6"""
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

class SettingsError(MopidyException):
    pass

class OptionalDependencyError(MopidyException):
    pass

from mopidy import settings as default_settings_module
from mopidy.utils.settings import SettingsProxy
settings = SettingsProxy(default_settings_module)
