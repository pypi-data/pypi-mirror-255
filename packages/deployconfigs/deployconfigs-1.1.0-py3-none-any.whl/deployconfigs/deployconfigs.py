#
"""
    DeployConfigs

    to lower the pip overhead, I include dj-database-url and dj-cache-url inline
"""
import configparser
import os
import urllib.parse as urlparse
from pathlib import Path
from typing import Union, Optional, Dict as Dict

BOOLEAN_STATES = dict(configparser.RawConfigParser.BOOLEAN_STATES)  # force copy

DEFAULT_ENV = 'DEPLOY_CONF'
DEFAULT_SECTION = 'deploy'
TEST_SECTION = 'TEST'


# TODO: add JsonLogger
# TODO: add WatchingFileHandler
# TODO: add log configurator

class DeployConfigException(Exception):
    pass


class ConfigIsRequiredButNotOverridden(DeployConfigException):
    pass


class Undefined(object):
    pass


class DeployConfigs(object):
    REQUIRED = '__REQUIRED__'

    def __init__(
            self, *,
            section=DEFAULT_SECTION,
            extra_conf_file: Union[str, Path] = None,
            extra_conf_file_env=DEFAULT_ENV,
            default_conf_file: Union[str, Path] = None,
            defaults: Dict[str, str] = None,
            configure=True,
    ):
        self.section = section
        self._extra_conf_should_exist = False
        if os.environ.get(extra_conf_file_env, None):
            self._extra_conf_should_exist = True
            self.extra_conf_file = self._to_path(os.environ[extra_conf_file_env])
        else:
            self.extra_conf_file = self._to_path(extra_conf_file)

        self.default_file = self._to_path(default_conf_file)
        if defaults is not None and default_conf_file is not None:
            raise ValueError('Should not pass both defaults and default_conf_file')
        if defaults is None and default_conf_file is None:
            raise ValueError('You should pass one one `defaults` or `default_conf_file`')
        self.ready = False
        self.defaults = defaults
        if defaults:
            for k, v in defaults.items():
                if not isinstance(v, str):
                    raise ValueError(f'Default value for `{k}` is not str')
                if not isinstance(k, str):
                    raise ValueError(f'Config key `{k}` is not str')
        self.overrides = {}
        if configure:
            self.configure()

    def configure(self):
        if self.default_file:
            if not self.default_file.exists():
                raise FileNotFoundError('Config file `{}` not exists'.format(self.default_file))
            cf = configparser.ConfigParser()
            with self.default_file.open() as f:
                cf.read_file(f)
            self.defaults = {k.upper(): v for k, v in cf.items(self.section)}

        if self._extra_conf_should_exist and not self.extra_conf_file.exists():
            raise FileNotFoundError('Extra config file `{}` not exists'.format(self.extra_conf_file))

        if self.extra_conf_file and self.extra_conf_file.exists():
            cf = configparser.ConfigParser()
            with self.extra_conf_file.open() as f:
                cf.read_file(f)
            self.overrides = {k.upper(): v for k, v in cf.items(self.section)}

        self.ready = True

    def _get(self, option, default=REQUIRED, _convert_func=lambda x: x):
        assert option.isupper(), 'Config keys should be uppercase'

        if not self.ready:
            raise RuntimeError('Not configured yet')

        # let environment overwrite what is in\or not in the conf file.
        val = os.environ.get(option, Undefined)
        if val is Undefined and option in self.overrides:
            val = self.overrides[option]
        if val is Undefined:
            if option in self.defaults:
                val = self.defaults[option]
            elif default == self.REQUIRED:
                raise ConfigIsRequiredButNotOverridden(option)
            else:
                val = default
        if val == self.REQUIRED:
            raise ConfigIsRequiredButNotOverridden(option)
        return _convert_func(val)

    def get(self, option, default=REQUIRED):
        return self._get(option, default)

    def get_int(self, option, default=REQUIRED) -> Optional[int]:
        return self._get(option, default, _convert_func=int)

    def get_bool(self, option, default=REQUIRED) -> bool:
        if default not in (True, False, self.REQUIRED):
            raise ValueError('default value for getboolean must be True or False')
        return self._get(option, default, _convert_func=as_boolean)

    def get_path(self, key: str, default: Union[Path, str] = Undefined) -> Optional[Path]:
        value: str = self.get(key) or default
        return self._to_path(value)

    def _to_path(self, value) -> Union[Path, bool]:
        return Path(value).resolve() if isinstance(value, (str, Path)) else value

    def general_dict(self, option, default=REQUIRED):
        url = self.get(option, default=default)
        return self.parse_url(url).__dict__

    def parse_url(self, url, schemes=None, upper=False, clean_path=True):
        if url is None:
            return UrlParseResult()
        url = urlparse.urlparse(url)

        backend = None

        if schemes:
            try:
                backend = schemes[url.scheme]
            except KeyError:
                raise RuntimeError('Unknown scheme `%s`' % url.scheme)

        transport, scheme = None, url.scheme
        if scheme and '+' in scheme:
            transport, scheme = scheme.rsplit('+', 1)

        # Split query strings from path.
        path, query = url.path, url.query
        if '?' in path and not url.query:
            # Handle python 2.6 broken url parsing
            path, query = path.split('?', 1)

        query_dict = dict([((key.upper() if upper else key), ';'.join(val))
                           for key, val in urlparse.parse_qs(query).items()])
        if ',' in url.netloc:
            hostname = port = ''
        else:
            port = url.port or ''
            hostname = url.hostname or ''

        if clean_path:
            if path and path[0] == '/':
                path = path[1:]

        result = UrlParseResult(
            backend=backend,
            transport=transport,
            scheme=scheme,
            netloc=url.netloc,
            username=urlparse.unquote(url.username or ''),
            password=urlparse.unquote(url.password or ''),
            hostname=hostname,
            port=port,
            path=path,
            query=query,
            query_dict=query_dict,
        )
        return result


class UrlParseResult(object):
    backend = transport = scheme = username = password = hostname = port = path = query_dict = None
    netloc = query = fragment = ''

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.__dict__.setdefault('query_dict', {})

    def is_empty(self):
        if len(self.query_dict.keys()) == 0 and len(self.__dict__) == 1:
            return True
        return False

    def __str__(self):
        return repr(self.__dict__)


def as_boolean(val):
    val = BOOLEAN_STATES.get(str(val or '0').lower())
    if val not in [False, True, None]:
        raise ValueError('Cannot interpret value as a boolean')
    return val is True
