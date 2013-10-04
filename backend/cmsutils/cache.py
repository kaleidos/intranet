"""
CACHE MODULE

Cache Managers
--------------

There are two cache methods implemented: explicit and implicit cache.

Mixin code from these sources:
  http://github.com/mmalone/django-caching/blob/master/app/managers.py
  http://code.djangoproject.com/ticket/7338

Usage examples::

  Example model:

  class Book(models.Model):
      title = models.CharField(max_length=200)
      objects = CachingManager()

  Simple explicit queryset cache:

  >>> from django.db import connection
  >>> Book.objects.filter(status='published').cache()
  [<Book: El Quijote>, <Book: Novelas Ejemplares>]
  >>> len(connection.db.queries)
  1
  >>> Book.objects.filter(status='published').cache()
  >>> len(connection.db.queries)
  1
  >>> Book.objects.flush_cache() # <----- this invalidates cache
  >>> Book.objects.filter(status='published').cache()
  >>> len(connection.db.queries)
  2

  Queryset cache with timeout:

  >>> Book.objects.cache(timeout=10)

  Object retrieval cache:

  >>> book = Book.object.get(id=1)
  >>> len(connection.db.queries)
  1
  >>> print book
  El Quijote
  >>> book.title = 'Quijote'
  >>> book.save()  # <----- this invalidates cache
  >>> len(connection.db.queries)
  2
  >>> Book.objects.get(id=1)
  <Book: Quijote>
  >>> len(connection.db.queries)
  3
  >>> Book.objects.get(id=1)
  <Book: Quijote>
  >>> len(connection.db.queries)
  3

  Disabling object retrieval cache:

  class Book(models.Model):
      title = models.CharField(max_length=200)
      objects = CachingManager(cache_object_retrieval=False)

  >>> Book.objects.get(id=1)
  <Book: Quijote>
  >>> len(connection.db.queries)
  1
  >>> Book.objects.get(id=1)
  <Book: Quijote>
  >>> len(connection.db.queries)
  2

"""

import time
import md5

from django.conf import settings
from django.core.cache import cache
from django.db import connection, models
from django.db.models import signals, sql
from django.db.models.query import QuerySet
from django.db.models.sql.where import WhereNode
from django.db.models.sql.constants import *
from django.utils.cache import _generate_cache_key, _generate_cache_header_key
from django.utils.encoding import iri_to_uri
from django.utils.hashcompat import md5_constructor


# The time an object is cached
if not hasattr(settings, 'CACHE_DB_SECONDS'):
    settings.CACHE_DB_SECONDS = 1800

# The time we wait for an object to be retrieved from DB
# to avoid concurrent retrieval
if not hasattr(settings, 'CACHE_DB_WAIT_SECONDS'):
    settings.CACHE_DB_WAIT_SECONDS = 10
CACHE_WAIT = '__wait__'


class CacheableDoesNotExist(Exception):
    """Cacheable DoesNotExist exception."""

    def __init__(self, args):
        self.args = args

def _model_cache_key(model):
    return "%s.%s" % (model._meta.app_label, model._meta.module_name)


def _cache_key(model, value):
    return "%s:%s" % (_model_cache_key(model), value)


def _get_cache_key(self):
    cache_key_field = getattr(self, '_cache_key_field', 'pk')
    return self._cache_key(getattr(self, cache_key_field))


class CachedModel(models.Model):
    from_cache = False

    class Meta:
        abstract = True


class CachingManager(models.Manager):
    """ Caching manager """

    def __init__(self, cache_object_retrieval=True, *args, **kwargs):
        super(CachingManager, self).__init__(*args, **kwargs)
        self.cache_object_retrieval = cache_object_retrieval

    def get_query_set(self):
        return CachingQuerySet(self.model)

    def contribute_to_class(self, model, name):
        signals.post_save.connect(self._post_save, sender=model)
        signals.post_delete.connect(self._post_delete, sender=model)
        setattr(model, '_cache_key', classmethod(_cache_key))
        setattr(model, '_get_cache_key', _get_cache_key)
        setattr(model, 'cache_key', property(_get_cache_key))
        setattr(model, '_cache_object_retrieval', self.cache_object_retrieval)
        return super(CachingManager, self).contribute_to_class(model, name)

    def _invalidate_cache(self, instance):
        """
        Explicitly set a None value instead of just deleting so we don't
        have any race conditions where:
            Thread 1 -> Cache miss, get object from DB
            Thread 2 -> Object saved, deleted from cache
            Thread 1 -> Store (stale) object fetched from DB in cache
        Five second should be more than enough time to prevent
        this from happening for a web app.
        """
        cache.set(instance.cache_key, None, 5)

    def _post_save(self, instance, **kwargs):
        self.flush_cache()
        self._invalidate_cache(instance)

    def _post_delete(self, instance, **kwargs):
        self.flush_cache()
        self._invalidate_cache(instance)

    def cache(self, timeout=3600):
        return self.get_query_set().cache(timeout=timeout) 

    def flush_cache(self): 
        model_cache_key = _model_cache_key(self.model)
        cache_register = cache.get(model_cache_key, []) 
        for cached_queryset_key in cache_register: 
            cache.delete(cached_queryset_key) 
        cache.delete(model_cache_key)


class CachingSQLQuery(sql.Query):
    """ sql.Query subclass that provides caching """

    def __init__(self, model, connection, where=WhereNode):
        super(CachingSQLQuery, self).__init__(model, connection, where)
        # Cached queryset atribute. None means no cached
        self.cache_timeout = None
        self.cache_key = None

    def clone(self, klass=None, **kwargs):
        """
        Creates a copy of the current instance. The 'kwargs' parameter can be
        used by clients to update attributes after copying has taken place.
        """
        obj = super(CachingSQLQuery, self).clone(klass, **kwargs)
        obj.cache_timeout = self.cache_timeout
        obj.cache_key = self.cache_key
        return obj

    def results_iter(self):
        """
        Returns an iterator over the results from executing this query.
        """
        resolve_columns = hasattr(self, 'resolve_columns')
        fields = None

        if self.cache_timeout is not None: 
            # Check cache for stored objects from an exactly equal query 
            k = str(self)
            try:
                import hashlib
            except ImportError:
                import sha
                k = sha.new(k).hexdigest()
            else:
                k = hashlib.sha1(k).hexdigest()

            self.cache_key = k

            if cache.has_key(k) and cache.get(k):
                sql_result = cache.get(k, [])
            else:
                sql_result = [i for i in self.execute_sql(MULTI)]
                cache.set(k, sql_result, self.cache_timeout)
                # register this cache key for allowing later invalidation
                model_cache_key = _model_cache_key(self.model)
                cache_register = cache.get(model_cache_key, [])
                cache_register.append(k)
                cache.set(model_cache_key, cache_register)
        else:
            sql_result = self.execute_sql(MULTI)

        for rows in sql_result:
            for row in rows:
                if resolve_columns:
                    if fields is None:
                        # We only set this up here because
                        # related_select_fields isn't populated until
                        # execute_sql() has been called.
                        if self.select_fields:
                            fields = self.select_fields + self.related_select_fields
                        else:
                            fields = self.model._meta.fields
                    row = self.resolve_columns(row, fields)

                if self.aggregate_select:
                    aggregate_start = len(self.extra_select.keys()) + len(self.select)
                    aggregate_end = aggregate_start + len(self.aggregate_select)
                    row = tuple(row[:aggregate_start]) + tuple([
                        self.resolve_aggregate(value, aggregate)
                        for (alias, aggregate), value
                        in zip(self.aggregate_select.items(), row[aggregate_start:aggregate_end])
                    ]) + tuple(row[aggregate_end:])

                yield row


class CachingQuerySet(QuerySet):
    """ QuerySet subclass that provides caching """

    def __init__(self, model=None, query=None):
        query = query or CachingSQLQuery(model, connection)
        super(CachingQuerySet, self).__init__(model, query)

    def cache(self, timeout=20): 
        """
        Forces the current queryset to check if a exact equal query has been 
        stored in the cache. The expiration time is the seconds in 'timeout' 
        variable. 
        """
        cloned_obj = self._clone()
        cloned_obj.query.cache_timeout = timeout
        return cloned_obj

    def iterator(self):
        """
        Cache objects when they are accesed.
        """
        superiter = super(CachingQuerySet, self).iterator()
        cache_object_retrieval = self.model._cache_object_retrieval
        while True:
            obj = superiter.next()
            if cache_object_retrieval:
                # Use cache.add instead of cache.set to prevent
                # race conditions (see CachingManager)
                cache.set(obj.cache_key, obj, settings.CACHE_DB_SECONDS)
            yield obj

    def get(self, *args, **kwargs):
        """
        Checks the cache to see if there's a cached entry for this pk.
        If not, fetches using super then stores the result in cache.

        Most of the logic here was gathered from a careful reading of
        ``django.db.models.sql.query.add_filter``
        """
        cache_object_retrieval = self.model._cache_object_retrieval
        if self.query.where or not cache_object_retrieval:
            # If there is any other ``where`` filter on this QuerySet just call
            # super. There will be a where clause if this QuerySet has already
            # been filtered/cloned.
            return super(CachingQuerySet, self).get(*args, **kwargs)

        cache_key = None
        # Punt on anything more complicated than get by pk/id only...
        if len(kwargs) == 1:
            k = kwargs.keys()[0]
            cache_key_field = getattr(self.model, '_cache_key_field', 'pk')
            if k in (cache_key_field, '%s__exact' % cache_key_field,
                    self.model._meta.pk.attname,
                    '%s__exact' % self.model._meta.pk.attname):
                cache_key = self.model._cache_key(kwargs.values()[0])
                while True:
                    obj = cache.get(cache_key)
                    if obj != CACHE_WAIT:
                        break
                    time.sleep(0.2)
                if isinstance(obj, CacheableDoesNotExist):
                    raise self.model.DoesNotExist(*obj.args)
                if obj is not None:
                    obj.from_cache = True
                    return obj
                # mark as we're waring, so no other threads/processes
                # have to fetch it too.
                cache.set(cache_key, CACHE_WAIT,
                    settings.CACHE_DB_WAIT_SECONDS)

        # Calls self.iterator to fetch objects, storing object in cache.
        try:
            return super(CachingQuerySet, self).get(*args, **kwargs)
        except self.model.DoesNotExist, e:
            if cache_key:
                # store in cache that object does not exist
                exc = CacheableDoesNotExist(e.args)
                cache.set(cache_key, exc, settings.CACHE_DB_SECONDS)
            raise e



def get_request_cache_key(request, key_prefix=None):
    """
    Based on django.utils.cache.get_cache_key function

    Returns a cache key based on the request path. It can be used in the
    request phase because it pulls the list of headers to take into account
    from the global path registry and uses those to build a cache key to check
    against.

    If there is no headerlist stored, the page needs to be rebuilt, so this
    function returns None.

    This function has been refactored to be able to call get_view_cache_key
    in a separately way. This is needed to define a request.path_cache_key
    attribute (see cmsutils.middleware.I18NFetchFromCacheMiddleware).
    """
    if key_prefix is None:
        key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    cache_key = _generate_cache_header_key(key_prefix, request)
    headerlist = cache.get(cache_key, None)
    if headerlist is not None:
        return _generate_cache_key(request, headerlist, key_prefix)
    else:
        return None
