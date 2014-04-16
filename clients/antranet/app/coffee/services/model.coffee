ModelProvider = ($q, $http, apiUrl, $rootScope) ->
    headers = ->
        token = $rootScope.token_auth
        if token
            return {"X-SESSION-TOKEN": token}
        return {}

    class Model
        constructor: (name, data, dataTypes) ->
            @._attrs = data
            @._name = name
            @._dataTypes = dataTypes

            @.setAttrs(data)
            @.initialize()

        applyCasts: ->
            for attrName, castName of @._dataTypes
                castMethod = service.casts[castName]
                if not castMethod
                    continue

                @._attrs[attrName] = castMethod(@._attrs[attrName])

        getIdAttrName: ->
            return "id"

        getUrl: ->
            return "#{apiUrl(@_name)}#{@.getAttrs()[@.getIdAttrName()]}/"

        getAttrs: (patch=false) ->
            if patch
                return _.extend({}, @._modifiedAttrs)
            return _.extend({}, @._attrs, @._modifiedAttrs)

        setAttrs: (attrs) ->
            @._attrs = attrs
            @._modifiedAttrs = {}

            @.applyCasts()
            @._isModified = false

        setAttr: (name, value) ->
            @._modifiedAttrs[name] = value
            @._isModified = true

        initialize: () ->
            self = @

            getter = (name) ->
                return ->
                    if name.substr(0,2) == "__"
                        return self[name]

                    if name not in _.keys(self._modifiedAttrs)
                        return self._attrs[name]

                    return self._modifiedAttrs[name]

            setter = (name) ->
                return (value) ->
                    if name.substr(0,2) == "__"
                        self[name] = value
                        return

                    if self._attrs[name] != value
                        self._modifiedAttrs[name] = value
                        self._isModified = true
                    else
                        delete self._modifiedAttrs[name]

                    return

            _.each @_attrs, (value, name) ->
                options =
                    get: getter(name)
                    set: setter(name)
                    enumerable: true
                    configurable: true

                Object.defineProperty(self, name, options)

        serialize: () ->
            data =
                "data": _.clone(@_attrs)
                "name": @_name

            return JSON.stringify(data)

        isModified: () ->
            return this._isModified

        markSaved: () ->
            @._isModified = false
            @._attrs = @.getAttrs()
            @._modifiedAttrs = {}

        revert: () ->
            @_modifiedAttrs = {}
            @_isModified = false

        delete: () ->
            defered = $q.defer()
            self = @

            params =
                method: "DELETE"
                url: @getUrl()
                headers: headers()

            promise = $http(params)
            promise.success (data, status) ->
                defered.resolve(self)

            promise.error (data, status) ->
                defered.reject(self)

            return defered.promise

        save: (patch=true, extraParams) ->
            self = @
            defered = $q.defer()

            if not @isModified() and patch
                defered.resolve(self)
                return defered.promise

            params =
                url: @getUrl()
                headers: headers(),

            if patch
                params.method = "PATCH"
            else
                params.method = "PUT"

            params.data = JSON.stringify(@.getAttrs(patch))

            params = _.extend({}, params, extraParams)

            promise = $http(params)
            promise.success (data, status) ->
                self._isModified = false
                self._attrs = _.extend(self.getAttrs(), data)
                self._modifiedAttrs = {}

                self.applyCasts()
                defered.resolve(self)

            promise.error (data, status) ->
                defered.reject(data)

            return defered.promise

        refresh: () ->
            defered = $q.defer()
            self = @

            params =
                method: "GET",
                url: @getUrl()
                headers: headers()

            promise = $http(params)
            promise.success (data, status) ->
                self._modifiedAttrs = {}
                self._attrs = data
                self._isModified = false
                self.applyCasts()

                defered.resolve(self)

            promise.error (data, status) ->
                defered.reject([data, status])

            return defered.promise

        @desSerialize = (sdata) ->
            ddata = JSON.parse(sdata)
            model = new Model(ddata.url, ddata.data)
            return model

    service = {}
    service.make_model = (name, data, cls=Model, dataTypes={}) ->
        return new cls(name, data, dataTypes)

    service.create = (name, data, cls=Model, dataTypes={}, extraParams={}) ->
        defered = $q.defer()

        params =
            method: "POST"
            url: apiUrl(name)
            headers: headers()
            data: JSON.stringify(data)
            params: extraParams

        promise = $http(params)
        promise.success (_data, _status) ->
            defered.resolve(service.make_model(name, _data, cls, dataTypes))

        promise.error (data, status) ->
            defered.reject(data)

        return defered.promise

    service.cls = Model
    service.casts =
        int: (value) ->
            return parseInt(value, 10)

        float: (value) ->
            return parseFloat(value, 10)

    return service

module = angular.module('antranet.services.model', [])
module.factory('$model', ['$q', '$http', 'apiUrl', '$rootScope', ModelProvider])
