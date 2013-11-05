# Filters
angular.module('antranet.filters', [])
    .filter('interpolate', ['version', (version) ->
        return (text) ->
            return String(text).replace(/\%VERSION\%/mg, version)
    ])
    .filter('getTotals', ['version', (imputations) ->
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
    ])
    .filter('sumDict', ['version', (dict) ->
        return (dict) ->
            return _.reduce(_.values(dict), (sum, num) -> parseInt(sum, 10) + parseInt(num, 10))
    ])
    .filter('mdate', ['version', (date, format) ->
        return (date, format) ->
            if date
                return moment(date).format(format)
            else
                return ""
    ])
    .filter('mfromNow', ['version', (date, without_suffix) ->
        return (date, without_suffix) ->
            if date
                return moment(date).fromNow(without_suffix or false)
            else
               return ""
    ])
