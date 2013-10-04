angular.module('antranet.directives.vimdings', []).directive('vimdings', ->
    state = {}
    state.command_mode = false
    state.command_text = ''
    state.warning = ''
    state.last_code = ''
    state.last_kd_code = ''
    state.last_ku_code = ''
    state.timeout = undefined

    return (scope, elm, attrs) ->
        redraw_warning = (command) ->
            $('#vimdings-warning').text(command + ": " + state.warning).show()
            if (state.timeout)
                clearTimeout(state.timeout)
            state.timeout = setTimeout( ->
                $('#vimdings-warning').fadeOut()
            , 3000)

        redraw_command_prompt = ->
            $('#vimdings-command-prompt').text(":" + state.command_text)

        setTargetHours = (target, value) ->
            project_id = target.parents('tr').attr('id')
            day = target.data('day')
            scope.imputations[project_id][day] = value

        elm.on 'keydown', (event) ->
            code = event.charCode || event.keyCode
            if (state.command_mode)
                # if esc
                if (code == 27)
                    event.preventDefault()
                    state.command_mode = false
                    state.command_text = ''
                    $('#vimdings-command-prompt').remove()
                # backspace
                else if (code == 8)
                    event.preventDefault()
                    state.command_text = state.command_text.slice(0, -1)
                    if (state.command_text == '')
                        state.command_mode = false
                        $('#vimdings-command-prompt').remove()
                    else
                        redraw_command_prompt()
                # enter
                else if (code == 13)
                    event.preventDefault()
                    command_splited = state.command_text.split(" ")

                    if (state['command_' + command_splited[0]]?)
                        state['command_' + command_splited[0]](event, command_splited.slice(1))
                    else
                        state.command_default(event, command_splited.slice(1))
                    state.command_text = ''
                    state.command_mode = false
                    $('#vimdings-command-prompt').remove()
                state.last_kd_code = code
            else if (event.target.tagName != "TEXTAREA")
                if (code == 8 or code == 46)
                    state.handle_x(event)
                else if (state['handle_kd_' + code]?)
                    state['handle_kd_' + code](event)
                else if (state['handle_kd_' + String.fromCharCode(code)]? && String.fromCharCode(code).length > 0)
                    state['handle_kd_' + String.fromCharCode(code)](event)
                else
                    state.handle_kd_default(event)
                state.last_kd_code = code

        elm.on 'keyup', (event) ->
            if (event.target.tagName != "TEXTAREA")
                code = event.charCode || event.keyCode
                if (code == 8 or code == 46)
                    state.handle_x(event)
                else if (state['handle_ku_' + code]?)
                    state['handle_ku_' + code](event)
                else if (state['handle_ku_' + String.fromCharCode(code)]? && String.fromCharCode(code).length > 0)
                    state['handle_ku_' + String.fromCharCode(code)](event)
                else
                    state.handle_ku_default(event)
                state.last_ku_code = code

        elm.on 'keypress', (event) ->
            code = event.charCode || event.keyCode
            if (state.command_mode)
                event.preventDefault()
                state.command_text = state.command_text + String.fromCharCode(code)
                redraw_command_prompt()
                state.last_code = code
            else if (event.target.tagName != "TEXTAREA")
                if (code == 8 or code == 46)
                    state.handle_x(event)
                else if (state['handle_' + code]?)
                    state['handle_' + code](event)
                else if (state['handle_' + String.fromCharCode(code)]?)
                    state['handle_' + String.fromCharCode(code)](event)
                else
                    state.handle_default(event)
                state.last_code = code

        # handle :
        state['handle_:'] = (event) ->
            event.preventDefault()
            state.command_mode = true
            $('body').append($('<div id="vimdings-command-prompt">:</div>"'))
            $('#vimdings-remove').remove()

        state.handle_kd_default = (event) ->

        state.handle_ku_default = (event) ->

        state.handle_default = (event) ->

        state.command_default = (event, params) ->
            if ($("div#vimdings-warning").length == 0)
                $('body').append($('<div id="vimdings-warning"></div>"'))
            state.warning = "Command not found"
            redraw_warning(state.command_text)

        # esc
        state.handle_kd_27 = (event) ->
            event.preventDefault()
            $('#help-lightbox').fadeOut()
            $('#overlay').fadeOut()

        # handle keyleft
        state.handle_kd_37 = (event) ->
            state.handle_h(event)

        # handle h (left)
        state.handle_h = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parent()
                    .parent()
                    .prev()
                    .children("span.day-imputation")
                    .children("input")
                    .focus()

        # handle keyright
        state.handle_kd_39 = (event) ->
            state.handle_l(event)

        # handle l (right)
        state.handle_l = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parent()
                    .parent()
                    .next()
                    .children("span.day-imputation")
                    .children("input")
                    .focus()

        # handle keyup
        state.handle_kd_38 = (event) ->
            state.handle_k(event)

        # handle k (up)
        state.handle_k = (event) ->
            event.preventDefault()
            target = $(event.target)
            col_index = target.parent().parent().parent().children().index(target.parent().parent()) + 1

            if (target.parent().parent().parent().prevAll(':visible'))
                target.parent()
                        .parent()
                        .parent()
                        .prevAll(':visible').first()
                        .children('td:nth-child(' + col_index + ')')
                        .children("span.day-imputation")
                        .children("input")
                        .focus()

        # handle keydown
        state.handle_kd_40 = (event) ->
            state.handle_j(event)

        # handle j (down)
        state.handle_j = (event) ->
            target = $(event.target)
            col_index = target.parent().parent().parent().children().index(target.parent().parent()) + 1

            event.preventDefault()

            if (target.parent().parent().parent().nextAll(':visible'))
                target.parent()
                        .parent()
                        .parent()
                        .nextAll(':visible').first()
                        .children('td:nth-child(' + col_index + ')')
                        .children("span.day-imputation")
                        .children("input")
                        .focus()

        # Handle y (copy)
        state.handle_y = (event) ->
            event.preventDefault()
            target = $(event.target)
            state.clipboard = target.val()

        # Handle x (cut)
        state.handle_x = (event) ->
            event.preventDefault()
            target = $(event.target)
            state.clipboard = target.val()
            scope.$apply ->
                setTargetHours(target, 0)

        # Handle p (paste)
        state.handle_p = (event) ->
            event.preventDefault()
            target = $(event.target)
            if (state.clipboard?)
                scope.$apply ->
                    setTargetHours(target, state.clipboard)

        # Handle + (increment)
        state['handle_+'] = (event) ->
            event.preventDefault()
            target = $(event.target)
            scope.$apply ->
                setTargetHours(target, parseFloat(target.val()) + 1)

        # Handle - (decrement)
        state['handle_-'] = (event) ->
            event.preventDefault()
            target = $(event.target)
            scope.$apply ->
                setTargetHours(target, parseFloat(target.val()) - 1)

        state['handle_^'] = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parents('tr').find("span.day-imputation input").first().focus()

        state['handle_?'] = (event) ->
            event.preventDefault()
            $('#help-lightbox').fadeIn()
            $('#overlay').fadeIn()

        state.handle_$ = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parents('tr').find("span.day-imputation input").last().focus()

        state.handle_H = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parents('tr').find('.hide-button').click()

        state.handle_S = (event) ->
            event.preventDefault()
            target = $(event.target)
            target.parents('tr').find('.unhide-button').click()

        state.handle_d = (event) ->
            event.preventDefault()
            if (String.fromCharCode(state.last_code) == 'd')
                target = $(event.target)
                inputs = target.parents('tr').find("span.day-imputation input")
                scope.$apply ->
                    for item in inputs
                        setTargetHours($(item), 0)

        state.command_wq = (event, params) ->
            $('.part-submit input').click()

        state['command_q!'] = (event, params) ->
            window.location.href = "/parts"

        state.command_all = (event, params) ->
            event.preventDefault()
            target = $(event.target)
            inputs = target.parents('tr').find("span.day-imputation input")
            scope.$apply ->
                for item in inputs
                    if ($(item).css('background-color') != 'rgb(245, 169, 169)')
                        setTargetHours($(item), 8)

        state.command_clear = (event, params) ->
            target = $(event.target)
            inputs = target.parents('tr').find("span.day-imputation input")

            event.preventDefault()

            scope.$apply ->
                for item in inputs
                    setTargetHours($(item), 0)

        state.command_clear_all = (event, params) ->
            target = $(event.target)
            inputs = target.parents('table').find("span.day-imputation input")

            event.preventDefault()

            scope.$apply ->
                for item in inputs
                    setTargetHours($(item), 0)

        state.command_hide = (event, params) ->
            event.preventDefault()
            $('a.hide-hidden').click()

        state.command_show = (event, params) ->
            event.preventDefault()
            $('a.show-hidden').click()

        state.handle_default = (event) ->
            code = event.charCode || event.keyCode
            if (code >= 48 and code <= 57)
            else if (code == 46)
            else
                event.preventDefault()
).directive('ngFocus', ($parse) ->
    return (scope, element, attr) ->
        fn = $parse(attr['ngFocus'])
        element.on 'focus', (event) ->
            scope.$apply () ->
                fn(scope, {$event:event})
)
