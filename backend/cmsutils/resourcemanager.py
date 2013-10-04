from django.conf import settings
from django.utils.safestring import mark_safe
from cmsutils.templatetags.merge import JSMergeNode, CSSMergeNode

class ResourceManager(object):
    """Simple registry to keep track of the (js and css) resources needed for
    a request"""
    CSS_TEMPLATE = '<link rel="stylesheet" type="text/css" href="/site_media/%s" />'
    JS_TEMPLATE = '<script type="text/javascript" src="/site_media/%s"></script>'

    def __init__(self):
        self.js = []
        self.css = []
    
    def add_resources(self, *resources):
        for resource in resources:
            if resource.lower().endswith('.js'):
                if resource not in self.js:
                    self.js.append(resource)
            elif resource.lower().endswith('.css'):
                if resource not in self.css:
                    self.css.append(resource)

    def __str__(self):
        return '%s\n%s' % (self.render_css(),
                           self.render_javascript_libraries())
    
    def __unicode__(self):
        return mark_safe(unicode(str(self)))

    def render_css(self):
        if self.css:
            if settings.DEBUG:
                return '\n'.join([self.CSS_TEMPLATE % css for css in self.css])
            else:
                # merge all the css files
                filename = 'cssmerge-%s' % id(''.join(self.css))
                merger = CSSMergeNode(filename, self.css)
                return merger.render(None)
        return ''
    
    def render_javascript_libraries(self):
        if self.js:
            if settings.DEBUG:
                return '\n'.join([self.JS_TEMPLATE % js for js in self.js])
            else:
                # compress and merge the javascript files
                filename = 'jsmerge-%s' % id(''.join(self.js))
                merger = JSMergeNode(filename, self.js)
                return merger.render(None)
        return ''

def get_resource_manager(obj):
    return obj['request'].resource_manager

def require_resources(*resources):
    def _decorator(view_function):
        def _add_resources(request, *args, **kwargs):
            request.resource_manager.add_resources(*resources)
            return view_function(request, *args, **kwargs)
        _decorator.__doc__ = view_function.__doc__
        _decorator.__dict__ = view_function.__dict__

        return _add_resources

    return _decorator
