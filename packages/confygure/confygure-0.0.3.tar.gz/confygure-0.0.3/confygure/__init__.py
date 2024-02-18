import logging
import logging.config
import os
import yaml

__config = {}
__setup = {
        'configure_logger': (),
        'config_files': ['config.yml']
        }


def setup(files: tuple | list | None = None, logger: tuple | None = None):
    '''Configure confygure.

    :param files: Tuple or list of configuration files. The first file that
                  exists will be used. Setting this to `None` will not modify
                  the default. The default is `('config.yml')`.
    :param logger: Tuple or list specifying the patch to a log level
                   configuration for the root logger.
    '''
    if files is not None:
        if type(files) not in (list, tuple):
            raise Exception('Configuration files must be a tuple or list')
        __setup['config_files'] = [os.path.expanduser(f) for f in files]
    if logger is not None:
        __setup['configure_logger'] = logger
    return __setup


def configuration_file():
    '''Find the best match for the configuration file.  The configuration file
    locations taken into consideration can be configured using `setup()`.

    :return: configuration file name or None
    '''
    for filename in __setup['config_files']:
        if os.path.isfile(filename):
            return filename


def update_configuration(filename: str | None = None):
    '''Update configuration from file.
    If no filename is specified, the best match from the files configured via
    `setup()` is being used.
    '''
    cfgfile = filename or configuration_file()
    if not cfgfile:
        return {}
    with open(cfgfile, 'r') as f:
        cfg = yaml.safe_load(f)
    globals()['__config'] = cfg

    # update logger
    logger_config = __setup['configure_logger']
    if logger_config:
        loglevel = (config(*logger_config) or 'INFO').upper()
        logging.root.setLevel(loglevel)
        logging.info('Updated configuration from %s', cfgfile)
        logging.info('Log level set to %s', loglevel)

    return cfg


def config(*args, allow_empty=True):
    '''Get a specific configuration value or the whole configuration, loading
    the configuration file if it was not before.

    :param key: optional configuration key to return
    :type key: string
    :return: dictionary containing the configuration or configuration value
    '''
    cfg = __config or update_configuration()
    for key in args:
        if cfg is None:
            if allow_empty:
                return
            raise KeyError(f'Missing configuration key {args}')
        cfg = cfg.get(key)
    return cfg
