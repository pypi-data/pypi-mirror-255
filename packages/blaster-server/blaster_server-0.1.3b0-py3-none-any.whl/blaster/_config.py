from os import environ
import sys
import os
import json
import inspect
# NOTE: don't import anything from blaster library,
# they may depend on config and won't load correctly.
# keep it isolated as much as possible
from . import env
from .env import IS_DEV, IS_PROD, IS_STAGING, \
    IS_STAGING_DEV, IS_TEST, IS_TEST_LOCAL

_this_ = sys.modules[__name__]


class Config:
    _config = None
    frozen_keys = None

    def __init__(self):
        self.frozen_keys = {k: v for k, v in vars(env).items() if not k.startswith("_")}
        self._config = dict(self.frozen_keys)

    def load(self, *paths):
        import yaml
        for path in paths or ["./"]:
            path = os.path.join(
                os.path.dirname(inspect.stack()[1][1]),  # caller file, called once usually, so no performance impact on app
                path
            ) if not path.startswith("/") else path
            config_files = []
            if(os.path.isfile(path)):
                config_files = [path]
            else:
                config_files.append(os.path.join(path, "app.yaml"))
                if(IS_DEV):  # DEV/LOCAL ENVIRONMENT
                    config_files.append(os.path.join(path, "dev.yaml"))
                    if(IS_TEST):
                        config_files.append(os.path.join(path, "test.yaml"))
                        if(IS_TEST_LOCAL):
                            config_files.append(os.path.join(path, "test_local.yaml"))
                elif(IS_PROD):  # PROD ENVIRONMENT
                    config_files.append(os.path.join(path, "prod.yaml"))
                    config_files.append(os.path.join(path, "prod.secrets.yaml"))
                    if(IS_STAGING):
                        config_files.append(os.path.join(path, "staging.yaml"))
                        config_files.append(os.path.join(path, "staging.secrets.yaml"))
                        if(IS_STAGING_DEV):
                            config_files.append(os.path.join(path, "staging.dev.yaml"))
                            config_files.append(os.path.join(path, "staging.dev.secrets.yaml"))
            for f in config_files:
                if(not os.path.isfile(f)):
                    continue
                print("Loading config file: ", f)
                for k, v in yaml.safe_load(open(f).read()).items():
                    self.set(k, v)

        self.__getattr__ = self._getattr_

    def set(self, key, value):
        if(self.frozen_keys.get(key) is not None):
            return
        self._config[key] = value

    def _getattr_(self, key):
        val = self._config.get(key, _this_)
        if(val is _this_):
            if(not self._config.get("BLASTER_FORK_ID")):  # None or 0
                caller_frame = inspect.stack()[1]
                if(not caller_frame[1].startswith("<frozen")):  # <frozen importlib._bootstrap>
                    print("MISSING CONFIG Key#: {} {}:{}".format(key, caller_frame[1], caller_frame[2]))
            return None
        return val


# hack: customized config module,
# that doesn't crash for missing config variables,
# they will be just None.
config = Config()

# more variables from env
if(gcloud_credential_file := environ.get("GOOGLE_APPLICATION_CREDENTIALS")):
    try:
        config.set("GCLOUD_CREDENTIALS", json.loads(open(gcloud_credential_file).read()))
    except Exception as ex:
        print(ex)

# BLASTER SPECIFIC CONFIGS, that can be overridden
config.set("BLASTER_HTTP_TOOK_LONG_WARN_THRESHOLD", 5000)
config.set("MONGO_WARN_MAX_RESULTS_RATE", 1000)  # can scan at a max of 1000 / sec
config.set("MONGO_MAX_RESULTS_AT_HIGH_SCAN_RATE", 30000)  # cannot scan more than this at high scan rate
config.set("MONGO_WARN_MAX_QUERY_RESPONSE_TIME_SECONDS", 3)  # cannot take more than 3 seconds


# Logging basics
