# -*- coding: utf-8 -*-

import os.path
import subprocess
import sys
import time
from xml.sax.saxutils import escape

import magic

# Make sure DJANGO_SETTINGS_MODULES is your project settings

class FilterError(Exception):
    """Exception thrown when there is no filter registered for a mime type
    or it fails"""


class FilterMeta(type):
    """Add filters to the registry automatically"""
    def __new__(mcs, name, bases, dict):
        klass = type.__new__(mcs, name, bases, dict)
        klass.add_filter()
        return klass


class BaseFilter(object):
    """Abstract class with a Registry API to get the filters"""
    __metaclass__ = FilterMeta

    __filters__ = [] # filter registry

    # Subclasses should define one or both of these attributes
    __magic_string__ = None
    __extension__ = None

    def __init__(self, filename):
        self.filename = filename

    def filter(self):
        body = None
        cmd = self._get_command(self.filename)
        pipe = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = pipe.communicate()
        retcode = pipe.wait()
        if retcode == 0: # sucessful execution
            body = stdout
        else:
            raise FilterError('The command "%s" returned %d'
                              % (' '.join(cmd), retcode))

        return body

    def _get_command(self, filename):
        """Return a list with the command and its arguments"""
        raise NotImplementedError("Subclasses should implement this")

    # Registry API
    @classmethod
    def add_filter(klass):
        if klass.__name__ != 'BaseFilter':
            klass.__filters__.append(klass)

    @classmethod
    def get_all_filters(klass):
        return klass.__filters__

    @classmethod
    def get_filter_for(klass, magic_string, extension=None):
        filters = [filter for filter in klass.__filters__
                   if magic_string.startswith(filter.__magic_string__)]
        if len(filters) > 1:
            found = None
            if extension is not None:
                for filter in filters:
                    if filter.__extension__ == extension.lower():
                        found = filter
                        break
            if found is not None:
                return found
            else:
                return filters[0]

        elif len(filters) == 1:
            return filters[0]
        else:
            raise FilterError('Sorry, no filter for this magic_string: %s (%s)'
                              % (magic_string, extension))


class RTFFilter(BaseFilter):
    __magic_string__ = r'Rich Text Format data'

    def _get_command(self, filename):
        # http://www.wagner.pp.ru/~vitus/software/catdoc/
        return ['catdoc', filename]


class OpenDocumentFilter(BaseFilter):
    __magic_string__ = 'OpenDocument Text'

    def _get_command(self, filename):
        # odt2txt: http://stosberg.net/odt2txt/
        return ['odt2txt', filename]


class PDFFilter(BaseFilter):
    __magic_string__ = 'PDF document'

    def _get_command(self, filename):
        # pdftotext is a command utility from the poppler-utils
        return ['pdftotext', filename, '-']


class WordFilter(BaseFilter):
    __magic_string__ = 'Microsoft Office Document'
    __extension__ = '.doc'

    def _get_command(self, filename):
        # http://www.wagner.pp.ru/~vitus/software/catdoc/
        return ['catdoc', filename]

class PowerPointFilter(BaseFilter):
    __magic_string__ = 'Microsoft Office Document'
    __extension__ = '.ppt'

    def _get_command(self, filename):
        # http://www.wagner.pp.ru/~vitus/software/catdoc/
        return ['catppt', filename]


class ASCIITextFilter(BaseFilter):
    __magic_string__ = 'ASCII text'

    def _get_command(self, filename):
        return ['cat', filename]


class UTF8TextFilter(ASCIITextFilter):
    __magic_string__ = 'UTF-8 Unicode text'


class ISO8859TextFilter(ASCIITextFilter):
    __magic_string__ = 'ISO-8859 text'


def process_file(filename, magic_cookie):
    try:
        if not os.path.exists(filename):
            return

        magic_string = magic_cookie.file(filename)
        if magic_string is None:
            return

        extension = None
        parts = os.path.splitext(filename)
        if len(parts) > 1:
            extension = parts[-1]
        filter = BaseFilter.get_filter_for(magic_string, extension)
        return filter(filename).filter()
    except FilterError, f_error:
        print  >> sys.stderr, f_error


def convert_to_unicode(text):
    if text is None:
        return

    for enc in ('utf-8', 'latin1', 'latin9'):
        try:
            return unicode(text, enc)
        except UnicodeDecodeError:
            pass

XML_TEMPLATE = """<document>
<id>%(id)d</id>
<group>%(group)d</group>
<timestamp>%(timestamp)d</timestamp>
<title>%(title)s</title>
<body>
%(body)s
</body>
</document>"""

def extract_objects(queryset, file_attr, buffered_output=True):
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    if buffered_output:
        docs = []
    for obj in queryset:
        file_obj = getattr(obj, file_attr)
        body = process_file(file_obj.path, ms)
        if body is not None:
            body = convert_to_unicode(body)

        if body is not None:
            title = os.path.splitext(file_obj.name)[0]
            title = title.replace(u'_', u' ').replace(u'-', u' ')

            xml = XML_TEMPLATE % {
                'id': obj.id,
                'group': 1,
                'timestamp': int(time.time()),
                'title': escape(title.encode('utf-8')),
                'body': escape(body.encode('utf-8')),
                }

            if buffered_output:
                docs.append(xml)
            else:
                print xml

        if hasattr(obj, 'indexed'):
            obj.indexed = True
            obj.save(reset_index=False)

    ms.close()
    if buffered_output:
        print '\n'.join(docs)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        body = process_file(filename, ms)
        ms.close()
        if body is not None:
            print body
