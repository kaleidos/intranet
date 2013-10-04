# -*- coding: utf-8 -*-
import datetime

try:
    import uuid
    _uuid = uuid
except ImportError: # uuid is new in python 2.5
    from cmsutils import uuid25
    _uuid = uuid25

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage

from cmsutils import log
from cmsutils.i18n import rotate_language

def add_or_edit_generic_view(request, title,
                             form_factory_function,
                             save_changes_function,
                             redirect_url=None,
                             button_label=_('Save object'),
                             image_field=None,
                             template='portal/edit_object.html',
                             extra_context={}):
    """ Generic view for adding/editing an object.

    The form_factory_function will be called to create a form. The signature of
    this callable is form_factory_function (is_post, new_data).

    The save_changes_function will be called to save the changes. The signature
    of this callable is save_changes_function(form, project, new_data)

    redirect_url is a template string that will be composed with the project
    url to get the url to redirect after a succesful process.

    button_label is the label of the submit button

    image_field can be specified if the content type has an image type field.
    """
    if request.method == 'POST':
        #if image_field is not None and image_field in request.FILES:
        #    read_image(request, image_field)
        new_data = request.POST.copy()
        new_files = request.FILES.copy()

        form = form_factory_function(True, new_data, new_files)

        if form.is_valid():
            next_url = save_changes_function(form, new_data, new_files)
            if not redirect_url:
                redirect_url = next_url
            return HttpResponseRedirect(redirect_url)
        else:
            log.send_error(request, _('Form has errors'))
    else:
        form = form_factory_function(False)

    context =  {'form': form,
                'title': title,
                'button_label': button_label,}
    context.update(extra_context)

    return render_to_response(template,
                              context,
                              context_instance = RequestContext(request))


def rotate_language_and_redirect(request):
    """ Generic view that rotates user language and then redirect to an url passed by http parameter """
    from django.conf import settings
    languages = dict(settings.LANGUAGES)

    next_url = request.REQUEST.get('next', '')
    response = HttpResponseRedirect(next_url)
    new_lang_code = rotate_language(request, response)
    new_lang = smart_unicode(str(languages[new_lang_code]))

    log.send_info(request, u'%s %s' % (_('Now you are editing content in'), new_lang))

    return response


def delete_object(request):
    content_type_id = request.POST.get('content_type_id', None)
    object_id = request.POST.get('object_id', None)
    if content_type_id is None or object_id is None:
        raise Http404

    # usar newsitem._meta.app_label y newsitem._meta.module_name para sacar
    # el content type en el templatetag
    content_type = ContentType.objects.get(id=int(content_type_id))
    if request.user.has_perm('delete_%s' % content_type.model) or \
       request.user.has_perm('%s.delete_%s' % (content_type.app_label, content_type.model)):
        obj = content_type.get_object_for_this_type(id=object_id)
        log.delete(request.user.id, obj)
        obj.delete()
    else:
        log.send_error(request, _('You do not have permission to delete %s objects')
                       % content_type.model)
    return HttpResponseRedirect('/')

def confirm_delete_object(request):
    content_type_id = request.GET.get('content_type_id', None)
    object_id = request.GET.get('object_id', None)
    if content_type_id is None or object_id is None:
        raise Http404
    return render_to_response('cmsutils/confirm_delete.html',
                              {'content_type_id': content_type_id,
                               'object_id': object_id},
                              context_instance=RequestContext(request))

def get_feed_entries(host, feed_id, model=None, attr_map={}, filter_args={},
                    order_by=None, max_items=-1):
    objects = []
    # Do the query
    if model is not None:
        if filter_args:
            objects = model.objects.filter(**filter_args)
        else:
            objects = model.objects.all()

        if order_by is not None:
            objects = objects.order_by(*order_by)

        if max_items != -1:
            objects = objects[:max_items]

    # Convert the model objects into feed entries
    entries = []
    for obj in objects:
        entry = dict([(key, getattr(obj, value))
                      for key, value in attr_map.items()])
        if hasattr(obj, 'get_absolute_url'):
            entry['link'] = 'http://%s%s' % (host,
                                             obj.get_absolute_url().encode('utf-8'))
        name = '%s.%s.%d' % (obj._meta.app_label, obj._meta.module_name, obj.id)
        entry['id'] = _uuid.uuid5(feed_id, name.encode('utf-8')).get_urn()
        entries.append(entry)

    return entries

def atom_view(request, subtitle=u'', model=None, attr_map={},
              filter_args={}, order_by=None, max_items=-1):
    host = request.get_host()
    feed_url = 'http://%s%s' % (host, request.get_full_path())
    feed_id = _uuid.uuid5(_uuid.NAMESPACE_URL, feed_url.encode('utf-8'))

    entries = get_feed_entries(host, feed_id,
                               model, attr_map, filter_args,
                               order_by, max_items)

    context = {
        'title': _('RSS Feeds'),
        'subtitle': subtitle,
        'rights': u'Copyright (c) 2007, Junta de Andalucía',
        'id': feed_id.get_urn(),
        'entries': entries,
        'updated': datetime.datetime.today(),
        }

    return render_to_response('cmsutils/atom.xml', context,
                              mimetype='text/xml',
                              context_instance=RequestContext(request))


def sequence_object_list(request, object_sequence, paginate_by=None, page=None,
        allow_empty=True, template_name=None, template_loader=loader,
        extra_context=None, context_processors=None, template_object_name='object',
        mimetype=None):
    """
    Generic list of objects.

    Templates: ``<app_label>/<model_name>_list.html``
    Context:
        object_list
            list of objects
        is_paginated
            are the results paginated?
        results_per_page
            number of objects per page (if paginated)
        has_next
            is there a next page?
        has_previous
            is there a prev page?
        page
            the current page
        next
            the next page
        previous
            the previous page
        pages
            number of pages, total
        hits
            number of objects, total
        last_on_page
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).
    """
    if extra_context is None: extra_context = {}
    if paginate_by:
        paginator = Paginator(object_sequence, paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                # Page is not 'last', nor can it be converted to an int.
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,

            # Legacy template context stuff. New templates should use page_obj
            # to access this instead.
            'is_paginated': page_obj.has_other_pages(),
            'results_per_page': paginator.per_page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_obj.number,
            'next': page_obj.next_page_number(),
            'previous': page_obj.previous_page_number(),
            'first_on_page': page_obj.start_index(),
            'last_on_page': page_obj.end_index(),
            'pages': paginator.num_pages,
            'hits': paginator.count,
            'page_range': paginator.page_range,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: object_sequence,
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
        }, context_processors)
        if not allow_empty and len(object_sequence) == 0:
            raise Http404
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    if not template_name:
        if len(object_sequence) > 0:
            sample = object_sequence[0]
            template_name = "%s/%s_list.html" % (object_sequence._meta.app_label, object_sequence._meta.object_name.lower())
        else:
            template_name = "object_list.html"
    t = template_loader.get_template(template_name)
    return HttpResponse(t.render(c), mimetype=mimetype)


def redirect_to_object(request, content_type_id, object_id):
    """
    Redirect to an object's page based on a content-type ID and an object ID.

    Modified from django.contrib.contenttypes.views.shortcut
    """
    # Look up the object, making sure it's got a get_absolute_url() function.
    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404("Content type %s object %s doesn't exist" % (content_type_id, object_id))
    try:
        absurl = obj.get_absolute_url()
    except AttributeError:
        raise Http404("%s objects don't have get_absolute_url() methods" % content_type.name)

    return HttpResponseRedirect(absurl)