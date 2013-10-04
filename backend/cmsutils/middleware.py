import md5
import os
import sys
import re
import tempfile
import StringIO
from operator import itemgetter

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import logout
from django.middleware.cache import FetchFromCacheMiddleware, UpdateCacheMiddleware
from django.utils import translation
from django.utils.cache import _generate_cache_header_key, patch_vary_headers, \
                               learn_cache_key, patch_response_headers, get_max_age

from cmsutils.cache import get_request_cache_key
from cmsutils.resourcemanager import ResourceManager
try:
    from multilingual import set_default_language
except ImportError:
    MULTILINGUAL_SUPPORT = False # no django-multilingual installed
else:
    MULTILINGUAL_SUPPORT = True

email_link_pat = re.compile(r'<a\s+href=("|\')?mailto:[^>]+>([^<]*)</a>')
email_pat = re.compile(r'(\b[-.\w]+)@([-.\w]+\.[a-z]{2,4}\b)')

def obfuscate_email(match):
    return '<a href="/show_mails">%s...%s</a>' % (match.group(1)[:6], match.group(2)[-6:])


class MultilingualMiddleware(object):
    def process_request(self, request):
        if not MULTILINGUAL_SUPPORT:
            return None
        set_default_language(request.LANGUAGE_CODE)


class ResourceManagerMiddleware(object):
    def process_request(self, request):
        """Add a resource manager instance to each request"""
        request.resource_manager = ResourceManager()

# Bassed on snippet:
# http://www.djangosnippets.org/snippets/536/
class ObfuscateEmailAddressMiddleware(object):
    def process_response(self, request, response):
        try:
            if not request.user.is_authenticated() and not request.session.get('show_mails',False):
                if('text/html' in response['Content-Type'] and request.method!='POST'):
                    response.content = email_link_pat.sub(r"\2", response.content)
                    response.content = email_pat.sub(obfuscate_email, response.content)
        except:
            pass
        return response

def get_browser_languages(request):
    """ return browser languages preferences """

    if not request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
        return []

    browser_pref_langs = request.META['HTTP_ACCEPT_LANGUAGE']
    browser_pref_langs = browser_pref_langs.split(',')

    i = 0
    langs = []
    length = len(browser_pref_langs)

    for lang in browser_pref_langs:
        lang = lang.strip().lower().replace('_', '-')
        if lang:
            l = lang.split(';', 2)
            quality = []
            if len(l) == 2:
                try:
                    q = l[1]
                    if q.startswith('q='):
                        q = q.split('=', 2)[1]
                        quality = float(q)
                except:
                    pass
            if quality == []:
                quality = float(length-i)
            language = l[0]
            baselanguage = language.split('-')[0]
            langs.append((quality, baselanguage))
            i = i + 1

    # sort it by quality
    langs.sort(reverse=True)

    # return only language codes
    langs = map(itemgetter(1), langs)

    return langs


def get_language_from_request(request):
    global _accepted
    from django.conf import settings
    supported = dict(settings.LANGUAGES)

    # If a previous midleware has decided the language use it
    if hasattr(request, 'LANGUAGE_CODE'):
        lang_code = request.LANGUAGE_CODE
        if lang_code in supported and lang_code is not None and translation.check_for_language(lang_code):
            return lang_code

    if hasattr(request, 'session'):
        lang_code = request.session.get('django_language', None)
        if lang_code in supported and lang_code is not None and translation.check_for_language(lang_code):
            return lang_code

    lang_code = request.COOKIES.get('django_language')

    if lang_code and lang_code in supported and translation.check_for_language(lang_code):
        return lang_code

    take_browser_prefs = getattr(settings, 'USE_BROWSER_LANGUAGE_PREFS', True)
    if take_browser_prefs:
        # try get it from browser preferences
        browser_pref_langs = get_browser_languages(request)
        for lang_code in browser_pref_langs:
            if lang_code in supported and translation.check_for_language(lang_code):
                return lang_code

    # Initially use the default language
    return settings.LANGUAGE_CODE


class LazyLocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context IGNORING the user accepted-languages. This allows 
    pages to be dynamically translated to the language the user desires 
    (if the language is available, of course).
    """

    def process_request(self, request):
        language = get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response


class AutomatizedTestingMiddleware(object):
    """
    This middleware parses a request and if detect a ?testing=1 parameter
    do several things to make work with automatized testing tools like selenium.
    """

    def process_request(self, request):
        testing = bool(request.REQUEST.get('testing', False))
        force_testing = hasattr(settings, 'FORCE_TESTING') and settings.FORCE_TESTING
        request.testing = testing or force_testing


def add_suffix_to_cache_key(cache_key, request, cache_query_string=False):
    full_cache_key = '%s-%s' % (cache_key, get_language_from_request(request))
    if cache_query_string:
        full_cache_key += '-%s' % md5.md5(request.META['QUERY_STRING']).hexdigest()
    return full_cache_key


class I18NUpdateCacheMiddleware(UpdateCacheMiddleware):
    """
    Special UpdateCacheMiddleware that inherits django one, but:

      1) adds language in cache key_prefix
      2) can cache QUERY_STRING from request (by default not caching)

    Must be used as part of the two-part update/fetch cache middleware.
    I18NUpdateCacheMiddleware must be the first piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the response phase.
    """
    def __init__(self):
        super(I18NUpdateCacheMiddleware, self).__init__()
        self.cache_query_string = getattr(settings, 'CACHE_QUERY_STRING', False)

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if not hasattr(request, '_cache_update_cache') or not request._cache_update_cache:
            # We don't need to update the cache, just return.
            return response
        if request.method != 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout == None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        if timeout:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix)
            cache_key = add_suffix_to_cache_key(cache_key, request,
                                                cache_query_string=self.cache_query_string)
            cache.set(cache_key, response, timeout)
        return response


class I18NFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    """
    Request-phase cache middleware that fetches a page from the cache.

    It inherits from django one, but:

      1) adds language in cache key_prefix
      2) can cache QUERY_STRING from request (by default not caching)

    Must be used as part of the two-part update/fetch cache middleware.
    FetchFromCacheMiddleware must be the last piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the request phase.
    """
    def __init__(self):
        super(I18NFetchFromCacheMiddleware, self).__init__()
        self.cache_query_string = getattr(settings, 'CACHE_QUERY_STRING', False)

    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        if self.cache_anonymous_only:
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."

        # we define these attributes for a possible later use in views
        request.path_cache_key = _generate_cache_header_key(self.key_prefix, request)
        request.cache_query_string = self.cache_query_string

        if not request.method in ('GET', 'HEAD') or (request.GET and not self.cache_query_string):
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        if self.cache_anonymous_only and request.user.is_authenticated():
            request._cache_update_cache = False
            return None # Don't cache requests from authenticated users.
        
        cache_key = get_request_cache_key(request, self.key_prefix)

        if cache_key is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        cache_key = add_suffix_to_cache_key(cache_key, request,
                                            cache_query_string=self.cache_query_string)

        response = cache.get(cache_key, None)
        if response is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        request._cache_update_cache = False
        return response


class I18NCacheMiddleware(I18NUpdateCacheMiddleware, I18NFetchFromCacheMiddleware):
    """
    Cache middleware that provides basic behavior for many simple sites.

    It have same behavior from django CacheMiddleware, but:

      1) adds language in cache key_prefix
      2) can cache QUERY_STRING from request (by default not caching)

    Also used as the hook point for the cache decorator, which is generated
    using the decorator-from-middleware utility.
    """
    def __init__(self, cache_timeout=None, key_prefix=None,
                 cache_anonymous_only=None, cache_query_string=None):
        self.cache_timeout = cache_timeout
        if cache_timeout is None:
            self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = key_prefix
        if key_prefix is None:
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        if cache_anonymous_only is None:
            self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
        else:
            self.cache_anonymous_only = cache_anonymous_only
        if cache_query_string is None:
            # caching request query string (False by default)
            self.cache_query_string = getattr(settings, 'CACHE_QUERY_STRING', False)
        else:
            self.cache_query_string = cache_query_string


class TestingMiddleware(object):

    def process_request(self, request):
        from django.contrib.auth import logout
        from django.http import HttpResponseRedirect
        from django.conf import settings

        if request.method == 'GET':
            if request.GET.get('logout', None) and request.META['PATH_INFO'] != settings.LOGIN_URL:
                logout(request)
                new_get_data = request.GET.copy()
                new_get_data.pop('logout')
                return HttpResponseRedirect('%s?%s' % (request.META['PATH_INFO'], new_get_data.urlencode()))


class SiteLogin(object):
    """
    Close entire site to anonymous user.

    Usage::
        1. Add 'cmsutils.middleware.SiteLogin' in your MIDDLEWARE_CLASSES settings
        2. Add a optional ANONYMOUS_URLS setting if you want to public some URLs regex. Example:
            ANONYMOUS_URLS = (
                r'^/blogs/', # blogs are anonymous
            )
    """

    def process_request(self, request):
        from django.contrib.auth.views import redirect_to_login, login
        request_path = request.META['PATH_INFO']
        if request_path.startswith(settings.MEDIA_URL):
            return
        if self._is_anonymous_url(request_path):
            return
        if request.user.is_anonymous() and request_path != settings.LOGIN_URL:
            logout(request)
            return redirect_to_login(request_path, login_url=settings.LOGIN_URL)
        elif request_path == settings.LOGIN_URL and request.method == 'POST':
            return login(request)

    def _is_anonymous_url(self, request_path):
        for regex in getattr(settings, 'ANONYMOUS_URLS', ()):
            if re.match(regex, request_path):
                return True
        return False


words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]


class ProfileMiddleware(object):
    """
    Code adapted from: http://djangosnippets.org/snippets/605/

    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "profile" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def show_profiling(self, request):
        return settings.DEBUG and request.GET.has_key('profile')

    def process_request(self, request):
        if self.show_profiling(request):
            import hotshot
            self.tmpfile = tempfile.mktemp()
            self.prof = hotshot.Profile(self.tmpfile)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.show_profiling(request):
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall( file )
            if name:
                return name[0]

    def get_summary(self, results_dict, sum):
        list = [ (item[1], item[0]) for item in results_dict.items() ]
        list.sort( reverse = True )
        list = list[:40]

        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        sum = 0

        for s in stats_str:
            fields = words_re.split(s);
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]

                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time

                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[ group ] = 0
                mygroups[ group ] += time

        return "<pre>" + \
               " ---- By file ----\n\n" + self.get_summary(mystats,sum) + "\n" + \
               " ---- By group ---\n\n" + self.get_summary(mygroups,sum) + \
               "</pre>"

    def process_response(self, request, response):
        if self.show_profiling(request):
            import hotshot.stats
            self.prof.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

            response.content = "\n".join(response.content.split("\n")[:40])

            response.content += self.summary_for_files(stats_str)

            os.unlink(self.tmpfile)

        return response