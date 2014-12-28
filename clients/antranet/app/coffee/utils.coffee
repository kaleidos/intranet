antranet = @.antranet

antranet.nl2br = (str) =>
    breakTag = '<br />'
    return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2')

antranet.bindMethods = (object) =>
    dependencies = _.keys(object)

    methods = []

    _.forIn object, (value, key) =>
        if key not in dependencies
            methods.push(key)

    _.bindAll(object, methods)

antranet.bindOnce = (scope, attr, continuation) =>
    val = scope.$eval(attr)
    if val != undefined
        return continuation(val)

    delBind = null
    delBind = scope.$watch attr, (val) ->
        return if val is undefined
        continuation(val)
        delBind() if delBind


antranet.mixOf = (base, mixins...) ->
    class Mixed extends base

    for mixin in mixins by -1 #earlier mixins override later ones
        for name, method of mixin::
            Mixed::[name] = method
    Mixed


antranet.trim = (data, char) ->
    return _.str.trim(data, char)


antranet.slugify = (data) ->
    return _.str.slugify(data)


antranet.unslugify = (data) ->
    if data
        return _.str.capitalize(data.replace(/-/g, ' '))
    return data


antranet.toggleText = (element, texts) ->
    nextTextPosition = element.data('nextTextPosition')
    nextTextPosition = 0 if not nextTextPosition? or nextTextPosition >= texts.length
    text = texts[nextTextPosition]
    element.data('nextTextPosition', nextTextPosition + 1)
    element.text(text)


antranet.groupBy = (coll, pred) ->
    result = {}
    for item in coll
        result[pred(item)] = item

    return result


antranet.timeout = (wait, continuation) ->
    return window.setTimeout(continuation, wait)


antranet.cancelTimeout = (timeoutVar) ->
    window.clearTimeout(timeoutVar)


antranet.scopeDefer = (scope, func) ->
    _.defer =>
        scope.$apply(func)


antranet.toString = (value) ->
    if _.isNumber(value)
        return value + ""
    else if _.isString(value)
        return value
    else if _.isPlainObject(value)
        return JSON.stringify(value)
    else if _.isUndefined(value)
        return ""
    return value.toString()


antranet.joinStr = (str, coll) ->
    return _.str.join(str, coll)


antranet.debounce = (wait, func) ->
    return _.debounce(func, wait, {leading: true, trailing: false})


antranet.debounceLeading = (wait, func) ->
    return _.debounce(func, wait, {leading: false, trailing: true})


antranet.startswith = (str1, str2) ->
    return _.str.startsWith(str1, str2)


antranet.sizeFormat = (input, precision=1) ->
    if isNaN(parseFloat(input)) or not isFinite(input)
        return "-"

    if input == 0
        return "0 bytes"

    units = ["bytes", "KB", "MB", "GB", "TB", "PB"]
    number = Math.floor(Math.log(input) / Math.log(1024))
    if number > 5
        number = 5
    size = (input / Math.pow(1024, number)).toFixed(precision)
    return  "#{size} #{units[number]}"
