import re
import urllib.parse as urlparse

from deployconfigs.deployconfigs import DeployConfigs, as_boolean

DEFAULT_DATABASE_ENV = 'DATABASE_URL'
DEFAULT_CACHE_ENV = 'CACHE_URL'
DEFAULT_EMAIL_ENV = 'EMAIL_URL'
DEFAULT_STORAGE_ENV = 'STORAGE_URL'

DATABASE_SCHEMES = {
    'postgres': 'django.db.backends.postgresql',
    'postgresql': 'django.db.backends.postgresql',
    'pgsql': 'django.db.backends.postgresql',
    'postgis': 'django.contrib.gis.db.backends.postgis',
    'mysql': 'django.db.backends.mysql',
    'mysql2': 'django.db.backends.mysql',
    'mysqlgis': 'django.contrib.gis.db.backends.mysql',
    'mysql-connector': 'mysql.connector.django',
    'spatialite': 'django.contrib.gis.db.backends.spatialite',
    'sqlite': 'django.db.backends.sqlite3',
    'oracle': 'django.db.backends.oracle',
    'oraclegis': 'django.contrib.gis.db.backends.oracle',
    'redshift': 'django_redshift_backend',
}

CACHE_SCHEMES = {
    'db': 'django.core.cache.backends.db.DatabaseCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'file': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache',
    'uwsgicache': 'uwsgicache.UWSGICache',
    'memcached': 'django.core.cache.backends.memcached.PyLibMCCache',
    'djangopylibmc': 'django_pylibmc.memcached.PyLibMCCache',
    'pymemcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'redis': 'django_redis.cache.RedisCache',
    'hiredis': 'django_redis.cache.RedisCache',
}

EMAIL_SCHEMES = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
    'file': 'django.core.mail.backends.filebased.EmailBackend',
    'memory': 'django.core.mail.backends.locmem.EmailBackend',
    'dummy': 'django.core.mail.backends.dummy.EmailBackend',
    'celery+smtp': 'djcelery_email.backends.CeleryEmailBackend',
    'celery+smtps': 'djcelery_email.backends.CeleryEmailBackend',
}

STORAGE_SCHEMES = {
    'local': 'django.core.files.storage.FileSystemStorage',
    's3': '',
    'asure': '',
}

# Register database, cache, email schemes in URLs.
urlparse.uses_netloc.extend(DATABASE_SCHEMES.keys())
urlparse.uses_netloc.extend(CACHE_SCHEMES.keys())
urlparse.uses_netloc.extend(EMAIL_SCHEMES.keys())
urlparse.uses_netloc.extend(STORAGE_SCHEMES.keys())


class DjangoConfigs(DeployConfigs):

    def database_dict(self, option=DEFAULT_DATABASE_ENV, engine=None, default=None):
        url = self.get(option, default=default)
        # Convert empty string to None
        return self.parse_database_url(url or None, engine=engine)

    def cache_dict(self, option=DEFAULT_CACHE_ENV, default=None):
        url = self.get(option, default=default)
        return self.parse_cache_url(url or default or 'locmem://')

    def email_dict(self, option=DEFAULT_EMAIL_ENV, default=None):
        url = self.get(option, default=default)
        return self.parse_email_url(url or None)

    def storage_dict(self, option=DEFAULT_STORAGE_ENV, default=None):
        url = self.get(option, default=default)
        return self.parse_storage_url(url or None)

    def parse_database_url(self, url, engine=None):
        if url == 'sqlite://:memory:':
            # this is a special case, because if we pass this URL into
            # urlparse, urlparse will choke trying to interpret "memory"
            # as a port number
            return {
                'ENGINE': DATABASE_SCHEMES['sqlite'],
                'NAME': ':memory:',
            }

        # otherwise parse the url as normal
        url = self.parse_url(url, DATABASE_SCHEMES)
        if url.backend is None:
            return {}

        # If we are using sqlite and we have no path, then assume we
        # want an in-memory database (this is the behaviour of sqlalchemy)
        if url.scheme == 'sqlite' and url.path == '':
            url.path = ':memory:'

        # Handle postgres percent-encoded paths.
        netloc = url.netloc
        if '@' in netloc:
            netloc = netloc.rsplit('@', 1)[1]
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        url.hostname = netloc or ''
        if '%2f' in url.hostname.lower():
            url.hostname = url.hostname.replace('%2f', '/').replace('%2F', '/')

        conn_max_age = int(url.query_dict.pop('conn_max_age', 0))

        config = {
            'ENGINE': engine or url.backend,
            'NAME': urlparse.unquote(url.path or ''),
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
            'CONN_MAX_AGE': conn_max_age,
        }

        if url.scheme == 'mysql' and 'ssl-ca' in url.query_dict:
            url.query_dict['ssl'] = {'ca': url.query_dict.pop('ssl-ca')}

        # Support for Postgres Schema URLs
        if 'currentSchema' in url.query_dict and config['ENGINE'] in (
            'django.contrib.gis.db.backends.postgis',
            'django.db.backends.postgresql',
            'django_redshift_backend',
        ):
            url.query_dict['options'] = '-c search_path={}'.format(url.query_dict.pop('currentSchema'))

        # Pass the query string into OPTIONS if any
        if url.query_dict:
            config.setdefault('OPTIONS', {}).update(url.query_dict)
            connect_timeout = config['OPTIONS'].get('connect_timeout')
            if connect_timeout:
                config['OPTIONS']['connect_timeout'] = int(connect_timeout)
        return config

    def parse_cache_url(self, url):
        url = self.parse_url(url, CACHE_SCHEMES, upper=True, clean_path=False)
        config = {
            'BACKEND': url.backend,
        }

        redis_options = {}
        if url.scheme == 'hiredis':
            redis_options['PARSER_CLASS'] = 'redis.connection.HiredisParser'

        # File based
        if not url.netloc:
            if url.scheme in ('memcached', 'pymemcached', 'djangopylibmc'):
                config['LOCATION'] = 'unix:' + url.path

            elif url.scheme in ('redis', 'hiredis'):
                match = re.match(r'.+?(?P<db>\d+)', url.path)
                if match:
                    db = match.group('db')
                    url.path = url.path[:url.path.rfind('/')]
                else:
                    db = '0'
                config['LOCATION'] = 'unix:%s:%s' % (url.path, db)
            else:
                config['LOCATION'] = url.path

        # URL based
        else:
            # Handle multiple hosts
            config['LOCATION'] = ';'.join(url.netloc.split(','))

            if url.scheme in ('redis', 'hiredis'):
                if url.password:
                    redis_options['PASSWORD'] = url.password
                # Specifying the database is optional, use db 0 if not specified.
                db = url.path[1:] or '0'
                config['LOCATION'] = 'redis://%s:%s/%s' % (url.hostname, url.port, db)

        if redis_options:
            config['OPTIONS'] = redis_options

        if url.scheme == 'uwsgicache':
            config['LOCATION'] = config.get('LOCATION') or 'default'

        # Pop special options from cache_args
        # https://docs.djangoproject.com/en/1.10/topics/cache/#cache-arguments
        options = {}
        for key in ('MAX_ENTRIES', 'CULL_FREQUENCY'):
            try:
                val = url.query_dict.pop(key)
                options[key] = int(val)
            except KeyError:
                pass

        if options:
            config.setdefault('OPTIONS', {}).update(options)

        config.update(url.query_dict)

        return config

    def parse_email_url(self, url):
        url = self.parse_url(url, EMAIL_SCHEMES)

        config = {
            'EMAIL_BACKEND': url.backend,
            'EMAIL_FILE_PATH': url.path,
            'EMAIL_HOST_USER': url.username,
            'EMAIL_HOST_PASSWORD': url.password,
            'EMAIL_HOST': url.hostname,
            'EMAIL_PORT': url.port,
            'SERVER_EMAIL': url.query_dict.get('error_from', url.username),
            'DEFAULT_FROM_EMAIL': url.query_dict.get('from', url.username),
            'EMAIL_SCHEME': url.scheme,
            'EMAIL_TRANSPORT': url.transport,
        }

        use_ssl = False
        use_tls = False
        if url.scheme == 'smtps':
            use_tls = True
        if as_boolean(url.query_dict.get('ssl')):
            use_ssl = True
            use_tls = False  # maybe user use smtps://?ssl=True
        elif as_boolean(url.query_dict.get('tls')):
            use_tls = True
        config['EMAIL_USE_SSL'] = use_ssl
        config['EMAIL_USE_TLS'] = use_tls

        if url.transport == 'celery':
            t = config['CELERY_EMAIL_TASK_CONFIG'] = url.query_dict.copy()
            for k in ('ssl', 'tls', 'from', 'error_from'):
                t.pop(k, None)

        return config

    def parse_storage_url(self, url):
        if url.startswith('local'):
            assert url.startswith('local:///'), \
                'please use local:/// to supress the parsing local path as netloc'

        url = self.parse_url(url, STORAGE_SCHEMES)
        config = url.__dict__

        return config

    def allowed_hosts_list(self, option='ALLOWED_HOSTS', default: list = None, sep=',') -> list[str]:
        return self.get_list(option, default=default, sep=sep)


DjangoDeployConfigs = DjangoConfigs
