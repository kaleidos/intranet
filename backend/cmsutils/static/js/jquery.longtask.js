(function ($) {


$.fn.longtask = function (settings) {

    var settings = $.extend({
        polling_frequency: 1000, // 1 second
        auto_start: false,
        GET_data: {},
        status_url: null
    }, settings);

    return this.each(function () {

        var container = $(this);
        
        var local_settings = $.extend({}, settings);
        
        $(".task_completed", container).hide();
        
        var monitor_interval = null;
        var progress_bar_width = $('.progress_bar', container).width();

        // Monitor the import status doing polling
        function monitor_progress() {
            $.getJSON(local_settings.status_url, local_settings.GET_data, function(data) {
                if (data.finished == true) {
                    clearInterval(monitor_interval);
                }
                $('.progress_bar', container).html('<p>' + (data.progress * 100) + '%</p>');
                $('.progress_bar p', container).width(data.progress * progress_bar_width);
                if (data.errors.length > 0) {
                    $('.errors', container).empty();
                    var errors = $.map(data.errors, function (error, i) {
                        return '<li>' + error + '</li>';
                    });
                    $('.errors', container).append(errors.join(''));
                }

                if (data.progress >= 1.0) { // Task finished
                    $(".task_completed", container).slideDown();
                }
            });
        }

        // Start the task automatically if the settings say so
        if (local_settings.auto_start && local_settings.status_url != null) {
            monitor_interval = setInterval(monitor_progress,
                                           local_settings.polling_frequency);
            monitor_progress();
        } else {
            // Start the task when submitting the form
            $(this).submit(function () {
                var url = $(this).attr("action");

                $.post(url, {}, function (data) {
                    local_settings = $.extend(local_settings, data);
                    
                    $("input", container).attr("disabled", "disabled");

                    monitor_interval = setInterval(monitor_progress,
                                                   local_settings.polling_frequency);
                    monitor_progress();
                }, "json");

                return false;
            });
        }

    }); // end of each
}; // end of smartsearch

})(jQuery);
