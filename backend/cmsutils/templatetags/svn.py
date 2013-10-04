from django.conf import settings
from django.template import Library
from django.utils.version import get_svn_revision

register = Library()


@register.simple_tag
def current_svn_rev():
    """Get the current SVN revision of the project."""
    if not settings.DEBUG:
        return ""
    project_dir = getattr(settings, 'SVNDIR', None) or getattr(settings, 'BASEDIR', None)
    if project_dir:
        if isinstance(project_dir, list):
            return ', '.join([get_svn_revision(path) for path in project_dir])
        else:
            return get_svn_revision(project_dir)
    else:
        return 'Define settings.SVNDIR or settings.BASEDIR'
