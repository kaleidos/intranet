import logging

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.utils import simplejson

# Add this to your settings.py:
#
# from django.conf import global_settings
# FILE_UPLOAD_HANDLERS = ('cmsutils.upload_handlers.UploadProgressCachedHandler', ) + global_settings.FILE_UPLOAD_HANDLERS
#
# Add a new url to retrieve the upload progress, for instance, if you have a url
# like this:
#     (r'^upload/$', 'yourapp.views.upload_form'),
# add an extra URL like this one:
#     (r'^upload/progress/$', 'cmsutils.upload_handlers.upload_progress'),    # (1)
#
# In your template you should use some javascript to retrieve through AJAX calls to 
# that URL (1) the progress status. You get a JSON object with two fields: size and 
# received. They contains the file size, and the current recieved data size, 
# respectively. Then, you can do whatever you want using your favourite JS toolkit.
# When submitting the form you must send an upload UUID (unique identifier) called
# X-Progress-ID that will be used by the upload handler and the view to identify 
# the current upload. Then, when asking the view, you also send that var.
#
# For better understanding, lets see an example:
#
# This is an example using jQuery that displays a progress bar, with the title of 
# the file, and the percentage of upload.
# 
#   Some styles...
#   --------------
#   <style>
#    #progress_container {
#	    font-size: .9em;
#	    width: 100%;
#	    height: 1.25em;
#	    position: relative;
#	    margin: 3em 0;
#	    display: none;
#    }
#
#    #progress_filename {
#	    font-size: 1.3em;
#	    width: 100%;
#    }
#
#    #progress_bar {
#	    width: 100%;
#	    border: 1px inset #999;
#    }
#
#    #progress_indicator {
#	    background: #79f;
#	    width: 0;
#	    height: 15px;
#    }  
#    </style> 
#
#    A few of HTML
#    -------------
#    <form id="upload_form" action="" method="post" enctype="multipart/form-data">
#      {{ form }}
#      <input type="submit" value="{{ form.button_label }}" />
#    </form>
#
#    <div id="progress_container">
#       <img src="{{MEDIA_URL}}img/ajax-loader.gif" style="float:left" />
#	    <div id="progress_filename">Uploading file...</div>
#	    <div id="progress_bar">
#		    <div id="progress_indicator"></div>
#	    </div>
#    </div>
#
#    A few of JS
#    ------------
#
#    <script type="text/javascript" charset="utf-8">
#    // Generate 32 char random uuid 
#    function gen_uuid() {
#	    var uuid = "";
#	    for (var i = 0; i < 32; i++) {
#		    uuid += Math.floor(Math.random() * 16).toString(16);
#	    }
#	    return uuid;
#    }
#
#    var uuid;
#    var progress_url = '{% url multimedia.views.video_upload_progress %}';
#    var filename;
#    var freq = 300;
#    var intervalID;
#
#    function update_progress_info() {
#	    $.getJSON(progress_url, 
#		    {
#		    'X-Progress-ID': uuid
#		    },
#		    function(data, status) {
#			    if (data) {
#				    console.log(data);
#				    if (data.received && data.size) {
#					    var progress = parseInt(data.received) / parseInt(data.size);
#					    var width = $('#progress_container').width();
#					    var progress_width = Math.floor(width * progress);
#					    $("#progress_indicator").width(progress_width);
#					    $("#progress_filename").text(gettext('Uploading') + ' ' + filename + ': ' + parseInt(progress * 100) + '%');
#				    }
#				    if (progress == 1 || data.state == 'done') {
#					    window.clearInterval(intervalID);
#					    $("#progress_filename").text(gettext('Upload of') + ' ' + filename + ' ' + gettext('complete. Processing...'));
#				    }
#			    }
#		    }
#	    );
#    };
#
#    $(document).ready(function() 
#	    { 
#		
#		    $("#upload_form").submit(
#			    function(eventObject) {
#				    if ($.data(this, 'submitted')) return false;
#
#				    uuid = gen_uuid();
#				    filename = $("#id_video_file").val().split(/[\/\\]/).pop();
#				    this.action += (this.action.indexOf('?') == -1 ? '?': '&') + 'X-Progress-ID=' + uuid;
#
#				    $("#upload_form").hide();
#				    $("#progress_filename").text(gettext('Uploading') + ' ' + filename + "...");
#				    $("#upload_form").slideUp(); 
#				    $("#progress_container").fadeIn(); 
#				
#				    intervalID = window.setInterval(update_progress_info, freq);
#
#				    $.data(this, 'submitted', true);
#			    }
#		    );
#	    }
#    );
#    </script>


class UploadProgressCachedHandler(MemoryFileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.handle_raw_input')
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']
        if self.progress_id:
            self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
            cache.set(self.cache_key, {
                'size': self.content_length,
                'received': 0
            })
            if settings.DEBUG:
                logger.debug('Initialized cache with %s' % cache.get(self.cache_key))
        else:
            logging.getLogger('UploadProgressCachedHandler').error("No progress ID!")

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.receive_data_chunk')
        if self.cache_key:
            data = cache.get(self.cache_key)
            data['received'] += self.chunk_size
            cache.set(self.cache_key, data)
            if settings.DEBUG:
                logger.debug('Updated cache with %s' % data)
        return raw_data
    
    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.upload_complete')
        if settings.DEBUG:
            logger.debug('Upload complete for %s' % self.cache_key)
        if self.cache_key:
            cache.delete(self.cache_key)


def upload_progress(request):
    """
    Sample view that checks the upload progress from cache and sends it to the client.
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    elif 'X-Progress-Id' in request.GET:
        # stupid Safari
        progress_id = request.META['X-Progress-Id']
    elif 'X-Progress-Id' in request.META:
        # stupid Safari
        progress_id = request.META['X-Progress-Id']
    if progress_id:        
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        
        data = cache.get(cache_key)
        json = simplejson.dumps(data)
        return HttpResponse(json)
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


