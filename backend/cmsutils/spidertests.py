"""
This module provides a base class for writing spider tests.

Introduction
------------

A spider test case traverse the urls specified in a .ini file
and use the Django test client to check if the urls do not
return an error. This is not a replacement for fully functional
tests just a fast way to write very simple tests.

Usage
-----

How to write your spider test:

1. Write a file with urls, something like myproject.ini
2. In the tests.py of your application do this:

from cmsutils.spidertests import BaseSpiderTests

class MyBaseSpiderTests(BaseSpiderTests):
    urls_file = 'myproject-urls.ini'
    fixtures = ['spider_tests']

Note that BaseSpiderTests inherits from django.test.TestCase so
standard features applies (like fixture loading).

Information about the format of the urls file
--------------------------------------------

It has two main sections: GET and POST. Each of these
sections is composed by urls options and other optional parts.

As you can guess, urls in the GET section are tested using
HTTP GET requests and urls in the POST section are tested using
HTTP POST requests.

In each section the urls are tested in lexicographic order

Each url named N can have two optional parts:

 - loginN: user and password separated by a colon. The test
           will try to login before testing the url
 - dataN: data in POST format sent as the body of a POST

Note that to send data in a GET request you should append
the data to the url itself

Currently the SpiderTests just checks that the return response
of these requests is not 500 nor 404.

Example:

[GET]
url1=/
url2=/mymodel/1/myview/

[POST]
url1=/mymodel/1/myeditview/
login1=admin:secret
data1=field1=value1&field2=value2

Optimizations
-------------

Django flushes the database and reload your test fixtures for every
test method call. This can be specially slow when using spider tests.

If you want to load the fixtures just once during your spider test
execution add this to your tests.py file:

import unittest
from cmsutils.spidertests import OptimizedSpiderSuite

def suite():
    return unittest.TestSuite((
            unittest.makeSuite(MySpiderTests, suiteClass=OptimizedSpiderSuite),
            ))

"""

import unittest
import ConfigParser

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test import TestCase


def read_data(value):
    return dict([p.split("=") for p in value.split("&")])


class SpiderMeta(type):

    def __new__(mcs, class_name, bases, namespace):
        urls_file = namespace.get('urls_file', None)
        if urls_file is not None:
            config = ConfigParser.ConfigParser()
            config.read(urls_file)
            maxqueries = None
            if config.has_option('GENERAL', 'maxqueries'):
                maxqueries = int(config.get('GENERAL', 'maxqueries'))

            login = None
            if config.has_option('GENERAL', 'login'):
                login = config.get('GENERAL', 'login')

            def method_factory(url, http_method, data, login, maxqueries):

                def test_method(self):
                    return self._test_url(url, http_method, data, login, maxqueries)
                return test_method

            for method in ('GET', 'POST'):
                if not config.has_section(method):
                    continue

                urls = [option for option in config.options(method)
                        if option.startswith('url')]
                urls.sort()
                for url_name in urls:
                    url = config.get(method, url_name)
                    index = url_name[3:]

                    data = {}
                    if config.has_option(method, 'data%s' % index):
                        value = config.get(method, 'data%s' % index)
                        data = read_data(value)

                    login_local = None
                    if config.has_option(method, 'login%s' % index):
                        login_local = config.get(method, 'login%s' % index)
                    else:
                        login_local = login

                    maxqueries_local = None
                    if config.has_option(method, 'maxqueries%s' % index):
                        maxqueries_local = config.get(method, 'maxqueries%s' % index)
                    else:
                        maxqueries_local = maxqueries

                    if maxqueries_local >= 0:
                        settings.DEBUG = True
                    else:
                        settings.DEBUG = False

                    func = method_factory(url, method, data, login_local, maxqueries_local)
                    name = 'test_%s_%s' % (method.lower(), url)
                    func.__name__ = name
                    while name in namespace:
                        name += '_'
                    namespace[name] = func

        return type.__new__(mcs, class_name, bases, namespace)


class BaseSpiderTests(TestCase):
    __metaclass__ = SpiderMeta

    urls_file = None

    def _test_url(self, url, method='GET', data={}, login=None, maxqueries=None):
        if login is not None:
            user, passwd = self._read_login(login)
            self.client.login(username=user, password=passwd)

        url_tester = getattr(self.client, method.lower())
        try:
            response = url_tester(url, data)
        except:
            self.assert_(False, "Unknown Error (possible 500 Error) at %s" % url)

        self.assertNotEquals(response.status_code, 404, url)
        self.assertNotEquals(response.status_code, 403, url)
        self.assertNotEquals(response.status_code, 401, url)
        if maxqueries is not None and maxqueries >= 0:
            self.assert_(len(connection.queries) <= maxqueries, url)

    def _read_login(self, value):
        return value.split(":")


class OptimizedSpiderSuite(unittest.TestSuite):
    "Suite that reload the fixtures only when required and not for every test"

    def run(self, result):
        last_fixtures = None

        def _void_pre_setup():
            pass

        for test in self._tests:
            if result.shouldStop:
                break

            if hasattr(test, '_pre_setup'):
                # monkey patch the _pre_setup to avoid flushing the DB and
                # loading the fixtures
                test._pre_setup = _void_pre_setup

            if hasattr(test, 'fixtures'):
                if test.fixtures != last_fixtures:
                    self._load_fixtures(test.fixtures)
                    last_fixtures = test.fixtures
            test(result)
        return result

    def _load_fixtures(self, fixtures):
        # this is a custom 'pre_setup' replacement
        call_command('flush', verbosity=0, interactive=False)
        call_command('loaddata', *fixtures, **{'verbosity': 0})


class SpiderTests(BaseSpiderTests):

    urls_file = 'urls.ini'
    fixtures = ['spider_tests']


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(SpiderTests, suiteClass=OptimizedSpiderSuite),
            ))
