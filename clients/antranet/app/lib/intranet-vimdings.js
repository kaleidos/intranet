var VimdingsView = VimdingsBaseView.extend({
    // handle esc
    handle_kd_27: function (event) {
        event.preventDefault();
        this.help_lb.close();
    },
    // handle keyleft
    handle_kd_37: function (event) {
        this.handle_h(event);
    },
    // handle h (left)
    handle_h: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parent()
                .parent()
                .prev()
                .children("span.day-imputation")
                .children("input")
                .focus();
    },
    // handle keyright
    handle_kd_39: function (event) {
        this.handle_l(event);
    },
    // handle l (right)
    handle_l: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parent()
                .parent()
                .next()
                .children("span.day-imputation")
                .children("input")
                .focus();
    },
    // handle keyup
    handle_kd_38: function (event) {
        this.handle_k(event);
    },
    // handle k (up)
    handle_k: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        var col_index = target.parent().parent().parent().children().index(target.parent().parent()) + 1;

        if (target.parent().parent().parent().prevAll(':visible')) {
            target.parent()
                    .parent()
                    .parent()
                    .prevAll(':visible').first()
                    .children('td:nth-child(' + col_index + ')')
                    .children("span.day-imputation")
                    .children("input")
                    .focus();
        }
    },
    // handle keydown
    handle_kd_40: function (event) {
        this.handle_j(event);
    },
    // handle j (down)
    handle_j: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        var col_index = target.parent().parent().parent().children().index(target.parent().parent()) + 1;

        if (target.parent().parent().parent().nextAll(':visible')) {
            target.parent()
                    .parent()
                    .parent()
                    .nextAll(':visible').first()
                    .children('td:nth-child(' + col_index + ')')
                    .children("span.day-imputation")
                    .children("input")
                    .focus()
        }
    },
    // Handle y (copy)
    handle_y: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        this.clipboard = target.val();
    },
    // Handle x (cut)
    handle_x: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        this.clipboard = target.val();
        target.val('0');
        target.change()
    },
    // Handle p (paste)
    handle_p: function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        if (this.clipboard != undefined) {
            target.val(this.clipboard);
            target.change()
        }
    },
    // Handle + (increment)
    'handle_+': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.val(parseInt(target.val()) + 1);
        target.change();
    },
    // Handle - (decrement)
    'handle_-': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.val(parseInt(target.val()) - 1);
        target.change();
    },
    'handle_^': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parents('tr').find("span.day-imputation input").first().focus();
    },
    'handle_?': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        this.help_lb.open();
    },
    'handle_$': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parents('tr').find("span.day-imputation input").last().focus();
    },
    'handle_H': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parents('tr').find('.hide-button').click();
    },
    'handle_S': function (event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        target.parents('tr').find('.unhide-button').click();
    },
    'handle_d': function (event) {
        event.preventDefault();
        if (String.fromCharCode(this.last_code) == 'd') {
            var target = $(event.currentTarget);
            inputs = target.parents('tr').find("span.day-imputation input");
            _.each(inputs, function (item) {
                $(item).val('0');
                $(item).change();
            });
        }
    },
    command_wq: function (event, params) {
        $('.part-submit input').click();
    },
    'command_q!': function (event, params) {
        window.location.href = "/parts";
    },
    'command_all': function (event, params) {
        event.preventDefault();
        var target = $(event.currentTarget);
        inputs = target.parents('tr').find("span.day-imputation input");
        _.each(inputs, function (item) {
            if ($(item).css('background-color')!='rgb(245, 169, 169)') {
                $(item).val('8');
                $(item).change();
            }
        });
    },
    'command_clear': function (event, params) {
        event.preventDefault();
        var target = $(event.currentTarget);
        inputs = target.parents('tr').find("span.day-imputation input");
        _.each(inputs, function (item) {
            $(item).val('0');
            $(item).change();
        });
    },
    'command_clear_all': function (event, params) {
        event.preventDefault();
        var target = $(event.currentTarget);
        inputs = target.parents('table').find("span.day-imputation input");
        _.each(inputs, function (item) {
            $(item).val('0');
            $(item).change();
        });
    },
    'command_hide': function (event, params) {
        event.preventDefault();
        $('a.hide-hidden').click()
    },
    'command_show': function (event, params) {
        event.preventDefault();
        $('a.show-hidden').click()
    },
    handle_default: function (event) {
        if (event.which < 48 || event.which > 57) {
            event.preventDefault();
        }
    }
});
