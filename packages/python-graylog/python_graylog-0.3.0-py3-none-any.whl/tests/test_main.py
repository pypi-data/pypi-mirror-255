import logging
import os
import sys

# Get the path of the current file
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_dir_path = os.path.dirname(os.path.dirname(current_file_path))

sys.path.append(parent_dir_path)

from graylog import GELFUDPHandler


def test():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)

    handler = GELFUDPHandler('82.157.73.141', 12202, facility='python-graylog')
    # handler = graylog.http.GELFHTTPHandler('log.kxxxl.com', 80)
    logger.addHandler(handler)

    details = {
        'foo': 'bar',
        'baz': 'qux',
    }

    logger = logging.LoggerAdapter(logger, {'appid': 'os.getenv("GRAYLOG_FACILITY")'})

    logger.debug(f'''This is a multiline message. {handler}''', extra=details)

    print('Done.')


if __name__ == '__main__':
    test()
