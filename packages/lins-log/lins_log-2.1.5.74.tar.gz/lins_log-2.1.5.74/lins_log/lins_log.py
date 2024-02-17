import os
import logging.config
import logging
from enum import Enum
from .validacoes import valida_envs


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

def get_environment_variable(key, default=None):
    return os.environ.get(key, default)

def env_to_dinamic_filter(graylog_extra_records, record):
    if graylog_extra_records:
        dados = graylog_extra_records.split(',')
        for item in dados:
            key, value = item.split('=')
            original, default = value.split(':')
            record[key] = get_environment_variable(original, default)
    return record

class LogFilter(logging.Filter):
    def filter(self, record):
        graylog_extra_records = get_environment_variable('GRAYLOG_EXTRA_RECORDS', None)
        record = env_to_dinamic_filter(graylog_extra_records, record)
        record.glf_node = get_environment_variable('GRAYLOG_NODE').lower()
        record.glf_service = get_environment_variable('GRAYLOG_SERVICE').lower()
        record.glf_company = get_environment_variable('GRAYLOG_COMPANY').lower()
        record.glf_application = get_environment_variable('GRAYLOG_APPLICATION').lower()
        record.glf_settings = get_environment_variable('GRAYLOG_SETTINGS').lower()
        record.glf_image = get_environment_variable('GRAYLOG_IMAGE').lower()
        return True

def configure_logging():
    DEFAULT_PORT = 12201

    valida_envs(os.environ)

    graylog_host = get_environment_variable('GRAYLOG_HOST')
    graylog_port = int(get_environment_variable('GRAYLOG_PORT', DEFAULT_PORT))

    logging_config = {
        'version': 1,
        "disable_existing_loggers": True,
        'filters': {
            'settings_filter': {
                '()': LogFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'graypy': {
                'host': graylog_host,
                'port': graylog_port,
                'class': 'graypy.GELFUDPHandler',
                'level_names': True,
                'extra_fields': True
            }
        },
        'root': {
            'level': LogLevel.INFO.value,
            'handlers': ['graypy', 'console'],
            'filters': ['settings_filter']
        }
    }

    logging.config.dictConfig(logging_config)

configure_logging()
