import os

from django.conf import settings
from django.core.management.base import AppCommand, CommandError


class Command(AppCommand):

    def handle_app(self, app, **options):
        app_name = app.__name__.split(".")[-2]
        app_dir = os.path.dirname(app.__file__)
        media_dir = os.path.join(app_dir, 'media')
        if not os.path.isdir(media_dir):
            raise CommandError("The application '%s' does not have a media "
                               "directory to install" % app_name)

        media_root = settings.MEDIA_ROOT

        try:
            os.symlink(media_dir, os.path.join(media_root, app_name))
        except OSError:
            raise CommandError("The media of '%s' is already installed"
                               % app_name)
