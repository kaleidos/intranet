from django.utils.decorators import decorator_from_middleware

from cmsutils.middleware import I18NCacheMiddleware

i18ncache_page = decorator_from_middleware(I18NCacheMiddleware)
i18ncache_page.__doc__ = """
Decorator to cache any views. Its like django cache_page,
with all his parameters, but is I18N aware by default and
you may cache request query string.

Usage::

  @i18ncache_page
  def foo_view(request, ...):
     # foo implementation

  @i18ncache_page(cache_query_string=True)
  def foo_view(request, ...):
     # foo implementation
"""