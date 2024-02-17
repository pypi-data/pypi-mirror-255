from lins_log.lins_log import LogLevel
from datetime import datetime
from logging import log

def send_log(message: str, task: str, extra: dict = {}, level=LogLevel.INFO):

    if level not in (LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR):
        raise ValueError('LogLevel inválido. Os levels disponíveis são: INFO, WARNING ou ERROR')

    msg = f"{task}: {datetime.now().strftime('%Y/%m/%d - %H:%M:%S')}: {message}"

    extra['task'] = task.lower()

    log(msg=msg, extra=extra, level=level.value)
