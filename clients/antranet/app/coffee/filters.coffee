# Filters

module = angular.module('antranet.filters', [])


interpolate = ->
    return (text) ->
        return String(text).replace(/\%VERSION\%/mg, version)

module.filter("interpolate", interpolate)


getTotals = ->
    return (imputations) ->
        totals = {}

        if (not imputations?)
            return []

        firstProjectId = _.keys(imputations)[0]
        _.each _.keys(imputations[firstProjectId]), (id) ->
            # Removing angular private attributes
            if id[0] != '$'
                totals[id] = 0

        for project in _.values(imputations)
            _.each project, (hours, id) ->
                # Removing angular private attributes
                if id[0] != '$'
                    totals[id] += parseInt(hours, 10)

        return totals

module.filter("getTotals", getTotals)


sumDict = ->
    return (dict) ->
        return _.reduce(_.values(dict), (sum, num) -> parseInt(sum, 10) + parseInt(num, 10))

module.filter("sumDict", sumDict)


mdate = ->
    return (date, format) ->
        if date
            return moment(date).format(format)
        else
            return ""

module.filter("mdate", mdate)


mfromNow = ->
    return (date, without_suffix) ->
        if date
            return moment(date).fromNow(without_suffix or false)
        else
           return ""

module.filter("mfromNow", mfromNow)


nl2br = ->
    return (msg, is_xhtml) ->
        breakTag = if is_xhtml? then '<br />' else '<br>'

        msg = "#{msg}".replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, "$1#{breakTag}$2")
        return msg

module.filter("nl2br", nl2br)
