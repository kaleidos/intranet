
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
            defaultHttpParams.url = "#{apiUrl(name)}#{id}"
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
            page_size: 0
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
            defaultHttpParams.url = "#{apiUrl(name)}#{id}"
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

    makeAction = (name, action, type, id, params, options, cls) ->
        defaultHttpParams = {method: type, headers: headers()}

        if id
            url = "#{apiUrl(name)}#{id}"
        else
            url = "#{apiUrl(name)}"
        if action
            url = "#{url}/#{action}/"

        defaultHttpParams.url = url

        if not _.isEmpty(params)
            defaultHttpParams.params = params

        httpParams =  _.extend({}, defaultHttpParams, options)

        defered = $q.defer()

        promise = $http(httpParams)
        promise.success (data, status) ->
            defered.resolve(data)

        promise.error (data, status) ->
            defered.reject()

        return defered.promise


    ## Custom services
    #################

    # Holidays

    service.listHolidaysYears = (params={}) ->
        return queryMany("holidays-years", params)

    service.listHolidaysRequests = (params={}) ->
        return queryMany("holidays-requests", params)


    # Talks

    service.listPaginatedTalks = (params={}) ->
        return queryPaginatedMany("talks", params)

    service.setTalkIWant = (id) ->
        return makeAction("talks", "i_want", "POST", id)

    service.setTalkINotWant = (id) ->
        return makeAction("talks", "i_want", "DELETE", id)

    service.setTalkITalk = (id) ->
        return makeAction("talks", "i_talk", "POST", id)

    service.setTalkINotTalk = (id) ->
        return makeAction("talks", "i_talk", "DELETE", id)

    service.setTalkersAreReady = (id) ->
        return makeAction("talks", "i_talkers_are_ready", "POST", id)

    service.setTalkersAreNotReady = (id) ->
        return makeAction("talks", "i_talkers_are_not_ready", "POST", id)


    return service


module = angular.module("antranet.services.resource", [])
module.factory("resource", ["$http", "apiUrl", "$q", "$model", "$rootScope", ResourceProvider])
