import os

try:
    import threading
    _threading = threading
except ImportError:
    import dummy_threading
    _threading = dummy_threading

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson


class LongTask(_threading.Thread):

    def __init__(self, size=100, log_file=None):
        super(LongTask, self).__init__()
        self.log_file = log_file
        self.finished = False
        self.size = size
        self.progress = 0
        self.errors = []

        if self.log_file is not None:
            self.log = file(self.log_file, 'w')

    def get_progress(self):
        return float(self.progress) / float(self.size)

    def is_finished(self):
        return self.finished

    def get_errors(self):
        return self.errors

    def get_log_file_relative(self):
        relative_path = self.log_file.replace(settings.LOGS_DIR, '')
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        return relative_path
    
    def finish(self):
        self.finished = True
        if self.log_file is not None:
            self.log.write('\n'.join(self.errors))
            self.log.close()



class BlockingTask(LongTask):
    """A long task that can only have one instance at a given time"""
    
    def __init__(self, lock_file='', *args, **kwargs):
        super(BlockingTask, self).__init__(*args, **kwargs)
        
        self.lock_file = lock_file
        file(self.lock_file, 'w').close() # create the lock file

    def finish(self):
        super(BlockingTask, self).finish()
        os.unlink(self.lock_file)


def long_task_status(request, task_name):
    """Ajax based view to monitor a long task"""
    for thread in _threading.enumerate():
        if thread.getName() == task_name:
            task = thread
            break
    else:
        task = None
    data = {}
    if task is not None:
        data['progress'] = task.get_progress()
        data['finished'] = task.is_finished()
        data['errors'] = task.get_errors()
    else:
        data['progress'] = 1.0
        data['finished'] = True
        data['errors'] = []

        log_file = request.GET.get('log_file', None)
        if log_file is not None:
            file_name = os.path.join(settings.LOGS_DIR, log_file)
            if os.path.exists(file_name):
                f = file(file_name, 'r')
                data['errors'] = [line.strip() for line in f.readlines()]
                f.close()
                os.unlink(file_name)

    return HttpResponse(simplejson.dumps(data), 'text/javascript')
