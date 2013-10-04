angular.module('antranet.services.storage', ['antranet.config'], ($provide) ->
    $provide.factory('storage', ['$rootScope', ($rootScope) ->
        service = {}
        helpers = {}

        service.get = (key) ->
            serializedValue = sessionStorage.getItem(key)
            if (serializedValue == null)
                return serializedValue

            return JSON.parse(serializedValue)

        service.set = (key, val) ->
            if (_.isObject(key))
                _.each key, (val, key) ->
                    service.set(key, val)
            else
                sessionStorage.setItem(key, JSON.stringify(val))

        service.remove = (key) ->
            sessionStorage.removeItem(key)

        service.clear = ->
            sessionStorage.clear()

        return service
    ])
)
