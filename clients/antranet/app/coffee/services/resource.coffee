
ResourceProvider = ($http, apiUrl, $q, $model, $rootScope) ->
    service = {}

    headers = () ->
        data = {}
        token = $rootScope.token_auth

        data["X-SESSION-TOKEN"] = token if token
        return data

    queryOne = (name, id, params, options, cls) ->
        defaultHttpParams = {method: "GET", headers:  headers()}

        if id
            defaultHttpParams.url = "#{apiUrl(name)}/#{id}"
        else
            defaultHttpParams.url = "#{apiUrl(name)}"

        if not _.isEmpty(params)
            defaultHttpParams.params = params

        httpParams =  _.extend({}, defaultHttpParams, options)

        defered = $q.defer()

        promise = $http(httpParams)
        promise.success (data, status) ->
            defered.resolve($model.make_model(name, data, cls))

        promise.error (data, status) ->
            defered.reject()

        return defered.promise

    queryMany = (name, params, options, urlParams) ->
        defaultHttpParams = {
            method: "GET",
            headers:  headers(),
            url: apiUrl(name, urlParams)
        }

        if not _.isEmpty(params)
            defaultHttpParams.params = params

        httpParams = _.extend({}, defaultHttpParams, options)
        defered = $q.defer()

        promise = $http(httpParams)
        promise.success (data, status) ->
            models = _.map data, (attrs) -> $model.make_model(name, attrs)
            defered.resolve(models)

        promise.error (data, status) ->
            defered.reject(data, status)

        return defered.promise

    queryPaginatedMany = (name, params, options, cls, datatypes) ->
        defauts = {method: "GET", headers:  headers()}
        current = {url: apiUrl(name), params: params or {}}

        httpParams = _.extend({}, defauts, options, current)
        defered = $q.defer()

        promise = $http(httpParams)
        promise.success (data, status) ->
            result = {}
            result.models = _.map(data.results, (attrs) -> $model.make_model(name, attrs, cls, datatypes))
            result.count = data.count
            result.next = data.next
            result.prev = data.previous
            result.counters = data.counters or {}
            defered.resolve(result)

        promise.error (data, status) ->
            defered.reject(data, status)

        return defered.promise

    queryRaw = (name, id, params, options, cls) ->
        defaultHttpParams = {method: "GET", headers:  headers()}

        if id
            defaultHttpParams.url = "#{apiUrl(name)}/#{id}"
        else
            defaultHttpParams.url = "#{apiUrl(name)}"

        if not _.isEmpty(params)
            defaultHttpParams.params = params

        httpParams =  _.extend({}, defaultHttpParams, options)

        defered = $q.defer()

        promise = $http(httpParams)
        promise.success (data, status) ->
            defered.resolve(data, cls)

        promise.error (data, status) ->
            defered.reject()

        return defered.promise


    ## Custom services
    #################

    # Holidays

    service.listHolidaysYears = ->
        return queryMany("holidays-years")

    service.listHolidaysRequests = (params={}) ->
        return queryMany("holidays-requests", params)


    return service


module = angular.module('antranet.services.resource', [])
module.factory('resource', ['$http', 'apiUrl', '$q', '$model', '$rootScope', ResourceProvider])
