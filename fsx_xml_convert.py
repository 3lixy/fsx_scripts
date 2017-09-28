# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function
import xml.etree.ElementTree as ElementTree
import re
import shutil
import sys
import os
import logging
import logging.handlers
import io
pattern = ur'''<WorldPosition>(?P<group1>[A-Za-z0-9]+)\s+(?P<group2>\d+)\s+(?P<group3>\d+\.\d{2})(?:\d+)?,(?P<group4>[A-Za-z0-9]+)\s+(?P<group5>\d+)\s+(?P<group6>\d+\.\d{2})(?:\d+)?,(?P<group7>(?:-|\+)?\d+\.\d+)</WorldPosition>'''

class CommentedTreeBuilder(ElementTree.XMLTreeBuilder):
    def __init__(self, html=0, target=None):
        ElementTree.XMLTreeBuilder.__init__(self, html, target)
        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(ElementTree.Comment, {})
        self._target.data(data)
        self._target.end(ElementTree.Comment)

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

if __name__ == "__main__":
    init_logging()
    log = logging.getLogger(__name__)
    log.debug(u'caled with %s', sys.argv)
    if len(sys.argv) == 2:
        source_file_path = sys.argv[1]
        if os.path.isfile(source_file_path):
            orig_source_file_path = '%s.orig' % source_file_path
            shutil.move(source_file_path, orig_source_file_path)
            log.debug('moved %s to %s', source_file_path, orig_source_file_path)
            orig = io.open(orig_source_file_path, 'r',  encoding="utf-8")
            new = io.open(source_file_path, 'w', encoding="utf-8")
            i = 1
            for line in orig.readlines():
                old_line = line
                new_line = re.sub(pattern, "<WorldPosition>\g<group1>° \g<group2>' \g<group3>,\g<group4>° \g<group5>' \g<group6>,\g<group7></WorldPosition>", line)
                if old_line != new_line:
                    log.debug(u'changed line# %s %s to %s', i, old_line, new_line)
                i += 1
                new.write(new_line)
            orig.close()
            new.close()
        else:
            log.error('path %s is not a file', source_file_path)
    else:
        usage()
