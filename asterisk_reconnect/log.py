import logging
from logging.config import dictConfig


def config_logging(logger):
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {},
        'formatters': {
            'verbose': {
                'format':
                '%(asctime)s %(module)s %(process)d %(thread)d %(levelname)s  %(message)s'
            },
            'timed': {
                'format': '%(asctime)s %(module)s %(levelname)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'syslog': {
                'format': '%(name)s (%(process)d): %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'null': {
                'class': 'logging.NullHandler'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'console-timed': {
                'class': 'logging.StreamHandler',
                'formatter': 'timed'
            },
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
                'filename': logger['log_file'],
            },
            'file-timed': {
                'class': 'logging.FileHandler',
                'formatter': 'timed',
                'filename': logger['log_file'],

            },
            'file-rotate': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'simple',
                'filename': logger['log_file'],
                'when': logger['rotate_at'],
                'interval': logger['rotate_interval'],
                'backupCount': logger['backup_count']
            },
            'file-timed-rotate': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'timed',
                'filename': logger['log_file'],
                'when': logger['rotate_at'],
                'interval': logger['rotate_interval'],
                'backupCount': logger['backup_count']
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'formatter': 'syslog',
            }
        },
        'loggers': {
            logger['log_name']: {
                'handlers': logger['log_handlers'].split(','),
                'level': logger['log_level'],
                'propagate': True,
            }
        }
    })

    return logging.getLogger(logger['log_name'])
