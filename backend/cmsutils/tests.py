import os 

import unittest

import magic

from django import template
from django.test import TestCase
from django.test import _doctest as doctest
from django.test.testcases import DocTestRunner
from django.test.simple import doctestOutputChecker
from django.views.generic.list_detail import object_list

from cmsutils.adminfilters import QuerySetWrapper
from cmsutils.docfilters import process_file
from cmsutils.forms import forms
from cmsutils.models import Parameter

class ParametersTest(TestCase):

    def test_read(self):
        p = Parameter.objects.create(name="portal_title",
                                     value="Portal Test")

        v = Parameter.objects.get_value('portal_title')
        self.assertEqual(v, u"Portal Test")

        s = u'{% load parameter %}{% param "portal_title" %}'
        t = template.Template(s)
        c = template.Context({})
        self.assertEqual(t.render(c), u'Portal Test')

        s = u'{% load parameter %}{% param "random_stuff" %}'
        t = template.Template(s)
        c = template.Context({})
        self.assertEqual(t.render(c),
                         u'There is no parameter with name random_stuff')

    def test_write(self):
        Parameter.objects.set_value("portal_owner", "John Doo")
        self.assertEqual(u"John Doo", Parameter.objects.get_value("portal_owner"))

        Parameter.objects.set_value("portal_owner", None)
        self.assertEqual(None, Parameter.objects.get_value("portal_owner"))


class SampleObject(object):
    """Sample object to test the breadcrumbs"""
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/absolute/path/to/object/%s' % self.name


def _remove_blank_lines(text):
    lines = [l for l in text.split(u'\n') if len(l.strip()) > 0]
    return u'\n'.join(lines)

class BreadcrumbsTagTest(TestCase):

    def test_simple(self):
        s = u'{% load breadcrumbs %}{% breadcrumbs foo:/foo bar:/bar %}'
        t = template.Template(s)
        c = template.Context({})
        result = u"""
<div class="breadcrumbs">
  <ul class="breadcrumbs">
    <li class="first-breadcrumbs previous">
      <a href="/">Home</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li class="previous">
      <a href="/foo">foo</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li>
      <a href="/bar">bar</a>
    </li>
  </ul>
</div>
"""
        self.assertEqual(_remove_blank_lines(t.render(c)),
                         _remove_blank_lines(result))

    def test_resolve(self):
        s = u'{% load breadcrumbs %}{% breadcrumbs foo bar:/bar %}'
        t = template.Template(s)
        c = template.Context({'foo': SampleObject(u'Foo')})
        result = u"""
<div class="breadcrumbs">
  <ul class="breadcrumbs">
    <li class="first-breadcrumbs previous">
      <a href="/">Home</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li class="previous">
      <a href="/absolute/path/to/object/Foo">Foo</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li>
      <a href="/bar">bar</a>
    </li>
  </ul>
</div>
"""
        self.assertEqual(_remove_blank_lines(t.render(c)),
                         _remove_blank_lines(result))

    def test_resolve_with_custom_url(self):
        s = u'{% load breadcrumbs %}{% breadcrumbs foo:/my_url bar:/bar %}'
        t = template.Template(s)
        c = template.Context({'foo': SampleObject(u'Foo')})
        result = u"""
<div class="breadcrumbs">
  <ul class="breadcrumbs">
    <li class="first-breadcrumbs previous">
      <a href="/">Home</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li class="previous">
      <a href="/my_url">Foo</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li>
      <a href="/bar">bar</a>
    </li>
  </ul>
</div>
"""
        self.assertEqual(_remove_blank_lines(t.render(c)),
                         _remove_blank_lines(result))

    def test_max_words(self):
        s = u'{% load breadcrumbs %}{% breadcrumbs foo:/my_url:2 %}'
        t = template.Template(s)
        c = template.Context({'foo': SampleObject(u'Very long name')})
        result = u"""
<div class="breadcrumbs">
  <ul class="breadcrumbs">
    <li class="first-breadcrumbs previous">
      <a href="/">Home</a> <span class="breadcrumbs-separator">&nbsp;</span>
    </li>
    <li>
      <a href="/my_url">Very long ...</a>
    </li>
  </ul>
</div>
"""
        self.assertEqual(_remove_blank_lines(t.render(c)),
                         _remove_blank_lines(result))


class FakeTemplateLoader(object):
    def __init__(self, data):
        self.data = data
    def get_template(self, name):
        return template.Template(self.data)

class QuerySetWrapperTests(TestCase):

    def test_simple(self):
        objects = [SampleObject(i) for i in range(10)]
        wrapper = QuerySetWrapper(objects)

        self.assertEqual(len(wrapper), 10)
        self.assertEqual(wrapper.count(), 10)
        self.assertEqual([o.name for o in wrapper[2:5]], [2,3,4])

    def test_objectlist(self):
        objects = [SampleObject(str(i)) for i in range(10)]
        request = None
        template = "{% for obj in object_list %}{{ obj }} {% endfor %}"
        loader = FakeTemplateLoader(template)
        ol = object_list(request, QuerySetWrapper(objects),
                         template_loader=loader, template_name='fake')
        result = "0 1 2 3 4 5 6 7 8 9 "
        self.assertEqual(ol.content, result)


class DocfiltersTests(TestCase):

    def test_samples(self):
        magic_cookie = magic.open(magic.MAGIC_NONE)
        magic_cookie.load()
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        samples_dir = os.path.join(parent_dir, 'samples')
        for f in os.listdir(samples_dir):
            if f.startswith("."):
                continue

            file_path = os.path.join(samples_dir, f)
            extension = os.path.splitext(f)[1]
            result = process_file(file_path, magic_cookie)
            if result is not None:
                msg = "This is a %s document" % extension[1:].upper()
                self.assertEqual(msg, result.strip())

        magic_cookie.close()


def suite():
    return unittest.TestSuite((
        unittest.makeSuite(ParametersTest),
        unittest.makeSuite(BreadcrumbsTagTest),
        unittest.makeSuite(QuerySetWrapperTests),
        unittest.makeSuite(DocfiltersTests),
        doctest.DocTestSuite(forms, checker=doctestOutputChecker,
                             runner=DocTestRunner),
        ))
