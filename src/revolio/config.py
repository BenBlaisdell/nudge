import abc
import json
import logging
import os
import re
import time

from cached_property import threaded_cached_property
import ruamel.yaml as ryaml


_log = logging.getLogger(__name__)


class ConfigService(metaclass=abc.ABCMeta):

    S3_CONFIG_URI = 'S3_CONFIG_URI'

    @abc.abstractmethod
    def ENV_VAR_PREFIX(self):
        return 'RV'

    def __init__(self, s3):
        self._s3 = s3

    def _get_env_var_name(self, key):
        return f'{self.ENV_VAR_PREFIX}_{key}'

    def _get_env_var(self, key):
        return json.loads(os.environ[self._get_env_var_name(key)])

    @threaded_cached_property
    def _config(self):
        return ryaml.load(self._raw_config, ryaml.Loader)

    @threaded_cached_property
    def _raw_config(self):
        s3_config_uri = self._get_env_var(ConfigService.S3_CONFIG_URI)

        while True:
            _log.info(f'Fetching S3 config: {s3_config_uri}')
            try:
                return self._s3.get_object(**_parse_s3_uri(s3_config_uri))['Body']
            except Exception as e:
                _log.warning(f'Error fetching S3 config: {e}')
                time.sleep(5)

    def __getitem__(self, key):
        return self._config[key]


_s3_uri_re = re.compile(r'\As3://(?P<Bucket>.*?)/(?P<Key>.*)\Z')


def _parse_s3_uri(uri):
    return _s3_uri_re.match(uri).groupdict()
