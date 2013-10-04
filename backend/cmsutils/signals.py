from django.dispatch import Signal

pre_rebuild_db = Signal()
post_rebuild_db_before_syncdb = Signal()
post_rebuild_db = Signal()
