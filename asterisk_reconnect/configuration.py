import configparser
import sys


def build_config(_config_file):
    conf = configparser.ConfigParser()

    if not conf.read(_config_file):
        sys.exit('Configuration file \'%s\' is not valid.' % _config_file)

    config = {}
    config['intervals'] = {}
    config['ami'] = {}
    config['logger'] = {}
    config['clients'] = {}

    try:
        for section in conf.sections():

            if section == 'intervals':
                config['intervals'].update({
                    'check_interval':
                    conf.getint(section, 'check_interval'),
                    'reconnect_interval':
                    conf.getint(section, 'reconnect_interval'),
                    'ping_interval':
                    conf.getint(section, 'ping_interval')
                })

            elif section == 'ami':
                config['ami'].update({
                    'host':
                    conf.get(section, 'host'),
                    'port':
                    conf.getint(section, 'port'),
                    'username':
                    conf.get(section, 'username'),
                    'password':
                    conf.get(section, 'password')
                })

            elif section == 'logger':

                config['logger'].update({
                    'log_file':
                    conf.get(section, 'log_file'),
                    'log_handlers':
                    conf.get(section, 'log_handlers'),
                    'log_level':
                    conf.get(section, 'log_level'),
                    'log_name':
                    conf.get(section, 'log_name'),
                    'rotate_at':
                    conf.get(section, 'rotate_at', fallback="midnight"),
                    'rotate_interval':
                    conf.getint(section, 'rotate_interval', fallback=1),
                    'backup_count':
                    conf.getint(section, 'backup_count', fallback=7)
                })

            else:

                config['clients'].update({
                    section: {
                        'context': conf.get(section, 'context'),
                        'extension': conf.get(section, 'extension'),
                        'uri': conf.get(section, 'uri')
                    }
                })

    except configparser.Error as err:
        print("Cannot parse configuration file. %s" % err)
        sys.exit('Cannot parse configuration file.')

    return config
