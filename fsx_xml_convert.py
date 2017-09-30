# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function
import re
import shutil
import sys
import os
import logging
import logging.handlers
pattern_wp = r'''<WorldPosition>(?P<group1>[A-Za-z0-9]+)\s+(?P<group2>\d+)\s+(?P<group3>\d+\.\d{2})(?:\d+)?,(?P<group4>[A-Za-z0-9]+)\s+(?P<group5>\d+)\s+(?P<group6>\d+\.\d{2})(?:\d+)?,(?P<group7>(?:-|\+)?\d+\.\d+)</WorldPosition>'''
pattern_xml_enc = r'''encoding="(?P<encoding>[^"]+)"'''

def init_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    _fh = logging.handlers.RotatingFileHandler('%s.log' % os.path.realpath(__file__), mode='a',
                                               maxBytes=200000000,
                                               backupCount=5,
                                               encoding='utf-8')
    _fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    # https://docs.python.org/2/library/string.html#format-specification-mini-language
    # https://stackoverflow.com/questions/16799075/in-a-python-logging-is-there-a-formatter-to-truncate-the-string
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)8s:%(name)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s')
    _fh.setFormatter(formatter)
    _ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(_fh)
    logger.addHandler(_ch)
    logger.info('Logger setup')

def usage():
   sys.stderr.write('Usage\r\n')
   sys.stderr.write('\r\n')
   sys.stderr.write('%s source_file\r\n' % sys.argv[0])
   sys.stderr.write('e.g. %s C:\\some\\path\\file.xml\r\n' % sys.argv[0])

def detect_encoding(file):
    with open(file, 'r') as f:
        first_line = f.readline()

    match = re.search(pattern_xml_enc, first_line)
    if match:
        return match.groupdict()['encoding']
    else:
        return None

if __name__ == "__main__":
    init_logging()
    log = logging.getLogger(__name__)
    log.debug('caled with %s', sys.argv)
    if len(sys.argv) == 2:
        log.debug('trying to identify the encoding of the file')
        source_file_path = sys.argv[1]
        if os.path.isfile(source_file_path):
            encoding = detect_encoding(source_file_path)
            if isinstance(encoding, basestring) and len(encoding) >= 3:
                orig_source_file_path = '%s.orig' % source_file_path
                shutil.move(source_file_path, orig_source_file_path)
                log.debug('moved %s to %s', source_file_path, orig_source_file_path)
                orig = open(orig_source_file_path, 'r')
                new = open(source_file_path, 'w')
                i = 1
                for line in orig.readlines():
                    old_line = line.decode(encoding)
                    new_line = re.sub(pattern_wp, "<WorldPosition>\g<group1>° \g<group2>' \g<group3>,\g<group4>° \g<group5>' \g<group6>,\g<group7></WorldPosition>", old_line)
                    if old_line != new_line:
                        log.debug('changed line# %s %s to %s', i, old_line, new_line)
                    i += 1
                    new.write(new_line.encode(encoding))
                orig.close()
                new.close()
            else:
                log.error('Cannot get encoding from file %s', source_file_path)
        else:
            log.error('path %s is not a file', source_file_path)
    else:
        usage()
