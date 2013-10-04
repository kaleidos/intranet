import os, re
from os import path

from django.template import Library, Node, TemplateSyntaxError
from django.conf import settings

register = Library()

class JSPacker:
    """ JS compressor. This commpress a javascript content
        This class code is adapted from http://plone.org/products/resourceregistries """

    def __init__(self):
        # protect this strings:
        #  match a single quote
        #  match anything but the single quote, a backslash and a newline "[^'\\\n]"
        #  or match a null escape (\0 not followed by another digit) "\\0(?![0-9])"
        #  or match a character escape (no newline) "\\[^\n]"
        self.patterns = []
        self.protect(r"""('(?:[^'\\\n]|\\0(?![0-9])|\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}|\\[^\n])*?'|"""
                     r""""(?:[^"\\\n]|\\0(?![0-9])|\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}|\\[^\n])*?")""")

        # protect regular expressions
        self.protect(r"""\s+(\/[^\/\n\r\*](?:\\/|[^\n\r])*\/g?i?)""")
        self.protect(r"""([^\w\$\/'"*)\?:]\/[^\/\n\r\*](?:\\/|[^\n\r])*\/g?i?)""")

        # protect IE conditional compilation
        self.protect(r'(/\*@.*?(?:\*/|\n|\*/(?!\n)))', re.DOTALL)

        # remove multiline comments
        self.sub(r'/\*.*?\*/', '', re.DOTALL)

        # strip whitespace at the beginning and end of each line
        self.sub(r'^[ \t\r\f\v]*(.*?)[ \t\r\f\v]*$', r'\1', re.MULTILINE)

        # after an equal sign a function definition is ok
        self.sub(r'=\s+(?=function)', r'=')

        # whitespace before some special chars
        self.sub(r'\s+([={},&|\?:\.()<>%!/\]])', r'\1')

        # whitespace before plus chars if no other plus char before i
        self.sub(r'(?<!\+)\s+\+', '+')

        # whitespace after plus chars if no other plus char after it
        self.sub(r'\+\s+(?!\+)', '+')
        # whitespace before minus chars if no other minus char before it
        self.sub(r'(?<!-)\s+-', '-')
        # whitespace after minus chars if no other minus char after it
        self.sub(r'-\s+(?!-)', '-')
        # remove redundant semi-colons
        self.sub(r';+\s*([};])', r'\1')
        # remove any excessive whitespace left except newlines
        self.sub(r'[ \t\r\f\v]+', ' ')
        # excessive newlines
        self.sub(r'\n+', '\n')
        # first newline
        self.sub(r'^\n', '')

    def protect(self, pattern, flags=None):
        if flags is None:
            self.patterns.append((re.compile(pattern), None))
        else:
            self.patterns.append((re.compile(pattern, flags), None))

    def sub(self, pattern, replacement, flags=None):
        if flags is None:
            self.patterns.append((re.compile(pattern), replacement))
        else:
            self.patterns.append((re.compile(pattern, flags), replacement))

    def copy(self):
        result = self.__class__()
        result.patterns = self.patterns[:]
        return result

    def _repl(self, match):
        # store protected part
        self.replacelist.append(match.group(1))
        # return escaped index
        return "\x00%i\x00" % len(self.replacelist)

    def pack(self, input):
        # list of protected parts
        self.replacelist = []
        output = input
        for regexp, replacement in self.patterns:
            if replacement is None:
                output = regexp.sub(self._repl, output)
            else:
                # substitute
                output = regexp.sub(replacement, output)
        # restore protected parts
        replacelist = list(enumerate(self.replacelist))
        replacelist.reverse() # from back to front, so 1 doesn't break 10 etc.
        for index, replacement in replacelist:
            # we use lambda in here, so the real string is used and no escaping
            # is done on it
            before = len(output)
            regexp = re.compile('\x00%i\x00' % (index+1))
            output = regexp.sub(lambda m:replacement, output)
        # done
        return output

# singleton object.
jspacker = JSPacker()

class MergeNode(Node):
    name_template = '%s'
    tag_template = '%s'

    def __init__(self, name, files):
        self.name = self.name_template % name
        self.files = files
        self.merge_filename = path.join(settings.MEDIA_ROOT, self.name)

    def render(self, context):
        if not path.exists(self.merge_filename) or not self.is_merge_updated():
            # we merge all files
            merge_file = open(self.merge_filename, 'w')
            for f in self.files:
                file_path = path.join(settings.MEDIA_ROOT, f)
                if not path.isfile(file_path):
                    continue
                self.merge(f, file_path, merge_file)
            merge_file.close()
        return self.tag()

    def is_merge_updated(self):
        """ compares modification time of all files with merged file """
        last_mtime = 0 # last modification time of a file 
        for f in self.files:
            file_path = path.join(settings.MEDIA_ROOT, f)
            file_stat = os.stat(file_path)
            mtime = file_stat[-2]
            if last_mtime < mtime:
                last_mtime = mtime
        merge_mtime = os.stat(self.merge_filename)[-2]
        return merge_mtime > last_mtime

    def merge(self, filename, file_path, fd):
        """ Simple merge, no compression """
        content = file(file_path).read()
        fd.write('/* -- %s -- */\n\n%s\n\n\n' % (filename, content))
    
    def tag(self):
        """ write js/css tag for merged file inclusion """
        url = '%s%s' % (settings.MEDIA_URL, self.name)
        return self.tag_template % url

class JSMergeNode(MergeNode):
    name_template = '%s.js'
    tag_template = '<script type="text/javascript" src="%s"></script>'

    def merge(self, jsname, jspath, fd):
        """ do merging and compressing of javascript """
        global jspacker
        jsfile = open(jspath)
        jscontent = jsfile.read()
        jscontent = jspacker.pack(jscontent)
        fd.write('/* -- %s -- */\n\n%s\n\n\n' % (jsname, jscontent))

class CSSMergeNode(MergeNode):
    name_template = '%s.css'
    tag_template = '<link rel="stylesheet" type="text/css" href="%s" />'


def create_merger(mergerNode):
    def do_merge(parser, token):
        """
        This will merge css/javascript files in only one compressed css/javascript.

        Usage::

            {% load [js|css]merge %}
            {% [js|css]merge name [file1] [file2] .. %} 

        Example::

            {% load jsmerge %}
            {% jsmerge jsmergefile  js/file1.js js/file2.js js/file3.js %}

        This will create (if not exists) a /media/cmsutils/jsmergefile.js with three
        files merged. The HTML output for this will be::

            <script type="text/javascript" src="/media/cmsutils/jsmergefile.js"></script>
        """
        tokens = token.contents.split()
        if len(tokens) < 2:
            raise TemplateSyntaxError(u"'%r' tag requires at least 1 arguments." % tokens[0])
        js_name = tokens[1]
        return mergerNode(js_name, tokens[2:])
    
    return do_merge

register.tag('jsmerge', create_merger(JSMergeNode))
register.tag('cssmerge', create_merger(CSSMergeNode))

